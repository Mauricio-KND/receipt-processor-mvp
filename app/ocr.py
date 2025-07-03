import re
import openpyxl
import openpyxl.styles
import pandas as pd
import cv2
import pytesseract
from typing import Dict, Optional

SPANISH_MONTHS = {'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                  'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'}

def preprocess_image(image_path: str) -> str:
    """
    Preprocess the image for OCR.
    Improved: Avoid inversion, use adaptive thresholding.
    """
    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Adaptive thresholding (no inversion)
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 31, 10
        )
        return thresh
    except Exception as e:
        raise ValueError(f"Error processing image (failed) {str(e)}")
    
def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from the preprocessed image.
    This function can be extended to include more OCR logic if needed.
    """
    try:
        # Preprocess the image
        preprocessed_image = preprocess_image(image_path)

        # Configuring tesseract
        custom_config = r'--oem 3 --psm 6' # OCR Engine Mode 3 and Page Segmentation Mode 6

        # Running OCR on the preprocessed image
        text = pytesseract.image_to_string(preprocessed_image, config=custom_config)
        print(f"\n--- OCR RAW TEXT ({image_path}) ---\n{text}\n-------------------\n")
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error extracting text from image (failed) {str(e)}")
    
def test_ocr(image_path: str) -> Dict:
    """
    Test the OCR functionality with a sample image.
    Test the full OCR pipeline with structured output and proper error handling
    Returns a dictionary with 'status' key and other metadata
    """
    try:
        # Extract raw text
        raw_text = extract_text_from_image(image_path)
        
        # Process receipt
        receipt_data = process_receipt(image_path)
        
        # Export to Excel
        excel_path = export_to_excel(receipt_data)
        
        return {
            "status": "success",
            "raw_text": raw_text,
            "structured_data": receipt_data,
            "excel_file": excel_path,
            "message": f"Recibo procesado correctamente. Excel guardado en {excel_path}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Error procesando el recibo"
        }
    
def extract_spanish_date(text: str) -> Optional[str]:
    """
    Extract a date in multiple format.
    Enhanced Spanish date extraction with several patterns
    """
    patterns = [
        # YYYY/MM/DD or YYYY-MM-DD
        r'(\d{4})[/-](\d{2})[/-](\d{2})',
        # DD/MM/YYYY or DD-MM-YYYY
        r'(\d{2})[/-](\d{2})[/-](\d{4})',
        # Pattern for dates like "26/06/2025" (found in receipt3)
        r'(?<!\d)(\d{2})[/-](\d{2})[/-](\d{4})(?!\d)',
        # Pattern for dates like "26-Jun-2025"
        r'(?<!\d)(\d{2})[-/](' + '|'.join([m[:3].lower() for m in SPANISH_MONTHS]) + r')[-/](\d{4})(?!\d)',
        # Pattern for dates like "26 de jun. 2025"
        r'(\d{1,2})\s+de\s+(' + '|'.join([m[:3].lower() + r'\.?' for m in SPANISH_MONTHS]) + r')\s+de?\s+(\d{4})'
        # DD/MM/YYYY or DD-MM-YYYY
        r'(?:\b|\D)(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b',
        # DD de MES de YYYY (15 de julio de 2023)
        r'(\d{1,2})\s+de\s+(' + '|'.join(SPANISH_MONTHS) + r')\s+de\s+(\d{4})',
        # Month abbreviations (15 jul. 2023)
        r'(\d{1,2})\s+(' + '|'.join([m[:3] + r'\.?' for m in SPANISH_MONTHS]) + r')\s+(\d{4})'
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            if len(match.groups()) == 3:
                if len(match.group(1)) == 4:  # YYYY/MM/DD
                    year, month, day = match.group(1), match.group(2), match.group(3)
                else:  # DD/MM/YYYY
                    day, month, year = match.group(1), match.group(2), match.group(3)
                return f"{day.zfill(2)}/{month.zfill(2)}/{year}"
    return None

def extract_vendor(text: str) -> str:
    """
    Robust vendor extraction:
    - First, looks for lines with common vendor keywords (e.g., FRUVER, AGROMERCADO).
    - Then, looks for lines with 'NIT', 'IT', '1T', etc.
    - Then, looks for lines with many uppercase letters (likely vendor names).
    - Finally, returns the first non-empty line.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    # 1. Look for common vendor keywords
    keywords = ['FRUVER', 'AGROMERCADO', 'SUPERMERCADO', 'TIENDA', 'MINIMERCADO', 'D1', 'EXITO']
    for line in lines:
        for kw in keywords:
            if kw in line.upper():
                return line
    # 2. Look for NIT/IT/1T pattern
    nit_regex = r'(.*?)(?:\s+)?(?:N[\s:]*[1I]T|NIT|IT|1T)[\s:]*([\w-]+)'
    for line in lines:
        match = re.search(nit_regex, line, re.IGNORECASE)
        if match:
            vendor = match.group(1).strip()
            if vendor and len(vendor) > 2:
                return vendor
    # 3. Look for lines with many uppercase letters (likely vendor names)
    for line in lines:
        if len(line) >= 8 and sum(1 for c in line if c.isupper()) >= 4:
            return line
    # 4. Fallback: first non-empty line
    return lines[0] if lines else "Vendedor desconocido"

