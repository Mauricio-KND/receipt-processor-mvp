import os
from typing import Dict
from app.ocr import export_to_excel, extract_text_from_image, process_receipt, test_ocr

def test_ocr(image_path: str) -> Dict:
    """
    Test the full OCR pipeline with structured output
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
