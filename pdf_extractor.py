#!/usr/bin/env python3
"""
PDF Text Extractor using pdfplumber
Extrae texto de archivos PDF de forma confiable
"""

import sys
import json
import pdfplumber
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """
    Extrae texto de un archivo PDF usando pdfplumber
    
    Args:
        pdf_path (str): Ruta al archivo PDF
        
    Returns:
        dict: Resultado con texto extraído o error
    """
    try:
        # Verificar que el archivo existe
        if not Path(pdf_path).exists():
            return {
                "success": False,
                "error": f"File not found: {pdf_path}"
            }
        
        # Extraer texto usando pdfplumber
        text_content = ""
        
        with pdfplumber.open(pdf_path) as pdf:
            # Extraer texto de todas las páginas
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_content += f"\n--- Página {page_num} ---\n"
                    text_content += page_text + "\n"
        
        # Limpiar y validar el texto extraído
        text_content = text_content.strip()
        
        if not text_content or len(text_content) < 10:
            return {
                "success": False,
                "error": "No text could be extracted from the PDF"
            }
        
        return {
            "success": True,
            "text": text_content,
            "length": len(text_content)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing PDF: {str(e)}"
        }

def main():
    """Función principal para uso desde línea de comandos"""
    if len(sys.argv) != 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python pdf_extractor.py <pdf_file_path>"
        }))
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    result = extract_text_from_pdf(pdf_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
