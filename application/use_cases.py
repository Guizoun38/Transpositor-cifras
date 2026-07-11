from application.conversion import validate_request
from application.models import ConversionRequest
from domain.errors import UnsupportedFileTypeError


def process_document(file_data: bytes, extension: str, request: ConversionRequest) -> bytes:
    validate_request(request)
    extension = extension.lower().lstrip(".")
    if extension == "docx":
        from infrastructure.docx_processor import DocxProcessor
        return DocxProcessor().process(file_data, request)
    if extension == "pdf":
        from infrastructure.pdf_processor import PdfProcessor
        return PdfProcessor().process(file_data, request)
    raise UnsupportedFileTypeError(f"Formato não suportado: .{extension}")
