# Início Rápido - Corretor Científico ABNT

## 1. Instalação

```powershell
# Navegue até o diretório do projeto
cd C:\dev\python\corretor

# Instale as dependências
pip install -r requirements.txt
```

## 2. Teste Rápido

```powershell
# Teste básico (substitua por seu arquivo)
python corretor.py seu_documento.docx

# Com verificação de links
python corretor.py seu_documento.pdf --verify-links

# Especificando saída
python corretor.py documento.docx -o resultado.md
```

## 3. Estrutura do Projeto

```
corretor/
├── corretor.py                    # CLI principal
├── requirements.txt               # Dependências Python
├── README.md                      # Documentação principal
├── EXAMPLES.md                    # Exemplos de uso
├── QUICKSTART.md                  # Este arquivo
├── core/                          # Módulos principais
│   ├── __init__.py
│   ├── docx_extractor.py         # Extrator Word
│   ├── pdf_extractor.py          # Extrator PDF
│   ├── citation_parser.py        # Parser de citações
│   ├── reference_formatter.py    # Formatador ABNT
│   ├── link_verifier.py          # Verificador de links
│   └── markdown_exporter.py      # Exportador Markdown
└── utils/                         # Utilitários
    └── __init__.py               # Funções auxiliares
```

## 4. Uso Básico

### Linha de Comando

```powershell
python corretor.py arquivo.docx
```

### Python Script

```python
from corretor import CorretorABNT

corretor = CorretorABNT("documento.docx")
resultado = corretor.processar_documento()

print(f"Sucesso: {resultado['success']}")
print(f"Arquivo: {resultado['output_file']}")
```

## 5. O que o Sistema Faz

✅ **Extração com Formatação Preservada**
- Negritos (**texto**)
- Itálicos (*texto*)
- Parágrafos
- Tabelas
- Hierarquia de títulos

✅ **Conversão de Citações**
- [1] → (AUTOR, 2020)
- [2,3] → (AUTOR1, 2020; AUTOR2, 2021)
- [4-6] → (Múltiplas citações ordenadas)

✅ **Formatação ABNT de Referências**
- **AUTOR EM MAIÚSCULAS**
- **Título em negrito**
- Ordem alfabética
- URLs formatadas: Disponível em: [URL]. Acesso em: [data].

✅ **Validação**
- Correspondência citações ↔ referências
- Links acessíveis (com --verify-links)
- Datas de acesso atualizadas

✅ **Exportação Markdown**
- HTML removido
- Unicode para subscritos/sobrescritos (H₂O, m²)
- Tag `<immersive>` para preservação de formatação

## 6. Requisitos do Documento

Para melhor resultado, seu documento deve ter:

1. **Seção de Referências** claramente marcada:
   - Título: "Referências", "REFERÊNCIAS", etc.
   - Pode ser Heading ou texto normal

2. **Referências no formato ABNT**:
   ```
   AUTOR, A. Título do trabalho. Ano.
   SILVA, J. et al. Outro trabalho. 2020. Disponível em: https://...
   ```

3. **Citações** (numéricas serão convertidas):
   - Formato numérico: [1], [2,3], [4-6]
   - Ou já em formato autor-data: (AUTOR, 2020)

## 7. Saída Esperada

```markdown
<immersive>

# Título do Documento

Parágrafo com **negrito** e *itálico* preservados. Citação convertida (AUTOR, 2020).

## Referências

**AUTOR, A.** **Título do trabalho.** 2020. Disponível em: https://example.com. Acesso em: 16 nov. 2025.

</immersive>
```

## 8. Troubleshooting

**Erro: Import could not be resolved**
- As dependências ainda não foram instaladas
- Execute: `pip install -r requirements.txt`

**Erro: Seção de Referências não encontrada**
- Certifique-se que há um título "Referências" no documento
- Pode estar em qualquer nível de heading

**Citações não convertidas**
- Verifique se as referências estão no formato: AUTOR, ANO.
- O sistema mapeia [1] para a primeira referência em ordem alfabética

**Formatação perdida**
- O sistema preserva negrito/itálico de "runs" do Word
- Se o documento tem estilos aplicados a parágrafos inteiros, eles são preservados

## 9. Próximos Passos

- Leia `EXAMPLES.md` para exemplos detalhados
- Leia `README.md` para documentação completa
- Teste com seus próprios documentos
- Customize conforme necessário

## 10. Ajuda

```powershell
# Ver todas as opções
python corretor.py --help

# Versão
python corretor.py --version
```

## 11. Exemplo Completo

```powershell
# Processar tese de doutorado
python corretor.py tese_completa.docx -o tese_corrigida.md --verify-links

# Resultado:
# ℹ️ Extraindo conteúdo de tese_completa.docx...
# ✅ ✓ Extraídos 150,000 caracteres
# ℹ️ Extraindo referências bibliográficas...
# ✅ ✓ Encontradas 85 referências
# ℹ️ Processando citações...
# ✅ ✓ Citações processadas
# ℹ️ Formatando referências ABNT...
# ✅ ✓ Referências formatadas
# ℹ️ Verificando links...
# ✅ ✓ 80/85 links acessíveis
# ℹ️ Exportando Markdown...
# ✅ ✓ Markdown exportado
# ℹ️ Salvando em tese_corrigida.md...
# ✅ ✓ Arquivo salvo: tese_corrigida.md
# 📊 ESTATÍSTICAS
#    • Caracteres: 150,000
#    • Palavras: 25,000
#    • Linhas: 3,500
#    • Referências: 85
#    • Citações: 342
# 🎉 PROCESSAMENTO CONCLUÍDO COM SUCESSO!
```

Pronto para começar! 🚀
