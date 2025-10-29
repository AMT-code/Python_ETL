import flet as ft
import os
import sys
import yaml
import subprocess
import threading
import re
from datetime import datetime

# Configurar path para importar módulos del programa
current_dir = os.path.dirname(os.path.abspath(__file__))
program_dir = os.path.join(current_dir, "..", "..", "program")
sys.path.insert(0, program_dir)

def write_to_log_file(message, level="INFO"):
    """Escribir directamente al archivo de log más reciente"""
    try:
        logs_dir = os.path.join(current_dir, "..", "..", "logs")
        
        # Buscar el archivo de log más reciente
        if os.path.exists(logs_dir):
            log_files = [f for f in os.listdir(logs_dir) if f.endswith('.txt')]
            if log_files:
                # Ordenar por fecha de modificación y obtener el más reciente
                log_files.sort(key=lambda x: os.path.getmtime(os.path.join(logs_dir, x)), reverse=True)
                latest_log = os.path.join(logs_dir, log_files[0])
                
                # Escribir en el archivo
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_line = f"[{timestamp}] | [{level}] | UI | {message}\n"
                
                with open(latest_log, 'a', encoding='utf-8') as f:
                    f.write(log_line)
                
                return True
    except Exception as e:
        print(f"Error writing to log file: {e}")
    
    return False

def run_pipeline(self):
    """Ejecutar el pipeline desde Flet con UI bloqueada y logs en tiempo real"""
    input_config = self.state.get('validated_input', {})
    output_config = self.state.get('validated_output', {})
    tables_path = self.state.get('validated_tables_path', '')

    if not input_config:
        self.toast.error("⛔ Please validate the input file first in the Input Parameters tab")
        return
    if not output_config:
        self.toast.error("⛔ Please configure the output file first in the Output Parameters tab")
        return
    if not tables_path:
        self.toast.error("⛔ Please validate the tables directory first in the Tables Parameters tab")
        return

    # Crear el config.yaml con los parámetros de la UI
    config_data = {
        "input_file": input_config.get("path"),
        "tables_path": tables_path,
        "output_file": output_config.get("path"),
        "input_file_config": {
            "type": input_config.get("file_type", "auto"),
            "delimiter": input_config.get("delimiter") if input_config.get("file_type") == "csv" else None
        },
        "output_file_config": {
            "type": output_config.get("file_type"),
            "format": output_config.get("file_type").replace(".", "").upper()
        },
        "enable_audit": self.state.get('enable_audit', True)
    }

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "..", "program", "config.yaml")
    program_dir = os.path.join(current_dir, "..", "..", "program")

    # Variable para controlar cancelación
    cancel_requested = [False]  # Usamos lista para poder modificarla en nested function
    process_ref = [None]  # Referencia al proceso para poder terminarlo

    def cancel_pipeline():
        """Callback para cancelar el pipeline"""
        cancel_requested[0] = True
        if process_ref[0]:
            try:
                process_ref[0].terminate()
                self.loading.add_log("Pipeline cancellation requested...", "WARNING")
            except:
                pass

    # Mostrar overlay de carga con opción de cancelar
    self.loading.show(
        "⚙️ Running Pipeline...", 
        allow_cancel=True, 
        cancel_callback=cancel_pipeline
    )
    
    # Deshabilitar el botón de ejecución
    self.run_button.current.disabled = True
    self.page.update()

    def parse_log_level(line):
        """Extraer nivel de log de una línea"""
        if "[ERROR]" in line or "[CRITICAL]" in line:
            return "ERROR"
        elif "[WARNING]" in line:
            return "WARNING"
        elif "[SUCCESS]" in line:
            return "SUCCESS"
        elif "[DEBUG]" in line:
            return "DEBUG"
        elif "[INFO]" in line:
            return "INFO"
        return "INFO"

    def clean_log_line(line):
        """Limpiar línea de log para mostrar solo el mensaje importante"""
        # Remover timestamp y módulo si existen: [HH:MM:SS] | [LEVEL] | Module |
        cleaned = re.sub(r'\[\d{2}:\d{2}:\d{2}\]\s*\|\s*\[[^\]]+\]\s*\|\s*[^\|]+\|\s*', '', line)
        return cleaned.strip() if cleaned else line

    def execute_pipeline():
        """Función que se ejecuta en thread separado"""
        try:
            # Escribir configuración YAML
            with open(config_path, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False)
            
            self.loading.add_log("Configuration file created", "SUCCESS")
            self.loading.add_log("Starting pipeline execution...", "INFO")
            
            # Ejecutar pipeline.py como proceso externo
            process = subprocess.Popen(
                ["python", "pipeline.py"],
                cwd=program_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True,
                bufsize=1  # Line buffered
            )
            
            process_ref[0] = process  # Guardar referencia para cancelación

            # Leer output en tiempo real
            output_lines = []
            while True:
                # Verificar si se solicitó cancelación
                if cancel_requested[0]:
                    # Registrar en el archivo de log oficial
                    write_to_log_file("=" * 60, "WARNING")
                    write_to_log_file("PIPELINE EXECUTION CANCELED BY USER", "ERROR")
                    write_to_log_file("User requested termination via UI", "WARNING")
                    write_to_log_file("=" * 60, "WARNING")
                    
                    # También mostrar en el overlay
                    self.loading.add_log("=" * 50, "WARNING")
                    self.loading.add_log("PIPELINE CANCELED BY USER", "ERROR")
                    self.loading.add_log("Terminating pipeline process...", "WARNING")
                    self.loading.add_log("=" * 50, "WARNING")
                    
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                        self.loading.add_log("Process terminated successfully", "SUCCESS")
                        write_to_log_file("Pipeline process terminated successfully", "INFO")
                    except subprocess.TimeoutExpired:
                        process.kill()
                        self.loading.add_log("Process killed (force termination)", "WARNING")
                        write_to_log_file("Pipeline process killed (force termination)", "WARNING")
                    break
                
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    output_lines.append(line)
                    print(line)  # Mantener en consola también
                    
                    # Agregar al overlay con nivel apropiado
                    level = parse_log_level(line)
                    cleaned_line = clean_log_line(line)
                    self.loading.add_log(cleaned_line, level)

            return_code = process.poll()
            
            # Ocultar overlay y mostrar resultado
            self.loading.hide()
            self.run_button.current.disabled = False
            
            if cancel_requested[0]:
                self.toast.warning("⚠️ Pipeline execution was canceled")
            elif return_code == 0:
                self.toast.success("🎉 Pipeline completed successfully!")
            else:
                stderr_output = process.stderr.read()
                self.toast.error(f"⛔ Pipeline failed with return code: {return_code}")
                if stderr_output:
                    print(f"Error details:\n{stderr_output}")
            
            self.page.update()

        except Exception as ex:
            # Asegurarse de ocultar overlay incluso si hay error
            self.loading.hide()
            self.run_button.current.disabled = False
            self.toast.error(f"⛔ Error running pipeline: {str(ex)}")
            print(f"Exception: {ex}")
            self.page.update()

    # Ejecutar en thread separado para no bloquear la UI de Flet
    threading.Thread(target=execute_pipeline, daemon=True).start()