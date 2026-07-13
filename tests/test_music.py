import pytest

from application.conversion import convert_musical_text
from application.models import ConversionRequest
from domain.models import ConversionMode
from domain.music import (chord_to_nashville, is_chord_line, is_nashville_line,
                          nashville_to_chord, replace_key, transpose_chord)


@pytest.mark.parametrize("chord, expected", [("Bbm7", "Dm7"), ("Ebsus4", "Gsus4"),
                                              ("Dbsus4", "Fsus4"), ("Eb/G", "G/B"), ("Ab9", "C9")])
def test_transpose_from_ab_to_c(chord, expected):
    assert transpose_chord(chord, "Ab", "C") == expected


@pytest.mark.parametrize("text", ["A porta está aberta", "E abri meu coração", "[Refrão]", "[Ponte] 2x"])
def test_lyrics_and_sections_are_not_chord_lines(text):
    assert is_chord_line(text) is False


def test_replace_key_changes_minister_key():
    assert replace_key("Pra. Giovanna - Tom Ab", "C") == "Pra. Giovanna - Tom C"


def test_original_key_metadata_is_preserved_during_conversion():
    request = ConversionRequest(ConversionMode.CHORDS_TO_CHORDS, "E", "C")
    metadata = "Artista/Banda: Fhop e Nívea Soares - Tom E; Bpm 72; 4/4"
    assert convert_musical_text(metadata, request) == metadata


def test_minister_key_is_changed_during_conversion():
    request = ConversionRequest(ConversionMode.CHORDS_TO_CHORDS, "E", "C")
    assert convert_musical_text("Pra. Giovanna - Tom E", request) == "Pra. Giovanna - Tom C"


@pytest.mark.parametrize("chord, expected", [("Ab", "1"), ("Fm", "6m"), ("Bbm7", "2m7"),
                                              ("Ebsus4", "5sus4"), ("Eb/G", "5/7")])
def test_chords_to_nashville(chord, expected):
    assert chord_to_nashville(chord, "Ab") == expected


@pytest.mark.parametrize("number, expected", [("1", "C"), ("6m", "Am"), ("2m7", "Dm7"),
                                               ("5sus4", "Gsus4"), ("5/7", "G/B"),
                                               ("b7", "Bb"), ("#4", "F#")])
def test_nashville_to_chords(number, expected):
    assert nashville_to_chord(number, "C") == expected


def test_chromatic_chord_to_nashville():
    assert chord_to_nashville("Bb", "C") == "b7"


@pytest.mark.parametrize("text, expected", [("1 5 6m 4", True), ("[Refrão] 2x", False),
                                              ("Bpm 69", False), ("4/4", False)])
def test_nashville_detection(text, expected):
    assert is_nashville_line(text) is expected


@pytest.mark.parametrize("text", ["| E /// |", "| E //// |"])
def test_short_chord_lines_with_repeated_slashes_are_detected(text):
    assert is_chord_line(text) is True


@pytest.mark.parametrize("text", ["| 6 /// |", "| 4 //// |"])
def test_short_nashville_lines_with_repeated_slashes_are_detected(text):
    assert is_nashville_line(text) is True


def test_text_conversion_preserves_structure():
    request = ConversionRequest(ConversionMode.CHORDS_TO_CHORDS, "Ab", "C")
    assert convert_musical_text("| Ab / Eb / | Db / Ab / |", request) == "| C / G / | F / C / |"


def test_intro_chord_line_is_transposed():
    request = ConversionRequest(ConversionMode.CHORDS_TO_CHORDS, "E", "C")
    assert convert_musical_text("| E /// |", request) == "| C /// |"


def test_intro_chord_line_converts_to_nashville():
    request = ConversionRequest(ConversionMode.CHORDS_TO_NASHVILLE, "E", None)
    assert convert_musical_text("| E /// |", request) == "| 1 /// |"


@pytest.mark.parametrize(
    "source, expected",
    [
        (
            "B A F#m   (frase guitarra em A)",
            "5 4 2m   (frase guitarra em A)",
        ),
        (
            "C#m DM E A G#m E (A partir da 3ªx - Apenas Guitarra e baixo)",
            "6m b7M 1 4 3m 1 (A partir da 3ªx - Apenas Guitarra e baixo)",
        ),
        (
            "| C#m /// | E /// | A/ G#m / | F#m / E / | (frase todos instrumentos Harmonia)",
            "| 6m /// | 1 /// | 4/ 3m / | 2m / 1 / | (frase todos instrumentos Harmonia)",
        ),
    ],
)
def test_chord_lines_with_trailing_performance_notes_convert_to_nashville(source, expected):
    request = ConversionRequest(ConversionMode.CHORDS_TO_NASHVILLE, "E", None)
    assert convert_musical_text(source, request) == expected


def test_parenthesized_chord_quality_is_still_converted():
    request = ConversionRequest(ConversionMode.CHORDS_TO_NASHVILLE, "C", None)
    assert convert_musical_text("C(add9) G", request) == "1(add9) 5"


@pytest.mark.parametrize("source, expected", [("| 6 /// |", "| A /// |"),
                                                ("| 4 /// |", "| F /// |")])
def test_intro_and_interlude_nashville_lines_convert_to_chords(source, expected):
    request = ConversionRequest(ConversionMode.NASHVILLE_TO_CHORDS, None, "C")
    assert convert_musical_text(source, request) == expected
