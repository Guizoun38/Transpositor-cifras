from abc import ABC, abstractmethod

from application.models import ConversionRequest


class DocumentProcessor(ABC):
    @abstractmethod
    def process(self, file_data: bytes, request: ConversionRequest) -> bytes:
        raise NotImplementedError
