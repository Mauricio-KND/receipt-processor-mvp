from datetime import datetime
import os
from app.ocr import test_ocr

def print_validation_details(data: dict):
    """Helper function to print validation results"""
    if not data.get('es_valido'):
        print("\n🔍 Problemas de validación:")
        validation = data.get('validation_details', {})
        
        for field, details in validation.items():
            status = "✅" if details['valid'] else "❌"
            print(f" {status} {field.upper():<10}: {data.get(field, 'MISSING')}")
            
            if not details['valid']:
                print(f"    - Razón: Campo {'requerido' if details['required'] else 'opcional'} no válido")

def test_sample_receipts():
    print("\n=== Procesador de Recibos - Pruebas ===")
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Procesando recibos de muestra...\n")
    
    sample_dir = "test/sample_receipts"
    stats = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'valid': 0,
        'invalid': 0
    }
    all_receipts = []  # <-- NEW: accumulate all receipts

    for filename in sorted(os.listdir(sample_dir)):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            stats['total'] += 1
            filepath = os.path.join(sample_dir, filename)
            print(f"\n📄 [{stats['total']}] Procesando: {filename}")
            
            result = test_ocr(filepath)
            
            # Basic error handling
            if not isinstance(result, dict):
                print("❌ Resultado inesperado: No es un diccionario")
                stats['failed'] += 1
                continue
                
            if result.get("status") == "success":
                stats['success'] += 1
                data = result.get("structured_data", {})
                all_receipts.append(data)  # <-- NEW: add to list

                if data.get("es_valido"):
                    stats['valid'] += 1
                    print("✅ VÁLIDO: Recibo procesado correctamente")
                else:
                    stats['invalid'] += 1
                    print("⚠️ INCOMPLETO: Recibo procesado con campos faltantes")
                
                print(f"📂 Archivo generado: {result.get('excel_file', '')}")
                print(f"📅 Fecha: {data.get('fecha', 'No encontrada')}")
                print(f"🏪 Vendedor: {data.get('vendedor', 'No encontrado')}")
                print(f"💰 Total: {data.get('total', 'No encontrado')}")
                print_validation_details(data)
            else:
                stats['failed'] += 1
                print(f"❌ FALLIDO: {result.get('error', 'Error desconocido')}")
                print(f"💬 Mensaje: {result.get('message', 'Ninguno')}")

    # Write all receipts to Excel at the end
    if all_receipts:
        from app.ocr import export_to_excel
        export_to_excel(all_receipts, output_path="recibo.xlsx")

    # Print summary
    print("\n📊 Resumen Final:")
    print(f"Total recibos: {stats['total']}")
    print(f"✅ Exitosa: {stats['success']} ({stats['success']/stats['total']:.0%})")
    print(f"  ├─ Válidos: {stats['valid']}")
    print(f"  └─ Inválidos: {stats['invalid']}")
    print(f"❌ Fallidos: {stats['failed']}")
    print(f"\nFinalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_sample_receipts()