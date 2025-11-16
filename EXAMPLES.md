# Exemplos de Uso - Corretor Científico ABNT

Este documento contém exemplos práticos de uso do Corretor Científico ABNT.

## Instalação

```bash
cd C:\dev\python\corretor
pip install -r requirements.txt
```

## Uso Básico

### 1. Processar documento Word

```bash
python corretor.py documento.docx
```

Saída: `documento_edited.md`

### 2. Processar PDF

```bash
python corretor.py artigo.pdf
```

Saída: `artigo_edited.md`

### 3. Especificar arquivo de saída

```bash
python corretor.py tese.docx -o resultado.md
```

### 4. Verificar e atualizar links

```bash
python corretor.py documento.docx --verify-links
```

### 5. Modo silencioso

```bash
python corretor.py artigo.pdf --quiet
```

## Uso como Módulo Python

```python
from corretor import CorretorABNT

# Criar instância
corretor = CorretorABNT(
    input_file="documento.docx",
    output_file="saida.md",
    verify_links=True,
    verbose=True
)

# Processar documento
resultado = corretor.processar_documento()

# Verificar sucesso
if resultado['success']:
    print(f"Arquivo gerado: {resultado['output_file']}")
    print(f"Estatísticas: {resultado['statistics']}")
else:
    print(f"Erro: {resultado['error']}")
```

## Exemplo de Conversão

### Entrada (Word/PDF):

```
O ultrassom point-of-care é essencial [1]. O protocolo BLUE demonstra eficácia [2,3].

Referências:
1. Lichtenstein D. Whole body ultrasonography in the critically ill. 2014.
2. Silva et al. Ultrasound applications. 2020.
3. Santos J. POCUS guidelines. 2021.
```

### Saída (Markdown):

```markdown
<immersive>

O ultrassom point-of-care é essencial (LICHTENSTEIN, 2014). O protocolo BLUE demonstra eficácia (SILVA, 2020; SANTOS, 2021).

## Referências

**LICHTENSTEIN, D.** **Whole body ultrasonography in the critically ill.** 2014. Disponível em: https://example.com/article1. Acesso em: 16 nov. 2025.

**SANTOS, J.** **POCUS guidelines.** 2021. Disponível em: https://example.com/article2. Acesso em: 16 nov. 2025.

**SILVA, ET AL.** **Ultrasound applications.** 2020. Disponível em: https://example.com/article3. Acesso em: 16 nov. 2025.

</immersive>
```

## Recursos Avançados

### Usar módulos individuais

```python
# Extrair apenas texto de Word
from core.docx_extractor import WordExtractor

extractor = WordExtractor("documento.docx")
markdown = extractor.to_markdown()
print(markdown)

# Extrair apenas texto de PDF
from core.pdf_extractor import PDFExtractor

extractor = PDFExtractor("artigo.pdf")
markdown = extractor.to_markdown()
print(markdown)

# Processar apenas citações
from core.citation_parser import CitationParser

parser = CitationParser(texto, referencias)
parser.build_numeric_mapping()
texto_convertido = parser.convert_numeric_to_author_date()

# Formatar apenas referências
from core.reference_formatter import ReferenceFormatter

formatter = ReferenceFormatter(referencias)
refs_formatadas = formatter.format_all()

# Verificar apenas links
from core.link_verifier import LinkVerifier

verifier = LinkVerifier()
resultado = verifier.verify_url("https://example.com")
print(f"Acessível: {resultado['accessible']}")
```

## Tratamento de Erros

```python
try:
    corretor = CorretorABNT("documento.docx")
    resultado = corretor.processar_documento()
    
    if not resultado['success']:
        print(f"Erro: {resultado['error']}")
        
except FileNotFoundError:
    print("Arquivo não encontrado")
except ValueError as e:
    print(f"Formato inválido: {e}")
except Exception as e:
    print(f"Erro inesperado: {e}")
```

## Configurações Personalizadas

```python
from core.citation_parser import CitationParser

# Adicionar termos técnicos personalizados
termos_customizados = [
    r'sinal do morcego',
    r'protocolo BLUE',
    r'seu termo técnico aqui'
]

parser = CitationParser(texto, referencias)
missing = parser.find_missing_citations(termos_customizados)
```

## Validação de Qualidade

```python
from core.markdown_exporter import MarkdownExporter

exporter = MarkdownExporter(conteudo)
validacoes = exporter.validate_markdown()

print(f"Sem HTML: {validacoes['no_html_tags']}")
print(f"Títulos corretos: {validacoes['proper_headings']}")
print(f"Símbolos Unicode: {validacoes['unicode_symbols']}")
```

## Dicas e Boas Práticas

1. **Sempre faça backup** dos documentos originais antes de processar
2. **Revise a saída** - o sistema é automatizado mas pode precisar de ajustes manuais
3. **Use --verify-links** para garantir que todas as URLs estão acessíveis
4. **Verifique a seção de Referências** no documento original está bem formatada
5. **Para documentos grandes**, considere dividir em seções menores

## Troubleshooting

### Problema: "Seção de Referências não encontrada"
**Solução**: Certifique-se que o documento tem um título "Referências" ou "REFERÊNCIAS"

### Problema: Citações não convertidas
**Solução**: Verifique se as referências estão no formato ABNT correto (AUTOR, ANO)

### Problema: Links não verificados
**Solução**: Use a flag `--verify-links` e certifique-se de ter conexão com internet

### Problema: Formatação perdida
**Solução**: O sistema preserva negrito/itálico. Se perdido, verifique se o documento original tem formatação aplicada nos "runs" do Word

## Suporte

Para issues e melhorias, consulte o README.md do projeto.
