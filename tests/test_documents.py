import io

import pymupdf as fitz
from docx import Document

from application.models import ConversionRequest
from application.use_cases import process_document
from domain.models import ConversionMode

REQUEST = ConversionRequest(ConversionMode.CHORDS_TO_CHORDS, "Ab", "C")


def _docx_text(data):
    doc = Document(io.BytesIO(data))
    return doc, "\n".join(p.text for p in doc.paragraphs)


def _pdf_words(document):
    return [word for page in document for word in page.get_text("words")]


def test_generated_docx_integration():
    original = Document()
    original.add_paragraph("Felipe Rodrigues - Tom Ab; Bpm 69; 4/4", style="Heading 1")
    original.add_paragraph("Ab Eb Fm Db")
    original.add_paragraph("Vem, Senhor")
    source = io.BytesIO(); original.save(source)
    result = process_document(source.getvalue(), ".docx", REQUEST)
    doc, text = _docx_text(result)
    assert "Tom C; Bpm 69; 4/4" in text
    assert "C G Am F" in text
    assert "Vem, Senhor" in text
    assert len(doc.paragraphs) == 3
    assert doc.paragraphs[0].style.name == "Heading 1"


def test_generated_pdf_integration():
    source_doc = fitz.open(); page = source_doc.new_page()
    page.insert_text((72, 72), "Tom Ab\n\nAb Eb Fm Db\nVem, Senhor")
    source = source_doc.tobytes(); source_doc.close()
    result = process_document(source, ".pdf", REQUEST)
    converted = fitz.open(stream=result, filetype="pdf")
    words = [word[4] for word in _pdf_words(converted)]
    assert len(converted) == 1
    assert all(token in words for token in ("Tom", "C", "G", "Am", "F", "Vem,"))
    assert not all(token in words for token in ("Ab", "Eb", "Fm", "Db"))
    converted.close()


def test_generated_pdf_chords_to_nashville_remain_visible():
    source_doc = fitz.open(); page = source_doc.new_page()
    page.insert_text((72, 72), "Tom Ab")
    page.insert_text((72, 100), "Ab9 Ebsus4 Bbm7 Db")
    source = source_doc.tobytes(); source_doc.close()
    request = ConversionRequest(ConversionMode.CHORDS_TO_NASHVILLE, "Ab", None)
    result = process_document(source, ".pdf", request)
    converted = fitz.open(stream=result, filetype="pdf")
    words = [word[4] for word in _pdf_words(converted)]
    assert all(token in words for token in ("19", "5sus4", "2m7", "4"))
    assert not any(token in words for token in ("Ab9", "Ebsus4", "Bbm7", "Db"))
    converted.close()


def test_pdf_untouched_lyrics_keep_original_formatting():
    source_doc = fitz.open(); page = source_doc.new_page()
    page.insert_text((72, 72), "Ab Eb Fm Db", fontsize=12, color=(1, 0.2, 0))
    page.insert_text((72, 100), "Vem, Senhor", fontsize=14, fontname="hebi", color=(0.2, 0.1, 0.7))
    source = source_doc.tobytes(); source_doc.close()

    original = fitz.open(stream=source, filetype="pdf")
    original_lyric = next(span for block in original[0].get_text("dict")["blocks"]
                          for line in block.get("lines", []) for span in line["spans"]
                          if span["text"] == "Vem, Senhor")
    result = process_document(source, ".pdf", REQUEST)
    converted = fitz.open(stream=result, filetype="pdf")
    converted_lyric = next(span for block in converted[0].get_text("dict")["blocks"]
                           for line in block.get("lines", []) for span in line["spans"]
                           if span["text"] == "Vem, Senhor")

    assert converted_lyric["font"] == original_lyric["font"]
    assert converted_lyric["size"] == original_lyric["size"]
    assert converted_lyric["color"] == original_lyric["color"]
    assert converted_lyric["bbox"] == original_lyric["bbox"]
    converted_words = [word[4] for word in converted[0].get_text("words")]
    assert all(token in converted_words for token in ("C", "G", "Am", "F"))
    original.close(); converted.close()


