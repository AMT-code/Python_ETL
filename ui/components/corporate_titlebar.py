import flet as ft
from components.corporate_colors import CorporateColors


class CorporateTitleBar:
    """
    Barra de título corporativa
    Responsabilidad: Solo UI de la barra superior
    """
    
    def __init__(self, page: ft.Page, app_name="ETL Pipeline Tool", version="v16.2"):
        self.page = page
        self.app_name = app_name
        self.version = version
    
    def build(self):
        """Construir la barra de título"""
        return ft.Container(
            content=ft.Row([
                # Logo e icono
                ft.Icon(
                    ft.Icons.DASHBOARD,
                    color=ft.Colors.WHITE,
                    size=20
                ),
                
                # Nombre de la aplicación
                ft.Text(
                    self.app_name,
                    color=ft.Colors.WHITE,
                    size=14,
                    weight=ft.FontWeight.W_600
                ),
                
                # Spacer
                ft.Container(expand=True),
                
                # Botón de ayuda
                ft.IconButton(
                    icon=ft.Icons.HELP_OUTLINE,
                    icon_color=ft.Colors.WHITE70,
                    icon_size=18,
                    tooltip="Documentation",
                    on_click=self._on_help_click
                ),
                
                # Versión
                ft.Text(
                    self.version,
                    color=ft.Colors.WHITE70,
                    size=11
                ),
            ], spacing=10),
            bgcolor=CorporateColors.SIDEBAR_BG,
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
        )
    
    def _on_help_click(self, e):
        """Handler para botón de ayuda"""
        # Por ahora solo un placeholder
        print("Help button clicked - Open documentation")
        # TODO: Abrir diálogo de ayuda o documentación