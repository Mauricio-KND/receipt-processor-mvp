import cv2
import pytesseract
from typing import Dict


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
    """
    raw_text = extract_text_from_image(image_path)

    return {
        "raw_text": raw_text,
        "line_count": len(raw_text.split('\n')),
        "word_count": len(raw_text.split())
    }
    