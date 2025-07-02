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
    This function can be extended to include more preprocessing steps if needed.
    """
    try:
        img = cv2.imread(image_path)

        # Convert the image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to get a binary image
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

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
    # Common Spanish date patterns
    patterns = [
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
        match = re.search(pattern, text.lower())
        if match:
            day = match.group(1)
            if len(pattern.split()) > 4:  # Text month format
                month_str = match.group(2)
                month = str([i+1 for i,m in enumerate(SPANISH_MONTHS) 
                           if m.startswith(month_str[:3])][0])
                year = match.group(3)
            else:  # Numeric format
                month = match.group(2)
                year = match.group(3)
            
            # Fix 2-digit years
            if len(year) == 2:
                year = f"20{year}" if int(year) < 30 else f"19{year}"
            
            return f"{day.zfill(2)}/{month.zfill(2)}/{year}"
    return None

def extract_vendor(text: str) -> str:
    """
    Extract the vendor name from the text.
    Improved vendor name extraction with cleaning
    """
    blacklist = {'espacio para', 'logo', 'nota', 'factura', 'recibo', 'cod', 'fecha', 'nit', 'gran contribuyente'}
    
    for line in text.split('\n'):
        line = line.strip()
        if (line and len(line) > 3 and 
            not any(word in line.lower() for word in blacklist)):
            
            # Clean up common patterns
            vendor = line.split('NIT')[0].split('Nit')[0].split('RUT')[0].split('RUC')[0]
            vendor = re.sub(r'\d+', '', vendor).strip()
            return vendor if vendor else "VENDEDOR NO ENCONTRADO"
    
    return "Vendedor desconocido"

def extract_total(text: str) -> str:
    """
    Improved total amount detection for Spanish receipts
    """
    # Look for total lines specifically
    total_lines = [line.lower() for line in text.split('\n') 
                  if any(word in line.lower() for word in ['total', 'pagar', 'importe'])]
    
    # Search patterns
    patterns = [
        r'(\d{1,3}(?:\.\d{3})*(?:,\d{2}))\s*(?:$|€|usd)',  # 1.000,00
        r'(\$\s*\d{1,3}(?:\.\d{3})*(?:,\d{2}))',          # $ 1.000,00
        r'(\d{1,3}(?:,\d{3})*(?:\.\d{2}))\s*(?:$|€|usd)'  # 1,000.00
    ]
    
    for line in total_lines + [text]:
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                amount = match.group(1)
                # Standardize format
                amount = amount.replace('$', '').replace(' ', '')
                if '.' in amount and ',' in amount:  # 1.000,00 format
                    amount = amount.replace('.', '').replace(',', '.')
                elif ',' in amount:  # 1,000.00 format
                    amount = amount.replace(',', '')
                try:
                    return f"${float(amount):.2f}".replace('.', ',')  # Spanish format
                except ValueError:
                    continue
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

def export_to_excel(data: Dict[str, str], output_path: str = "recibo.xlsx") -> str:
    """
    Export extracted data to Excel with Spanish headers
    Enhanced Excel export with better formatting
    Fixed Excel export using proper openpyxl formatting
    """
    try:
        # Create DataFrame
        df = pd.DataFrame([{
            "FECHA": data.get("fecha", ""),
            "VENDEDOR": data.get("vendedor", ""),
            "TOTAL": data.get("total", ""),
            "ARTÍCULOS": data.get("articulos", ""),
            "TEXTO COMPLETO": data.get("texto_crudo", "")
        }])
        
        # Write to Excel with basic formatting
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Datos del Recibo')
            
            # Get worksheet and workbook objects
            worksheet = writer.sheets['Datos del Recibo']
            workbook = writer.book
            
            # Set column widths
            worksheet.column_dimensions['A'].width = 15  # Date
            worksheet.column_dimensions['B'].width = 25  # Vendor
            worksheet.column_dimensions['C'].width = 15  # Total
            worksheet.column_dimensions['D'].width = 40  # Items
            worksheet.column_dimensions['E'].width = 80  # Raw text
            
            # Format header row
            for cell in worksheet[1]:
                cell.font = openpyxl.styles.Font(bold=True, color="FFFFFF")
                cell.fill = openpyxl.styles.PatternFill("solid", fgColor="4F81BD")
                cell.border = openpyxl.styles.Border(
                    left=openpyxl.styles.Side(style='thin'),
                    right=openpyxl.styles.Side(style='thin'),
                    top=openpyxl.styles.Side(style='thin'),
                    bottom=openpyxl.styles.Side(style='thin')
                )
            
            # Format currency
            for cell in worksheet['C']:
                if cell.row > 1:  # Skip header
                    cell.number_format = '"$"#,##0.00'
        
        return output_path
    except Exception as e:
        raise ValueError(f"Error al exportar a Excel: {str(e)}")