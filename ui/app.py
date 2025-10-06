import streamlit as st
import pandas as pd
import os
import glob


# Función para ejecutar el pipeline
def run_pipeline_process():
    """Ejecuta el pipeline con la configuración actual"""
    import subprocess
    import yaml
    import time
    
    # Verificar que tenemos una configuración de input validada
    input_config = st.session_state.get('validated_input', {})
    if not input_config:
        st.error("❌ Please validate the input file first in the Input Parameters tab")
        return
    
    # Verificar que tenemos una configuración de output validada
    output_config = st.session_state.get('validated_output', {})
    if not output_config:
        st.error("❌ Please configure the output file first in the Output Parameters tab")
        return
    
    # Crear el config.yaml con los parámetros de la UI (incluyendo configuración de archivos)
    config_data = {
        "input_file": input_config.get("path"),
        "tables_path": tables_path,
        "output_file": output_config.get("path"),
        # Configuración de archivo de input
        "input_file_config": {
            "type": input_config.get("file_type", "auto"),
            "delimiter": input_config.get("delimiter") if input_config.get("file_type") == "csv" else None
        },
        # Configuración de archivo de output
        "output_file_config": {
            "type": output_config.get("file_type"),
            "format": output_config.get("file_type").replace(".", "").upper()  # CSV o RPT
        }
    }
    
    # Obtener la ruta absoluta del directorio actual (ui/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Ruta al config.yaml en la carpeta program
    config_path = os.path.join(current_dir, "..", "program", "config.yaml")
    # Ruta al directorio program para ejecutar el pipeline
    program_dir = os.path.join(current_dir, "..", "program")
    
    try:
        # Escribir configuración
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)
        
        st.success("✅ Configuration file updated!")
        st.info(f"📁 Config saved to: {config_path}")
        
        # Mostrar configuración que se guardó
        with st.expander("📋 Configuration details"):
            st.json(config_data)
        
        # Crear contenedor para mostrar progreso
        progress_container = st.container()
        
        with progress_container:
            st.info("🚀 Starting pipeline execution...")
            
            # Crear placeholder para logs en tiempo real
            log_placeholder = st.empty()
            
            # Ejecutar pipeline
            process = subprocess.Popen(
                ["python", "pipeline.py"],
                cwd=program_dir,  # Ejecutar desde la carpeta program
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )
            
            # Leer output en tiempo real
            output_lines = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    output_lines.append(output.strip())
                    # Mostrar últimas 10 líneas del output
                    with log_placeholder:
                        st.code('\n'.join(output_lines[-10:]), language='text')
                    time.sleep(0.1)
            
            # Obtener código de salida
            return_code = process.poll()
            
            if return_code == 0:
                st.success("🎉 Pipeline completed successfully!")
                st.balloons()
                
                # Forzar actualización de la tab de logs
                if 'log_selector' in st.session_state:
                    st.rerun()
            else:
                # Mostrar errores si los hay
                stderr_output = process.stderr.read()
                st.error(f"❌ Pipeline failed with return code: {return_code}")
                if stderr_output:
                    st.error(f"Error details:\n{stderr_output}")

    except Exception as e:
        st.error(f"❌ Error running pipeline: {str(e)}")
        st.error(f"📁 Attempted config path: {config_path}")
        st.error(f"📁 Attempted program dir: {program_dir}")
        st.exception(e)

st.set_page_config(page_title="ETL Pipeline demo", layout="wide")
st.title("🔄 ETL Pipeline Configuration")

# Crear las tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📁 Input Parameters", 
    "📊 Tables Parameters", 
    "💾 Output Parameters", 
    "⚙️ Code View/Adjustments",
    "📋 Log",
    "✅ Results"
])

