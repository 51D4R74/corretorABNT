"""
Parser de citações científicas - converte citações numéricas para formato autor-data ABNT
"""

import re
from typing import Dict, List, Set, Tuple


class CitationParser:
    """
    Processa citações no texto:
    - Converte citações numéricas [1], [2] para (AUTOR, ano)
    - Identifica citações faltantes
    - Valida correspondência com referências
    """
    
    def __init__(self, content: str, references: Dict[str, Dict]):
        self.content = content
        self.references = references  # Mapeamento de chave para dados da referência
        self.numeric_to_author = {}  # Mapeamento [1] -> (AUTOR, ano)
        
    def build_numeric_mapping(self) -> Dict[str, str]:
        """
        Constrói mapeamento de citações numéricas para autor-data
        Procura padrões como [1], [2] e associa com referências na ordem
        
        Returns:
            Dict mapeando número para citação autor-data
        """
        # Extrair todas as citações numéricas do texto
        numeric_pattern = r'\[(\d+)\]'
        numeric_citations = re.findall(numeric_pattern, self.content)
        unique_numbers = sorted(set(int(n) for n in numeric_citations))
        
        # Ordenar referências alfabeticamente
        sorted_refs = sorted(self.references.items(), 
                           key=lambda x: x[1]['last_name'].upper())
        
        # Mapear números para referências
        mapping = {}
        for idx, (key, ref) in enumerate(sorted_refs, start=1):
            if idx in unique_numbers:
                mapping[str(idx)] = key
        
        self.numeric_to_author = mapping
        return mapping
    
    def convert_numeric_to_author_date(self) -> str:
        """
        Converte todas as citações numéricas para formato autor-data
        
        Examples:
            [1] -> (LICHTENSTEIN, 2014)
            [2,3] -> (SILVA, 2020; SANTOS, 2021)
            [4-6] -> (AUTOR1, 2019; AUTOR2, 2020; AUTOR3, 2021)
        
        Returns:
            Texto com citações convertidas
        """
        content = self.content
        
        # Padrão para citações numéricas complexas
        patterns = [
            (r'\[(\d+)\]', self._replace_single),  # [1]
            (r'\[(\d+)\s*,\s*(\d+(?:\s*,\s*\d+)*)\]', self._replace_multiple),  # [1,2,3]
            (r'\[(\d+)\s*-\s*(\d+)\]', self._replace_range),  # [1-5]
        ]
        
        for pattern, replacer in patterns:
            content = re.sub(pattern, replacer, content)
        
        self.content = content
        return content
    
    def _replace_single(self, match) -> str:
        """Substitui citação numérica simples [1]"""
        num = match.group(1)
        if num in self.numeric_to_author:
            return f"({self.numeric_to_author[num]})"
        return match.group(0)  # Manter original se não encontrar
    
    def _replace_multiple(self, match) -> str:
        """Substitui citações múltiplas [1,2,3]"""
        numbers = re.findall(r'\d+', match.group(0))
        citations = []
        
        for num in numbers:
            if num in self.numeric_to_author:
                citations.append(self.numeric_to_author[num])
        
        if citations:
            return f"({'; '.join(citations)})"
        return match.group(0)
    
    def _replace_range(self, match) -> str:
        """Substitui range de citações [1-5]"""
        start = int(match.group(1))
        end = int(match.group(2))
        citations = []
        
        for num in range(start, end + 1):
            num_str = str(num)
            if num_str in self.numeric_to_author:
                citations.append(self.numeric_to_author[num_str])
        
        if citations:
            return f"({'; '.join(citations)})"
        return match.group(0)
    
    def find_missing_citations(self, technical_terms: List[str] = None) -> List[Tuple[str, str]]:
        """
        Identifica termos técnicos ou afirmações sem citação
        
        Args:
            technical_terms: Lista de termos que devem ter citação
            
        Returns:
            Lista de tuplas (termo, citação_sugerida)
        """
        if technical_terms is None:
            technical_terms = [
                r'sinal do morcego',
                r'protocolo BLUE',
                r'sinal da praia',
                r'ultrassom point-of-care',
                r'POCUS',
                r'sinal da estratosfera',
                r'artefato em cauda de cometa',
            ]
        
        missing = []
        
        for term in technical_terms:
            # Procurar termo sem citação logo após
            pattern = rf'\b({term})\b(?!\s*\([A-Z][A-Za-zÀ-ÿ\s]+,\s*\d{{4}}\))'
            matches = re.finditer(pattern, self.content, re.IGNORECASE)
            
            for match in matches:
                # Tentar encontrar referência apropriada
                citation = self._find_citation_for_term(term)
                if citation:
                    missing.append((match.group(1), citation))
        
        return missing
    
    def _find_citation_for_term(self, term: str) -> str:
        """
        Busca referência apropriada para um termo técnico
        
        Args:
            term: Termo técnico
            
        Returns:
            Citação no formato (AUTOR, ano) ou string vazia
        """
        term_lower = term.lower()
        
        # Buscar nas referências
        for key, ref in self.references.items():
            full_entry = ref.get('full_entry', '').lower()
            if term_lower in full_entry:
                return key
        
        return ''
    
    def add_missing_citations(self, missing_citations: List[Tuple[str, str]] = None) -> str:
        """
        Adiciona citações faltantes ao texto
        
        Args:
            missing_citations: Lista de (termo, citação) para adicionar
            
        Returns:
            Texto com citações adicionadas
        """
        if missing_citations is None:
            missing_citations = self.find_missing_citations()
        
        content = self.content
        
        for term, citation in missing_citations:
            # Adicionar citação apenas na primeira ocorrência
            pattern = rf'\b({re.escape(term)})\b(?!\s*\([A-Z])'
            content = re.sub(
                pattern,
                rf'\1 ({citation})',
                content,
                count=1,
                flags=re.IGNORECASE
            )
        
        self.content = content
        return content
    
    def extract_all_citations(self) -> Set[str]:
        """
        Extrai todas as citações autor-data presentes no texto
        
        Returns:
            Set de citações no formato "AUTOR, ano"
        """
        # Padrão para citações autor-data
        pattern = r'\(([A-Z][A-ZÀ-ÿa-zà-ÿ\s]+(?:\s+et\s+al\.?)?),\s*(\d{4})\)'
        citations = re.findall(pattern, self.content)
        
        # Normalizar e criar set
        citation_set = set()
        for author, year in citations:
            # Limpar autor
            author = author.strip()
            author = re.sub(r'\s+et\s+al\.?', '', author, flags=re.IGNORECASE)
            # Pegar sobrenome principal
            last_name = author.split()[-1].upper()
            citation_set.add(f"{last_name}, {year}")
        
        return citation_set
    
    def validate_citations_with_references(self) -> Tuple[Set[str], Set[str]]:
        """
        Valida correspondência 1:1 entre citações e referências
        
        Returns:
            Tupla (citações_sem_referência, referências_não_citadas)
        """
        citations_in_text = self.extract_all_citations()
        references_listed = set(self.references.keys())
        
        missing_refs = citations_in_text - references_listed
        unused_refs = references_listed - citations_in_text
        
        return missing_refs, unused_refs
    
    def normalize_multiple_citations(self) -> str:
        """
        Normaliza múltiplas citações para ordem alfabética e formato correto
        
        Example:
            (SILVA, 2020; SANTOS, 2021) mantém ordem
            (SANTOS, 2021; SILVA, 2020) -> (SANTOS, 2021; SILVA, 2020)
        
        Returns:
            Texto com citações normalizadas
        """
        content = self.content
        
        # Padrão para múltiplas citações
        pattern = r'\(([A-Z][^)]+;\s*[A-Z][^)]+)\)'
        
        def sort_citations(match):
            citations_str = match.group(1)
            # Separar citações individuais
            citations = [c.strip() for c in citations_str.split(';')]
            # Ordenar alfabeticamente
            citations.sort()
            return f"({'; '.join(citations)})"
        
        content = re.sub(pattern, sort_citations, content)
        self.content = content
        return content
