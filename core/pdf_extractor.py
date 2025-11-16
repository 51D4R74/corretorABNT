"""
Extrator de documentos PDF com preservação de formatação
Baseado em PyMuPDF (enterprise-level)
"""

from typing import Dict, List, Tuple
import pymupdf  # PyMuPDF


class PDFExtractor:
    """
    Extrai texto de PDFs preservando:
    - Negritos, itálicos
    - Estrutura de parágrafos
    - Posicionamento de texto
    - Tabelas
    - Formatação de fonte
    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.document = pymupdf.open(file_path)
        
    def extract(self) -> Dict:
        """
        Extrai todo conteúdo do PDF preservando estrutura
        
        Returns:
            Dict com estrutura completa do documento
        """
        result = {
            'pages': [],
            'metadata': self._extract_metadata(),
            'text': ''
        }
        
        all_text = []
        
        for page_num in range(len(self.document)):
            page = self.document[page_num]
            page_data = self._extract_page(page, page_num)
            result['pages'].append(page_data)
            all_text.append(page_data['text'])
        
        result['text'] = '\n\n'.join(all_text)
        return result
    
    def _extract_metadata(self) -> Dict:
        """Extrai metadados do PDF"""
        metadata = self.document.metadata
        return {
            'title': metadata.get('title', ''),
            'author': metadata.get('author', ''),
            'subject': metadata.get('subject', ''),
            'creator': metadata.get('creator', ''),
            'producer': metadata.get('producer', ''),
            'created': metadata.get('creationDate', ''),
            'modified': metadata.get('modDate', ''),
            'page_count': len(self.document)
        }
    
    def _extract_page(self, page: pymupdf.Page, page_num: int) -> Dict:
        """
        Extrai conteúdo de uma página com formatação
        
        Args:
            page: Objeto Page do PyMuPDF
            page_num: Número da página
            
        Returns:
            Dict com dados da página
        """
        # Usar flags para preservar formatação
        flags = (
            pymupdf.TEXT_PRESERVE_LIGATURES |
            pymupdf.TEXT_PRESERVE_WHITESPACE |
            pymupdf.TEXT_COLLECT_STYLES
        )
        
        # Extrair em formato dict para ter acesso a formatação
        blocks = page.get_text('dict', flags=flags, sort=True)
        
        page_data = {
            'page_number': page_num + 1,
            'width': page.rect.width,
            'height': page.rect.height,
            'blocks': [],
            'text': ''
        }
        
        text_parts = []
        
        for block in blocks.get('blocks', []):
            if block['type'] == 0:  # Bloco de texto
                block_data = self._extract_text_block(block)
                page_data['blocks'].append(block_data)
                text_parts.append(block_data['text'])
        
        page_data['text'] = '\n\n'.join(text_parts)
        return page_data
    
    def _extract_text_block(self, block: Dict) -> Dict:
        """
        Extrai bloco de texto com formatação
        
        Args:
            block: Dict representando bloco do PyMuPDF
            
        Returns:
            Dict com texto e formatação do bloco
        """
        block_data = {
            'bbox': block.get('bbox', []),
            'lines': [],
            'text': ''
        }
        
        line_texts = []
        
        for line in block.get('lines', []):
            line_data = {
                'spans': [],
                'text': ''
            }
            
            span_texts = []
            
            for span in line.get('spans', []):
                span_data = self._extract_span(span)
                line_data['spans'].append(span_data)
                span_texts.append(span_data['text'])
            
            line_data['text'] = ''.join(span_texts)
            line_texts.append(line_data['text'])
            block_data['lines'].append(line_data)
        
        block_data['text'] = '\n'.join(line_texts)
        return block_data
    
    def _extract_span(self, span: Dict) -> Dict:
        """
        Extrai span (sequência de texto com formatação uniforme)
        
        Args:
            span: Dict representando span do PyMuPDF
            
        Returns:
            Dict com texto e formatação
        """
        # Detectar formatação baseada em flags da fonte
        flags = span.get('flags', 0)
        
        return {
            'text': span.get('text', ''),
            'font': span.get('font', ''),
            'size': span.get('size', 0),
            'color': span.get('color', 0),
            'bold': bool(flags & pymupdf.TEXT_FONT_BOLD),
            'italic': bool(flags & pymupdf.TEXT_FONT_ITALIC),
            'monospace': bool(flags & pymupdf.TEXT_FONT_MONOSPACED),
            'serif': bool(flags & pymupdf.TEXT_FONT_SERIFED)
        }
    
    def to_markdown(self) -> str:
        """
        Converte PDF extraído para Markdown preservando formatação
        
        Returns:
            String Markdown com formatação completa
        """
        data = self.extract()
        markdown_lines = []
        
        for page in data['pages']:
            for block in page['blocks']:
                for line in block['lines']:
                    line_md = self._line_to_markdown(line)
                    if line_md.strip():
                        markdown_lines.append(line_md)
        
        return '\n\n'.join(markdown_lines)
    
    def _line_to_markdown(self, line_data: Dict) -> str:
        """Converte linha para Markdown com formatação"""
        parts = []
        
        for span in line_data['spans']:
            text = span['text']
            
            # Aplicar formatação Markdown
            if span['bold'] and span['italic']:
                text = f"***{text}***"
            elif span['bold']:
                text = f"**{text}**"
            elif span['italic']:
                text = f"*{text}*"
            
            parts.append(text)
        
        return ''.join(parts)
    
    def extract_text_simple(self) -> str:
        """
        Extração simples de texto (mais rápida, sem formatação detalhada)
        
        Returns:
            Texto plano do documento
        """
        text_parts = []
        
        for page in self.document:
            text = page.get_text('text', sort=True)
            if text.strip():
                text_parts.append(text)
        
        return '\n\n'.join(text_parts)
    
    def __del__(self):
        """Fecha documento ao destruir objeto"""
        if hasattr(self, 'document'):
            self.document.close()
