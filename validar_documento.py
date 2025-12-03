"""
Script de validação ABNT - Testa conformidade de documentos acadêmicos
Uso: python validar_documento.py <arquivo.docx ou .pdf>
"""

import sys
from pathlib import Path

# Importar módulos do corretor
from core.docx_extractor import WordExtractor
from core.pdf_extractor import PDFExtractor
from core.abnt_validator import ABNTValidator


def main():
    if len(sys.argv) < 2:
        print("❌ Uso: python validar_documento.py <arquivo>")
        print("   Exemplo: python validar_documento.py meu_artigo.docx")
        return
    
    input_file = sys.argv[1]
    file_path = Path(input_file)
    
    if not file_path.exists():
        print(f"❌ Arquivo não encontrado: {input_file}")
        return
    
    print(f"\n🔬 VALIDADOR ABNT - Análise de Formatação")
    print(f"📄 Arquivo: {file_path.name}")
    print("=" * 70)
    
    # Extrair conteúdo
    print("\n📖 Etapa 1: Extraindo conteúdo...")
    
    try:
        if file_path.suffix.lower() in ['.docx', '.doc']:
            extractor = WordExtractor(str(file_path))
            content = extractor.extract()
        elif file_path.suffix.lower() == '.pdf':
            extractor = PDFExtractor(str(file_path))
            content = extractor.extract()
        else:
            print(f"❌ Formato não suportado: {file_path.suffix}")
            return
        
        print(f"   ✓ {len(content)} caracteres extraídos")
        print(f"   ✓ ~{len(content.split())} palavras")
        
    except Exception as e:
        print(f"❌ Erro ao extrair conteúdo: {e}")
        return
    
    # Validar formatação ABNT
    print("\n🔍 Etapa 2: Validando formatação ABNT...")
    
    validator = ABNTValidator(content)
    issues = validator.validate_all()
    
    # Estatísticas
    stats = validator.get_statistics()
    print(f"\n📊 ESTATÍSTICAS DO DOCUMENTO:")
    print(f"   • Palavras: {stats['palavras']:,}")
    print(f"   • Caracteres: {stats['caracteres']:,}")
    print(f"   • Citações no texto: {stats['total_citacoes']}")
    print(f"   • Referências listadas: {stats['total_referencias']}")
    
    # Relatório detalhado
    report = validator.generate_report()
    print(report)
    
    # Salvar relatório
    report_file = file_path.parent / f"{file_path.stem}_validacao_ABNT.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"RELATÓRIO DE VALIDAÇÃO ABNT\n")
        f.write(f"Arquivo: {file_path.name}\n")
        f.write(f"Data: {Path(__file__).stat().st_mtime}\n")
        f.write("\n" + "=" * 70 + "\n\n")
        f.write(f"ESTATÍSTICAS:\n")
        for key, value in stats.items():
            f.write(f"  {key}: {value:,}\n")
        f.write("\n" + report)
    
    print(f"📝 Relatório salvo em: {report_file}")
    
    # Sumário final
    if stats['erros'] == 0:
        print("\n✅ Documento aprovado! Nenhum erro crítico detectado.")
    else:
        print(f"\n⚠️ Documento requer revisão: {stats['erros']} erro(s) crítico(s).")
    
    if stats['avisos'] > 0:
        print(f"💡 {stats['avisos']} aviso(s) de melhoria encontrado(s).")


if __name__ == "__main__":
    main()
