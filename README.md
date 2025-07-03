# Procesador de Recibos MVP

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.1.1-green.svg)

Aplicación web para extraer datos estructurados de imágenes de recibos y exportarlos a Excel.

## Características principales
- Procesamiento de imágenes de recibos mediante OCR (Tesseract)
- Extracción robusta de datos clave (fecha, vendedor, total) con validación y fallback
- Exportación a formato Excel compatible, siempre actualizado con todos los recibos procesados
- Interfaz web simple (Flask) para subir imágenes y descargar el Excel generado
- Almacenamiento persistente de recibos procesados en un archivo JSON

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
   python3 -m venv venv
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

Para iniciar la aplicación web:
```bash
python app/web.py
```

Luego abre tu navegador en [http://localhost:5000](http://localhost:5000) y sube imágenes de recibos para procesarlas.

## 📝 Estructura del Proyecto
```
receipt-processor-mvp/
├── app/                   # Código principal
│   ├── ocr.py             # Funciones de procesamiento OCR y extracción de datos
│   ├── web.py             # Aplicación Flask (interfaz web)
│   └── templates/         # Plantillas HTML para la web
├── test/                  # Pruebas
│   └── sample_receipts/   # Imágenes de prueba
├── recibos.json           # Base de datos simple de recibos procesados
├── recibo.xlsx            # Archivo Excel generado con todos los recibos
└── requirements.txt       # Dependencias
```

## 📄 Licencia
MIT

