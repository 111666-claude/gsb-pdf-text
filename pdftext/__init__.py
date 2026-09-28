"""从 PDF 里抽文本（最小子集）。"""

from .extract import PdfError, extract

__all__ = ["PdfError", "extract"]
