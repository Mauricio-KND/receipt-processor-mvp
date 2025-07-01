# receipt-processor-mvp
Browser-based Python app that extracts structured data from receipt images and outputs to Excel
# Procesador de Recibos MVP

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.1.1-green.svg)

Aplicación web para extraer datos estructurados de imágenes de recibos y exportarlos a Excel.

## Características principales
- Procesamiento de imágenes de recibos mediante OCR (Tesseract)
- Extracción de datos clave (fecha, vendedor, total)
- Exportación a formato Excel compatible
- Interfaz web simple (Flask)

## 📋 Requisitos

- Python 3.8+
- Tesseract OCR instalado en el sistema
- Dependencias de Python (ver `requirements.txt`)

## 🛠️ Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/Mauricio-KND/receipt-processor-mvp.git
   cd receipt-processor-mvp
   ```

2. Crear y activar entorno virtual:
   ```bash
   source venv/bin/activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Instalar Tesseract OCR:
   - **Linux**: `sudo apt install tesseract-ocr`

## 🚀 Uso

Para probar el módulo OCR:
```bash
python test/test_ocr.py
```

Para iniciar la aplicación web (próximamente):
```bash
python app/main.py
```

## 📝 Estructura del Proyecto
```
receipt-processor-mvp/
├── app/               # Código principal
│   ├── ocr.py         # Funciones de procesamiento OCR
│   └── main.py        # Aplicación Flask
├── test/              # Pruebas
│   └── sample_receipts/ # Imágenes de prueba
└── requirements.txt   # Dependencias
```

## 📄 Licencia
MIT License

---

# Receipt Processor MVP

Web app to extract structured data from receipt images and export to Excel.

## 📋 Requirements

- Python 3.8+
- Tesseract OCR installed
- Python dependencies (see `requirements.txt`)

## 🛠️ Installation
(Similar to Spanish version above)

## 🚀 Usage
(Similar to Spanish version above)