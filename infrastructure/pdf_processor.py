import io
from collections import defaultdict

try:
    import pymupdf as fitz
except ModuleNotFoundError:
    try:
        import fitz
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "PyMuPDF não está instalado no ambiente que executa a aplicação. "
            "Execute: python -m pip install -r requirements.txt"
        ) from exc

from application.conversion import convert_musical_text
from application.ports import DocumentProcessor
from domain.errors import UnsupportedPdfError


def _color(value):
    return (
        (value >> 16 & 255) / 255,
        (value >> 8 & 255) / 255,
        (value & 255) / 255,
    )


def _base14_font(span):
    """Approximate the original face while retaining bold/italic traits."""
    name = span.get("font", "").lower()
    flags = span.get("flags", 0)
    bold = "bold" in name or bool(flags & 16)
    italic = "italic" in name or "oblique" in name or bool(flags & 2)
    if "times" in name or "serif" in name:
        return "tibi" if bold and italic else "tibo" if bold else "tiit" if italic else "tiro"
    if "cour" in name or "mono" in name:
        return "cobi" if bold and italic else "cobo" if bold else "coit" if italic else "cour"
    return "hebi" if bold and italic else "hebo" if bold else "heit" if italic else "helv"


def _span_for_word(spans, word_rect):
    for span in spans:
        if fitz.Rect(span["bbox"]).intersects(word_rect):
            return span
    return spans[0] if spans else {"size": 11, "color": 0, "origin": (word_rect.x0, word_rect.y1 - 1)}


def _plan_line_changes(words, spans, converted_tokens):
    """Reflow only tokens reached by a wider replacement, preserving glyph proportions."""
    changes = []
    rendered_end = None
    previous_original_end = None
    reflow_active = False

    for word, new in zip(words, converted_tokens):
        old = word[4]
        rect = fitz.Rect(word[:4])
        span = _span_for_word(spans, rect)
        new_x = rect.x0

        if reflow_active:
            original_gap = max(rect.x0 - previous_original_end, 0)
            preserved_gap = max(original_gap, 2.0)
            new_x = max(new_x, rendered_end + preserved_gap)

        moved = abs(new_x - rect.x0) > 0.01
        if old != new or moved:
            reflow_active = True
            fontname = _base14_font(span)
            fontsize = span.get("size", 11)
            rendered_end = new_x + fitz.get_text_length(new, fontname=fontname, fontsize=fontsize)
            changes.append((rect, new, span, new_x))
        else:
            rendered_end = rect.x1

        previous_original_end = rect.x1

    return changes


def _page_lines(page):
    """Return words and their original spans grouped by PDF text line."""
    words_by_line = defaultdict(list)
    for word in page.get_text("words"):
        # x0, y0, x1, y1, text, block, line, word
        words_by_line[(word[5], word[6])].append(word)

    spans_by_line = defaultdict(list)
    for block_number, block in enumerate(page.get_text("dict")["blocks"]):
        for line_number, line in enumerate(block.get("lines", [])):
            spans_by_line[(block_number, line_number)].extend(line.get("spans", []))

    for key, words in words_by_line.items():
        yield sorted(words, key=lambda item: item[7]), spans_by_line[key]


class PdfProcessor(DocumentProcessor):
    def process(self, file_data, request):
        document = fitz.open(stream=file_data, filetype="pdf")
        if not any(page.get_text().strip() for page in document):
            document.close()
            raise UnsupportedPdfError("O PDF não contém texto selecionável.")

        for page in document:
            changes = []
            for words, spans in _page_lines(page):
                original_tokens = [word[4] for word in words]
                original_line = " ".join(original_tokens)
                converted_line = convert_musical_text(original_line, request)
                converted_tokens = converted_line.split()

                # Conversions never need to change token count. If extraction
                # produced an ambiguous line, leave it untouched.
                if converted_line == original_line or len(converted_tokens) != len(original_tokens):
                    continue

                changes.extend(_plan_line_changes(words, spans, converted_tokens))

            # Only changed words are redacted. Lyrics, headings, links and all
            # other spans remain the original PDF objects and keep formatting.
            for rect, _, _, _ in changes:
                page.add_redact_annot(rect, fill=(1, 1, 1))
            if changes:
                page.apply_redactions()

            for rect, text, span, new_x in changes:
                baseline = span.get("origin", (rect.x0, rect.y1 - 1))[1]
                point = fitz.Point(new_x, baseline)
                fontsize = span.get("size", 11)
                fontname = _base14_font(span)
                page.insert_text(
                    point,
                    text,
                    fontsize=fontsize,
                    fontname=fontname,
                    color=_color(span.get("color", 0)),
                    overlay=True,
                )

        output = io.BytesIO()
        document.save(output, garbage=4, deflate=True)
        document.close()
        return output.getvalue()