def extract_total(text: str) -> str:
    """
    Extracts the largest integer from lines containing 'TOTAL'.
    Handles Colombian peso formatting (comma as thousands separator).
    """
    total_lines = [line for line in text.split('\n') if 'total' in line.lower()]
    amounts = []
    for line in total_lines:
        # Find all numbers with thousands separators, possibly decimals
        found = re.findall(r'(\d{1,3}(?:[.,]\d{3})+|\d+)', line)
        for amt in found:
            # Remove all non-digit characters (keep only numbers)
            amt_clean = re.sub(r'[^\d]', '', amt)
            try:
                amounts.append(int(amt_clean))
            except Exception:
                continue
    if amounts:
        max_amount = max(amounts)
        # Format as $12.930 (COP style, no decimals)
        return f"${max_amount:,}".replace(',', '.')
    return "TOTAL NO ENCONTRADO"

def extract_items(text: str) -> str:
    """
    Extract potential items from receipt (lines with prices)
    """
    item_lines = []
    for line in text.split('\n'):
        if re.search(r'\d+[\.,]\d{2}', line):  # Contains price pattern
            # Clean up line
            clean_line = ' '.join(line.strip().split())
            item_lines.append(clean_line)
    return '\n'.join(item_lines) if item_lines else "ARTÍCULOS NO ENCONTRADOS"

def validate_receipt_data(data: Dict) -> Dict:
    """
    Validate extracted receipt data and add validation flag
    Enhanced validation with specific checks
    """
    # Field validation rules
    validation = {
        'fecha': {
            'required': True,
            'valid': bool(data.get('fecha')) and data['fecha'] != "None"
        },
        'vendedor': {
            'required': True,
            'valid': bool(data.get('vendedor')) and "NO ENCONTRADO" not in data['vendedor']
        },
        'total': {
            'required': True,
            'valid': bool(data.get('total')) and "NO ENCONTRADO" not in data['total']
        }
    }
    
    # Calculate overall status
    is_valid = all(v['valid'] for v in validation.values() if v['required'])
    missing_fields = [k for k, v in validation.items() 
                     if v['required'] and not v['valid']]
    
    # Add validation info to data
    validated_data = data.copy()
    validated_data.update({
        'es_valido': is_valid,
        'campos_faltantes': missing_fields,
        'validation_details': validation
    })
    
    return validated_data

def process_receipt(image_path: str) -> Dict[str, str]:
    """
    Main function to process receipt and return structured data
    """
    raw_text = extract_text_from_image(image_path)
    
    extracted_data = {
        "fecha": extract_spanish_date(raw_text),
        "vendedor": extract_vendor(raw_text),
        "total": extract_total(raw_text),
        "articulos": extract_items(raw_text),
        "texto_crudo": raw_text
    }
    
    # Add validation
    return validate_receipt_data(extracted_data)

def export_to_excel(data, output_path="recibo.xlsx"):
    """
    Export header columns to Excel.
    """
    if isinstance(data, dict):
        data = [data]
    df = pd.DataFrame([{
        "FECHA": d.get("fecha", ""),
        "VENDEDOR": d.get("vendedor", ""),
        "TOTAL": d.get("total", "")
    } for d in data])
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Recibos')
        worksheet = writer.sheets['Recibos']
        worksheet.column_dimensions['A'].width = 15
        worksheet.column_dimensions['B'].width = 30
        worksheet.column_dimensions['C'].width = 15
    return output_path