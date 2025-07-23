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

class PDFReader:
    """
    Classe para leitura de PDFs usando múltiplas bibliotecas.
    Otimizada para extração de dados estruturados ferroviários.
    """
    
    def __init__(self, file_path, verbose=True):
        self.file_path = file_path
        self.verbose = verbose
        self.validate_file()
    
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

class DataStructureDetector:
    """
    Classe para detectar dados estruturados em texto extraído de PDFs.
    Otimizada para dados ferroviários.
    """
    
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.keywords = [
            'código:', 'fer-', 'extensão:', 'município', 'tarifa', 'características',
            'bitola', 'estação', 'viagem', 'demanda', 'passageiros', 'quilométrica',
            'operacional', 'física', 'receita', 'classe', 'econômica', 'executiva',
            'produção', 'tempo', 'categoria', 'empreendimento'
        ]
    
    def _print(self, message):
        """Print condicional baseado no verbose"""
        if self.verbose:
            print(message)
    
    def check_structured_data(self, text):
        """Verifica se o texto contém dados estruturados"""
        text_lower = text.lower()
        found_keywords = [keyword for keyword in self.keywords if keyword in text_lower]
        
        # Considera estruturado se tiver pelo menos 3 palavras-chave
        is_structured = len(found_keywords) >= 3
        
        return {
            'is_structured': is_structured,
            'found_keywords': found_keywords,
            'keyword_count': len(found_keywords),
            'confidence': len(found_keywords) / len(self.keywords)
        }
    
    def extract_structured_data(self, text):
        """Extrai dados estruturados usando regex"""
        data = {}
        
        # Extrair código
        codigo_match = re.search(r'Código:\s*([A-Z0-9-]+)', text, re.IGNORECASE)
        if codigo_match:
            data['codigo'] = codigo_match.group(1)
        
        # Extrair categoria
        categoria_match = re.search(r'Categoria:\s*([^\n]+)', text, re.IGNORECASE)
        if categoria_match:
            data['categoria'] = categoria_match.group(1).strip()
        
        # Extrair tipo de empreendimento
        tipo_match = re.search(r'Tipo\s+de\s+Empreendimento:\s*([^\n]+)', text, re.IGNORECASE)
        if tipo_match:
            data['tipo_empreendimento'] = tipo_match.group(1).strip()
        
        # Extrair extensão
        extensao_match = re.search(r'Extensão:\s*(\d+(?:\.\d+)?)\s*km', text, re.IGNORECASE)
        if extensao_match:
            data['extensao_km'] = float(extensao_match.group(1))
        
        # Extrair tipo de bitola
        bitola_match = re.search(r'Tipo\s+de\s+bitola:\s*([^\n]+)', text, re.IGNORECASE)
        if bitola_match:
            data['tipo_bitola'] = bitola_match.group(1).strip()
        
        # Extrair número de estações
        estacoes_match = re.search(r'(?:Total\s+de\s+)?estações:\s*(\d+)', text, re.IGNORECASE)
        if estacoes_match:
            data['total_estacoes'] = int(estacoes_match.group(1))
        
        # Extrair municípios
        municipios = []
        municipio_pattern = r'(\d+)\.\s*([^-]+?)\s*-\s*Extensão\s+acumulada:\s*(\d+(?:\.\d+)?)\s*km'
        for match in re.finditer(municipio_pattern, text, re.IGNORECASE):
            municipios.append({
                'ordem': int(match.group(1)),
                'municipio': match.group(2).strip(),
                'extensao_acumulada_km': float(match.group(3))
            })
        
        if municipios:
            data['municipios_atendidos'] = municipios
        
        # Extrair características operacionais
        operacionais = self._extract_operational_data(text)
        if operacionais:
            data['caracteristicas_operacionais'] = operacionais
        
        # Extrair tarifas
        tarifas = self._extract_tariff_data(text)
        if tarifas:
            data['tarifas'] = tarifas
        
        # Extrair desempenho
        desempenho = self._extract_performance_data(text)
        if desempenho:
            data['desempenho'] = desempenho
        
        return data
    
    def _extract_operational_data(self, text):
        """Extrai características operacionais"""
        operacionais = {}
        
        # Tempo de viagem ida
        tempo_ida_match = re.search(r'Tempo\s+de\s+viagem.*?ida.*?:\s*(\d+)\s*minutos', text, re.IGNORECASE)
        if tempo_ida_match:
            operacionais['tempo_viagem_ida_min'] = int(tempo_ida_match.group(1))
        
        # Tempo de viagem ida e volta
        tempo_ida_volta_match = re.search(r'Tempo\s+de\s+viagem.*?ida\s+e\s+volta.*?:\s*(\d+)\s*minutos', text, re.IGNORECASE)
        if tempo_ida_volta_match:
            operacionais['tempo_viagem_ida_volta_min'] = int(tempo_ida_volta_match.group(1))
        
        # Viagens por mês
        viagens_match = re.search(r'Viagens\s+por\s+mês:\s*(\d+)', text, re.IGNORECASE)
        if viagens_match:
            operacionais['viagens_mes'] = int(viagens_match.group(1))
        
        # Dias de operação por ano
        dias_match = re.search(r'Dias\s+de\s+operação\s+por\s+ano:\s*(\d+)', text, re.IGNORECASE)
        if dias_match:
            operacionais['dias_operacao_ano'] = int(dias_match.group(1))
        
        # Demanda por ano
        demanda_match = re.search(r'Demanda\s+por\s+ano:\s*([\d.,]+)\s*passageiros', text, re.IGNORECASE)
        if demanda_match:
            demanda_str = demanda_match.group(1).replace('.', '').replace(',', '')
            operacionais['demanda_ano'] = int(demanda_str)
        
        # Produção quilométrica
        producao_match = re.search(r'Produção\s+quilométrica\s+por\s+ano:\s*([\d.,]+)\s*km', text, re.IGNORECASE)
        if producao_match:
            producao_str = producao_match.group(1).replace('.', '').replace(',', '')
            operacionais['producao_quilometrica_km_ano'] = int(producao_str)
        
        return operacionais
    
    def _extract_tariff_data(self, text):
        """Extrai dados de tarifas"""
        tarifas = {}
        
        # Tarifa econômica
        tarifa_eco_fixa = re.search(r'Classe\s+Econômica:.*?Tarifa\s+fixa:\s*R\$\s*([\d,]+)', text, re.IGNORECASE | re.DOTALL)
        tarifa_eco_km = re.search(r'Classe\s+Econômica:.*?Tarifa\s+quilométrica:\s*R\$\s*([\d,]+)', text, re.IGNORECASE | re.DOTALL)
        
        if tarifa_eco_fixa or tarifa_eco_km:
            tarifas['economica'] = {}
            if tarifa_eco_fixa:
                tarifas['economica']['tarifa_fixa_reais'] = float(tarifa_eco_fixa.group(1).replace(',', '.'))
            if tarifa_eco_km:
                tarifas['economica']['tarifa_quilometrica_reais'] = float(tarifa_eco_km.group(1).replace(',', '.'))
        
        # Tarifa executiva
        tarifa_exec_fixa = re.search(r'Classe\s+Executiva:.*?Tarifa\s+fixa:\s*R\$\s*([\d,]+)', text, re.IGNORECASE | re.DOTALL)
        tarifa_exec_km = re.search(r'Classe\s+Executiva:.*?Tarifa\s+quilométrica:\s*R\$\s*([\d,]+)', text, re.IGNORECASE | re.DOTALL)
        
        if tarifa_exec_fixa or tarifa_exec_km:
            tarifas['executiva'] = {}
            if tarifa_exec_fixa:
                tarifas['executiva']['tarifa_fixa_reais'] = float(tarifa_exec_fixa.group(1).replace(',', '.'))
            if tarifa_exec_km:
                tarifas['executiva']['tarifa_quilometrica_reais'] = float(tarifa_exec_km.group(1).replace(',', '.'))
        
        return tarifas
    
    def _extract_performance_data(self, text):
        """Extrai dados de desempenho"""
        desempenho = {}
        
        # Pass.ano/km
        pass_ano_km_match = re.search(r'Pass\.ano/km:\s*([\d.,]+)', text, re.IGNORECASE)
        if pass_ano_km_match:
            desempenho['pass_ano_km'] = float(pass_ano_km_match.group(1).replace('.', '').replace(',', '.'))
        
        # Receita ano/km
        receita_match = re.search(r'Receita\s+ano/km:\s*R\$\s*([\d.,]+)', text, re.IGNORECASE)
        if receita_match:
            desempenho['receita_ano_km'] = float(receita_match.group(1).replace('.', '').replace(',', '.'))
        
        return desempenho
