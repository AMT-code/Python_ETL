import os
import shutil
import subprocess
import time

"""
Script para ejecutar la matriz de pruebas 4x4
- 4 tamaños de BBDD: 100k, 1M, 1.5M, 2M
- 4 niveles de complejidad: SIMPLE, MEDIUM, COMPLEX, VERY_COMPLEX

Uso:
    python test_complexity_matrix.py
"""

# Configuración
PROGRAM_DIR = "program"
TRANSFORMERS_DIR = os.path.join(PROGRAM_DIR, "transformers")
FUNCTIONS_FILE = os.path.join(TRANSFORMERS_DIR, "functions.py")
BACKUP_FILE = os.path.join(TRANSFORMERS_DIR, "functions_backup.py")

# Versiones de functions.py
VERSIONS = {
    "SIMPLE": "functions_simple.py",
    "MEDIUM": "functions_medium.py",  # La original actual
    "COMPLEX": "functions_complex.py",
    # "VERY_COMPLEX": "functions_very_complex.py"
}

# Archivos de input
INPUT_FILES = {
    "100K": "inputs/data_100k.csv",
    "1M": "inputs/data_1000k.csv",
    "1.5M": "inputs/data_1500k.csv",
    "2M": "inputs/data_2000k.csv"
}

# Archivos de output
OUTPUT_FILES = {
    "100K": "outputs/res_100k.csv",
    "1M": "outputs/res_1000k.csv",
    "1.5M": "outputs/res_1500k.csv",
    "2M": "outputs/res_2000k.csv"
}


def backup_current_functions():
    """Hacer backup del functions.py actual"""
    if os.path.exists(FUNCTIONS_FILE):
        shutil.copy(FUNCTIONS_FILE, BACKUP_FILE)
        print(f"✅ Backup created: {BACKUP_FILE}")


def restore_functions_backup():
    """Restaurar el backup"""
    if os.path.exists(BACKUP_FILE):
        shutil.copy(BACKUP_FILE, FUNCTIONS_FILE)
        print(f"✅ Restored from backup")


def switch_functions_version(complexity):
    """Cambiar a una versión específica de functions.py"""
    version_file = os.path.join(TRANSFORMERS_DIR, VERSIONS[complexity])
    
    if not os.path.exists(version_file):
        print(f"❌ Version file not found: {version_file}")
        return False
    
    shutil.copy(version_file, FUNCTIONS_FILE)
    print(f"✅ Switched to {complexity} complexity")
    return True


def update_config(input_file, output_file):
    """Actualizar config.yaml con los paths correctos"""
    config_path = os.path.join(PROGRAM_DIR, "config.yaml")
    
    config_content = f"""input_file: {input_file}
tables_path: tables
output_file: {output_file}
input_file_config:
  type: csv
  delimiter: ','
output_file_config:
  type: .csv
  format: CSV
"""
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"✅ Config updated: {input_file} → {output_file}")


def run_pipeline():
    """Ejecutar el pipeline"""
    try:
        print("🚀 Running pipeline...")
        result = subprocess.run(
            ["python", "pipeline.py"],
            cwd=PROGRAM_DIR,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos timeout
        )
        
        if result.returncode == 0:
            print("✅ Pipeline completed successfully")
            return True
        else:
            print(f"❌ Pipeline failed with return code: {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr[:500]}")
            return False
    except subprocess.TimeoutExpired:
        print("⏰ Pipeline timeout (5 minutes)")
        return False
    except Exception as e:
        print(f"❌ Error running pipeline: {e}")
        return False


