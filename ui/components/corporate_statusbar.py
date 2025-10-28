import flet as ft
from components.corporate_colors import CorporateColors


class CorporateStatusBar:
    """
    Barra de estado inferior
    Responsabilidad: Mostrar estado general e indicadores de configuración
    """
    
    def __init__(self, page: ft.Page, state):
        self.page = page
        self.state = state
        
        # Referencias a elementos de UI
        self.status_icon = None
        self.status_text = None
        self.last_execution_text = None
        self.indicators = {}
        self.container = None
    
    def build(self):
        """Construir la barra de estado"""
        # Crear elementos
        self.status_icon = ft.Icon(
            ft.Icons.CIRCLE,
            color=CorporateColors.SECONDARY,
            size=10
        )
        
        self.status_text = ft.Text(
            "Ready",
            size=11,
            color=CorporateColors.TEXT_SECONDARY
        )
        
        self.last_execution_text = ft.Text(
            "",
            size=11,
            color=CorporateColors.TEXT_SECONDARY
        )
        
        # Indicadores de configuración
        self.indicators = {
            'input': ft.Text(
                "Input: ✗",
                size=11,
                color=CorporateColors.ERROR
            ),
            'tables': ft.Text(
                "Tables: ✗",
                size=11,
                color=CorporateColors.ERROR
            ),
            'output': ft.Text(
                "Output: ✗",
                size=11,
                color=CorporateColors.ERROR
            ),
        }
        
        # Container principal
        self.container = ft.Container(
            content=ft.Row([
                self.status_icon,
                self.status_text,
                ft.Container(width=20),
                self.last_execution_text,
                ft.Container(expand=True),
                self.indicators['input'],
                ft.Container(width=10),
                self.indicators['tables'],
                ft.Container(width=10),
                self.indicators['output'],
            ], spacing=5),
            bgcolor=CorporateColors.BACKGROUND,
            padding=ft.padding.symmetric(horizontal=20, vertical=8),
            border=ft.border.only(top=ft.BorderSide(1, CorporateColors.BORDER))
        )
        
        return self.container
    
    def update_status(self):
        """Actualizar indicadores basado en el estado"""
        # Verificar configuración
        input_ok = bool(self.state.get('validated_input', {}).get('path'))
        tables_ok = bool(self.state.get('validated_tables_path'))
        output_ok = bool(self.state.get('validated_output', {}).get('path'))
        
        # Actualizar indicadores individuales
        self.indicators['input'].value = "Input: ✓" if input_ok else "Input: ✗"
        self.indicators['input'].color = CorporateColors.SUCCESS if input_ok else CorporateColors.ERROR
        
        self.indicators['tables'].value = "Tables: ✓" if tables_ok else "Tables: ✗"
        self.indicators['tables'].color = CorporateColors.SUCCESS if tables_ok else CorporateColors.ERROR
        
        self.indicators['output'].value = "Output: ✓" if output_ok else "Output: ✗"
        self.indicators['output'].color = CorporateColors.SUCCESS if output_ok else CorporateColors.ERROR
        
        # Actualizar estado general
        config_complete = input_ok and tables_ok and output_ok
        
        if config_complete:
            self.status_icon.color = CorporateColors.SUCCESS
            self.status_text.value = "Ready"
            self.status_text.color = CorporateColors.SUCCESS
        else:
            self.status_icon.color = CorporateColors.WARNING
            self.status_text.value = "Configuration incomplete"
            self.status_text.color = CorporateColors.WARNING
        
        # Actualizar UI
        if self.container:
            self.page.update()
    
    def set_last_execution(self, text):
        """Actualizar texto de última ejecución"""
        if self.last_execution_text:
            self.last_execution_text.value = text
            self.page.update()
    
    def set_status(self, status_text, status_type="info"):
        """
        Cambiar el estado general
        
        Args:
            status_text: Texto a mostrar
            status_type: 'success', 'warning', 'error', 'info'
        """
        color_map = {
            'success': CorporateColors.SUCCESS,
            'warning': CorporateColors.WARNING,
            'error': CorporateColors.ERROR,
            'info': CorporateColors.INFO
        }
        
        self.status_text.value = status_text
        self.status_text.color = color_map.get(status_type, CorporateColors.TEXT_SECONDARY)
        self.status_icon.color = color_map.get(status_type, CorporateColors.SECONDARY)
        
        if self.container:
            self.page.update()