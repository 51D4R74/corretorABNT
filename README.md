# Corretor Científico ABNT

Aplicativo Python para processar documentos Word (.docx) e PDF, extraindo texto com formatação preservada e corrigindo citações e referências científicas conforme normas ABNT.

## Funcionalidades

- ✅ Extração de texto de Word/PDF com preservação total de formatação (negrito, itálico, parágrafos, espaçamentos)
- ✅ Conversão de citações numéricas [1], [2] para formato autor-data (SOBRENOME, ano)
- ✅ Formatação automática de referências conforme ABNT NBR 6023
- ✅ Verificação e atualização de links (DOI/URL) e datas de acesso
- ✅ Validação de correspondência entre citações e referências
- ✅ Identificação e inserção de citações faltantes
- ✅ Exportação em Markdown com formatação preservada

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

### Linha de Comando

```bash
# Processar um documento Word
python corretor.py input.docx -o output.md

# Processar um PDF
python corretor.py input.pdf -o output.md

# Com verificação de links
python corretor.py input.docx -o output.md --verify-links
```

### Como Módulo Python

```python
from corretor import CorretorABNT

corretor = CorretorABNT()
resultado = corretor.processar_documento("arquivo.docx")

# Salvar resultado
with open("saida.md", "w", encoding="utf-8") as f:
    f.write(resultado["markdown"])
```

## Estrutura do Projeto

```
corretor/
├── corretor.py              # CLI principal
├── core/
│   ├── __init__.py
│   ├── docx_extractor.py    # Extração de Word com formatação
│   ├── pdf_extractor.py     # Extração de PDF com formatação
│   ├── citation_parser.py   # Parser de citações
│   ├── reference_formatter.py # Formatador ABNT
│   ├── link_verifier.py     # Verificador de links
│   └── markdown_exporter.py # Exportador Markdown
├── utils/
│   ├── __init__.py
│   └── text_utils.py        # Utilitários de texto
├── requirements.txt
└── README.md
```

## Requisitos

- Python 3.8+
- python-docx
- PyMuPDF
- requests
- beautifulsoup4
- python-dateutil

## Especificações ABNT

Este aplicativo segue as normas:
- **ABNT NBR 10520**: Citações em documentos
- **ABNT NBR 6023**: Referências bibliográficas

## Exemplos

### Entrada (Word/PDF com citações numéricas):
```
O ultrassom à beira leito é uma técnica essencial [1]. Estudos mostram sua eficácia [2,3].

Referências:
1. Lichtenstein D. Whole body ultrasonography in the critically ill. 2014.
```

### Saída (Markdown com citações autor-data):
```markdown
O ultrassom à beira leito é uma técnica essencial (LICHTENSTEIN, 2014). Estudos mostram sua eficácia (SILVA, 2020; SANTOS, 2021).

## Referências

**LICHTENSTEIN, D.** Whole body ultrasonography in the critically ill. 2014. Disponível em: https://example.com. Acesso em: 16 nov. 2025.
```

## Licença

MIT License
