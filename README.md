# Receipt Processor MVP (receipt2sheet)

Extracts the **vendor** and **total value** from purchase receipt images and exports them to an Excel file.  
Includes a web interface for uploading images and downloading the updated Excel.

---

## Tech Stack

- **Python 3.8+**
- **Flask** (web interface)
- **OpenCV** (image preprocessing)
- **pytesseract** (OCR)
- **pandas** (Excel export)
- **openpyxl** (Excel formatting)
- **Bootstrap 5** (web UI)
- **Tesseract OCR** (must be installed on your system)

---

## Requirements

- Python 3.8+
- Tesseract OCR installed (`sudo apt install tesseract-ocr`)
- Python dependencies (`requirements.txt`)

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Mauricio-KND/receipt-processor-mvp.git
   cd receipt-processor-mvp
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install Tesseract OCR:
   ```bash
   sudo apt install tesseract-ocr
   ```

---

## Usage

### Web App:
```bash
python app/web.py
```
Open [http://localhost:5000](http://localhost:5000) in your browser, upload receipt images, and download the updated Excel file.

---

## Deployment

### Local
Just run:
```bash
python app/web.py
```
and open [http://localhost:5000](http://localhost:5000).

### Railway (Cloud) Deployment

This project includes a `Dockerfile` for seamless deployment on Railway or any Docker-compatible platform.

**Steps:**
1. Push your code (with the Dockerfile) to GitHub.
2. Create a new Railway project and link your repository.
3. Railway will auto-detect and use the Dockerfile.
4. The app will be available at your Railway-provided URL.

**What the Dockerfile does:**
- Installs all system dependencies for Tesseract OCR and OpenCV.
- Installs Python dependencies from `requirements.txt`.
- Exposes port 8080 (used by Railway).
- Starts the Flask app with `python app/web.py`.

**Note:**  
If you want to run the app locally with Docker:
```bash
docker build -t receipt-processor-mvp .
docker run -p 8080:8080 receipt-processor-mvp
```
Then open [http://localhost:8080](http://localhost:8080).

---

## 📝 Project Structure

```
receipt-processor-mvp/
├── app/
│   ├── ocr.py             # OCR and extraction logic
│   ├── web.py             # Flask web app
│   ├── __init__.py
│   └── templates/         # HTML templates
│       ├── index.html
│       └── result.html
├── recibo.xlsx            # Generated Excel file (always up to date)
├── recibos.json           # Persistent storage of processed receipts
├── requirements.txt
└── README.md
```

---

## Features

- Extracts **vendor** and **total value** from receipts (robust to OCR errors).
- Prevents duplicate receipts.
- Always-up-to-date Excel export with only the relevant columns.
- Simple, user-friendly web interface.
- Error and warning messages for missing/invalid fields.
- **Deployment on Railway with Docker support.**

---

## Notes

- To reset the processed receipts, delete `recibos.json`.
- The Excel file will always contain all unique processed receipts.
- Some receipts with extreme OCR errors or highly unusual layouts may not be extracted properly.

---

