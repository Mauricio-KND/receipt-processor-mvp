# Procesador de Recibos MVP

Procesa imágenes de recibos, extrae datos específicos (fecha, vendedor, total) y los exporta a un archivo Excel. Incluye una interfaz web para subir imágenes y descargar el archivo generado.

---

## 🖥️ Tech Stack

- **Python 3.8+**
- **Flask** (interfaz web)
- **OpenCV** (preprocesamiento de imágenes)
- **pytesseract** (OCR)
- **pandas** (exportación a Excel)
- **openpyxl** (formato Excel)
- **Bootstrap 5** (estilizado web)
- **Tesseract OCR** (debe estar instalado en el sistema)

---

## 📋 Requisitos

- Python 3.8+
- Tesseract OCR instalado en el sistema
- Dependencias de Python (ver `requirements.txt`)

---

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

---

## 🚀 Uso

### Terminal:
```bash
python test/test_ocr.py
```

```bash
python test/test_receipt_processor.py
```

### Iniciar la aplicación web:
```bash
python app/web.py
```
Luego abre tu navegador en [http://localhost:5000](http://localhost:5000) y sube imágenes de recibos para procesarlas.  
Podrás descargar el archivo Excel actualizado con todos los recibos procesados.

---

## 📝 Estructura del Proyecto

```
receipt-processor-mvp/
├── app/
│   ├── ocr.py             # Funciones de procesamiento OCR y extracción de datos
│   ├── web.py             # Aplicación Flask (interfaz web)
│   ├── __init__.py
│   └── templates/         # HTML (Bootstrap)
│       ├── index.html
│       └── result.html
├── test/                  # Pruebas y recibos de ejemplo
│   └── ...
├── recibo.xlsx            # Archivo Excel generado (siempre actualizado)
├── recibos.json           # Base de datos simple de recibos procesados
├── requirements.txt
└── README.md
```

---

## ✅ Funcionalidades

- Extracción robusta de fecha, vendedor y total desde imágenes de recibos.
- Procesamiento de múltiples recibos (persistencia en JSON).
- Exportación a Excel con los datos clave.
- Interfaz web amigable con Bootstrap.
- Mensajes de error y advertencia para campos faltantes o archivos inválidos.
- Botón de descarga para el Excel actualizado.

---

## ℹ️ Notas

- Para reiniciar la base de datos de recibos, borra el archivo `recibos.json`.
- El archivo Excel siempre contendrá todos los recibos procesados hasta el momento.

---

## 📦 Próximos upgrades

- Mejorar la extracción de ítems detallados (opcional).
- Permitir edición/corrección manual de campos desde la web (opcional).
- Despliegue en la nube (opcional).

---

# 🚀 ¡Listo para usar y seguir desarrollando!

