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
    Extract the vendor name from the text.
    Improved: Look for lines with NIT/RUT and extract vendor name before that.
    Fallback: first uppercase line with at least 4 letters.
    """
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        match = re.search(r'^(.*?)(?:\s+)?(?:NIT|RUT)[\s:]*([\w-]+)', line, re.IGNORECASE)
        if match:
            vendor = match.group(1).strip()
            if vendor and len(vendor) > 2:
                return vendor
    # Fallback: first line with mostly uppercase letters and at least 4 letters
    for line in text.split('\n'):
        line = line.strip()
        if len(line) > 3 and sum(1 for c in line if c.isupper()) > 3:
            return line
    # Fallback: first non-empty line
    for line in text.split('\n'):
        line = line.strip()
        if line and len(line) > 3:
            return line
    return "Vendedor desconocido"

def extract_total(text: str) -> str:
    """
    Improved total amount detection for Spanish receipts.
    Looks for the largest number in lines containing 'TOTAL'.
    """
    total_lines = [line for line in text.split('\n') if 'total' in line.lower()]
    amounts = []
    for line in total_lines:
        # Busca todos los números con separadores de miles y decimales
        found = re.findall(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2,3})?)', line)
        for amt in found:
            # Normaliza el formato
            amt_norm = amt.replace('.', '').replace(',', '.')
            try:
                amounts.append(float(amt_norm))
            except Exception:
                continue
    if amounts:
        max_amount = max(amounts)
        # Devuelve en formato español
        return f"${max_amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
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

def export_to_excel(data, output_path: str = "recibo.xlsx") -> str:
    """
    Export extracted data to Excel with Spanish headers.
    Accepts a list of dicts (for multiple receipts) or a single dict.
    """
    import pandas as pd
    try:
        # If single dict, wrap in list
        if isinstance(data, dict):
            data = [data]
        df = pd.DataFrame([{
            "FECHA": d.get("fecha", ""),
            "VENDEDOR": d.get("vendedor", ""),
            "TOTAL": d.get("total", ""),
            "ARTÍCULOS": d.get("articulos", ""),
            "TEXTO COMPLETO": d.get("texto_crudo", "")
        } for d in data])
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Datos del Recibo')
            worksheet = writer.sheets['Datos del Recibo']
            worksheet.column_dimensions['A'].width = 15
            worksheet.column_dimensions['B'].width = 25
            worksheet.column_dimensions['C'].width = 15
            worksheet.column_dimensions['D'].width = 40
            worksheet.column_dimensions['E'].width = 80
        return output_path
    except Exception as e:
        raise ValueError(f"Error exporting to Excel: {str(e)}")