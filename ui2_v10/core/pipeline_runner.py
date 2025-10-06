import flet as ft
import os
import yaml
import subprocess

def run_pipeline(self):

    """Ejecutar el pipeline desde Flet"""
    input_config = self.state.get('validated_input', {})
    output_config = self.state.get('validated_output', {})
    tables_path = self.state.get('validated_tables_path', '')

    if not input_config:
        self.toast.error("❌ Please validate the input file first in the Input Parameters tab")
        return
    if not output_config:
        self.toast.error("❌ Please configure the output file first in the Output Parameters tab")
        return
    if not tables_path:
        self.toast.error("❌ Please validate the tables directory first in the Tables Parameters tab")
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
            "format": output_config.get("file_type").replace(".", "").upper()  # CSV o RPT
        }
    }

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "..", "program", "config.yaml")
    program_dir = os.path.join(current_dir, "..", "..", "program")

    try:
        # Escribir configuración YAML
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)
        self.toast.success("✅ Configuration file updated!")
        self.toast.info(f"📁 Config saved to: {config_path}")

        # Ejecutar pipeline.py como proceso externo
        self.toast.info("🚀 Starting pipeline execution...")
        process = subprocess.Popen(
            ["python", "pipeline.py"],
            cwd=program_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            universal_newlines=True
        )

        # Leer output en tiempo real (solo muestra en consola por ahora)
        output_lines = []
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                output_lines.append(output.strip())
                print(output.strip())  # Puedes mostrar en un área de log en la UI si lo deseas

        return_code = process.poll()
        if return_code == 0:
            self.toast.success("🎉 Pipeline completed successfully!")
        else:
            stderr_output = process.stderr.read()
            self.toast.error(f"❌ Pipeline failed with return code: {return_code}")
            if stderr_output:
                self.toast.error(f"Error details:\n{stderr_output}")

    except Exception as ex:
        self.toast.error(f"❌ Error running pipeline: {str(ex)}")
        self.toast.error(f"📁 Attempted config path: {config_path}")
        self.toast.error(f"📁 Attempted program dir: {program_dir}")
        print(ex)