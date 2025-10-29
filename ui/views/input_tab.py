import flet as ft
import os
import pandas as pd
from views.components import create_data_preview
from components.corporate_colors import CorporateColors


class InputTab:
    """Tab para configuración de archivos de entrada - Diseño Corporativo"""

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

    def build_content(self):
        """Construir el contenido del tab con diseño corporativo"""
        return ft.Container(
            content=ft.Column([
                # Card 1: File Selection
                self._create_card(
                    "File Selection",
                    self._build_file_selection()
                ),
                
                # Card 2: File Type & Delimiter
                self._create_card(
                    "File Configuration",
                    self._build_file_config()
                ),
                
                # Card 3: Data Preview
                self._create_card(
                    "Data Preview",
                    self._build_preview_section(),
                    expand=True
                )
            ], 
            scroll=ft.ScrollMode.AUTO,
            spacing=20),
            padding=30,
            expand=True
        )
    
    def _create_card(self, title, content, expand=False):
        """Crear card corporativa consistente"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    title,
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=CorporateColors.TEXT_PRIMARY
                ),
                ft.Divider(height=1, color=CorporateColors.BORDER),
                content
            ], spacing=15),
            padding=20,
            bgcolor=CorporateColors.SURFACE,
            border_radius=8,
            border=ft.border.all(1, CorporateColors.BORDER),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                offset=ft.Offset(0, 2)
            ),
            expand=expand
        )
    
    def _build_file_selection(self):
        """Sección de selección de archivo"""
        return ft.Column([
            ft.Row([
                ft.TextField(
                    label="File Path",
                    hint_text="Enter file path or browse",
                    expand=True,
                    on_change=self.input_path_changed,
                    ref=self.input_path_field,
                    border_color=CorporateColors.BORDER,
                    focused_border_color=CorporateColors.PRIMARY,
                    text_size=13
                ),
                ft.IconButton(
                    icon=ft.Icons.FOLDER_OPEN,
                    icon_color=CorporateColors.PRIMARY,
                    tooltip="Browse files",
                    on_click=self._browse_file
                )
            ], spacing=10),
            
            ft.Text(
                "Supported formats: CSV, Excel (.xlsx, .xls), Parquet",
                size=11,
                color=CorporateColors.TEXT_SECONDARY,
                italic=True
            )
        ], spacing=10)
    
    def _build_file_config(self):
        """Sección de configuración de archivo"""
        return ft.Column([
            ft.Dropdown(
                label="File Type",
                width=250,
                options=[
                    ft.dropdown.Option("auto", "Auto-detect"),
                    ft.dropdown.Option("csv", "CSV/Delimited"),
                    ft.dropdown.Option("excel", "Excel (xlsx/xls)"),
                    ft.dropdown.Option("parquet", "Parquet"),
                ],
                value="auto",
                on_change=self.file_type_changed,
                ref=self.file_type_dropdown,
                border_color=CorporateColors.BORDER,
                focused_border_color=CorporateColors.PRIMARY,
                text_size=13
            ),
            
            # Delimiter configuration (oculto inicialmente)
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Delimiter Settings",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=CorporateColors.TEXT_PRIMARY
                    ),
                    ft.Row([
                        ft.TextField(
                            label="Delimiter",
                            value=",",
                            width=100,
                            max_length=3,
                            hint_text=", ; |",
                            ref=self.delimiter_field,
                            border_color=CorporateColors.BORDER,
                            focused_border_color=CorporateColors.PRIMARY,
                            text_size=13
                        ),
                        ft.Checkbox(
                            label="Tab delimited",
                            on_change=self.tab_delimiter_changed,
                            ref=self.tab_delimiter_checkbox
                        )
                    ], spacing=15)
                ], spacing=10),
                padding=ft.padding.only(top=10),
                visible=False,
                ref=self.delimiter_container
            )
        ], spacing=10)
    
    def _build_preview_section(self):
        """Sección de preview de datos"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=CorporateColors.INFO),
                    ft.Text(
                        "Select and validate a file to see preview",
                        size=12,
                        color=CorporateColors.TEXT_SECONDARY
                    )
                ], spacing=8)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=40,
            bgcolor=CorporateColors.BACKGROUND,
            border_radius=8,
            alignment=ft.alignment.center,
            ref=self.preview_container,
            expand=True
        )
    
    def _browse_file(self, e):
        """Abrir explorador de archivos (placeholder)"""
        self.toast.info("📁 File browser - Coming soon")
        # TODO: Implementar file picker
    
    # Event handlers
    def input_path_changed(self, e):
        """Manejar cambios en el path del archivo"""
        if self.state.get('validated_input'):
            self.state.reset_input()
    
    def file_type_changed(self, e):
        """Manejar cambios en el tipo de archivo"""
        show_delimiter = e.control.value == "csv"
        self.delimiter_container.current.visible = show_delimiter
        self.page.update()
    
    def tab_delimiter_changed(self, e):
        """Manejar checkbox de tab delimiter"""
        is_tab = e.control.value
        
        self.delimiter_field.current.disabled = is_tab
        
        if is_tab:
            self.delimiter_field.current.value = ""
            self.delimiter_field.current.hint_text = "Using tab"
        else:
            self.delimiter_field.current.value = ","
            self.delimiter_field.current.hint_text = ", ; |"
        
        self.page.update()
    
    def validate_input(self, e):
        """Validar archivo de input (llamado por botón Save del header)"""
        input_path = self.input_path_field.current.value
        file_type = self.file_type_dropdown.current.value
        
        if not input_path:
            self.toast.warning("⚠️ Please enter a file path first")
            return
        
        if not os.path.exists(input_path):
            self.toast.error("⛔ File not found! Please check the path")
            return
        
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
                    self.toast.error(f"⛔ Cannot auto-detect file format: {file_ext}")
                    return
            else:
                final_file_type = file_type
            
            # Parámetros de lectura
            read_params = {}
            delimiter = ","
            
            if final_file_type == "csv":
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
                
                # Success y preview
                self.toast.success(f"✅ File validated: {df_preview.shape[0]:,} rows × {df_preview.shape[1]} cols")
                self.update_preview(df_preview, input_path, final_file_type)

        except Exception as ex:
            self.toast.error(f"⛔ Error reading file: {str(ex)}")
            if "delimiter" in str(ex).lower():
                self.toast.info("💡 Try changing the delimiter setting")
        
        finally:
            if self.update_sidebar:
                self.update_sidebar()
    
    def read_file(self, file_path: str, file_type: str, read_params: dict):
        """Leer archivo según su tipo"""
        if file_type == "csv":
            return pd.read_csv(file_path, **read_params)
        elif file_type == "excel":
            return pd.read_excel(file_path, **read_params)
        elif file_type == "parquet":
            return pd.read_parquet(file_path, **read_params)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def update_preview(self, df: pd.DataFrame, file_path: str, file_type: str):
        """Actualizar el área de preview con datos reales"""
        # Estadísticas rápidas
        stats_row = ft.Row([
            self._create_stat_badge("Rows", f"{len(df):,}", ft.Icons.TABLE_ROWS),
            self._create_stat_badge("Columns", f"{len(df.columns)}", ft.Icons.VIEW_COLUMN),
            self._create_stat_badge("Size", f"{os.path.getsize(file_path) / 1024:.1f} KB", ft.Icons.STORAGE),
        ], spacing=15)
        
        # Preview de datos usando componente existente
        preview_content = create_data_preview(df, file_path, file_type, max_rows=10)
        
        # Actualizar container
        self.preview_container.current.content = ft.Column([
            stats_row,
            ft.Container(height=10),
            preview_content
        ], spacing=10, expand=True)
        
        self.preview_container.current.padding = 20
        self.preview_container.current.bgcolor = None
        self.preview_container.current.alignment = None
        
        self.page.update()
    
    def _create_stat_badge(self, label, value, icon):
        """Badge de estadística corporativo"""
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=CorporateColors.PRIMARY, size=18),
                ft.Column([
                    ft.Text(label, size=11, color=CorporateColors.TEXT_SECONDARY),
                    ft.Text(value, size=14, weight=ft.FontWeight.W_600, color=CorporateColors.TEXT_PRIMARY),
                ], spacing=2, tight=True)
            ], spacing=10, tight=True),
            bgcolor=CorporateColors.BACKGROUND,
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            border_radius=6,
            border=ft.border.all(1, CorporateColors.BORDER)
        )