from dataclasses import dataclass
from enum import Enum


class ConversionMode(Enum):
    CHORDS_TO_CHORDS = "chords_to_chords"
    CHORDS_TO_NASHVILLE = "chords_to_nashville"
    NASHVILLE_TO_CHORDS = "nashville_to_chords"


@dataclass(frozen=True)
class Chord:
    root: str
    quality: str = ""
    bass: str | None = None


@dataclass(frozen=True)
class NashvilleChord:
    degree: int
    accidental: str = ""
    quality: str = ""
    bass_degree: int | None = None
    bass_accidental: str = ""
