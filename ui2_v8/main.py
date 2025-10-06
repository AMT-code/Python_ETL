import flet as ft
import pandas as pd
import os
import glob
import time
import threading
import yaml
import subprocess
from typing import Dict, Any


class SimpleToast:
    """Versión ultra-simple para copiar y pegar en tu app"""
    
    def __init__(self, page):
        self.page = page
        self.container = ft.Container(
            visible=False,
            alignment=ft.Alignment(0, 0.8),
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        )
        self.page.overlay.append(self.container)
    
    def success(self, msg): self._show(msg, ft.Colors.GREEN_600, ft.Icons.CHECK_CIRCLE)
    def error(self, msg): self._show(msg, ft.Colors.RED_600, ft.Icons.ERROR)
    def warning(self, msg): self._show(msg, ft.Colors.ORANGE_600, ft.Icons.WARNING)
    def info(self, msg): self._show(msg, ft.Colors.BLUE_600, ft.Icons.INFO)
    
    def _show(self, msg, color, icon):
        self.container.content = ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=ft.Colors.WHITE, size=20),
                ft.Text(msg, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=color,
            padding=15,
            border_radius=25,
        )
        self.container.visible = True
        self.container.opacity = 1
        self.page.update()
        
        def hide():
            time.sleep(3)
            self.container.opacity = 0
            self.page.update()
            time.sleep(0.3)
            self.container.visible = False
            self.page.update()
        
        threading.Thread(target=hide, daemon=True).start()


class ETLPipelineApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        self.init_state()
        # Inicializar toast DESPUÉS de setup_page
        self.toast = SimpleToast(self.page)
        self.build_ui()
    
    def setup_page(self):
        """Configuración inicial de la página"""
        self.page.title = "ETL Pipeline Configuration"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.bgcolor = ft.Colors.BLUE_GREY_50
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_min_width = 800
        self.page.window_min_height = 600
        
        # Configurar colores del tema
        self.page.theme = ft.Theme(
            primary_swatch=ft.Colors.BLUE,
        )

        # Ya no necesitamos snackbar
        # self.page.snack_bar = ft.SnackBar(
        #     content=ft.Text(""),
        #     action="OK"
        # )
        
    def init_state(self):
        """Inicializar el estado de la aplicación"""
        self.state = {
            'validated_input': {},
            'validated_output': {},
            'validated_tables_path': '',
            'csv_files': [],
            'current_tab': 0
        }

        # Referencias a elementos de UI que necesitamos modificar
        self.input_path_field = ft.Ref[ft.TextField]()
        self.file_type_dropdown = ft.Ref[ft.Dropdown]()
        self.delimiter_container = ft.Ref[ft.Container]()
        self.delimiter_field = ft.Ref[ft.TextField]()
        self.tab_delimiter_checkbox = ft.Ref[ft.Checkbox]()
        self.preview_container = ft.Ref[ft.Container]()
        self.validate_button = ft.Ref[ft.ElevatedButton]()

        # Referencias para Tab 2 - Tables
        self.tables_path_field = ft.Ref[ft.TextField]()
        self.validate_tables_button = ft.Ref[ft.ElevatedButton]()
        self.tables_dropdown = ft.Ref[ft.Dropdown]()
        self.tables_preview_container = ft.Ref[ft.Container]()
        self.tables_dropdown_container = ft.Ref[ft.Container]()

        # Referencias para Tab 3 - Output
        self.output_path_field = ft.Ref[ft.TextField]()
        self.csv_checkbox = ft.Ref[ft.Checkbox]()
        self.rpt_checkbox = ft.Ref[ft.Checkbox]()
        self.output_status = ft.Ref[ft.Text]()

        # Referencias para SideBar
        self.run_button = ft.Ref[ft.ElevatedButton]()
        self.run_button_warning = ft.Ref[ft.Text]()
        self.config_items = ft.Ref[ft.Column]()
        self.log_container = ft.Ref[ft.Container]()

    def build_ui(self):
        """Construir la interfaz de usuario"""
        # Crear las tabs
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="📁 Input Parameters",
                    content=self.build_input_tab()
                ),
                ft.Tab(
                    text="📊 Tables Parameters", 
                    content=self.build_tables_tab()
                ),
                ft.Tab(
                    text="💾 Output Parameters",
                    content=self.build_output_tab()
                ),
                ft.Tab(
                    text="⚙️ Code View",
                    content=self.build_code_tab()
                ),
                ft.Tab(
                    text="📋 Log",
                    content=self.build_log_tab()
                ),
                ft.Tab(
                    text="✅ Results",
                    content=self.build_results_tab()
                )
            ],
            on_change=self.tab_changed
        )
        
        # Crear el sidebar
        sidebar = self.build_sidebar()
        
        # Layout principal
        main_content = ft.Row([
            # Sidebar
            ft.Container(
                content=sidebar,
                width=300,
                bgcolor=ft.Colors.BLUE_GREY_100,
                padding=20,
                border_radius=10
            ),
            # Contenido principal
            ft.Container(
                content=self.tabs,
                expand=True,
                padding=20
            )
        ], expand=True)
        
        # Agregar todo a la página
        self.page.add(
            ft.Container(
                content=main_content,
                expand=True,
                padding=10
            )
        )
    
    def tab_changed(self, e):
        """Manejar cambio de tab"""
        self.state['current_tab'] = e.control.selected_index
        print(f"Cambiado a tab: {e.control.selected_index}")
    
    def build_input_tab(self):
        """Tab 1: Input Parameters"""
        return ft.Container(
            content=ft.Column([
                ft.Text("Input File Configuration", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                
                # Input file path
                ft.TextField(
                    label="Input file path",
                    hint_text="e.g., inputs/data.csv, C:/path/to/file.xlsx",
                    helper_text="Supported formats: CSV, Excel (.xlsx, .xls), Parquet",
                    expand=True,
                    on_change=self.input_path_changed,
                    ref=self.input_path_field
                ),
                
                ft.Row([
                    # File type selector
                    ft.Dropdown(
                        label="File type",
                        width=200,
                        options=[
                            ft.dropdown.Option("auto", "Auto-detect"),
                            ft.dropdown.Option("csv", "CSV/Delimited"),
                            ft.dropdown.Option("excel", "Excel (xlsx/xls)"),
                            ft.dropdown.Option("parquet", "Parquet"),
                        ],
                        value="auto",
                        on_change=self.file_type_changed,
                        ref=self.file_type_dropdown
                    ),
                    
                    # Validate button
                    ft.ElevatedButton(
                        "Validate Input",
                        icon=ft.Icons.SEARCH,
                        on_click=self.validate_input,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.BLUE
                        ),
                        ref=self.validate_button
                    )
                ]),
                
                # Delimiter configuration (inicialmente oculto)
                ft.Container(
                    content=ft.Column([
                        ft.Text("📝 Delimiter Configuration", size=16, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.TextField(
                                label="Delimiter",
                                value=",",
                                width=100,
                                max_length=3,
                                hint_text=", ; |",
                                ref=self.delimiter_field
                            ),
                            ft.Checkbox(
                                label="Tab delimited",
                                on_change=self.tab_delimiter_changed,
                                ref=self.tab_delimiter_checkbox
                            )
                        ])
                    ]),
                    visible=False,  # Inicialmente oculto
                    ref=self.delimiter_container
                ),
                
                # Preview area
                ft.Container(
                    content=ft.Column([
                        ft.Text("📋 File Preview", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text("Select and validate a file to see preview", color=ft.Colors.GREY_600)
                    ]),
                    padding=20,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=10,
                    ref=self.preview_container
                )
            ], 
            scroll=ft.ScrollMode.AUTO,
            spacing=20),
            padding=20
        )
    
    def build_tables_tab(self):
        """Tab 2: Tables Parameters - Funcionalidad completa"""
        return ft.Container(
            content=ft.Column([
                ft.Text("Tables Configuration", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                
                # Tables directory path
                ft.TextField(
                    label="Tables directory path",
                    hint_text="e.g., tables/, C:/path/to/tables/",
                    helper_text="Directory containing CSV table files",
                    expand=True,
                    on_change=self.tables_path_changed,
                    ref=self.tables_path_field
                ),
                
                ft.Row([
                    # Validate button
                    ft.ElevatedButton(
                        "Validate Tables",
                        icon=ft.Icons.FOLDER_OPEN,
                        on_click=self.validate_tables,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.BLUE
                        ),
                        ref=self.validate_tables_button
                    )
                ]),
                
                # Dropdown para seleccionar tabla (inicialmente oculto)
                ft.Container(
                    content=ft.Column([
                        ft.Text("📂 Available Tables", size=16, weight=ft.FontWeight.BOLD),
                        ft.Dropdown(
                            label="Select a table to preview",
                            hint_text="Choose from available CSV files",
                            on_change=self.table_selected,
                            ref=self.tables_dropdown,
                            expand=True
                        )
                    ]),
                    visible=False,
                    ref=self.tables_dropdown_container
                ),
                
                # Preview area para tablas
                ft.Container(
                    content=ft.Column([
                        ft.Text("📋 Table Preview", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text("Validate tables directory first to see available files", color=ft.Colors.GREY_600)
                    ]),
                    padding=20,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=10,
                    ref=self.tables_preview_container
                )
            ], 
            scroll=ft.ScrollMode.AUTO,
            spacing=20),
            padding=20
        )
    
    def build_output_tab(self):
        """Tab 3: Output Parameters - Placeholder por ahora"""
        return ft.Container(
        content=ft.Column([
            ft.Text("Output Configuration", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.TextField(
                label="Output file location",
                hint_text="e.g., outputs/results.csv, C:/path/to/output.rpt",
                helper_text="Where to save the processed file",
                expand=False,
                on_change=self.validate_output,
                ref=self.output_path_field
            ),
            
            ft.Row([ft.Text("File Format", size=16, weight=ft.FontWeight.BOLD),
                ft.Checkbox(
                    label="CSV (.csv)",
                    value=False,
                    on_change=self.on_format_change,
                    ref=self.csv_checkbox
                ),
                ft.Checkbox(
                    label="RPT (.rpt)",
                    value=False,
                    on_change=self.on_format_change,
                    ref=self.rpt_checkbox
                ),
            ]),

            ft.Text("", color=ft.Colors.BLUE_600, ref=self.output_status),
        ], spacing=20),
        padding=20
    )
    
    def build_code_tab(self):
        """Tab 4: Code View - Placeholder por ahora"""
        return ft.Container(
            content=ft.Column([
                ft.Text("Code Editor", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("🚧 Coming soon...", size=16, color=ft.Colors.ORANGE_600)
            ]),
            padding=20
        )
    
    def build_log_tab(self):
        """Tab 5: Log - Placeholder por ahora"""
        return ft.Container(
            content=ft.Column([
                ft.Text("Pipeline Logs", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("🚧 Coming soon...", size=16, color=ft.Colors.ORANGE_600)
            ]),
            padding=20
        )
    
    def build_results_tab(self):
        """Tab 6: Results - Placeholder por ahora"""
        return ft.Container(
            content=ft.Column([
                ft.Text("Results", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("🚧 Coming soon...", size=16, color=ft.Colors.ORANGE_600)
            ]),
            padding=20
        )
    
    def build_sidebar(self):
        # Llamar a update_sidebar cada vez que se navega entre tabs
        self.page.on_resize = lambda _: self.update_sidebar()
        self.page.on_route_change = lambda _: self.update_sidebar()

        """Construir el sidebar con controles del pipeline y resumen de configuración"""
        return ft.Column([
            ft.Text("Pipeline Control", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            # Botón principal
            ft.ElevatedButton(
                "▶️ Run Pipeline",
                width=200,
                height=50,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.GREEN,
                    shape=ft.RoundedRectangleBorder(radius=10)
                ),
                on_click=self.run_pipeline,
                disabled=True,  # Inicialmente deshabilitado,
                ref=self.run_button
            ),

            ft.Text("⚠️ Complete all configuration tabs first", color=ft.Colors.ORANGE_600, ref=self.run_button_warning),
            ft.Divider(),
            
            # Current Configuration
            ft.Text("📋 Current Configuration", size=16, weight=ft.FontWeight.BOLD),
            
            ft.Container(
                content=ft.Column([#],
                    self.create_config_item("Input File", "❌ Not set"),
                    self.create_config_item("Tables Path", "❌ Not set"),
                    self.create_config_item("Output File", "❌ Not set"),
                ], 
                ref=self.config_items),
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_500),
                border_radius=8,
                bgcolor=ft.Colors.BLUE_GREY_100
            ),

            ft.Divider(),
            ft.Container(
                content=ft.Column([]),
                ref=self.log_container
            )               
        ], spacing=10)
        self.update_sidebar()

    def create_config_item(self, label: str, value: str):
        """Crear un item de configuración para el sidebar"""
        icon = "✅" if "❌" not in value else "❌"
        color = ft.Colors.GREEN_600 if "❌" not in value else ft.Colors.RED_600
        # print(f"Config item created: {label} - {value}")
        
        return ft.Row([
            ft.Text(f"{label}:", weight=ft.FontWeight.BOLD, size=12),
            ft.Text(f"{icon} {value.replace('❌ ', '').replace('✅ ', '')}", 
                    color=color, size=12, expand=True)
        ], tight=True)


    # Event handlers
    def input_path_changed(self, e):
        """Manejar cambios en el path del archivo"""
        print(f"Input path changed: {e.control.value}")
        # Limpiar estado anterior si cambia el path
        if 'validated_input' in self.state:
            self.state['validated_input'] = {}
    
    def file_type_changed(self, e):
        """Manejar cambios en el tipo de archivo"""
        print(f"File type changed: {e.control.value}")
        # Mostrar/ocultar configuración de delimiter
        show_delimiter = e.control.value == "csv"
        self.delimiter_container.current.visible = show_delimiter
        self.page.update()
    
    def tables_path_changed(self, e):
        """Manejar cambios en el path del directorio de tablas"""
        print(f"Tables path changed: {e.control.value}")
        # Limpiar estado anterior si cambia el path
        if 'validated_tables_path' in self.state:
            self.state['validated_tables_path'] = ''
            self.state['csv_files'] = []
    
    def validate_tables(self, e):
        """Validar directorio de tablas"""
        print("Validating tables directory...")
        
        tables_path = self.tables_path_field.current.value
        
        if not tables_path:
            self.toast.warning("Please enter a directory path first.")
            self.state['validated_tables_path'] = ''
            return
        
        if not os.path.exists(tables_path):
            self.toast.error("Directory not found! Please check the path.")
            self.state['validated_tables_path'] = ''
            return
        
        if not os.path.isdir(tables_path):
            self.toast.error("Path is not a directory! Please enter a valid directory path.")
            self.state['validated_tables_path'] = ''
            return
        
        # Cambiar botón a estado "loading"
        self.validate_tables_button.current.disabled = True
        self.validate_tables_button.current.text = "🔄 Validating..."
        self.page.update()
        
        try:
            # Buscar archivos CSV
            csv_files = glob.glob(os.path.join(tables_path, "*.csv"))
            csv_filenames = [os.path.basename(f) for f in csv_files]
            
            if csv_filenames:
                # Guardar en estado
                self.state['validated_tables_path'] = tables_path
                self.state['csv_files'] = csv_filenames
                
                # Mostrar dropdown con archivos
                self.show_tables_dropdown(csv_filenames)
                
                # Success message
                self.toast.success(f"✅ Directory found! {len(csv_filenames)} CSV files detected.")
                
                print(f"📂 Found CSV files: {csv_filenames}")
                
            else:
                self.toast.warning("⚠️ No CSV files found in the specified directory.")
                self.hide_tables_dropdown()
                
        except Exception as ex:
            self.toast.error(f"Error scanning directory: {str(ex)}")
            self.hide_tables_dropdown()
        
        finally:
            # Restaurar botón
            self.validate_tables_button.current.disabled = False
            self.validate_tables_button.current.text = "Validate Tables"
            self.update_sidebar()
            self.page.update()
    
    def show_tables_dropdown(self, csv_filenames):
        """Mostrar dropdown con archivos CSV disponibles"""
        # Actualizar opciones del dropdown
        dropdown_options = [ft.dropdown.Option("", "Select a file...")] + \
                            [ft.dropdown.Option(filename, filename) for filename in csv_filenames]
        
        self.tables_dropdown.current.options = dropdown_options
        self.tables_dropdown.current.value = ""  # Reset selection
        
        # Mostrar el container del dropdown
        self.tables_dropdown_container.current.visible = True
        
        self.page.update()
    
    def hide_tables_dropdown(self):
        """Ocultar dropdown de tablas"""
        # Ocultar container
        self.tables_dropdown_container.current.visible = False
        
        # Reset dropdown
        self.tables_dropdown.current.options = []
        self.tables_dropdown.current.value = ""
        
        # Reset preview
        self.reset_tables_preview()
        
        self.page.update()
    
    def table_selected(self, e):
        """Manejar selección de tabla"""
        selected_file = e.control.value
        print(f"Table selected: {selected_file}")
        
        if not selected_file or selected_file == "":
            self.reset_tables_preview()
            return
        
        # Cargar y mostrar preview de la tabla seleccionada
        self.load_table_preview(selected_file)
    
    def load_table_preview(self, filename):
        """Cargar y mostrar preview de una tabla"""
        try:
            tables_path = self.state.get('validated_tables_path', '')
            if not tables_path:
                self.toast.error("❌ Tables directory not validated.")
                return
            
            file_path = os.path.join(tables_path, filename)
            
            # Leer archivo CSV
            df_preview = pd.read_csv(file_path)
            
            # Crear preview usando nuestro método reutilizable
            preview_content = self.create_data_preview(df_preview, file_path, "csv", max_rows=5)
            
            # Actualizar preview container
            self.tables_preview_container.current.content = ft.Column([
                ft.Text(f"📋 Table Preview: {filename}", size=16, weight=ft.FontWeight.BOLD),
                preview_content,
            ], spacing=10, expand=True)
            
            self.page.update()
            
            print(f"📊 Loaded table {filename}: {df_preview.shape}")
            
        except Exception as ex:
            self.toast.error(f"❌ Error reading table {filename}: {str(ex)}")
            self.reset_tables_preview()
    
    def reset_tables_preview(self):
        """Resetear preview de tablas al estado inicial"""
        self.tables_preview_container.current.content = ft.Column([
            ft.Text("📋 Table Preview", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("Select a table from the dropdown to see preview", color=ft.Colors.GREY_600)
        ])
        self.page.update()
    
    def tab_delimiter_changed(self, e):
        """Manejar checkbox de tab delimiter"""
        is_tab = e.control.value
        print(f"Tab delimiter: {is_tab}")
        
        # Habilitar/deshabilitar campo de delimiter
        self.delimiter_field.current.disabled = is_tab
        
        if is_tab:
            self.delimiter_field.current.value = ""
            self.delimiter_field.current.hint_text = "Using tab"
        else:
            self.delimiter_field.current.value = ","
            self.delimiter_field.current.hint_text = ", ; |"
        
        self.page.update()
    
    def validate_input(self, e):
        """Validar archivo de input"""
        print("Validating input...")
        
        input_path = self.input_path_field.current.value
        file_type = self.file_type_dropdown.current.value
        
        if not input_path:
            self.toast.warning("Please enter a file path first.")
            return
        
        if not os.path.exists(input_path):
            self.toast.error("File not found! Please check the path.")
            return
        
        # Cambiar botón a estado "loading"
        self.validate_button.current.disabled = True
        self.validate_button.current.text = "🔄 Validating..."
        self.page.update()
        
        try:
            # Determinar tipo de archivo
            file_ext = os.path.splitext(input_path)[1].lower()
            
            if file_type == "auto":
                if file_ext == '.csv':
                    final_file_type = "csv"
                elif file_ext in ['.xlsx', '.xls']:
                    final_file_type = "excel"
                elif file_ext == '.parquet':
                    final_file_type = "parquet"
                else:
                    self.toast.error(f"❌ Cannot auto-detect file format for extension: {file_ext}")
                    return
            else:
                final_file_type = file_type
            
            # Parámetros de lectura
            read_params = {}
            delimiter = ","
            
            if final_file_type == "csv":
                # Obtener delimiter
                if self.tab_delimiter_checkbox.current.value:
                    delimiter = "\t"
                else:
                    delimiter = self.delimiter_field.current.value or ","
                read_params = {"sep": delimiter}
            
            # Leer archivo
            df_preview = self.read_file(input_path, final_file_type, read_params)
            
            if df_preview is not None:
                # Guardar configuración validada
                self.state['validated_input'] = {
                    "path": input_path,
                    "file_type": final_file_type,
                    "delimiter": delimiter if final_file_type == "csv" else None,
                    "read_params": read_params
                }
                
                # Mostrar success y preview
                self.toast.success(f"File found! Shape: {df_preview.shape}")
                self.show_file_info_console(df_preview, final_file_type, delimiter, file_ext)
                self.update_preview(df_preview, input_path, final_file_type)
    
        except Exception as ex:
            self.toast.error(f"Error reading file: {str(ex)}")
            if "delimiter" in str(ex).lower() or "sep" in str(ex).lower():
                self.toast.info("Try changing the delimiter setting")
            elif "encoding" in str(ex).lower():
                self.toast.info("The file might have encoding issues")
    
        finally:
            # Restaurar botón
            self.validate_button.current.disabled = False
            self.validate_button.current.text = "Validate Input"
            self.update_sidebar()
            self.page.update()
    
    def read_file(self, file_path: str, file_type: str, read_params: dict):
        """Leer archivo según su tipo"""
        try:
            if file_type == "csv":
                return pd.read_csv(file_path, **read_params)
            elif file_type == "excel":
                return pd.read_excel(file_path, **read_params)
            elif file_type == "parquet":
                return pd.read_parquet(file_path, **read_params)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            raise e
        
    def create_data_preview(self, df: pd.DataFrame, file_path: str, file_type: str, max_rows: int = 10):
        """Crear preview de datos reutilizable para diferentes tabs"""
        
        # Información del archivo
        file_info = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"📁 File: {os.path.basename(file_path)}", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"📊 Shape: {df.shape[0]:,} rows × {df.shape[1]} columns", size=14),
                ]),
                ft.Row([
                    ft.Text(f"📋 Type: {file_type.upper()}", size=12, color=ft.Colors.BLUE_600),
                    ft.Text(f"💾 Size: {os.path.getsize(file_path) / 1024:.1f} KB", size=12, color=ft.Colors.BLUE_600),
                ])
            ]),
            padding=10,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=8
        )
        
        # Crear tabla de datos con scroll horizontal y vertical
        preview_rows = []
        
        # Data rows (máximo según max_rows)
        for i in range(min(max_rows, len(df))):
            row_cells = []
            for col in df.columns:
                value = str(df.iloc[i][col])
                # Truncar valores muy largos para mejor visualización
                if len(value) > 50:
                    value = value[:47] + "..."
                row_cells.append(ft.DataCell(ft.Text(value, size=12)))
            preview_rows.append(ft.DataRow(cells=row_cells))
        
        # Crear tabla
        data_table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(str(col), weight=ft.FontWeight.BOLD, size=10)) for col in df.columns],
            rows=preview_rows,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            data_row_max_height=35,
        )
        
        # Container scrolleable en ambas direcciones
        scrollable_table = ft.Container(
            content=ft.Row([
                data_table
            ], scroll=ft.ScrollMode.ALWAYS),  # Scroll horizontal
            height=460,  # Altura fija mayor para acomodar más filas
            expand=True,  # Expandir horizontalmente
            padding=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
        )
        
        return ft.Column([
            file_info,
            scrollable_table,
        ], spacing=10, expand=True)
    
    def show_file_info_console(self, df: pd.DataFrame, file_type: str, delimiter: str, file_ext: str):
        """Mostrar información del archivo en consola (temporal)"""
        print(f"📋 Detected as: {file_type.upper()}")
        if file_type == "csv":
            print(f"📋 Delimiter: '{delimiter}'")
        print(f"📊 Shape: {df.shape}")
        print(f"📊 Columns: {list(df.columns)}")
    
    def update_preview(self, df: pd.DataFrame, file_path: str, file_type: str):
        """Actualizar el área de preview con datos reales"""
        
        # Usar el método reutilizable
        preview_content = self.create_data_preview(df, file_path, file_type)
        
        # Actualizar el preview container
        self.preview_container.current.content = ft.Column([
            ft.Text("📋 File Preview", size=16, weight=ft.FontWeight.BOLD),
            preview_content,
        ], spacing=10, expand=True)
        
        self.page.update()
    
    def on_format_change(self, e):
    # Solo uno puede estar seleccionado
        if e.control == self.csv_checkbox.current and e.control.value:
            self.rpt_checkbox.current.value = False
        elif e.control == self.rpt_checkbox.current and e.control.value:
            self.csv_checkbox.current.value = False
        self.page.update()
        self.validate_output(None)

    def validate_output(self, e):
        output_path = self.output_path_field.current.value
        csv_selected = self.csv_checkbox.current.value
        rpt_selected = self.rpt_checkbox.current.value

        if csv_selected and rpt_selected:
            self.output_status.current.value = "❌ Please select only one file format"
            self.state['validated_output'] = {}
        elif csv_selected:
            selected_format = ".csv"
        elif rpt_selected:
            selected_format = ".rpt"
        else:
            selected_format = None

        if output_path and selected_format:
            # Agregar extensión si falta
            if not output_path.lower().endswith(selected_format):
                base_path = os.path.splitext(output_path)[0]
                final_output_path = base_path + selected_format
            else:
                final_output_path = output_path
            output_dir = os.path.dirname(final_output_path)
            if output_dir and not os.path.exists(output_dir):
                self.output_status.current.value = f"⚠️ Directory '{output_dir}' doesn't exist. It will be created when running the pipeline."
            else:
                self.output_status.current.value = f"✅ Output configured: {final_output_path} ({selected_format.upper()})"
            self.state['validated_output'] = {
                "path": final_output_path,
                "file_type": selected_format
            }
        elif output_path and not selected_format:
            self.output_status.current.value = "⚠️ Please select a file format"
            self.state['validated_output'] = {}
        elif selected_format and not output_path:
            self.output_status.current.value = "⚠️ Please enter an output path"
            self.state['validated_output'] = {}
        else:
            self.output_status.current.value = "🚧 Configure output file and format"
            self.state['validated_output'] = {}
        
        self.update_sidebar()
        self.page.update()

    def update_sidebar(self):
        # Verificar si todos los parámetros están configurados
        input_ok = bool(self.state.get('validated_input', {}).get('path'))
        tables_ok = bool(self.state.get('validated_tables_path'))
        output_ok = bool(self.state.get('validated_output', {}).get('path'))
        config_complete = input_ok and tables_ok and output_ok

        # Actualizar botón
        self.run_button.current.disabled = not config_complete
        self.run_button_warning.current.visible = not config_complete
        self.page.update()

        # Actualizar resumen de configuración
        config_data = {
            "Input File": self.state.get('validated_input', {}).get('path', "❌ Not set"),
            "Tables Path": self.state.get('validated_tables_path') or "❌ Not set",
            "Output File": self.state.get('validated_output', {}).get('path', "❌ Not set"),
        }
        self.config_items.current.controls = [
            self.create_config_item(key, value) for key, value in config_data.items()
        ]
        self.page.update()

    def run_pipeline(self, e):
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
        config_path = os.path.join(current_dir, "..", "program", "config.yaml")
        program_dir = os.path.join(current_dir, "..", "program")

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

def main(page: ft.Page):
    app = ETLPipelineApp(page)


if __name__ == "__main__":
    ft.app(target=main) #Ese ft.app() arranca la aplicación Flet, instancia un Page y se lo pasa como argumento a main.