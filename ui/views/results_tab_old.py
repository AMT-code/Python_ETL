import flet as ft
import os
import pandas as pd
from views.components import create_data_preview

class ResultsTab:
    def __init__(self, page, state, toast):
        self.page = page
        self.state = state
        self.toast = toast
        
        # Containers principales
        self.main_container = ft.Container()
        self.content_column = ft.Column(spacing=20)

    def build_content(self):
        """Construir el contenido del tab Results"""
        self.content_column.controls.clear()
        
        # Verificar si hay resultados validados
        validated_output = self.state.get('validated_output', {})
        
        if not validated_output or not validated_output.get('path'):
            # No hay resultados disponibles
            self.content_column.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "No results available yet",
                            size=20,
                            color=ft.Colors.GREY_600,
                            weight=ft.FontWeight.W_500
                        ),
                        ft.Text(
                            "Run the pipeline first, to see results here",
                            size=14,
                            color=ft.Colors.GREY_500
                        )
                    ], 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10),
                    padding=40,
                    alignment=ft.alignment.center
                )
            )
        else:
            # Hay resultados disponibles
            self._build_results_content(validated_output)
        
        self.main_container = ft.Container(
            content=ft.Column([
                ft.Text("Pipeline results (preview - 10 first rows)", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(height=1, color=ft.Colors.GREY_300),
                ft.Button(text="Refresh", icon=ft.Icons.REFRESH, on_click=lambda _: self.refresh_content()),
                self.content_column
            ],scroll=ft.ScrollMode.AUTO),
            padding=20,
            expand=True,
        )
        
        return self.main_container
    
    def _build_results_content(self, validated_output):
        """Construir el contenido cuando hay resultados disponibles"""
        final_output_path = validated_output.get('path')
        file_type = validated_output.get('file_type', 'csv')
        
        try:
            # Leer el archivo de resultados
            if file_type.lower() == 'csv':
                df = pd.read_csv(final_output_path)
            elif file_type.lower() in ['xlsx', 'excel']:
                df = pd.read_excel(final_output_path)
            else:
                df = pd.read_csv(final_output_path)  # Fallback
            
            output_file = os.path.basename(final_output_path)
            
            # Preview de datos usando el componente reutilizable
            data_preview = create_data_preview(df, final_output_path, file_type, max_rows=10)
            self.content_column.controls.append(data_preview)
            
            # Botones de acción
            action_buttons = ft.Row([
                ft.OutlinedButton(
                    text="Open Folder",
                    icon=ft.Icons.FOLDER_OPEN,
                    on_click=lambda _: self._open_folder(final_output_path),
                )
            ], spacing=10)
            
            self.content_column.controls.append(
                ft.Container(content=action_buttons, margin=ft.margin.only(top=15))
            )
            
            # Información expandible del archivo (simplificada ya que create_data_preview ya muestra info básica)
            # info_expander = self._create_additional_info_expander(df, final_output_path)
            # self.content_column.controls.append(info_expander)
            
        except Exception as e:
            # Error al leer el archivo
            error_container = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR, size=48, color=ft.Colors.RED_400),
                    ft.Text(
                        "❌ Error reading results",
                        size=18,
                        color=ft.Colors.RED_600,
                        weight=ft.FontWeight.W_600
                    ),
                    ft.Text(
                        str(e),
                        size=14,
                        color=ft.Colors.RED_500
                    )
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10),
                padding=30,
                bgcolor=ft.Colors.RED_50,
                border_radius=8,
                border=ft.border.all(1, ft.Colors.RED_200)
            )
            self.content_column.controls.append(error_container)
            
            if self.toast:
                self.toast.error(f"Error reading results: {str(e)}")
    
    def _create_additional_info_expander(self, df, file_path):
        """Crear el expander con información adicional del archivo"""
        # Solo tipos de columnas ya que la info básica está en create_data_preview
        dtypes_data = []
        for col, dtype in df.dtypes.items():
            dtypes_data.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(col), size=12)),
                ft.DataCell(ft.Text(str(dtype), size=12))
            ]))
        
        dtypes_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Column", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Data Type", weight=ft.FontWeight.BOLD))
            ],
            rows=dtypes_data,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            data_row_max_height=40
        )
        
        info_content = ft.Column([
            ft.Text("📋 Column Details:", size=14, weight=ft.FontWeight.W_600),
            ft.Container(
                content=dtypes_table,
                height=min(300, len(df.columns) * 45 + 50)  # Altura dinámica con máximo
            )
        ], spacing=10)
        
        return ft.ExpansionTile(
            title=ft.Text(f"📊 Detailed Information"),
            subtitle=ft.Text("Column types and additional details"),
            leading=ft.Icon(ft.Icons.INFO_OUTLINE),
            controls=[ft.Container(content=info_content, padding=15)]
        )
    
    def _open_folder(self, file_path):
        """Abrir la carpeta que contiene el archivo"""
        try:
            import subprocess
            import platform
            
            folder_path = os.path.dirname(file_path)
            
            if platform.system() == "Windows":
                subprocess.run(f'explorer "{folder_path}"', shell=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
                
            if self.toast:
                self.toast.success("Folder opened successfully")
        except Exception as e:
            if self.toast:
                self.toast.error(f"Could not open folder: {str(e)}")
    
    def refresh_content(self):
        """Método para refrescar el contenido cuando cambie el estado"""
        self.build_content()
        self.page.update()
    
