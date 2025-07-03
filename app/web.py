from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import os
import json
from app.ocr import process_receipt, export_to_excel

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

EXCEL_FILENAME = "recibo.xlsx"
EXCEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), EXCEL_FILENAME)
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recibos.json")

def load_all_receipts():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_all_receipts(receipts):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(receipts, f, ensure_ascii=False, indent=2)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "receipt" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["receipt"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            data = process_receipt(filepath)
            # Load, append, save all receipts
            all_receipts = load_all_receipts()
            all_receipts.append(data)
            save_all_receipts(all_receipts)
            # Regenerate Excel with all receipts
            export_to_excel(all_receipts, output_path=EXCEL_PATH)
            return render_template("result.html", data=data, excel_file=EXCEL_FILENAME)
    return render_template("index.html")

@app.route("/download/<filename>")
def download(filename):
    # Use the correct absolute path
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)