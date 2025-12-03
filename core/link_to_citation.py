"""
Conversor de Links para Citações ABNT
Funcionalidade PRINCIPAL: Substitui hyperlinks por citações autor-data e adiciona referências
"""

import re
import requests
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from bs4 import BeautifulSoup


class LinkToCitationConverter:
    """
    Converte hyperlinks em citações ABNT e adiciona referências automaticamente
    
    FUNCIONALIDADE PRINCIPAL - NÃO PODE FALHAR
    """
    
    def __init__(self, content: str, existing_references: Dict[str, Dict]):
        self.content = content
        self.existing_references = existing_references
        self.new_references = {}
        self.conversions = []  # Log de conversões realizadas
        
    def extract_links_from_text(self) -> List[Tuple[str, str]]:
        """
        Extrai todos os hyperlinks do texto
        
        Padrões suportados:
        - [texto](http://url)  - Markdown
        - http://url com texto ao redor
        - <a href="url">texto</a> - HTML
        
        Returns:
            Lista de tuplas (texto_contexto, url)
        """
        links = []
        
        # Padrão 1: Markdown [texto](url)
        markdown_pattern = r'\[([^\]]+)\]\((https?://[^\)]+)\)'
        for match in re.finditer(markdown_pattern, self.content):
            text = match.group(1)
            url = match.group(2)
            links.append((text, url, match.start(), match.end()))
        
        # Padrão 2: URL pura no texto
        url_pattern = r'(https?://[^\s\)]+)'
        for match in re.finditer(url_pattern, self.content):
            url = match.group(1)
            # Pegar contexto ao redor (30 caracteres antes)
            start = max(0, match.start() - 30)
            context = self.content[start:match.start()].strip()
            links.append((context, url, match.start(), match.end()))
        
        # Padrão 3: HTML <a href="url">texto</a>
        html_pattern = r'<a\s+href=["\']?(https?://[^"\'>\s]+)["\']?[^>]*>([^<]+)</a>'
        for match in re.finditer(html_pattern, self.content, re.IGNORECASE):
            url = match.group(1)
            text = match.group(2)
            links.append((text, url, match.start(), match.end()))
        
        # Remover duplicatas e ordenar por posição
        unique_links = []
        seen_urls = set()
        for text, url, start, end in sorted(links, key=lambda x: x[2]):
            if url not in seen_urls:
                seen_urls.add(url)
                unique_links.append((text, url))
        
        return unique_links
    
    def fetch_metadata_from_url(self, url: str) -> Optional[Dict[str, str]]:
        """
        Busca metadados (autor, ano, título) de uma URL
        
        Tenta múltiplas estratégias:
        1. CrossRef DOI API (para DOIs)
        2. OpenGraph/Twitter Cards
        3. Meta tags HTML
        4. Heurísticas na página
        
        Returns:
            Dict com author, year, title ou None
        """
        try:
            # Detectar DOI na URL
            doi_match = re.search(r'10\.\d{4,}/[^\s]+', url)
            if doi_match:
                doi = doi_match.group(0)
                metadata = self._fetch_from_crossref(doi)
                if metadata:
                    return metadata
            
            # Buscar metadados da página HTML
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Estratégia 1: Meta tags OpenGraph
            metadata = self._extract_opengraph(soup)
            if metadata and metadata.get('author') and metadata.get('year'):
                return metadata
            
            # Estratégia 2: Meta tags padrão
            metadata = self._extract_standard_meta(soup)
            if metadata and metadata.get('author') and metadata.get('year'):
                return metadata
            
            # Estratégia 3: Heurísticas na página
            metadata = self._extract_from_content(soup, url)
            return metadata
            
        except Exception as e:
            print(f"   Erro ao buscar metadados de {url[:50]}...: {e}")
            return None
    
    def _fetch_from_crossref(self, doi: str) -> Optional[Dict[str, str]]:
        """Busca metadados via CrossRef API"""
        try:
            api_url = f"https://api.crossref.org/works/{doi}"
            response = requests.get(api_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()['message']
                
                # Extrair autor
                authors = data.get('author', [])
                if authors:
                    first_author = authors[0]
                    author = first_author.get('family', '')
                else:
                    author = data.get('publisher', 'AUTOR DESCONHECIDO')
                
                # Extrair ano
                published = data.get('published-print') or data.get('published-online') or data.get('created')
                year = str(published['date-parts'][0][0]) if published else str(datetime.now().year)
                
                # Extrair título
                title = data.get('title', [''])[0]
                
                # Extrair revista/publicação
                container = data.get('container-title', [''])[0] if data.get('container-title') else ''
                
                return {
                    'author': author.upper(),
                    'year': year,
                    'title': title,
                    'container': container,
                    'doi': doi,
                    'url': f"https://doi.org/{doi}"
                }
        except Exception:
            return None
    
    def _extract_opengraph(self, soup) -> Optional[Dict[str, str]]:
        """Extrai metadados OpenGraph"""
        og_title = soup.find('meta', property='og:title')
        og_author = soup.find('meta', property='article:author')
        og_published = soup.find('meta', property='article:published_time')
        
        if og_title:
            title = og_title.get('content', '')
            author = og_author.get('content', '') if og_author else ''
            
            # Extrair ano da data
            year = ''
            if og_published:
                date_str = og_published.get('content', '')
                year_match = re.search(r'(\d{4})', date_str)
                if year_match:
                    year = year_match.group(1)
            
            if author and year:
                return {
                    'author': author.split()[0].upper(),  # Primeiro nome
                    'year': year,
                    'title': title
                }
        
        return None
    
    def _extract_standard_meta(self, soup) -> Optional[Dict[str, str]]:
        """Extrai metadados de meta tags padrão"""
        author_meta = soup.find('meta', attrs={'name': re.compile(r'author', re.I)})
        date_meta = soup.find('meta', attrs={'name': re.compile(r'(date|published)', re.I)})
        title_meta = soup.find('meta', attrs={'name': re.compile(r'(title|headline)', re.I)})
        
        if author_meta:
            author = author_meta.get('content', '')
            year = ''
            
            if date_meta:
                date_str = date_meta.get('content', '')
                year_match = re.search(r'(\d{4})', date_str)
                if year_match:
                    year = year_match.group(1)
            
            title = title_meta.get('content', '') if title_meta else soup.title.string if soup.title else ''
            
            if author and year:
                return {
                    'author': author.split()[0].upper(),
                    'year': year,
                    'title': title
                }
        
        return None
    
    def _extract_from_content(self, soup, url: str) -> Optional[Dict[str, str]]:
        """Extrai metadados do conteúdo da página usando heurísticas"""
        # Extrair título
        title = ''
        if soup.title:
            title = soup.title.string
        elif soup.h1:
            title = soup.h1.get_text()
        
        # Tentar extrair ano da URL ou conteúdo
        year = ''
        year_match = re.search(r'/(\d{4})/', url)
        if year_match:
            year = year_match.group(1)
        else:
            # Buscar ano no texto
            text_content = soup.get_text()
            year_match = re.search(r'\b(20\d{2})\b', text_content)
            if year_match:
                year = year_match.group(1)
        
        # Usar domínio como "autor" se não encontrar
        domain_match = re.search(r'://([^/]+)', url)
        author = domain_match.group(1).upper() if domain_match else 'WEB'
        
        if year and title:
            return {
                'author': author,
                'year': year,
                'title': title[:100]  # Limitar título
            }
        
        return None
    
    def generate_citation_key(self, metadata: Dict[str, str]) -> str:
        """Gera chave de citação (AUTOR, ano)"""
        author = metadata.get('author', 'AUTOR').upper()
        year = metadata.get('year', str(datetime.now().year))
        return f"{author}, {year}"
    
    def generate_full_reference(self, metadata: Dict[str, str], url: str) -> str:
        """
        Gera referência completa ABNT a partir dos metadados
        
        Formato: AUTOR. Título. Publicação, ano. Disponível em: URL. Acesso em: data.
        """
        author = metadata.get('author', 'AUTOR').upper()
        year = metadata.get('year', str(datetime.now().year))
        title = metadata.get('title', 'Título não disponível')
        container = metadata.get('container', '')
        
        # Construir referência
        parts = [f"{author}."]
        
        if title:
            parts.append(f"{title}.")
        
        if container:
            parts.append(f"{container},")
        
        parts.append(f"{year}.")
        
        # Adicionar URL e data de acesso
        current_date = datetime.now().strftime("%d %b. %Y")
        parts.append(f"Disponível em: {url}.")
        parts.append(f"Acesso em: {current_date}.")
        
        return ' '.join(parts)
    
    def convert_links_to_citations(self) -> Tuple[str, Dict[str, Dict]]:
        """
        FUNÇÃO PRINCIPAL: Converte todos os links em citações
        
        Returns:
            Tupla (content_atualizado, novas_referencias)
        """
        print("\n" + "="*70)
        print("CONVERSAO DE LINKS PARA CITACOES (PRIORIDADE MAXIMA)")
        print("="*70)
        
        links = self.extract_links_from_text()
        print(f"   [OK] Encontrados {len(links)} links no documento")
        
        if not links:
            print("   [INFO] Nenhum link para converter")
            return self.content, {}
        
        content = self.content
        conversions_count = 0
        
        for i, (context, url) in enumerate(links, 1):
            print(f"\n   [{i}/{len(links)}] Processando: {url[:60]}...")
            
            # Buscar metadados
            metadata = self.fetch_metadata_from_url(url)
            
            if not metadata:
                print(f"      [AVISO] Nao foi possivel extrair metadados, usando fallback")
                # Fallback: usar domínio e ano atual
                domain_match = re.search(r'://([^/]+)', url)
                domain = domain_match.group(1).replace('www.', '').upper() if domain_match else 'WEB'
                metadata = {
                    'author': domain,
                    'year': str(datetime.now().year),
                    'title': context[:100] if context else 'Documento online'
                }
            
            # Gerar citação
            citation_key = self.generate_citation_key(metadata)
            print(f"      [OK] Citacao: ({citation_key})")
            
            # Verificar se já existe nas referências
            if citation_key not in self.existing_references:
                # Gerar referência completa
                full_ref = self.generate_full_reference(metadata, url)
                self.new_references[citation_key] = {
                    'full_author': metadata['author'],
                    'year': metadata['year'],
                    'last_name': metadata['author'].split()[0],
                    'full_entry': full_ref,
                    'original_entry': full_ref,
                    'has_url': True,
                    'url': url,
                    'access_date': datetime.now().strftime("%d %b. %Y")
                }
                print(f"      [OK] Referencia adicionada a lista")
            else:
                print(f"      [INFO] Referencia ja existe")
            
            # Substituir link por citação no texto
            # Padrão Markdown [texto](url)
            content = re.sub(
                rf'\[{re.escape(context)}\]\({re.escape(url)}\)',
                f'({citation_key})',
                content
            )
            # URL pura
            content = content.replace(url, f'({citation_key})')
            # HTML <a href>
            content = re.sub(
                rf'<a\s+href=["\']?{re.escape(url)}["\']?[^>]*>{re.escape(context)}</a>',
                f'({citation_key})',
                content,
                flags=re.IGNORECASE
            )
            
            conversions_count += 1
            self.conversions.append({
                'url': url,
                'citation': citation_key,
                'context': context
            })
        
        print(f"\n   [OK] {conversions_count} links convertidos em citacoes")
        print(f"   [OK] {len(self.new_references)} novas referencias adicionadas")
        print("="*70)
        
        return content, self.new_references
