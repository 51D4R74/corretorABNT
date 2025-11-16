"""
Utilitários de texto
"""

import re
import unicodedata
from typing import List


def normalize_text(text: str) -> str:
    """
    Normaliza texto removendo acentos e convertendo para minúsculas
    
    Args:
        text: Texto para normalizar
        
    Returns:
        Texto normalizado
    """
    # Remover acentos
    nfd = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    
    # Converter para minúsculas
    return text.lower()


def extract_author_lastname(author_string: str) -> str:
    """
    Extrai sobrenome principal de string de autor
    
    Args:
        author_string: Nome do autor
        
    Returns:
        Sobrenome principal
    """
    # Remover "et al."
    author_string = re.sub(r'\s+et\s+al\.?', '', author_string, flags=re.IGNORECASE)
    
    # Separar por vírgulas ou pontos
    parts = re.split(r'[,;.]', author_string)
    if parts:
        last_name = parts[0].strip()
        # Remover preposições comuns
        last_name = re.sub(r'\b(de|da|do|dos|das|e)\b', '', last_name, flags=re.IGNORECASE)
        last_name = ' '.join(last_name.split())  # Limpar espaços extras
        
        # Pegar última palavra se houver múltiplas
        if ' ' in last_name:
            return last_name.split()[-1]
        return last_name
    
    return author_string.split()[0] if author_string else ""


def clean_whitespace(text: str) -> str:
    """
    Remove espaços em branco excessivos
    
    Args:
        text: Texto para limpar
        
    Returns:
        Texto limpo
    """
    # Múltiplos espaços para um só
    text = re.sub(r' +', ' ', text)
    
    # Múltiplas quebras de linha para no máximo duas
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remover espaços no início/fim de linhas
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    text = '\n'.join(lines)
    
    return text.strip()


def split_into_sentences(text: str) -> List[str]:
    """
    Divide texto em sentenças
    
    Args:
        text: Texto para dividir
        
    Returns:
        Lista de sentenças
    """
    # Padrão para fim de sentença
    # Ponto/exclamação/interrogação seguido de espaço e maiúscula
    pattern = r'(?<=[.!?])\s+(?=[A-ZÀÁÂÃÉÊÍÓÔÕÚÇ])'
    
    sentences = re.split(pattern, text)
    return [s.strip() for s in sentences if s.strip()]


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Trunca texto para comprimento máximo
    
    Args:
        text: Texto para truncar
        max_length: Comprimento máximo
        suffix: Sufixo para adicionar se truncado
        
    Returns:
        Texto truncado
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)].strip() + suffix


def count_words(text: str) -> int:
    """
    Conta palavras no texto
    
    Args:
        text: Texto para contar
        
    Returns:
        Número de palavras
    """
    words = re.findall(r'\b\w+\b', text)
    return len(words)


def is_valid_url(url: str) -> bool:
    """
    Verifica se string é uma URL válida
    
    Args:
        url: String para verificar
        
    Returns:
        True se for URL válida
    """
    url_pattern = r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)$'
    return bool(re.match(url_pattern, url))


def extract_year(text: str) -> str:
    """
    Extrai ano (4 dígitos) de texto
    
    Args:
        text: Texto contendo ano
        
    Returns:
        Ano encontrado ou string vazia
    """
    match = re.search(r'\b(19|20)\d{2}\b', text)
    return match.group(0) if match else ""


def format_author_abnt(author: str) -> str:
    """
    Formata nome de autor para formato ABNT (SOBRENOME, Nome)
    
    Args:
        author: Nome do autor
        
    Returns:
        Nome formatado
    """
    # Se já estiver no formato correto, retornar
    if ',' in author:
        parts = author.split(',')
        surname = parts[0].strip().upper()
        given = parts[1].strip() if len(parts) > 1 else ''
        return f"{surname}, {given}" if given else surname
    
    # Caso contrário, tentar formatar
    parts = author.strip().split()
    if len(parts) > 1:
        surname = parts[-1].upper()
        given_names = ' '.join(parts[:-1])
        return f"{surname}, {given_names}"
    
    return author.upper()
