"""
Validador ABNT - Verifica conformidade com NBR 6023 e NBR 10520
Foco em revisão automática de formatação, não geração de conteúdo
"""

import re
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass


@dataclass
class ValidationIssue:
    """Representa um problema de formatação detectado"""
    severity: str  # 'error', 'warning', 'info'
    category: str  # 'citacao', 'referencia', 'formato', 'link'
    location: str  # Localização aproximada no texto
    message: str
    suggestion: str = ""


class ABNTValidator:
    """
    Validador automático de formatação ABNT para documentos acadêmicos.
    
    Verifica:
    - Correspondência 1:1 entre citações e referências
    - Formato correto de citações (autor-data, não numérico)
    - Presença de links (DOI/URL) em 100% das referências
    - Ausência de tags HTML no texto
    - Uso correto de caracteres Unicode
    """
    
    def __init__(self, content: str):
        self.content = content
        self.issues: List[ValidationIssue] = []
        self.citations_in_text: Set[str] = set()
        self.references: Dict[str, str] = {}
        
    def validate_all(self) -> List[ValidationIssue]:
        """Executa todas as validações e retorna lista de problemas"""
        self.issues = []
        
        print("[*] Validando formato ABNT...")
        
        # 1. Detectar citações numéricas (proibidas)
        self._check_numeric_citations()
        
        # 2. Validar formato de citações autor-data
        self._validate_citation_format()
        
        # 3. Extrair referências
        self._extract_references()
        
        # 4. Verificar correspondência 1:1
        self._check_citation_reference_match()
        
        # 5. Validar formato de referências ABNT
        self._validate_reference_format()
        
        # 6. Verificar links em referências
        self._check_reference_links()
        
        # 7. Detectar tags HTML
        self._detect_html_tags()
        
        # 8. Verificar uso de Unicode
        self._check_unicode_usage()
        
        return self.issues
    
    def _check_numeric_citations(self):
        """Detecta citações numéricas (sistema Vancouver - proibido)"""
        numeric_pattern = r'\[(\d+(?:\s*[-,]\s*\d+)*)\]'
        matches = re.finditer(numeric_pattern, self.content)
        
        for match in matches:
            self.issues.append(ValidationIssue(
                severity='error',
                category='citacao',
                location=f"Posição {match.start()}-{match.end()}",
                message=f"Citação numérica detectada: {match.group(0)}",
                suggestion="Use sistema autor-data (SOBRENOME, ano) conforme ABNT NBR 10520"
            ))
    
    def _validate_citation_format(self):
        """Valida formato de citações autor-data"""
        # Padrão correto: (SOBRENOME, ano) ou (SOBRENOME et al., ano)
        citation_pattern = r'\(([A-ZÀÁÂÃÉÊÍÓÔÕÚÇ][A-ZÀÁÂÃÉÊÍÓÔÕÚÇa-zàáâãéêíóôõúç\s]+(?:\s+et\s+al\.)?),\s*(\d{4}[a-z]?)\)'
        
        matches = re.finditer(citation_pattern, self.content)
        for match in matches:
            author = match.group(1).strip()
            year = match.group(2).strip()
            citation_key = f"{author.upper()}, {year}"
            self.citations_in_text.add(citation_key)
            
            # Verificar se autor está em maiúsculas
            if not author.isupper() and author != author.upper():
                self.issues.append(ValidationIssue(
                    severity='warning',
                    category='citacao',
                    location=f"Citação: {match.group(0)}",
                    message=f"Sobrenome '{author}' não está em maiúsculas",
                    suggestion=f"Use: ({author.upper()}, {year})"
                ))
    
    def _extract_references(self):
        """Extrai seção de referências do documento"""
        ref_pattern = r'(?:^|\n)(?:#+\s*)?(?:REFERÊNCIAS|Referências|REFERENCIAS|Referencias)(?:\s*\n|$)'
        match = re.search(ref_pattern, self.content, re.MULTILINE)
        
        if not match:
            self.issues.append(ValidationIssue(
                severity='error',
                category='referencia',
                location="Documento completo",
                message="Seção REFERÊNCIAS não encontrada",
                suggestion="Adicione seção 'REFERÊNCIAS' ou 'Referências' ao documento"
            ))
            return
        
        ref_start = match.end()
        ref_text = self.content[ref_start:]
        
        # Dividir em entradas individuais
        ref_entries = re.split(r'\n\s*\n', ref_text)
        
        for entry in ref_entries:
            entry = entry.strip()
            if len(entry) < 20:
                continue
            
            # Extrair autor e ano
            author_year_pattern = r'^([A-ZÀÁÂÃÉÊÍÓÔÕÚÇ][A-ZÀÁÂÃÉÊÍÓÔÕÚÇa-zàáâãéêíóôõúç\s,]+?)(?:,|\.)\s*(\d{4}[a-z]?)'
            match = re.search(author_year_pattern, entry)
            
            if match:
                author = match.group(1).strip()
                year = match.group(2).strip()
                
                # Extrair sobrenome principal
                last_name = self._extract_last_name(author)
                key = f"{last_name.upper()}, {year}"
                
                self.references[key] = entry
    
    def _extract_last_name(self, author_string: str) -> str:
        """Extrai sobrenome principal do autor"""
        author_string = re.sub(r'\s+et\s+al\.?', '', author_string, flags=re.IGNORECASE)
        parts = re.split(r'[,;.]', author_string)
        
        if parts:
            last_name = parts[0].strip()
            last_name = re.sub(r'\s+(de|da|do|dos|das|e)\s+', ' ', last_name, flags=re.IGNORECASE)
            return last_name.split()[-1] if ' ' in last_name else last_name
        
        return author_string.split()[0] if author_string else ""
    
    def _check_citation_reference_match(self):
        """Verifica correspondência 1:1 entre citações e referências"""
        # Citações sem referência
        missing_refs = self.citations_in_text - set(self.references.keys())
        for citation in missing_refs:
            self.issues.append(ValidationIssue(
                severity='error',
                category='correspondencia',
                location=f"Citação: {citation}",
                message=f"Citação '{citation}' não tem referência correspondente",
                suggestion="Adicione a referência completa na seção REFERÊNCIAS"
            ))
        
        # Referências não citadas
        unused_refs = set(self.references.keys()) - self.citations_in_text
        for ref in unused_refs:
            self.issues.append(ValidationIssue(
                severity='warning',
                category='correspondencia',
                location=f"Referência: {ref}",
                message=f"Referência '{ref}' não é citada no texto",
                suggestion="Remova a referência ou cite-a no texto"
            ))
    
    def _validate_reference_format(self):
        """Valida formato de referências conforme ABNT NBR 6023"""
        for key, entry in self.references.items():
            # Verificar se autor está em maiúsculas
            author_pattern = r'^([A-ZÀÁÂÃÉÊÍÓÔÕÚÇ][A-ZÀÁÂÃÉÊÍÓÔÕÚÇ\s,]+?)(?:\.|,)'
            match = re.search(author_pattern, entry)
            
            if not match:
                self.issues.append(ValidationIssue(
                    severity='warning',
                    category='referencia',
                    location=f"Referência: {key}",
                    message="Sobrenome do autor não está em maiúsculas",
                    suggestion="Sobrenomes devem estar em MAIÚSCULAS conforme ABNT NBR 6023"
                ))
    
    def _check_reference_links(self):
        """Verifica se todas as referências têm links (DOI ou URL)"""
        for key, entry in self.references.items():
            has_doi = bool(re.search(r'(?:doi|DOI):\s*10\.\d+', entry))
            has_url = bool(re.search(r'https?://\S+', entry))
            has_disponivel = bool(re.search(r'Disponível em:', entry))
            has_acesso = bool(re.search(r'Acesso em:', entry))
            
            if not (has_doi or has_url):
                self.issues.append(ValidationIssue(
                    severity='error',
                    category='link',
                    location=f"Referência: {key}",
                    message="Referência sem link (DOI ou URL)",
                    suggestion="Adicione DOI ou URL com 'Disponível em:' e 'Acesso em:'"
                ))
            elif has_url and not has_disponivel:
                self.issues.append(ValidationIssue(
                    severity='warning',
                    category='link',
                    location=f"Referência: {key}",
                    message="URL sem 'Disponível em:'",
                    suggestion="Use formato: Disponível em: <URL>. Acesso em: <data>"
                ))
            elif has_url and not has_acesso:
                self.issues.append(ValidationIssue(
                    severity='warning',
                    category='link',
                    location=f"Referência: {key}",
                    message="URL sem data de acesso ('Acesso em:')",
                    suggestion="Adicione 'Acesso em: <data>' após a URL"
                ))
    
    def _detect_html_tags(self):
        """Detecta tags HTML no texto (proibidas)"""
        html_patterns = [
            (r'<sub>.*?</sub>', 'subscrito'),
            (r'<sup>.*?</sup>', 'sobrescrito'),
            (r'<br\s*/?>', 'quebra de linha'),
            (r'</?p>', 'parágrafo'),
            (r'</?div[^>]*>', 'div'),
            (r'</?span[^>]*>', 'span'),
        ]
        
        for pattern, tag_type in html_patterns:
            matches = re.finditer(pattern, self.content, re.IGNORECASE)
            for match in matches:
                self.issues.append(ValidationIssue(
                    severity='error',
                    category='formato',
                    location=f"Posição {match.start()}-{match.end()}",
                    message=f"Tag HTML detectada: {match.group(0)} ({tag_type})",
                    suggestion="Use caracteres Unicode apropriados em vez de HTML"
                ))
    
    def _check_unicode_usage(self):
        """Verifica uso correto de caracteres Unicode científicos"""
        # Padrões que DEVERIAM usar Unicode mas podem estar mal formatados
        problematic_patterns = [
            (r'\bVO2max\b', 'VO₂máx', 'subscrito'),
            (r'\bCa2\+', 'Ca²⁺', 'subscrito e sobrescrito'),
            (r'\bmg/kg/min\b', 'mL·kg⁻¹·min⁻¹', 'unidades'),
        ]
        
        for pattern, correct, description in problematic_patterns:
            matches = re.finditer(pattern, self.content)
            for match in matches:
                self.issues.append(ValidationIssue(
                    severity='info',
                    category='formato',
                    location=f"Texto: {match.group(0)}",
                    message=f"Possível formatação incorreta de {description}",
                    suggestion=f"Considere usar: {correct}"
                ))
    
    def generate_report(self) -> str:
        """Gera relatório formatado dos problemas encontrados"""
        if not self.issues:
            return "[OK] Nenhum problema de formatacao ABNT detectado!\n"
        
        report = ["\n[RELATORIO DE VALIDACAO ABNT]\n" + "=" * 60]
        
        # Agrupar por severidade
        errors = [i for i in self.issues if i.severity == 'error']
        warnings = [i for i in self.issues if i.severity == 'warning']
        infos = [i for i in self.issues if i.severity == 'info']
        
        report.append(f"\n[RESUMO]:")
        report.append(f"   [!] Erros criticos: {len(errors)}")
        report.append(f"   [*] Avisos: {len(warnings)}")
        report.append(f"   [i] Sugestoes: {len(infos)}")
        
        # Agrupar por categoria
        categories = {}
        for issue in self.issues:
            if issue.category not in categories:
                categories[issue.category] = []
            categories[issue.category].append(issue)
        
        report.append(f"\n[POR CATEGORIA]:")
        for cat, issues_list in categories.items():
            report.append(f"   - {cat}: {len(issues_list)} problema(s)")
        
        # Detalhes dos erros
        if errors:
            report.append("\n\n[!] ERROS CRITICOS (devem ser corrigidos):")
            for i, issue in enumerate(errors, 1):
                report.append(f"\n{i}. [{issue.category.upper()}] {issue.message}")
                report.append(f"   Local: {issue.location}")
                if issue.suggestion:
                    report.append(f"   >> Sugestao: {issue.suggestion}")
        
        # Avisos
        if warnings:
            report.append("\n\n[*] AVISOS (recomendado corrigir):")
            for i, issue in enumerate(warnings, 1):
                report.append(f"\n{i}. [{issue.category.upper()}] {issue.message}")
                report.append(f"   Local: {issue.location}")
                if issue.suggestion:
                    report.append(f"   >> Sugestao: {issue.suggestion}")
        
        # Informações
        if infos:
            report.append("\n\n[i] SUGESTOES DE MELHORIA:")
            for i, issue in enumerate(infos, 1):
                report.append(f"\n{i}. {issue.message}")
                if issue.suggestion:
                    report.append(f"   >> {issue.suggestion}")
        
        report.append("\n" + "=" * 60 + "\n")
        
        return "\n".join(report)
    
    def get_statistics(self) -> Dict[str, int]:
        """Retorna estatísticas do documento"""
        return {
            'total_citacoes': len(self.citations_in_text),
            'total_referencias': len(self.references),
            'erros': len([i for i in self.issues if i.severity == 'error']),
            'avisos': len([i for i in self.issues if i.severity == 'warning']),
            'sugestoes': len([i for i in self.issues if i.severity == 'info']),
            'palavras': len(self.content.split()),
            'caracteres': len(self.content)
        }
