import flet as ft
import os
import glob
import pandas as pd
from views.components import create_data_preview


class TablesTab:
    """Tab para configuración de directorio de tablas"""
    
    def __init__(self, page, state, toast, update_sidebar=None):
        self.page = page
        self.state = state
        self.toast = toast
        self.update_sidebar = update_sidebar
        
        # Referencias a elementos de UI
        self.tables_path_field = ft.Ref[ft.TextField]()
        self.validate_tables_button = ft.Ref[ft.ElevatedButton]()
        self.tables_dropdown = ft.Ref[ft.Dropdown]()
        self.tables_preview_container = ft.Ref[ft.Container]()
        self.tables_dropdown_container = ft.Ref[ft.Container]()

    def build_content(self):
        """Construir el contenido del tab"""
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
    
    # Event handlers
    def tables_path_changed(self, e):
        """Manejar cambios en el path del directorio de tablas"""
        print(f"Tables path changed: {e.control.value}")
        # Limpiar estado anterior si cambia el path
        if self.state.get('validated_tables_path'):
            self.state.reset_tables()
    
    def validate_tables(self, e):
        """Validar directorio de tablas"""
        print("Validating tables directory...")
        
        tables_path = self.tables_path_field.current.value
        
        if not tables_path:
            self.toast.warning("Please enter a directory path first.")
            self.state.set('validated_tables_path', '')
            return
        
        if not os.path.exists(tables_path):
            self.toast.error("Directory not found! Please check the path.")
            self.state.set('validated_tables_path', '')
            return
        
        if not os.path.isdir(tables_path):
            self.toast.error("Path is not a directory! Please enter a valid directory path.")
            self.state.set('validated_tables_path', '')
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
                self.state.set('validated_tables_path', tables_path)
                self.state.set('csv_files', csv_filenames)
                
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
            self.page.update()
            if self.update_sidebar:
                self.update_sidebar()
    
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
            preview_content = create_data_preview(df_preview, file_path, "csv", max_rows=5)
            
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
