import PyPDF2
import pdfplumber
from pdfminer.high_level import extract_text
from pdfminer.pdfpage import PDFPage
import os
import re
import json
import time
import pandas as pd
import numpy as np
from tqdm import tqdm
from pathlib import Path

# Carregar configurações do .env se existir
def load_env_config():
    """Carrega configurações do arquivo .env"""
    env_path = Path(__file__).parent / '.env'
    config = {}
    
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    
    return config

# Carregar configurações
ENV_CONFIG = load_env_config()

class PDFReader:
    """
    Classe para leitura de PDFs usando múltiplas bibliotecas.
    Otimizada para extração de dados estruturados ferroviários.
    Configurações via .env suportadas: PDF_MAX_PAGES, PDF_TIMEOUT
    """
    
    def __init__(self, file_path, verbose=None):
        self.file_path = file_path
        # Usar configuração do .env ou padrão
        if verbose is None:
            verbose = ENV_CONFIG.get('VERBOSE_LOGGING', 'True').lower() == 'true'
        self.verbose = verbose
        
        # Configurações do .env
        self.max_pages = int(ENV_CONFIG.get('PDF_MAX_PAGES', '100'))
        self.timeout = int(ENV_CONFIG.get('PDF_TIMEOUT', '600'))
        
        self.validate_file()
        
        if self.verbose:
            print(f"📄 PDFReader inicializado para: {Path(file_path).name}")
            print(f"⚙️ Max páginas: {self.max_pages}, Timeout: {self.timeout}s")
    
    def validate_file(self):
        """Valida se o arquivo PDF existe e é válido"""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {self.file_path}")
        
        if not self.file_path.lower().endswith('.pdf'):
            raise ValueError("O arquivo deve ser um PDF")
        
        # Verificar se o arquivo não está corrompido
        try:
            with open(self.file_path, 'rb') as file:
                PyPDF2.PdfReader(file)
        except Exception as e:
            raise ValueError(f"Arquivo PDF corrompido ou inválido: {e}")
    
    def _print(self, message):
        """Print condicional baseado no verbose"""
        if self.verbose:
            print(message)
    
    def get_num_pages(self):
        """Retorna o número total de páginas do PDF"""
        with open(self.file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return len(reader.pages)
    
    def extract_text_pypdf2(self, start_page=1, end_page=None):
        """
        Extrai texto usando PyPDF2 (método 1 - rápido)
        """
        if end_page is None:
            end_page = self.get_num_pages()
        
        pages = []
        
        with open(self.file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)
            
            # Validar páginas
            start_page = max(1, min(start_page, total_pages))
            end_page = max(start_page, min(end_page, total_pages))
            
            for page_num in range(start_page - 1, end_page):
                try:
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text and text.strip():
                        pages.append({
                            'page': page_num + 1,
                            'text': text.strip(),
                            'char_count': len(text.strip()),
                            'method': 'PyPDF2'
                        })
                except Exception as e:
                    self._print(f"⚠️ Erro ao extrair página {page_num + 1} com PyPDF2: {e}")
                    continue
        
        return pages
    
    def extract_text_pdfplumber(self, start_page=1, end_page=None):
        """
        Extrai texto usando pdfplumber (método 2 - mais preciso)
        """
        if end_page is None:
            end_page = self.get_num_pages()
        
        pages = []
        
        try:
            with pdfplumber.open(self.file_path) as pdf:
                total_pages = len(pdf.pages)
                
                # Validar páginas
                start_page = max(1, min(start_page, total_pages))
                end_page = max(start_page, min(end_page, total_pages))
                
                for page_num in range(start_page - 1, end_page):
                    try:
                        page = pdf.pages[page_num]
                        text = page.extract_text()
                        
                        if text and text.strip():
                            pages.append({
                                'page': page_num + 1,
                                'text': text.strip(),
                                'char_count': len(text.strip()),
                                'method': 'pdfplumber'
                            })
                    except Exception as e:
                        self._print(f"⚠️ Erro ao extrair página {page_num + 1} com pdfplumber: {e}")
                        continue
        
        except Exception as e:
            self._print(f"❌ Erro ao abrir PDF com pdfplumber: {e}")
            return []
        
        return pages
    
    def extract_text_pdfminer(self, start_page=1, end_page=None):
        """
        Extrai texto usando pdfminer (método 3 - mais robusto)
        """
        if end_page is None:
            end_page = self.get_num_pages()
        
        pages = []
        
        try:
            with open(self.file_path, 'rb') as file:
                all_pages = list(PDFPage.get_pages(file))
                total_pages = len(all_pages)
                
                # Validar páginas
                start_page = max(1, min(start_page, total_pages))
                end_page = max(start_page, min(end_page, total_pages))
                
                for page_num in range(start_page - 1, end_page):
                    try:
                        # Extrair texto da página específica
                        text = extract_text(self.file_path, page_numbers=[page_num])
                        
                        if text and text.strip():
                            pages.append({
                                'page': page_num + 1,
                                'text': text.strip(),
                                'char_count': len(text.strip()),
                                'method': 'pdfminer'
                            })
                    except Exception as e:
                        self._print(f"⚠️ Erro ao extrair página {page_num + 1} com pdfminer: {e}")
                        continue
        
        except Exception as e:
            self._print(f"❌ Erro ao processar PDF com pdfminer: {e}")
            return []
        
        return pages
    
    def extract_text_best_method(self, start_page=1, end_page=None):
        """
        Extrai texto usando o melhor método disponível.
        Tenta múltiplas bibliotecas para garantir melhor resultado.
        """
        self._print(f"🔍 Extraindo texto das páginas {start_page} a {end_page or 'fim'}")
        
        methods = [
            ("pdfplumber", self.extract_text_pdfplumber),
            ("PyPDF2", self.extract_text_pypdf2),
            ("pdfminer", self.extract_text_pdfminer)
        ]
        
        best_result = []
        best_method = None
        
        for method_name, method_func in methods:
            try:
                self._print(f"🔄 Tentando método: {method_name}")
                result = method_func(start_page, end_page)
                
                if result and len(result) > len(best_result):
                    best_result = result
                    best_method = method_name
                    self._print(f"✅ {method_name}: {len(result)} páginas extraídas")
                elif result:
                    self._print(f"✅ {method_name}: {len(result)} páginas extraídas")
                else:
                    self._print(f"❌ {method_name}: Nenhuma página extraída")
                
            except Exception as e:
                self._print(f"❌ Erro com {method_name}: {e}")
                continue
        
        if best_result:
            self._print(f"🎯 Melhor método: {best_method} ({len(best_result)} páginas)")
            return best_result
        else:
            self._print("❌ Nenhum método conseguiu extrair texto")
            return []
    
    def extract_text_from_page(self, page_number):
        """Extrai texto de uma página específica"""
        return self.extract_text_best_method(page_number, page_number)
    
    def get_file_info(self):
        """Retorna informações sobre o arquivo PDF"""
        file_size = os.path.getsize(self.file_path)
        num_pages = self.get_num_pages()
        
        return {
            'file_path': self.file_path,
            'file_size_mb': file_size / (1024 * 1024),
            'num_pages': num_pages,
            'file_name': os.path.basename(self.file_path)
        }
