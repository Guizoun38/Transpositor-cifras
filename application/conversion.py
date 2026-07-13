import re

from application.models import ConversionRequest
from domain.errors import InvalidConversionRequestError
from domain.models import ConversionMode
from domain.music import (chord_to_nashville, is_chord_line,
                          is_nashville_line, is_original_key_metadata,
                          nashville_to_chord, replace_key, transpose_chord)


def validate_request(request: ConversionRequest):
    if request.mode is ConversionMode.CHORDS_TO_CHORDS and (not request.source_key or not request.target_key):
        raise InvalidConversionRequestError("Indique o tom original e o novo tom.")
    if request.mode is ConversionMode.CHORDS_TO_NASHVILLE and not request.source_key:
        raise InvalidConversionRequestError("Indique o tom original.")
    if request.mode is ConversionMode.NASHVILLE_TO_CHORDS and not request.target_key:
        raise InvalidConversionRequestError("Indique o tom de destino.")


def convert_musical_text(text: str, request: ConversionRequest) -> str:
    validate_request(request)
    if request.mode is not ConversionMode.CHORDS_TO_NASHVILLE and re.search(r"\bTom\s+", text, re.I):
        if is_original_key_metadata(text):
            return text
        return replace_key(text, request.target_key)
    chord_mode = request.mode in (ConversionMode.CHORDS_TO_CHORDS, ConversionMode.CHORDS_TO_NASHVILLE)
    if chord_mode and not is_chord_line(text):
        return text
    if not chord_mode and not is_nashville_line(text):
        return text
    converter = {
        ConversionMode.CHORDS_TO_CHORDS: lambda token: transpose_chord(token, request.source_key, request.target_key),
        ConversionMode.CHORDS_TO_NASHVILLE: lambda token: chord_to_nashville(token, request.source_key),
        ConversionMode.NASHVILLE_TO_CHORDS: lambda token: nashville_to_chord(token, request.target_key),
    }[request.mode]
    pattern = r"[A-G](?:#|b)?[^\s|/]*(?:/[A-G](?:#|b)?)?" if chord_mode else r"[b#]?[1-7][^\s|/]*(?:/[b#]?[1-7])?"
    def repl(match):
        try:
            return converter(match.group())
        except ValueError:
            return match.group()
    return re.sub(pattern, repl, text)
