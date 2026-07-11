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


def test_only_header_key_is_changed():
    assert replace_key("Felipe Rodrigues - Tom Ab; Bpm 69; 4/4", "C") == "Felipe Rodrigues - Tom C; Bpm 69; 4/4"


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


def test_text_conversion_preserves_structure():
    request = ConversionRequest(ConversionMode.CHORDS_TO_CHORDS, "Ab", "C")
    assert convert_musical_text("| Ab / Eb / | Db / Ab / |", request) == "| C / G / | F / C / |"
