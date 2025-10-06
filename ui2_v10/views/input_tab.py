import flet as ft
import os
import pandas as pd
from views.components import create_data_preview


class InputTab:
    """Tab para configuración de archivos de entrada"""

    def __init__(self, page, state, toast, update_sidebar=None):
        self.page = page
        self.state = state
        self.toast = toast
        self.update_sidebar = update_sidebar

        # Referencias a elementos de UI
        self.input_path_field = ft.Ref[ft.TextField]()
        self.file_type_dropdown = ft.Ref[ft.Dropdown]()
        self.delimiter_container = ft.Ref[ft.Container]()
        self.delimiter_field = ft.Ref[ft.TextField]()
        self.tab_delimiter_checkbox = ft.Ref[ft.Checkbox]()
        self.preview_container = ft.Ref[ft.Container]()
        self.validate_button = ft.Ref[ft.ElevatedButton]()

    def build_content(self):
        """Construir el contenido del tab"""
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
                        ft.Text("📄 Delimiter Configuration", size=16, weight=ft.FontWeight.BOLD),
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
                        ft.Text("📋 File Preview (First 10 rows)", size=16, weight=ft.FontWeight.BOLD),
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
    
    # Event handlers
    def input_path_changed(self, e):
        """Manejar cambios en el path del archivo"""
        print(f"Input path changed: {e.control.value}")
        # Limpiar estado anterior si cambia el path
        if self.state.get('validated_input'):
            self.state.reset_input()
    
    def file_type_changed(self, e):
        """Manejar cambios en el tipo de archivo"""
        print(f"File type changed: {e.control.value}")
        # Mostrar/ocultar configuración de delimiter
        show_delimiter = e.control.value == "csv"
        self.delimiter_container.current.visible = show_delimiter
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
                self.state.set('validated_input', {
                    "path": input_path,
                    "file_type": final_file_type,
                    "delimiter": delimiter if final_file_type == "csv" else None,
                    "read_params": read_params
                })
                
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
            self.page.update()
            if self.update_sidebar:
                self.update_sidebar()
    
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
    
    def show_file_info_console(self, df: pd.DataFrame, file_type: str, delimiter: str, file_ext: str):
        """Mostrar información del archivo en consola (temporal)"""
        print(f"📋 Detected as: {file_type.upper()}")
        if file_type == "csv":
            print(f"📋 Delimiter: '{delimiter}'")
        print(f"📊 Shape: {df.shape}")
        print(f"📊 Columns: {list(df.columns)}")
    
    def update_preview(self, df: pd.DataFrame, file_path: str, file_type: str):
        """Actualizar el área de preview con datos reales"""
        
        # Usar el método reutilizable (por ahora lo copiamos aquí)
        preview_content = create_data_preview(df, file_path, file_type)
        
        # Actualizar el preview container
        self.preview_container.current.content = ft.Column([
            ft.Text("📋 File Preview (First 10 rows)", size=16, weight=ft.FontWeight.BOLD),
            preview_content,
        ], spacing=10, expand=True)
        
        self.page.update()
