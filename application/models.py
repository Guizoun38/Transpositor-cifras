from dataclasses import dataclass

from domain.models import ConversionMode


@dataclass(frozen=True)
class ConversionRequest:
    mode: ConversionMode
    source_key: str | None = None
    target_key: str | None = None
