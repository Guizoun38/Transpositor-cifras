import re

from domain.errors import InvalidChordError, InvalidKeyError
from domain.models import NashvilleChord

SHARP_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLAT_NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
NOTE_TO_SEMITONE = {"C": 0, "B#": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
                    "E": 4, "Fb": 4, "F": 5, "E#": 5, "F#": 6, "Gb": 6, "G": 7,
                    "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11, "Cb": 11}
FLAT_KEYS = {"F", "Bb", "Eb", "Ab", "Db", "Gb", "Cb", "Dm", "Gm", "Cm", "Fm", "Bbm", "Ebm", "Abm"}
TONES = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
CHORD_RE = re.compile(r"^([A-G](?:#|b)?)([^/\s]*?)(?:/([A-G](?:#|b)?))?$")
NASHVILLE_RE = re.compile(r"^([b#]?)([1-7])([^/\s]*?)(?:/([b#]?)([1-7]))?$")
TOM_RE = re.compile(r"(Tom\s+)([A-G](?:#|b)?m?)\b", re.IGNORECASE)
ORIGINAL_KEY_CONTEXT_RE = re.compile(
    r"\b(?:artista|banda|ritmo|bpm|tom\s+original)\b",
    re.IGNORECASE,
)
STRUCTURAL_SLASH_RE = re.compile(r"^/+$")


def _root(key: str) -> str:
    root = key[:-1] if key.endswith("m") else key
    if root not in NOTE_TO_SEMITONE:
        raise InvalidKeyError(f"Tonalidade inválida: {key}")
    return root


def uses_flats(key: str) -> bool:
    _root(key)
    return key in FLAT_KEYS or _root(key) in FLAT_KEYS


def parse_chord(value: str):
    match = CHORD_RE.fullmatch(value)
    if not match:
        raise InvalidChordError(f"Acorde inválido: {value}")
    return match.groups()


def transpose_chord(chord: str, source_key: str, target_key: str) -> str:
    root, quality, bass = parse_chord(chord)
    diff = (NOTE_TO_SEMITONE[_root(target_key)] - NOTE_TO_SEMITONE[_root(source_key)]) % 12
    names = FLAT_NAMES if uses_flats(target_key) else SHARP_NAMES
    result = names[(NOTE_TO_SEMITONE[root] + diff) % 12] + quality
    if bass:
        result += "/" + names[(NOTE_TO_SEMITONE[bass] + diff) % 12]
    return result


def _degree_candidates(key: str):
    tonic = NOTE_TO_SEMITONE[_root(key)]
    return [(tonic + offset) % 12 for offset in (0, 2, 4, 5, 7, 9, 11)]


def _pitch_to_degree(pitch: int, key: str):
    scale = _degree_candidates(key)
    if pitch in scale:
        return "", scale.index(pitch) + 1
    candidates = []
    for degree, natural in enumerate(scale, 1):
        delta = (pitch - natural) % 12
        if delta == 1:
            candidates.append(("#", degree))
        elif delta == 11:
            candidates.append(("b", degree))
    flat = next((c for c in candidates if c[0] == "b"), None)
    return flat or candidates[0]


def chord_to_nashville(chord: str, source_key: str) -> str:
    root, quality, bass = parse_chord(chord)
    accidental, degree = _pitch_to_degree(NOTE_TO_SEMITONE[root], source_key)
    result = f"{accidental}{degree}{quality}"
    if bass:
        bass_accidental, bass_degree = _pitch_to_degree(NOTE_TO_SEMITONE[bass], source_key)
        result += f"/{bass_accidental}{bass_degree}"
    return result


def parse_nashville(value: str) -> NashvilleChord:
    match = NASHVILLE_RE.fullmatch(value)
    if not match:
        raise InvalidChordError(f"Grau Nashville inválido: {value}")
    accidental, degree, quality, bass_accidental, bass_degree = match.groups()
    return NashvilleChord(int(degree), accidental, quality, int(bass_degree) if bass_degree else None, bass_accidental or "")


def _degree_pitch(degree: int, accidental: str, key: str) -> int:
    pitch = _degree_candidates(key)[degree - 1]
    return (pitch + {"b": -1, "#": 1, "": 0}[accidental]) % 12


def nashville_to_chord(value: str, target_key: str) -> str:
    chord = parse_nashville(value)
    default_names = FLAT_NAMES if uses_flats(target_key) else SHARP_NAMES
    names = FLAT_NAMES if chord.accidental == "b" else SHARP_NAMES if chord.accidental == "#" else default_names
    result = names[_degree_pitch(chord.degree, chord.accidental, target_key)] + chord.quality
    if chord.bass_degree:
        bass_names = FLAT_NAMES if chord.bass_accidental == "b" else SHARP_NAMES if chord.bass_accidental == "#" else default_names
        result += "/" + bass_names[_degree_pitch(chord.bass_degree, chord.bass_accidental, target_key)]
    return result


def is_chord_line(text: str) -> bool:
    stripped = text.strip()
    if not stripped or stripped.startswith("[") or TOM_RE.search(stripped):
        return False
    tokens = [
        token
        for token in re.findall(r"[^\s|]+", stripped)
        if not STRUCTURAL_SLASH_RE.fullmatch(token)
    ]
    if not tokens:
        return False
    valid = sum(bool(CHORD_RE.fullmatch(t)) for t in tokens)
    return valid >= (1 if len(tokens) <= 2 else 2) and valid / len(tokens) >= 0.6


def is_nashville_line(text: str) -> bool:
    stripped = text.strip()
    if not stripped or stripped.startswith("[") or re.search(r"\b(?:bpm|tom)\b", stripped, re.I) or re.fullmatch(r"\s*4/4\s*", stripped):
        return False
    tokens = [
        token
        for token in re.findall(r"[^\s|]+", stripped)
        if not STRUCTURAL_SLASH_RE.fullmatch(token)
    ]
    return bool(tokens) and sum(bool(NASHVILLE_RE.fullmatch(t)) for t in tokens) / len(tokens) >= 0.7


def is_original_key_metadata(text: str) -> bool:
    """Identify the descriptive source-key line, which must stay unchanged."""
    return bool(TOM_RE.search(text) and ORIGINAL_KEY_CONTEXT_RE.search(text))


def replace_key(text: str, target_key: str) -> str:
    _root(target_key)
    return TOM_RE.sub(lambda m: m.group(1) + target_key, text)
