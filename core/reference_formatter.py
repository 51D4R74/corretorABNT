"""
Formatador de referências bibliográficas conforme ABNT NBR 6023
"""

import re
from datetime import datetime
from typing import Dict, List


class ReferenceFormatter:
    """
    Formata referências bibliográficas conforme ABNT NBR 6023:
    - Ordem alfabética
    - Autor em MAIÚSCULAS
    - Título em negrito
    - URL com formato correto
    - Data de acesso atualizada
    """
    
    def __init__(self, references: Dict[str, Dict]):
        self.references = references
        
    def format_all(self) -> List[str]:
        """
        Formata todas as referências conforme ABNT
        
        Returns:
            Lista de referências formatadas
        """
        # Ordenar alfabeticamente por sobrenome do autor
        sorted_refs = sorted(
            self.references.items(),
            key=lambda x: x[1]['last_name'].upper()
        )
        
        formatted = []
        for key, ref in sorted_refs:
            formatted_ref = self.format_reference(ref)
            formatted.append(formatted_ref)
        
        return formatted
    
    def format_reference(self, ref: Dict) -> str:
        """
        Formata uma referência individual conforme ABNT
        
        Args:
            ref: Dict com dados da referência
            
        Returns:
            Referência formatada
        """
        # Autor em MAIÚSCULAS
        author = ref.get('full_author', '').upper()
        
        # Ano
        year = ref.get('year', '')
        
        # Extrair e formatar título (primeira sentença após o ano)
        full_entry = ref.get('full_entry', '')
        title = self._extract_title(full_entry, year)
        
        # Construir referência base
        parts = [f"**{author}.**"]
        
        if title:
            parts.append(f"**{title}**")
        
        parts.append(f"{year}.")
        
        # Adicionar demais informações
        remaining = self._extract_remaining_info(full_entry, author, year, title)
        if remaining:
            parts.append(remaining)
        
        # Adicionar URL e data de acesso se existir
        if ref.get('has_url') and ref.get('url'):
            url_part = self._format_url_and_access(ref)
            parts.append(url_part)
        
        return ' '.join(parts)
    
    def _extract_title(self, full_entry: str, year: str) -> str:
        """Extrai título da referência"""
        # Procurar texto após o ano até o primeiro ponto
        pattern = rf'{year}\.?\s*([^.]+\.)'
        match = re.search(pattern, full_entry)
        
        if match:
            title = match.group(1).strip()
            # Remover ponto final se existir
            title = title.rstrip('.')
            return title
        
        return ''
    
    def _extract_remaining_info(self, full_entry: str, author: str, year: str, title: str) -> str:
        """Extrai informações adicionais (editora, local, etc.)"""
        # Remover autor, ano e título para pegar o resto
        text = full_entry
        
        # Remover autor (case insensitive)
        text = re.sub(re.escape(author), '', text, flags=re.IGNORECASE)
        
        # Remover ano
        text = re.sub(rf'\b{year}\b\.?', '', text)
        
        # Remover título
        if title:
            text = re.sub(re.escape(title), '', text, flags=re.IGNORECASE)
        
        # Remover URL e data de acesso (serão adicionados depois)
        text = re.sub(r'Disponível em:.*?(?=\.|$)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Acesso em:.*?(?=\.|$)', '', text, flags=re.IGNORECASE)
        
        # Limpar espaços extras
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'^\W+', '', text)  # Remover pontuação no início
        
        return text if text else ''
    
    def _format_url_and_access(self, ref: Dict) -> str:
        """
        Formata URL e data de acesso conforme ABNT
        
        Format: Disponível em: [URL]. Acesso em: [data].
        """
        url = ref.get('url', '')
        
        # Usar data de acesso atualizada (data atual)
        current_date = datetime.now()
        months_pt = {
            1: 'jan.', 2: 'fev.', 3: 'mar.', 4: 'abr.',
            5: 'maio', 6: 'jun.', 7: 'jul.', 8: 'ago.',
            9: 'set.', 10: 'out.', 11: 'nov.', 12: 'dez.'
        }
        
        access_date = f"{current_date.day} {months_pt[current_date.month]} {current_date.year}"
        
        return f"Disponível em: {url}. Acesso em: {access_date}."
    
    def generate_references_section(self, formatted_refs: List[str] = None) -> str:
        """
        Gera seção completa de referências em Markdown
        
        Args:
            formatted_refs: Lista de referências já formatadas (opcional)
            
        Returns:
            Seção de referências formatada
        """
        if formatted_refs is None:
            formatted_refs = self.format_all()
        
        lines = [
            "## Referências",
            ""
        ]
        
        for ref in formatted_refs:
            lines.append(ref)
            lines.append("")  # Linha em branco entre referências
        
        return '\n'.join(lines)
    
    def validate_abnt_format(self, reference: str) -> Dict[str, bool]:
        """
        Valida se uma referência está em formato ABNT correto
        
        Args:
            reference: String da referência
            
        Returns:
            Dict com validações individuais
        """
        validations = {
            'has_author': bool(re.search(r'^[A-ZÀÁÂÃÉÊÍÓÔÕÚÇ]', reference)),
            'has_year': bool(re.search(r'\b\d{4}\b', reference)),
            'author_uppercase': bool(re.search(r'^[A-ZÀÁÂÃÉÊÍÓÔÕÚÇ\s,\.]+', reference)),
            'has_title': bool(re.search(r'\*\*.*?\*\*', reference)),
            'url_format': True  # Sempre válido se não tiver URL
        }
        
        # Validar formato de URL se existir
        if 'Disponível em:' in reference:
            validations['url_format'] = bool(
                re.search(r'Disponível em:\s*https?://\S+', reference)
            )
            validations['has_access_date'] = bool(
                re.search(r'Acesso em:\s*\d{1,2}\s+\w+\.?\s+\d{4}', reference)
            )
        
        return validations
    
    def sort_references(self, references: List[str]) -> List[str]:
        """
        Ordena referências alfabeticamente conforme ABNT
        
        Args:
            references: Lista de referências em texto
            
        Returns:
            Lista ordenada
        """
        def get_sort_key(ref: str) -> str:
            # Extrair autor (primeira palavra em maiúsculas)
            match = re.match(r'\*\*([A-ZÀÁÂÃÉÊÍÓÔÕÚÇ][A-Za-zÀ-ÿ\s,]+?)[,\.]', ref)
            if match:
                author = match.group(1).strip()
                # Remover "et al."
                author = re.sub(r'\s+et\s+al\.?', '', author, flags=re.IGNORECASE)
                return author.upper()
            return ref[:50].upper()
        
        return sorted(references, key=get_sort_key)