def run_test_matrix(complexities=None, sizes=None):
    """
    Ejecutar matriz de pruebas
    
    Args:
        complexities: Lista de complejidades a probar (None = todas)
        sizes: Lista de tamaños a probar (None = todos)
    """
    # Defaults
    if complexities is None:
        complexities = ["SIMPLE", 
                        "MEDIUM",
                        "COMPLEX"]
                        #"VERY_COMPLEX"]
    if sizes is None:
        sizes = ["100K", "1M", "1.5M", "2M"]
    
    # Backup inicial
    print("\n" + "="*80)
    print("COMPLEXITY MATRIX TEST")
    print("="*80)
    backup_current_functions()
    
    total_tests = len(complexities) * len(sizes)
    current_test = 0
    successful = 0
    failed = 0
    
    results = []
    
    print(f"\nRunning {total_tests} tests ({len(complexities)} complexities × {len(sizes)} sizes)")
    print("-"*80)
    
    for complexity in complexities:
        for size in sizes:
            current_test += 1
            print(f"\n[{current_test}/{total_tests}] Testing: {complexity} + {size}")
            print("-"*40)
            
            # Cambiar versión de functions.py
            if not switch_functions_version(complexity):
                failed += 1
                results.append({
                    'complexity': complexity,
                    'size': size,
                    'status': 'FAILED',
                    'reason': 'Version file not found'
                })
                continue
            
            # Actualizar config
            update_config(INPUT_FILES[size], OUTPUT_FILES[size])
            
            # Ejecutar pipeline
            start_time = time.time()
            success = run_pipeline()
            elapsed = time.time() - start_time
            
            if success:
                successful += 1
                status = "SUCCESS"
                print(f"✅ Test completed in {elapsed:.2f}s")
            else:
                failed += 1
                status = "FAILED"
                print(f"❌ Test failed after {elapsed:.2f}s")
            
            results.append({
                'complexity': complexity,
                'size': size,
                'status': status,
                'time': elapsed
            })
            
            # Pequeña pausa entre tests
            time.sleep(1)
    
    # Restaurar backup
    print("\n" + "="*80)
    restore_functions_backup()
    
    # Resumen final
    print("\n" + "="*80)
    print("TEST MATRIX SUMMARY")
    print("="*80)
    print(f"Total tests: {total_tests}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful/total_tests*100):.1f}%")
    
    # Tabla de resultados
    print("\nRESULTS MATRIX:")
    print("-"*80)
    print(f"{'Complexity':<15} {'Size':<10} {'Status':<10} {'Time (s)':<10}")
    print("-"*80)
    for result in results:
        print(f"{result['complexity']:<15} {result['size']:<10} {result['status']:<10} {result.get('time', 0):>8.2f}")
    
    print("="*80)
    print("\n💡 Check the logs/ folder for detailed audit files")
    print("💡 Run 'python audit_analyzer.py' to consolidate results\n")


def run_single_test(complexity, size):
    """Ejecutar un solo test específico"""
    print(f"\n🎯 Single test: {complexity} + {size}")
    print("="*80)
    
    backup_current_functions()
    
    if not switch_functions_version(complexity):
        print("❌ Test aborted")
        return
    
    update_config(INPUT_FILES[size], OUTPUT_FILES[size])
    
    start_time = time.time()
    success = run_pipeline()
    elapsed = time.time() - start_time
    
    if success:
        print(f"\n✅ Test completed successfully in {elapsed:.2f}s")
    else:
        print(f"\n❌ Test failed after {elapsed:.2f}s")
    
    restore_functions_backup()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Modo single test
        if len(sys.argv) == 3:
            complexity = sys.argv[1].upper()
            size = sys.argv[2].upper()
            
            if complexity not in VERSIONS:
                print(f"❌ Invalid complexity: {complexity}")
                print(f"   Valid options: {', '.join(VERSIONS.keys())}")
                sys.exit(1)
            
            if size not in INPUT_FILES:
                print(f"❌ Invalid size: {size}")
                print(f"   Valid options: {', '.join(INPUT_FILES.keys())}")
                sys.exit(1)
            
            run_single_test(complexity, size)
        else:
            print("Usage:")
            print("  Full matrix:  python test_complexity_matrix.py")
            print("  Single test:  python test_complexity_matrix.py <complexity> <size>")
            print()
            print("Examples:")
            print("  python test_complexity_matrix.py SIMPLE 100K")
            print("  python test_complexity_matrix.py COMPLEX 2M")
    else:
        # Modo full matrix
        run_test_matrix()