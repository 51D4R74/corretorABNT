"""
Core package for scientific document processing
"""

from .docx_extractor import WordExtractor
from .pdf_extractor import PDFExtractor
from .citation_parser import CitationParser
from .reference_formatter import ReferenceFormatter
from .link_verifier import LinkVerifier
from .markdown_exporter import MarkdownExporter

__all__ = [
    'WordExtractor',
    'PDFExtractor',
    'CitationParser',
    'ReferenceFormatter',
    'LinkVerifier',
    'MarkdownExporter'
]
