"""
Exportador de Markdown com formatação preservada
"""

import re
from typing import Dict, List


class MarkdownExporter:
    """
    Exporta conteúdo processado para Markdown puro
    - Remove tags HTML
    - Usa Unicode para subscritos/sobrescritos
    - Preserva formatação (negrito, itálico)
    - Garante estrutura correta de parágrafos
    """
    
    def __init__(self, content: str):
        self.content = content
        
    def remove_html_tags(self) -> str:
        """
        Remove todas as tags HTML e substitui por equivalentes Unicode/Markdown
        
        Returns:
            Texto sem HTML
        """
        content = self.content
        
        # Subscritos - converter para Unicode
        subscript_map = {'0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
                        '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'}
        
        def replace_subscript(match):
            text = match.group(1)
            return ''.join(subscript_map.get(c, c) for c in text)
        
        content = re.sub(r'<sub>(.*?)</sub>', replace_subscript, content, flags=re.IGNORECASE)
        
        # Sobrescritos - converter para Unicode
        superscript_map = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
                          '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
                          '+': '⁺', '-': '⁻', '=': '⁼', '(': '⁽', ')': '⁾'}
        
        def replace_superscript(match):
            text = match.group(1)
            return ''.join(superscript_map.get(c, c) for c in text)
        
        content = re.sub(r'<sup>(.*?)</sup>', replace_superscript, content, flags=re.IGNORECASE)
        
        # Quebras de linha
        content = re.sub(r'<br\s*/?>', '\n', content, flags=re.IGNORECASE)
        
        # Parágrafos
        content = re.sub(r'<p>', '\n\n', content, flags=re.IGNORECASE)
        content = re.sub(r'</p>', '\n\n', content, flags=re.IGNORECASE)
        
        # Remover spans e divs (preservar conteúdo)
        content = re.sub(r'</?(?:span|div)[^>]*>', '', content, flags=re.IGNORECASE)
        
        # Negrito
        content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', content, flags=re.IGNORECASE)
        content = re.sub(r'<b>(.*?)</b>', r'**\1**', content, flags=re.IGNORECASE)
        
        # Itálico
        content = re.sub(r'<em>(.*?)</em>', r'*\1*', content, flags=re.IGNORECASE)
        content = re.sub(r'<i>(.*?)</i>', r'*\1*', content, flags=re.IGNORECASE)
        
        # Remover quaisquer outras tags HTML
        content = re.sub(r'<[^>]+>', '', content)
        
        # Decodificar entidades HTML comuns
        html_entities = {
            '&nbsp;': ' ',
            '&lt;': '<',
            '&gt;': '>',
            '&amp;': '&',
            '&quot;': '"',
            '&#39;': "'",
            '&mdash;': '—',
            '&ndash;': '–',
        }
        
        for entity, char in html_entities.items():
            content = content.replace(entity, char)
        
        self.content = content
        return content
    
    def normalize_whitespace(self) -> str:
        """
        Normaliza espaços em branco preservando estrutura
        
        Returns:
            Texto com espaçamento normalizado
        """
        content = self.content
        
        # Remover espaços múltiplos (mas não quebras de linha)
        content = re.sub(r' +', ' ', content)
        
        # Limitar quebras de linha consecutivas a no máximo 2
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Remover espaços no início e fim de linhas
        lines = content.split('\n')
        lines = [line.rstrip() for line in lines]
        content = '\n'.join(lines)
        
        self.content = content
        return content
    
    def preserve_paragraph_structure(self) -> str:
        """
        Garante que estrutura de parágrafos seja preservada
        
        Returns:
            Texto com estrutura de parágrafos correta
        """
        content = self.content
        
        # Garantir linha em branco entre parágrafos
        # Detectar fim de parágrafo (linha com ponto final ou similar)
        lines = content.split('\n')
        result_lines = []
        
        for i, line in enumerate(lines):
            result_lines.append(line)
            
            # Se linha atual termina com pontuação de fim de frase
            # e próxima linha existe e não está vazia
            if (line.strip() and 
                line.strip()[-1] in '.!?:' and 
                i < len(lines) - 1 and 
                lines[i + 1].strip() and
                not lines[i + 1].strip().startswith('#')):  # Não é título
                
                # Adicionar linha em branco se ainda não houver
                if i < len(lines) - 1 and lines[i + 1]:
                    result_lines.append('')
        
        content = '\n'.join(result_lines)
        
        # Limpar linhas em branco extras
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        self.content = content
        return content
    
    def use_unicode_symbols(self) -> str:
        """
        Substitui representações textuais por símbolos Unicode apropriados
        
        Returns:
            Texto com símbolos Unicode
        """
        content = self.content
        
        # Símbolos científicos comuns
        replacements = {
            r'\bMHz\b': 'MHz',
            r'\bcm2\b': 'cm²',
            r'\bcm3\b': 'cm³',
            r'\bm2\b': 'm²',
            r'\bm3\b': 'm³',
            r'\bmm2\b': 'mm²',
            r'\bmm3\b': 'mm³',
            r'(\d+)\s*%': r'\1%',  # Remover espaço antes de %
            r'<=': '≤',
            r'>=': '≥',
            r'!=': '≠',
            r'\\pm': '±',
            r'\\times': '×',
            r'\\div': '÷',
            r'\\degree': '°',
            r'\\alpha': 'α',
            r'\\beta': 'β',
            r'\\gamma': 'γ',
            r'\\delta': 'δ',
            r'\\mu': 'μ',
        }
        
        for pattern, replacement in replacements.items():
            content = re.sub(pattern, replacement, content)
        
        self.content = content
        return content
    
    def wrap_in_immersive_tag(self, content: str = None) -> str:
        """
        Envolve conteúdo em tag <immersive> conforme especificação
        
        Args:
            content: Conteúdo a ser envolvido (usa self.content se None)
            
        Returns:
            Conteúdo envolvido
        """
        if content is None:
            content = self.content
        
        return f"<immersive>\n\n{content}\n\n</immersive>"
    
    def export(self, wrap_immersive: bool = True) -> str:
        """
        Executa pipeline completo de exportação
        
        Args:
            wrap_immersive: Se True, envolve em tag <immersive>
            
        Returns:
            Markdown final formatado
        """
        # Pipeline de limpeza e formatação
        self.remove_html_tags()
        self.use_unicode_symbols()
        self.normalize_whitespace()
        self.preserve_paragraph_structure()
        
        # Limpar linhas em branco no início e fim
        content = self.content.strip()
        
        # Envolver em tag immersive se solicitado
        if wrap_immersive:
            content = self.wrap_in_immersive_tag(content)
        
        return content
    
    def validate_markdown(self) -> Dict[str, bool]:
        """
        Valida se Markdown está correto
        
        Returns:
            Dict com validações
        """
        validations = {
            'no_html_tags': not bool(re.search(r'<(?!immersive)[^>]+>', self.content)),
            'proper_headings': bool(re.search(r'^#{1,6}\s+\S', self.content, re.MULTILINE)),
            'no_excessive_whitespace': not bool(re.search(r'\n{4,}', self.content)),
            'unicode_symbols': bool(re.search(r'[²³°±×÷≤≥≠]', self.content)),
        }
        
        return validations
