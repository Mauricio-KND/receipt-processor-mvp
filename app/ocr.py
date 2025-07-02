import re
import pandas as pd
import cv2
import pytesseract
from typing import Dict

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
    
def extract_spanish_date(text: str) -> str:
    """
    Extract a date in multiple format.
    The month must be in Spanish.
    """
    date_pattern1 = r'(\d{1,2})[/-](\d{1,2})[/\-](\d{2,4})'
    date_pattern2 = r'(\d{1,2})\s*(?:de)?\s*(' + '|'.join(SPANISH_MONTHS) + r')\s*(?:de)?\s*(\d{4})'

    for pattern in [date_pattern1, date_pattern2]:
        match = re.search(pattern, text.lower())
        if match:
            if pattern in date_pattern1:
                day, month, year = match.groups()
                return f"{day.zfill(2)}/{month.zfill(2)}/{year.zfill(4)}"
            else:
                day, month, year = match.groups()
                month_num = list(SPANISH_MONTHS).index(month) + 1
                return f"{day.zfill(2)}/{str(month_num).zfill(2)}/{year.zfill(4)}"
    return None

def extract_vendor(text: str) -> str:
    """
    Extract the vendor name from the text.
    This function can be extended to include more vendor extraction logic if needed.
    """
    # Example logic to extract vendor name
    # This is a placeholder and should be replaced with actual logic
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return lines[0] if lines else "Vendedor desconocido"

def extract_total(text: str) -> str:
    """
    Extract the total amount from the text.
    This function can be extended to include more total extraction logic if needed.
    """
    patterns = [
        r'total\s*:\s*(\$\d+[\.,]\d{2})',  # $1,000.00
        r'total\s*:\s*(\d+[\.,]\d{2}\s*€)',  # 1,000.00 €
        r'total\s*[\w\s]*\s*(\d+[\.,]\d{2})',  # Total a pagar: 1,000.00
        r'importe\s*total\s*:\s*(\d+[\.,]\d{2})'  # Importe total: 1,000.00
    ]

    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            amount = match.group(1)
            # Standardize decimal separator
            amount = amount.replace(',', '.')
            return amount
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

def process_receipt(image_path: str) -> Dict[str, str]:
    """
    Main function to process receipt and return structured data
    """
    raw_text = extract_text_from_image(image_path)
    
    return {
        "fecha": extract_spanish_date(raw_text),
        "vendedor": extract_vendor(raw_text),
        "total": extract_total(raw_text),
        "articulos": extract_items(raw_text),
        "texto_crudo": raw_text
    }

def export_to_excel(data: Dict[str, str], output_path: str = "recibo.xlsx") -> str:
    """
    Export extracted data to Excel with Spanish headers
    """
    try:
        df = pd.DataFrame([{
            "FECHA": data["fecha"],
            "VENDEDOR": data["vendedor"],
            "TOTAL": data["total"],
            "ARTÍCULOS": data["articulos"],
            "TEXTO COMPLETO": data["texto_crudo"]
        }])
        
        # Format Excel output
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Datos del Recibo')
            worksheet = writer.sheets['Datos del Recibo']
            
            # Adjust column widths
            worksheet.column_dimensions['A'].width = 15
            worksheet.column_dimensions['B'].width = 30
            worksheet.column_dimensions['C'].width = 15
            worksheet.column_dimensions['D'].width = 50
            worksheet.column_dimensions['E'].width = 80
            
        return output_path
    except Exception as e:
        raise ValueError(f"Error al exportar a Excel: {str(e)}")