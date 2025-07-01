import os
from app.ocr import test_ocr

def run_tests():
    """
    Run the OCR tests.
    """
    # Define the path to the test image
    sample_dir = "test/sample_receipts"
    for filename in os.listdir(sample_dir):
        if filename.lower().endswith((".jpg", ".png", ".jpeg")):
            print(f"\nTesting OCR on {filename}...")
            try:
                result = test_ocr(os.path.join(sample_dir, filename))
                print(f"Extracted: {result['word_count']} words, {result['line_count']} lines")
                print("First 50 characters of raw text:")
                print(result['raw_text'][:50] + "...")
            except Exception as e:
                print(f"Error processing {str(e)}")

if __name__ == "__main__":
    run_tests()
