#!/usr/bin/env python3
"""
Corretor Científico ABNT - Editor de Documentos Acadêmicos
Extrai texto de Word/PDF preservando formatação e corrige citações/referências ABNT

Uso:
    python corretor.py input.docx -o output.md
    python corretor.py input.pdf -o output.md --verify-links
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Optional
import re

# Importar módulos do projeto
from core.docx_extractor import WordExtractor
from core.pdf_extractor import PDFExtractor
from core.citation_parser import CitationParser
from core.reference_formatter import ReferenceFormatter
from core.link_verifier import LinkVerifier
from core.docx_exporter import DocxExporter
from utils import clean_whitespace, count_words


class CorretorABNT:
    """
    Classe principal que integra todos os módulos para processar documentos
    """
    
    def __init__(self, input_file: str, output_file: Optional[str] = None, 
                 verify_links: bool = False, verbose: bool = True):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else self._generate_output_path()
        self.verify_links = verify_links
        self.verbose = verbose
        
        # Validações
        if not self.input_file.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.input_file}")
        
        self.extension = self.input_file.suffix.lower()
        if self.extension not in ['.docx', '.pdf']:
            raise ValueError(f"Formato não suportado: {self.extension}. Use .docx ou .pdf")
        
        # Dados extraídos
        self.raw_content = ""
        self.markdown_content = ""
        self.references = {}
        self.statistics = {}
        
    def _generate_output_path(self) -> Path:
        """Gera caminho de saída automático"""
        return self.input_file.parent / f"{self.input_file.stem}_edited.docx"
    
    def _log(self, message: str, level: str = "INFO"):
        """Log de mensagens se verbose ativado"""
        if self.verbose:
            symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "PROCESS": "🔄"}
            print(f"{symbols.get(level, '•')} {message}")
    
    def extract_document(self) -> str:
        """
        Extrai conteúdo do documento preservando formatação
        
        Returns:
            Conteúdo em formato Markdown
        """
        self._log(f"Extraindo conteúdo de {self.input_file.name}...", "PROCESS")
        
        try:
            if self.extension == '.docx':
                extractor = WordExtractor(str(self.input_file))
                self.markdown_content = extractor.to_markdown()
            elif self.extension == '.pdf':
                extractor = PDFExtractor(str(self.input_file))
                self.markdown_content = extractor.to_markdown()
            
            self._log(f"✓ Extraídos {len(self.markdown_content)} caracteres", "SUCCESS")
            return self.markdown_content
            
        except Exception as e:
            self._log(f"Erro na extração: {e}", "ERROR")
            raise
    
    def extract_references(self) -> Dict:
        """
        Extrai seção de referências do documento
        
        Returns:
            Dicionário de referências
        """
        self._log("Extraindo referências bibliográficas...", "PROCESS")
        
        # Procurar seção de referências
        ref_pattern = r'(?:^|\n)(#{1,3}\s*)?(?:REFERÊNCIAS|Referências|REFERENCIAS|Referencias)(?:\s*\n|$)'
        match = re.search(ref_pattern, self.markdown_content, re.MULTILINE | re.IGNORECASE)
        
        if not match:
            self._log("Seção de Referências não encontrada", "WARNING")
            return {}
        
        # Extrair texto após "Referências"
        ref_start = match.end()
        ref_text = self.markdown_content[ref_start:]
        
        # Parsear referências individuais
        references = {}
        ref_entries = re.split(r'\n\s*\n', ref_text)
        
        for entry in ref_entries:
            entry = entry.strip()
            if not entry or len(entry) < 20:
                continue
            
            # Extrair autor e ano (padrão ABNT)
            author_year_pattern = r'\*?\*?([A-ZÀÁÂÃÉÊÍÓÔÕÚÇ][A-ZÀ-ÿa-zà-ÿ\s,\.]+?)[\.,]\*?\*?\s*(\d{4})'
            match = re.search(author_year_pattern, entry)
            
            if match:
                author = match.group(1).strip()
                year = match.group(2).strip()
                
                # Extrair sobrenome principal
                last_name = self._extract_lastname(author)
                key = f"{last_name.upper()}, {year}"
                
                references[key] = {
                    'full_author': author,
                    'year': year,
                    'last_name': last_name,
                    'full_entry': entry,
                    'has_url': bool(re.search(r'https?://', entry)),
                    'url': self._extract_url(entry),
                    'access_date': self._extract_access_date(entry)
                }
        
        self.references = references
        self._log(f"✓ Encontradas {len(references)} referências", "SUCCESS")
        return references
    
    def _extract_lastname(self, author_string: str) -> str:
        """Extrai sobrenome principal do autor"""
        author_string = re.sub(r'\s+et\s+al\.?', '', author_string, flags=re.IGNORECASE)
        parts = re.split(r'[,;.]', author_string)
        if parts:
            last_name = parts[0].strip()
            last_name = re.sub(r'\b(de|da|do|dos|das|e)\b', '', last_name, flags=re.IGNORECASE)
            last_name = ' '.join(last_name.split())
            return last_name.split()[-1] if ' ' in last_name else last_name
        return author_string.split()[0] if author_string else ""
    
    def _extract_url(self, entry: str) -> str:
        """Extrai URL da referência"""
        url_pattern = r'(?:Disponível em:|Available at:)?\s*(https?://[^\s]+)'
        match = re.search(url_pattern, entry)
        return match.group(1).strip() if match else ""
    
    def _extract_access_date(self, entry: str) -> str:
        """Extrai data de acesso da referência"""
        date_pattern = r'Acesso em:\s*(\d{1,2}\s+\w+\.?\s+\d{4})'
        match = re.search(date_pattern, entry)
        return match.group(1).strip() if match else ""
    
    def process_citations(self) -> str:
        """
        Processa citações: converte numéricas para autor-data e adiciona faltantes
        
        Returns:
            Conteúdo com citações processadas
        """
        self._log("Processando citações...", "PROCESS")
        
        citation_parser = CitationParser(self.markdown_content, self.references)
        
        # Construir mapeamento de citações numéricas
        citation_parser.build_numeric_mapping()
        
        # Converter citações numéricas
        self.markdown_content = citation_parser.convert_numeric_to_author_date()
        
        # Adicionar citações faltantes
        missing = citation_parser.find_missing_citations()
        if missing:
            self._log(f"Encontrados {len(missing)} termos sem citação", "WARNING")
            self.markdown_content = citation_parser.add_missing_citations(missing)
        
        # Normalizar múltiplas citações
        self.markdown_content = citation_parser.normalize_multiple_citations()
        
        # Validar correspondência
        missing_refs, unused_refs = citation_parser.validate_citations_with_references()
        
        if missing_refs:
            self._log(f"Citações sem referência: {len(missing_refs)}", "WARNING")
            if self.verbose:
                for ref in list(missing_refs)[:5]:  # Mostrar apenas primeiras 5
                    print(f"   • {ref}")
        
        if unused_refs:
            self._log(f"Referências não citadas: {len(unused_refs)}", "WARNING")
            if self.verbose:
                for ref in list(unused_refs)[:5]:
                    print(f"   • {ref}")
        
        self._log("✓ Citações processadas", "SUCCESS")
        return self.markdown_content
    
    def format_references(self) -> str:
        """
        Formata referências conforme ABNT NBR 6023
        
        Returns:
            Conteúdo com referências formatadas
        """
        self._log("Formatando referências ABNT...", "PROCESS")
        
        formatter = ReferenceFormatter(self.references)
        formatted_refs = formatter.format_all()
        
        # Substituir seção de referências antiga pela nova
        ref_pattern = r'((?:^|\n)(?:#{1,3}\s*)?(?:REFERÊNCIAS|Referências)).*'
        new_section = formatter.generate_references_section(formatted_refs)
        
        self.markdown_content = re.sub(
            ref_pattern,
            new_section,
            self.markdown_content,
            flags=re.MULTILINE | re.IGNORECASE | re.DOTALL
        )
        
        self._log("✓ Referências formatadas", "SUCCESS")
        return self.markdown_content
    
    def verify_and_update_links(self) -> None:
        """Verifica links e atualiza datas de acesso"""
        if not self.verify_links:
            return
        
        self._log("Verificando links...", "PROCESS")
        
        verifier = LinkVerifier()
        references_list = [ref['full_entry'] for ref in self.references.values()]
        results = verifier.batch_verify_references(references_list)
        
        accessible = sum(1 for r in results if r['all_accessible'])
        self._log(f"✓ {accessible}/{len(results)} links acessíveis", "SUCCESS")
        
        # Atualizar datas de acesso
        for key, ref in self.references.items():
            if ref['has_url']:
                updated_entry = verifier.update_access_date(ref['full_entry'])
                self.references[key]['full_entry'] = updated_entry
    
    def export_docx(self) -> None:
        """
        Exporta conteúdo final em formato Word (.docx)
        """
        self._log("Exportando para Word (DOCX)...", "PROCESS")
        
        exporter = DocxExporter(self.markdown_content)
        exporter.export(str(self.output_file))
        
        self._log("✓ Documento Word exportado", "SUCCESS")
    
    def save_output(self, content: str = None) -> None:
        """Salva conteúdo processado em arquivo (não necessário para DOCX)"""
        # DocxExporter já salva diretamente
        pass
    
    def generate_statistics(self) -> Dict:
        """Gera estatísticas do processamento"""
        stats = {
            'input_file': str(self.input_file),
            'output_file': str(self.output_file),
            'format': self.extension,
            'character_count': len(self.markdown_content),
            'word_count': count_words(self.markdown_content),
            'line_count': self.markdown_content.count('\n'),
            'references_count': len(self.references),
            'citations_count': len(re.findall(r'\([A-Z][^)]+,\s*\d{4}\)', self.markdown_content))
        }
        
        self.statistics = stats
        return stats
    
    def processar_documento(self) -> Dict:
        """
        Pipeline completo de processamento
        
        Returns:
            Dict com resultados do processamento
        """
        self._log("="*60, "INFO")
        self._log("🔬 CORRETOR CIENTÍFICO ABNT", "INFO")
        self._log("="*60, "INFO")
        
        try:
            # Etapa 1: Extração
            self.extract_document()
            
            # Etapa 2: Extrair referências
            self.extract_references()
            
            # Etapa 3: Processar citações
            self.process_citations()
            
            # Etapa 4: Formatar referências
            self.format_references()
            
            # Etapa 5: Verificar links (opcional)
            if self.verify_links:
                self.verify_and_update_links()
            
            # Etapa 6: Exportar para DOCX
            self.export_docx()
            
            # Gerar estatísticas
            stats = self.generate_statistics()
            
            # Exibir resumo
            self._log("="*60, "INFO")
            self._log("📊 ESTATÍSTICAS", "INFO")
            self._log(f"   • Caracteres: {stats['character_count']:,}", "INFO")
            self._log(f"   • Palavras: {stats['word_count']:,}", "INFO")
            self._log(f"   • Linhas: {stats['line_count']:,}", "INFO")
            self._log(f"   • Referências: {stats['references_count']}", "INFO")
            self._log(f"   • Citações: {stats['citations_count']}", "INFO")
            self._log("="*60, "INFO")
            self._log("🎉 PROCESSAMENTO CONCLUÍDO COM SUCESSO!", "SUCCESS")
            
            return {
                'success': True,
                'output_file': str(self.output_file),
                'statistics': stats
            }
            
        except Exception as e:
            self._log(f"Erro durante processamento: {e}", "ERROR")
            return {
                'success': False,
                'error': str(e)
            }


def main():
    """Função principal CLI"""
    parser = argparse.ArgumentParser(
        description='Corretor Científico ABNT - Processa documentos Word/PDF e corrige citações/referências',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s documento.docx
  %(prog)s artigo.pdf -o saida.md
  %(prog)s tese.docx -o resultado.md --verify-links
  %(prog)s documento.pdf --quiet
        """
    )
    
    parser.add_argument('input', help='Arquivo de entrada (Word .docx ou PDF)')
    parser.add_argument('-o', '--output', help='Arquivo de saída (Markdown)', default=None)
    parser.add_argument('--verify-links', action='store_true', 
                       help='Verificar e atualizar links nas referências')
    parser.add_argument('--quiet', action='store_true',
                       help='Modo silencioso (sem mensagens de progresso)')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
    args = parser.parse_args()
    
    # Validar arquivo de entrada
    if not Path(args.input).exists():
        print(f"❌ Erro: Arquivo não encontrado: {args.input}")
        sys.exit(1)
    
    try:
        # Criar e executar corretor
        corretor = CorretorABNT(
            input_file=args.input,
            output_file=args.output,
            verify_links=args.verify_links,
            verbose=not args.quiet
        )
        
        result = corretor.processar_documento()
        
        if result['success']:
            sys.exit(0)
        else:
            print(f"❌ Erro: {result.get('error', 'Erro desconhecido')}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Processamento interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
