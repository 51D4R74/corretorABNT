"""
Gerador de Relatórios de Alterações - documenta todas as modificações realizadas
"""

from typing import Dict, List, Set
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ChangeRecord:
    """Registro de uma alteração específica"""
    category: str  # 'citacao', 'referencia', 'formato', 'link'
    action: str  # 'corrigido', 'adicionado', 'removido', 'atualizado'
    before: str
    after: str
    location: str = ""
    
    
@dataclass
class ValidationResults:
    """Resultados da validação ABNT"""
    citations_numeric: int = 0  # Citações numéricas convertidas
    citations_added: int = 0  # Citações adicionadas
    references_sorted: int = 0  # Referências ordenadas
    links_verified: int = 0  # Links verificados
    links_updated: int = 0  # Links atualizados
    html_tags_removed: int = 0  # Tags HTML removidas
    format_corrections: int = 0  # Correções de formato
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class ReportGenerator:
    """
    Gera relatórios detalhados das alterações realizadas no documento
    """
    
    def __init__(self, input_filename: str, output_filename: str):
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.timestamp = datetime.now()
        self.changes: List[ChangeRecord] = []
        self.validation_results = ValidationResults()
        self.statistics_before = {}
        self.statistics_after = {}
        
    def add_change(self, category: str, action: str, before: str, after: str, location: str = ""):
        """Registra uma alteração"""
        self.changes.append(ChangeRecord(
            category=category,
            action=action,
            before=before,
            after=after,
            location=location
        ))
        
    def set_statistics(self, before: Dict, after: Dict):
        """Define estatísticas antes e depois"""
        self.statistics_before = before
        self.statistics_after = after
        
    def generate_markdown_report(self) -> str:
        """Gera relatório em formato Markdown"""
        lines = []
        
        # Cabeçalho
        lines.append("# RELATÓRIO DE CORREÇÕES ABNT")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"**Arquivo de entrada:** `{self.input_filename}`")
        lines.append(f"**Arquivo de saída:** `{self.output_filename}`")
        lines.append(f"**Data/Hora:** {self.timestamp.strftime('%d/%m/%Y %H:%M:%S')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Resumo executivo
        lines.append("## RESUMO EXECUTIVO")
        lines.append("")
        
        total_changes = len(self.changes)
        lines.append(f"**Total de alterações:** {total_changes}")
        lines.append("")
        
        # Agrupar por categoria
        by_category = {}
        for change in self.changes:
            if change.category not in by_category:
                by_category[change.category] = []
            by_category[change.category].append(change)
        
        lines.append("**Por categoria:**")
        for cat, items in sorted(by_category.items()):
            lines.append(f"- **{cat.title()}:** {len(items)} alteração(ões)")
        lines.append("")
        
        # Validações ABNT
        lines.append("### Validações e Correções")
        lines.append("")
        
        val = self.validation_results
        if val.citations_numeric > 0:
            lines.append(f"- ✓ **{val.citations_numeric}** citações numéricas convertidas para autor-data")
        if val.citations_added > 0:
            lines.append(f"- ✓ **{val.citations_added}** citações adicionadas")
        if val.references_sorted > 0:
            lines.append(f"- ✓ **{val.references_sorted}** referências ordenadas alfabeticamente")
        if val.links_verified > 0:
            lines.append(f"- ✓ **{val.links_verified}** links verificados")
        if val.links_updated > 0:
            lines.append(f"- ✓ **{val.links_updated}** datas de acesso atualizadas")
        if val.html_tags_removed > 0:
            lines.append(f"- ✓ **{val.html_tags_removed}** tags HTML removidas")
        if val.format_corrections > 0:
            lines.append(f"- ✓ **{val.format_corrections}** correções de formatação")
        
        lines.append("")
        
        # Avisos
        if val.warnings:
            lines.append("### ⚠️ Avisos")
            lines.append("")
            for warning in val.warnings:
                lines.append(f"- {warning}")
            lines.append("")
        
        # Erros
        if val.errors:
            lines.append("### ❌ Erros/Problemas Não Resolvidos")
            lines.append("")
            for error in val.errors:
                lines.append(f"- {error}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # Estatísticas comparativas
        if self.statistics_before and self.statistics_after:
            lines.append("## ESTATÍSTICAS COMPARATIVAS")
            lines.append("")
            lines.append("| Métrica | Antes | Depois | Variação |")
            lines.append("|---------|-------|--------|----------|")
            
            metrics = [
                ('palavras', 'Palavras'),
                ('caracteres', 'Caracteres'),
                ('citacoes', 'Citações'),
                ('referencias', 'Referências'),
            ]
            
            for key, label in metrics:
                before = self.statistics_before.get(key, 0)
                after = self.statistics_after.get(key, 0)
                diff = after - before
                diff_str = f"+{diff}" if diff > 0 else str(diff)
                lines.append(f"| {label} | {before:,} | {after:,} | {diff_str} |")
            
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # Detalhamento das alterações
        if self.changes:
            lines.append("## DETALHAMENTO DAS ALTERAÇÕES")
            lines.append("")
            
            for category, items in sorted(by_category.items()):
                lines.append(f"### {category.upper()}")
                lines.append("")
                
                for i, change in enumerate(items[:10], 1):  # Limitar a 10 por categoria
                    lines.append(f"**{i}. {change.action.title()}**")
                    if change.location:
                        lines.append(f"   - Local: {change.location}")
                    lines.append(f"   - Antes: `{change.before[:80]}{'...' if len(change.before) > 80 else ''}`")
                    lines.append(f"   - Depois: `{change.after[:80]}{'...' if len(change.after) > 80 else ''}`")
                    lines.append("")
                
                if len(items) > 10:
                    lines.append(f"*... e mais {len(items) - 10} alteração(ões) nesta categoria*")
                    lines.append("")
        
        # Rodapé
        lines.append("---")
        lines.append("")
        lines.append("**Gerado por:** Corretor Científico ABNT")
        lines.append(f"**Versão:** 1.0")
        lines.append("")
        
        return "\n".join(lines)
    
    def generate_text_report(self) -> str:
        """Gera relatório em formato texto simples (para console)"""
        lines = []
        
        lines.append("")
        lines.append("=" * 70)
        lines.append("RELATORIO DE CORRECOES ABNT")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Arquivo: {self.input_filename} -> {self.output_filename}")
        lines.append(f"Data: {self.timestamp.strftime('%d/%m/%Y %H:%M:%S')}")
        lines.append("")
        
        # Resumo
        lines.append("-" * 70)
        lines.append("RESUMO")
        lines.append("-" * 70)
        lines.append(f"Total de alteracoes: {len(self.changes)}")
        lines.append("")
        
        val = self.validation_results
        lines.append("Validacoes realizadas:")
        if val.citations_numeric > 0:
            lines.append(f"  [OK] {val.citations_numeric} citacoes numericas convertidas")
        if val.citations_added > 0:
            lines.append(f"  [OK] {val.citations_added} citacoes adicionadas")
        if val.references_sorted > 0:
            lines.append(f"  [OK] {val.references_sorted} referencias ordenadas")
        if val.links_verified > 0:
            lines.append(f"  [OK] {val.links_verified} links verificados")
        if val.links_updated > 0:
            lines.append(f"  [OK] {val.links_updated} datas de acesso atualizadas")
        if val.html_tags_removed > 0:
            lines.append(f"  [OK] {val.html_tags_removed} tags HTML removidas")
        if val.format_corrections > 0:
            lines.append(f"  [OK] {val.format_corrections} correcoes de formato")
        
        lines.append("")
        
        # Avisos
        if val.warnings:
            lines.append("Avisos:")
            for warning in val.warnings:
                lines.append(f"  [!] {warning}")
            lines.append("")
        
        # Erros
        if val.errors:
            lines.append("Erros nao resolvidos:")
            for error in val.errors:
                lines.append(f"  [X] {error}")
            lines.append("")
        
        # Estatísticas
        if self.statistics_before and self.statistics_after:
            lines.append("-" * 70)
            lines.append("ESTATISTICAS")
            lines.append("-" * 70)
            
            metrics = [
                ('palavras', 'Palavras'),
                ('caracteres', 'Caracteres'),
                ('citacoes', 'Citacoes'),
                ('referencias', 'Referencias'),
            ]
            
            for key, label in metrics:
                before = self.statistics_before.get(key, 0)
                after = self.statistics_after.get(key, 0)
                diff = after - before
                lines.append(f"{label:15} Antes: {before:6,}  Depois: {after:6,}  ({diff:+d})")
            
            lines.append("")
        
        lines.append("=" * 70)
        lines.append("")
        
        return "\n".join(lines)
    
    def save_report(self, output_path: str, format: str = "markdown"):
        """
        Salva relatório em arquivo
        
        Args:
            output_path: Caminho do arquivo de saída
            format: 'markdown' ou 'text'
        """
        if format == "markdown":
            content = self.generate_markdown_report()
        else:
            content = self.generate_text_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