# TAB 1: INPUT PARAMETERS (versión mejorada)
with tab1:
    st.header("Input File Configuration")
    
    # Input file path
    input_path = st.text_input(
        "Input file path:",
        placeholder="e.g., inputs/data.csv, C:/path/to/file.xlsx, data.parquet",
        help="Supported formats: CSV, Excel (.xlsx, .xls), Parquet"
    )
    
    # File type selector
    col1, col2 = st.columns([1, 4])
    with col1:
        file_type = st.selectbox(
        "File type:",
        options=["Auto-detect", "CSV/Delimited", "Excel (xlsx/xls)", "Parquet"],
        help="Select the file type or let auto-detect based on extension"
        )
    
    # Delimiter configuration (only show if CSV/Delimited is selected)
    delimiter = ","  # default value
    if file_type == "CSV/Delimited":
        st.subheader("📝 Delimiter Configuration")
        col1, col2, col3 = st.columns([1, 1, 3])
        # Primero el checkbox para controlar el estado
        with col2:
            is_tab = st.checkbox("Tab delimited", help="Override delimiter with tab")
        
        with col1:
            delimiter = st.text_input(
                "Delimiter:", 
                value= "" if is_tab else ",",  # Vacío si tab está seleccionado
                help=", ; | etc.",
                max_chars=3,
                disabled=is_tab  # Bloqueado si tab está activado
            )
        
        if is_tab:
            delimiter = "\t"
            st.info("Using tab delimiter")
        else:
            st.info(f"Using delimiter: '{delimiter}'")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        validate_input = st.button("🔍 Validate Input", type="primary")
    
    # Validación del archivo de input
    if validate_input and input_path:
        if os.path.exists(input_path):
            try:
                # Detectar formato del archivo automáticamente si es "Auto-detect"
                file_ext = os.path.splitext(input_path)[1].lower()
                
                # Determinar el tipo de archivo final
                if file_type == "Auto-detect":
                    if file_ext == '.csv':
                        final_file_type = "csv"
                        read_params = {}
                    elif file_ext in ['.xlsx', '.xls']:
                        final_file_type = "excel"
                        read_params = {}
                    elif file_ext == '.parquet':
                        final_file_type = "parquet"
                        read_params = {}
                    else:
                        st.error(f"❌ Cannot auto-detect file format for extension: {file_ext}")
                        st.stop()
                elif file_type == "CSV/Delimited":
                    final_file_type = "csv"
                    read_params = {"sep": delimiter}
                elif file_type == "Excel (xlsx/xls)":
                    final_file_type = "excel"
                    read_params = {}
                elif file_type == "Parquet":
                    final_file_type = "parquet"
                    read_params = {}
                
                # Intentar leer el archivo con los parámetros configurados
                if final_file_type == "csv":
                    df_preview = pd.read_csv(input_path, **read_params)
                elif final_file_type == "excel":
                    df_preview = pd.read_excel(input_path, **read_params)
                elif final_file_type == "parquet":
                    df_preview = pd.read_parquet(input_path, **read_params)
                
                # Guardar la configuración validada en session_state
                st.session_state.validated_input = {
                    "path": input_path,
                    "file_type": final_file_type,
                    "delimiter": delimiter if final_file_type == "csv" else None,
                    "read_params": read_params
                }
                
                st.success(f"✅ File found! Shape: {df_preview.shape}")
                st.info(f"📋 Detected as: {final_file_type.upper()}" + 
                        (f" with delimiter '{delimiter}'" if final_file_type == "csv" and delimiter != "\t" else " tab"))
                
                # Vista previa
                st.subheader("📋 File Preview (first 10 rows)")
                st.dataframe(df_preview.head(10), use_container_width=True)
                
                # Información adicional
                with st.expander("📊 File Information"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Rows:** {len(df_preview):,}")
                        st.write(f"**Columns:** {len(df_preview.columns)}")
                        st.write(f"**File size:** {os.path.getsize(input_path) / 1024:.2f} KB")
                    with col2:
                        st.write(f"**File type:** {final_file_type.upper()}")
                        if final_file_type == "csv":
                            st.write(f"**Delimiter:** '{delimiter}'")
                        st.write(f"**Extension:** {file_ext}")
                    
                    st.write("**Column types:**")
                    st.dataframe(df_preview.dtypes.to_frame("Data Type"))
                    
                    # Mostrar primeras filas sin procesar para CSV (útil para debugging delimiters)
                    if final_file_type == "csv":
                        with st.expander("🔍 Raw file preview (first 5 lines)"):
                            try:
                                with open(input_path, 'r', encoding='utf-8') as f:
                                    raw_lines = [f.readline().strip() for _ in range(5)]
                                for i, line in enumerate(raw_lines, 1):
                                    st.code(f"{i}: {line}")
                            except Exception as e:
                                st.error(f"Error reading raw file: {e}")

            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
                # Sugerencias específicas para errores comunes
                if "delimiter" in str(e).lower() or "sep" in str(e).lower():
                    st.info("💡 Try changing the delimiter setting above")
                elif "encoding" in str(e).lower():
                    st.info("💡 The file might have encoding issues")
                elif "excel" in str(e).lower():
                    st.info("💡 Make sure the Excel file is not corrupted or password-protected")
        else:
            st.error("❌ File not found! Please check the path.")
    elif validate_input and not input_path:
        st.warning("⚠️ Please enter a file path first.")

# TAB 2: TABLES PARAMETERS
with tab2:
    st.header("Tables Configuration")
    
    # Tables path
    tables_path = st.text_input(
        "Tables directory path:",
        placeholder="e.g., tables/, C:/path/to/tables/",
        help="Directory containing CSV table files"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        validate_tables = st.button("🔍 Validate Tables", type="primary")
    
    # Validación del directorio de tablas
    if validate_tables and tables_path:
        if os.path.exists(tables_path) and os.path.isdir(tables_path):
            # Buscar archivos CSV
            csv_files = glob.glob(os.path.join(tables_path, "*.csv"))
            csv_filenames = [os.path.basename(f) for f in csv_files]
            
            if csv_filenames:
                # Guardar en session_state para persistir
                st.session_state.validated_tables_path = tables_path
                st.session_state.csv_files = csv_filenames
                st.success(f"✅ Directory found! {len(csv_filenames)} CSV files detected.")
            else:
                st.warning("⚠️ No CSV files found in the specified directory.")
                if 'csv_files' in st.session_state:
                    del st.session_state.csv_files
        else:
            st.error("❌ Directory not found! Please check the path.")
            if 'csv_files' in st.session_state:
                del st.session_state.csv_files
    elif validate_tables and not tables_path:
        st.warning("⚠️ Please enter a directory path first.")
    
    # Mostrar dropdown si hay archivos validados
    if 'csv_files' in st.session_state and st.session_state.csv_files:
        # Dropdown para seleccionar archivo
        selected_file = st.selectbox(
            "📂 Select a table to preview:",
            options=["Select a file..."] + st.session_state.csv_files,
            key="table_selector"
        )
        
        # Vista previa del archivo seleccionado
        if selected_file and selected_file != "Select a file...":
            try:
                selected_path = os.path.join(st.session_state.validated_tables_path, selected_file)
                table_preview = pd.read_csv(selected_path)
                
                st.subheader(f"📋 Preview: {selected_file}")
                st.dataframe(table_preview.head(10), use_container_width=True)
                
                # Información de la tabla
                with st.expander(f"📊 {selected_file} Information"):
                    st.write(f"**Rows:** {len(table_preview)}")
                    st.write(f"**Columns:** {len(table_preview.columns)}")
                    st.write(f"**File size:** {os.path.getsize(selected_path) / 1024:.2f} KB")
                    st.write("**Column types:**")
                    st.dataframe(table_preview.dtypes.to_frame("Data Type"))
                    
            except Exception as e:
                st.error(f"❌ Error reading table: {str(e)}")

# TAB 3: OUTPUT PARAMETERS
with tab3:
    st.header("Output Configuration")
    
    output_path = st.text_input(
        "Output file location:",
        placeholder="e.g., outputs/results.csv, C:/path/to/output.rpt",
        help="Where to save the processed file"
    )
    
    # Checkbox para selección de extensión
    st.subheader("File Format")
    col1, col2, col3 = st.columns([1,1,3])
    
    with col1:
        csv_selected = st.checkbox("CSV (.csv)", key="csv_format")
    with col2:
        rpt_selected = st.checkbox("RPT (.rpt)", key="rpt_format")
    
    # Validación de selección única
    if csv_selected and rpt_selected:
        st.error("❌ Please select only one file format")
        output_path = ""
        selected_format = None
    elif csv_selected:
        selected_format = ".csv"
    elif rpt_selected:
        selected_format = ".rpt"
    else:
        selected_format = None
    
    # Validación y guardado en session_state
    if output_path and selected_format:
        # Validar que el directorio padre existe
        output_dir = os.path.dirname(output_path)
        
        # Agregar la extensión al path si no la tiene
        if not output_path.lower().endswith(selected_format.lower()):
            # Quitar cualquier extensión existente y agregar la seleccionada
            base_path = os.path.splitext(output_path)[0]
            final_output_path = base_path + selected_format
        else:
            final_output_path = output_path
        
        # Verificar directorio
        if output_dir and not os.path.exists(output_dir):
            st.warning(f"⚠️ Directory '{output_dir}' doesn't exist. It will be created when running the pipeline.")
        
        # Guardar en session_state
        st.session_state.validated_output = {
            "path": final_output_path,
            "file_type": selected_format
        }
        
        st.success(f"✅ Output configured: {final_output_path}")
        st.info(f"📁 Format: {selected_format.upper()}")
        
    elif output_path and not selected_format:
        st.warning("⚠️ Please select a file format")
    elif selected_format and not output_path:
        st.warning("⚠️ Please enter an output path")
    else:
        # Limpiar session_state si no hay configuración válida
        if "validated_output" in st.session_state:
            del st.session_state.validated_output

# TAB 4: CODE VIEW/ADJUSTMENTS
with tab4:
    st.header("Code section")
    
    # Ruta al archivo functions.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    functions_path = os.path.join(current_dir, "..", "program", "transformers", "functions.py")
    backup_path = os.path.join(current_dir, "..", "program", "transformers", "functions_backup.py")
    
    # Verificar que existe el archivo
    if os.path.exists(functions_path):
        # Inicializar session_state para el editor
        if 'code_content' not in st.session_state:
            try:
                with open(functions_path, 'r', encoding='utf-8') as f:
                    st.session_state.code_content = f.read()
            except Exception as e:
                st.error(f"❌ Error reading functions.py: {e}")
                st.session_state.code_content = ""
        
        # Controles superiores
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        
        with col1:
            reload_file = st.button("📁 Reload File", help="Reload original file (lose unsaved changes)")
        
        with col2:
            create_backup = st.button("💾 Create Backup", help="Save current file as backup")
        
        with col3:
            restore_backup = st.button("🔄 Restore Backup", help="Restore from backup file")
        
        # Status del backup
        backup_exists = os.path.exists(backup_path)
        if backup_exists:
            backup_time = os.path.getmtime(backup_path)
            backup_date = pd.to_datetime(backup_time, unit='s').strftime('%Y-%m-%d %H:%M:%S')
            st.info(f"📋 Backup available from: {backup_date}")
        else:
            st.warning("⚠️ No backup file found")
        
        # Manejar acciones de botones
        if reload_file:
            try:
                with open(functions_path, 'r', encoding='utf-8') as f:
                    new_content = f.read()
                st.session_state.code_content = new_content
                st.session_state.force_reload = True
                st.session_state.reload_counter = st.session_state.get("reload_counter", 0) + 1
                st.success("✅ File reloaded!")
            except Exception as e:
                st.error(f"❌ Error reloading: {e}")
        
        # Crear backup
        if create_backup:
            try:
                with open(functions_path, 'r', encoding='utf-8') as f:
                    current_content = f.read()
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(current_content)
                st.success("✅ Backup created successfully!")
                # Forzar recálculo del estado del backup
                st.session_state.backup_created = True
            except Exception as e:
                st.error(f"❌ Error creating backup: {e}")
        
        # Restaurar backup
        if restore_backup:
            if backup_exists:
                try:
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        backup_content = f.read()
                    st.session_state.code_content = backup_content
                    st.session_state.force_reload = True
                    st.session_state.reload_counter = st.session_state.get("reload_counter", 0) + 1
                    st.success("✅ Backup restored to editor!")
                except Exception as e:
                    st.error(f"❌ Error restoring backup: {e}")
            else:
                st.error("❌ No backup file to restore!")

        # Editor de código con syntax highlighting
        st.subheader("📝 Code Editor")

        # Generar dinámicamente un key para resetear el editor
        editor_key = "functions_editor"
        if st.session_state.get("force_reload", False):
            editor_key = f"functions_editor_{st.session_state.get('reload_counter', 0)}"
            st.session_state.force_reload = False  # reset flag

        # Usar st_ace (si está disponible) o text_area como fallback
        try:
            from streamlit_ace import st_ace
            code_content = st_ace(
                value=st.session_state.code_content,
                language='python',
                theme='monokai',
                key=editor_key,
                height=500,
                auto_update=False,
                font_size=12,
                tab_size=4,
                wrap=True,
                annotations=None
            )
        except ImportError:
            st.warning("💡 Install streamlit-ace for better syntax highlighting: `pip install streamlit-ace`")
            code_content = st.text_area(
                "Python Code:",
                value=st.session_state.code_content,
                height=500,
                key='functions_editor_fallback',
                help="Edit your functions.py code here"
            )

        # Actualizar session state si cambió el contenido
        if code_content != st.session_state.code_content:
            st.session_state.code_content = code_content
        
        # Controles inferiores
        st.subheader("🔧 Actions")
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            validate_syntax = st.button("✅ Validate Syntax", type="secondary")
        
        with col2:
            save_changes = st.button("💾 Save Changes", type="primary")
        
        # Validación de sintaxis
        if validate_syntax:
            try:
                compile(st.session_state.code_content, '<string>', 'exec')
                st.success("✅ Syntax is valid! Ready to save.")
            except SyntaxError as e:
                st.error(f"❌ Syntax Error: {e}")
                st.error(f"📍 Line {e.lineno}: {e.text}")
            except Exception as e:
                st.error(f"❌ Compilation Error: {e}")
        
        # Guardar cambios
        if save_changes:
            # Validar primero
            try:
                compile(st.session_state.code_content, '<string>', 'exec')
                
                # Si la validación pasa, guardar
                try:
                    with open(functions_path, 'w', encoding='utf-8') as f:
                        f.write(st.session_state.code_content)
                    st.success("🎉 Changes saved successfully!")
                except Exception as e:
                    st.error(f"❌ Error saving file: {e}")
                    
            except SyntaxError as e:
                st.error("❌ Cannot save: Syntax errors found!")
                st.error(f"📍 Line {e.lineno}: {e.text}")
            except Exception as e:
                st.error(f"❌ Cannot save: Compilation error: {e}")
        
        # Información del archivo
        with st.expander("📊 File Information"):
            try:
                file_stats = os.stat(functions_path)
                file_size = file_stats.st_size
                file_modified = pd.to_datetime(file_stats.st_mtime, unit='s').strftime('%Y-%m-%d %H:%M:%S')
                
                lines_count = len(st.session_state.code_content.split('\n'))
                chars_count = len(st.session_state.code_content)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**File size:** {file_size} bytes")
                    st.write(f"**Lines:** {lines_count}")
                with col2:
                    st.write(f"**Characters:** {chars_count}")
                    st.write(f"**Last modified:** {file_modified}")
                    
            except Exception as e:
                st.error(f"Error getting file info: {e}")
        
        # Advertencia
        st.warning("⚠️ **Important:** Changes will affect the next pipeline execution. Test your changes carefully!")
        
    else:
        st.error(f"❌ functions.py not found at: {functions_path}")
        st.info("💡 Make sure your file structure is correct and the file exists.")

# TAB 5: LOG
with tab5:
    st.header("Pipeline Logs")
    
    # Buscar archivos de log
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(current_dir, "..", "logs")

    if os.path.exists(log_dir):
        log_files = glob.glob(os.path.join(log_dir, "*.txt"))
        log_filenames = [os.path.basename(f) for f in sorted(log_files, reverse=True)]
        
        if log_filenames:
            selected_log = st.selectbox(
                "📂 Select a log file:",
                options=log_filenames,
                key="log_selector"
            )
            
            if selected_log:
                log_path = os.path.join(log_dir, selected_log)
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        log_content = f.read()
                    
                    # Información del archivo
                    file_stats = os.stat(log_path)
                    file_time = pd.to_datetime(file_stats.st_mtime, unit='s').tz_localize("UTC").tz_convert("America/Argentina/Buenos_Aires")
                    # file_time = pd.to_datetime(file_stats.st_mtime, unit='s', utc=True)
                    file_size = file_stats.st_size
                    
                    st.subheader(f"📋 Log: {selected_log}")
                    
                    # Información del log
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📅 Created", file_time.strftime('%Y-%m-%d'))
                    with col2:
                        st.metric("🕐 Time", file_time.strftime('%H:%M:%S'))
                    with col3:
                        st.metric("📏 Size", f"{file_size} bytes")
                    
                    # Controles del log
                    col1, col2, col3 = st.columns([1, 1, 2])

                    with col1:
                        filter_log_level = st.checkbox("🔍 Filter by log level")

                    with col2:
                        show_line_numbers = st.checkbox("📝 Show line numbers", value=False)
                    
                    # Filtros por nivel de log
                    if filter_log_level: #st.checkbox("🔍 Filter by log level"):
                        levels = ['INFO', 'SUCCESS', 'WARNING', 'ERROR', 'CRITICAL', 'DEBUG']
                        selected_levels = st.multiselect(
                            "Select levels to show:",
                            options=levels,
                            default=levels
                        )
                        
                        # Filtrar contenido por nivel
                        filtered_lines = []
                        for line in log_content.split('\n'):
                            if any(f"[{level}]" in line for level in selected_levels):
                                filtered_lines.append(line)
                        
                        display_content = '\n'.join(filtered_lines)
                    else:
                        display_content = log_content
                    
                    # Agregar números de línea si se solicita
                    if show_line_numbers and display_content:
                        lines = display_content.split('\n')
                        numbered_lines = [f"{i+1:4d}: {line}" for i, line in enumerate(lines)]
                        display_content = '\n'.join(numbered_lines)
                    
                    # Mostrar log en un text area
                    log_height = min(500, max(200, len(display_content.split('\n')) * 20))
                    
                    st.text_area(
                        "Log content:",
                        value=display_content,
                        height=log_height,
                        disabled=True,
                        key=f"log_content_{selected_log}",
                        help="This log shows the complete pipeline execution details"
                    )
                    
                    
                    # Estadísticas del log
                    with st.expander("📊 Log Statistics"):
                        lines = log_content.split('\n')
                        total_lines = len(lines)
                        
                        # Contar por nivel
                        level_counts = {}
                        for level in ['DEBUG', 'INFO', 'SUCCESS', 'WARNING', 'ERROR', 'CRITICAL']:
                            count = sum(1 for line in lines if f"[{level}]" in line)
                            level_counts[level] = count
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Line counts:**")
                            st.write(f"Total lines: {total_lines}")
                            st.write(f"Non-empty lines: {sum(1 for line in lines if line.strip())}")
                        
                        with col2:
                            st.write("**Log levels:**")
                            for level, count in level_counts.items():
                                if count > 0:
                                    st.write(f"{level}: {count}")
                    
                    # Botones de acción
                    col1, col2, col3 = st.columns([1, 1, 2])
                    
                    with col1:
                        st.download_button(
                            label="📥 Download Log",
                            data=log_content,
                            file_name=selected_log,
                            mime="text/plain"
                        )
                    
                    with col2:
                        if st.button("🔄 Refresh Log"):
                            st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error reading log file: {str(e)}")
        else:
            st.info("📭 No log files found.")
    else:
        st.info("📭 Log directory doesn't exist yet. Run the pipeline first to generate logs.")

# TAB 6: RESULTS
with tab6:
    st.header("Results")   
    
    col1, col2 = st.columns([1, 4])
    with col1:
        check_results = st.button("🔍 Check results", type="primary")
    
    # Validación del directorio de tablas
    if check_results and final_output_path:
            try:
                output_file = os.path.basename(final_output_path)
                output_preview = pd.read_csv(final_output_path)

                st.subheader(f"📋 Preview: {output_file}")
                st.dataframe(output_preview.head(10), use_container_width=True)
                    
                # Botón para descargar log
                st.download_button(
                    label="📥 Download Results",
                    data=output_preview.to_csv(index=False),
                    file_name=output_file,
                    mime="text/csv"
                )

                # Información de la tabla
                with st.expander(f"📊 {final_output_path} Information"):
                    st.write(f"**Rows:** {len(output_preview)}")
                    st.write(f"**Columns:** {len(output_preview.columns)}")
                    st.write(f"**File size:** {os.path.getsize(final_output_path) / 1024:.2f} KB")
                    st.write("**Column types:**")
                    st.dataframe(output_preview.dtypes.to_frame("Data Type"))

            except Exception as e:
                st.error(f"❌ Error reading results: {str(e)}")


# SIDEBAR: Pipeline Control
with st.sidebar:
    st.header("Pipeline Control")

    # Verificar que todos los parámetros estén configurados
    config_complete = (
        'input_path' in locals() and input_path and  
        'tables_path' in locals() and tables_path and 
        'output_path' in locals() and output_path
    )

    if config_complete:
        if st.button("▶️ Run Pipeline", type="primary", use_container_width=True):
            run_pipeline_process()
    else:
        st.button("▶️ Run Pipeline", type="primary", use_container_width=True, disabled=True)
        st.warning("⚠️ Complete all configuration tabs first")
    
    st.divider()
    
    # Configuración actual
    st.subheader("📋 Current Configuration")
    config_data = {
        "Input File": input_path if 'input_path' in locals() and input_path else "❌ Not set",
        "Tables Path": tables_path if 'tables_path' in locals() and tables_path else "❌ Not set", 
        "Output File": output_path if 'output_path' in locals() and output_path else "❌ Not set"
    }
    
    for key, value in config_data.items():
        if "❌" in value:
            st.write(f"**{key}:** {value}")
        else:
            st.write(f"**{key}:** ✅ {value}")

