import os
from app.ocr import test_ocr

def test_sample_receipts():
    print("\n=== Procesador de Recibos - Pruebas ===")
    print("Procesando recibos de muestra...\n")
    
    sample_dir = "test/sample_receipts"
    for filename in os.listdir(sample_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(sample_dir, filename)
            print(f"\nProcesando: {filename}")
            
            result = test_ocr(filepath)
            
            # Defensive check for status key
            if not isinstance(result, dict) or 'status' not in result:
                print("\n⚠️ Resultado inesperado del procesamiento:")
                print(result)
                continue
                
            if result["status"] == "success":
                print(f"\n✅ Datos extraídos:")
                print(f"Fecha: {result['structured_data'].get('fecha', 'No encontrada')}")
                print(f"Vendedor: {result['structured_data'].get('vendedor', 'No encontrado')}")
                print(f"Total: {result['structured_data'].get('total', 'No encontrado')}")
                print(f"\nArchivo Excel generado: {result.get('excel_file', 'No generado')}")
            else:
                print(f"\n❌ Error: {result.get('error', 'Desconocido')}")
                print(f"Mensaje: {result.get('message', 'Ninguno')}")

if __name__ == "__main__":
    test_sample_receipts()