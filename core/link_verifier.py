"""
Verificador de links (URLs e DOIs) e atualizador de datas de acesso
"""

import re
import requests
from datetime import datetime
from typing import Dict, List, Tuple
from urllib.parse import urlparse


class LinkVerifier:
    """
    Verifica links em referências:
    - Valida URLs e DOIs
    - Verifica se estão acessíveis
    - Atualiza datas de acesso
    """
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def verify_url(self, url: str) -> Dict[str, any]:
        """
        Verifica se URL está acessível
        
        Args:
            url: URL para verificar
            
        Returns:
            Dict com status da verificação
        """
        result = {
            'url': url,
            'valid': False,
            'accessible': False,
            'status_code': None,
            'error': None,
            'final_url': url  # URL final após redirecionamentos
        }
        
        # Validar formato da URL
        try:
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                result['error'] = 'URL inválida'
                return result
            result['valid'] = True
        except Exception as e:
            result['error'] = str(e)
            return result
        
        # Tentar acessar URL
        try:
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
            result['status_code'] = response.status_code
            result['final_url'] = response.url
            
            if response.status_code < 400:
                result['accessible'] = True
            else:
                # Tentar GET se HEAD falhar
                response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                result['status_code'] = response.status_code
                result['accessible'] = response.status_code < 400
                
        except requests.exceptions.Timeout:
            result['error'] = 'Timeout'
        except requests.exceptions.ConnectionError:
            result['error'] = 'Erro de conexão'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def verify_doi(self, doi: str) -> Dict[str, any]:
        """
        Verifica se DOI é válido e resolve para URL
        
        Args:
            doi: DOI para verificar (pode incluir ou não https://doi.org/)
            
        Returns:
            Dict com status da verificação
        """
        # Limpar DOI
        doi_clean = doi.replace('https://doi.org/', '').replace('http://dx.doi.org/', '')
        doi_url = f'https://doi.org/{doi_clean}'
        
        result = {
            'doi': doi_clean,
            'doi_url': doi_url,
            'valid': False,
            'resolves': False,
            'resolved_url': None,
            'error': None
        }
        
        # Validar formato do DOI
        doi_pattern = r'^10\.\d{4,}/\S+$'
        if not re.match(doi_pattern, doi_clean):
            result['error'] = 'Formato de DOI inválido'
            return result
        
        result['valid'] = True
        
        # Tentar resolver DOI
        try:
            response = self.session.head(doi_url, timeout=self.timeout, allow_redirects=True)
            if response.status_code < 400:
                result['resolves'] = True
                result['resolved_url'] = response.url
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def extract_links_from_reference(self, reference: str) -> List[Dict]:
        """
        Extrai todos os links (URLs e DOIs) de uma referência
        
        Args:
            reference: Texto da referência
            
        Returns:
            Lista de dicts com informações dos links encontrados
        """
        links = []
        
        # Extrair URLs
        url_pattern = r'https?://[^\s<>"]+'
        urls = re.findall(url_pattern, reference)
        for url in urls:
            # Remover pontuação final
            url = url.rstrip('.,;:')
            links.append({
                'type': 'url',
                'value': url,
                'position': reference.find(url)
            })
        
        # Extrair DOIs
        doi_pattern = r'(?:doi:|DOI:)?\s*(10\.\d{4,}/[^\s<>"]+)'
        dois = re.findall(doi_pattern, reference)
        for doi in dois:
            doi = doi.rstrip('.,;:')
            links.append({
                'type': 'doi',
                'value': doi,
                'position': reference.find(doi)
            })
        
        return sorted(links, key=lambda x: x['position'])
    
    def verify_reference_links(self, reference: str) -> Dict[str, any]:
        """
        Verifica todos os links em uma referência
        
        Args:
            reference: Texto da referência
            
        Returns:
            Dict com resultados da verificação
        """
        links = self.extract_links_from_reference(reference)
        
        results = {
            'reference': reference,
            'links_found': len(links),
            'links': [],
            'all_valid': True,
            'all_accessible': True
        }
        
        for link_info in links:
            if link_info['type'] == 'url':
                verification = self.verify_url(link_info['value'])
            elif link_info['type'] == 'doi':
                verification = self.verify_doi(link_info['value'])
            
            results['links'].append({
                'type': link_info['type'],
                'value': link_info['value'],
                'verification': verification
            })
            
            if not verification.get('valid', False):
                results['all_valid'] = False
            if not verification.get('accessible', False) and not verification.get('resolves', False):
                results['all_accessible'] = False
        
        return results
    
    def update_access_date(self, reference: str, new_date: datetime = None) -> str:
        """
        Atualiza data de acesso em uma referência
        
        Args:
            reference: Texto da referência
            new_date: Nova data (usa data atual se None)
            
        Returns:
            Referência com data atualizada
        """
        if new_date is None:
            new_date = datetime.now()
        
        # Meses em português
        months_pt = {
            1: 'jan.', 2: 'fev.', 3: 'mar.', 4: 'abr.',
            5: 'maio', 6: 'jun.', 7: 'jul.', 8: 'ago.',
            9: 'set.', 10: 'out.', 11: 'nov.', 12: 'dez.'
        }
        
        formatted_date = f"{new_date.day} {months_pt[new_date.month]} {new_date.year}"
        
        # Padrão para encontrar data de acesso existente
        access_pattern = r'Acesso em:\s*\d{1,2}\s+\w+\.?\s+\d{4}'
        
        if re.search(access_pattern, reference):
            # Atualizar data existente
            updated = re.sub(
                access_pattern,
                f'Acesso em: {formatted_date}',
                reference
            )
        else:
            # Adicionar data de acesso se não existir
            # Procurar onde inserir (após URL)
            url_pattern = r'(Disponível em:\s*https?://[^\s<>"]+)'
            if re.search(url_pattern, reference):
                updated = re.sub(
                    url_pattern,
                    rf'\1. Acesso em: {formatted_date}',
                    reference
                )
            else:
                # Adicionar no final
                updated = reference.rstrip('.') + f'. Acesso em: {formatted_date}.'
        
        return updated
    
    def should_update_date(self, reference: str, days_threshold: int = 30) -> bool:
        """
        Verifica se data de acesso deve ser atualizada
        
        Args:
            reference: Texto da referência
            days_threshold: Limiar em dias para considerar data antiga
            
        Returns:
            True se deve atualizar
        """
        # Extrair data de acesso atual
        access_pattern = r'Acesso em:\s*(\d{1,2})\s+(\w+)\.?\s+(\d{4})'
        match = re.search(access_pattern, reference)
        
        if not match:
            return True  # Não tem data, deve adicionar
        
        day, month_str, year = match.groups()
        
        # Mapear mês
        months_map = {
            'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4,
            'maio': 5, 'jun': 6, 'jul': 7, 'ago': 8,
            'set': 9, 'out': 10, 'nov': 11, 'dez': 12
        }
        
        month_abbr = month_str.lower().rstrip('.')
        month = months_map.get(month_abbr, 1)
        
        try:
            access_date = datetime(int(year), month, int(day))
            days_diff = (datetime.now() - access_date).days
            return days_diff > days_threshold
        except:
            return True  # Erro ao parsear, atualizar por segurança
    
    def batch_verify_references(self, references: List[str]) -> List[Dict]:
        """
        Verifica links em múltiplas referências
        
        Args:
            references: Lista de referências
            
        Returns:
            Lista de resultados
        """
        results = []
        
        for i, ref in enumerate(references):
            print(f"Verificando referência {i+1}/{len(references)}...")
            result = self.verify_reference_links(ref)
            results.append(result)
        
        return results
