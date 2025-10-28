import flet as ft
from components.corporate_colors import CorporateColors


class CorporateSidebar:
    """
    Sidebar lateral corporativo
    Responsabilidad: UI de navegación + botón Run Pipeline (sin lógica de ejecución)
    """
    
    def __init__(self, page: ft.Page, state, on_view_change=None, on_run_click=None):
        self.page = page
        self.state = state
        self.on_view_change = on_view_change  # Callback para cambio de vista
        self.on_run_click = on_run_click      # Callback para ejecutar pipeline
        self.current_view = "input"
        
        # Referencias
        self.menu_buttons = {}
        self.run_button = None
        self.run_status_text = None
        self.container = None
    
    def build(self):
        """Construir el sidebar completo"""
        # Definir items del menú
        menu_items = [
            ("input", "Input", ft.Icons.UPLOAD_FILE),
            ("tables", "Tables", ft.Icons.TABLE_CHART),
            ("output", "Output", ft.Icons.SAVE),
            ("code", "Code", ft.Icons.CODE),
            ("logs", "Logs", ft.Icons.DESCRIPTION),
            ("results", "Results", ft.Icons.CHECK_CIRCLE),
        ]
        
        # Crear botones de menú
        menu_buttons_list = []
        for view_id, label, icon in menu_items:
            btn = self._create_menu_button(view_id, label, icon)
            self.menu_buttons[view_id] = btn
            menu_buttons_list.append(btn)
        
        # Sección Run Pipeline
        run_section = self._create_run_section()
        
        # Container principal
        self.container = ft.Container(
            content=ft.Column([
                ft.Container(height=10),
                *menu_buttons_list,
                ft.Container(expand=True),
                ft.Divider(color=ft.Colors.WHITE12, height=1),
                run_section
            ], spacing=4),
            width=240,
            bgcolor=CorporateColors.SIDEBAR_BG,
            padding=ft.padding.only(top=10, bottom=10)
        )
        
        return self.container
    
    def _create_menu_button(self, view_id, label, icon):
        """Crear botón individual del menú"""
        is_selected = view_id == self.current_view
        
        btn = ft.Container(
            content=ft.Row([
                ft.Icon(
                    icon,
                    color=CorporateColors.PRIMARY_LIGHT if is_selected else ft.Colors.WHITE70,
                    size=18
                ),
                ft.Text(
                    label,
                    color=ft.Colors.WHITE if is_selected else ft.Colors.WHITE70,
                    size=13,
                    weight=ft.FontWeight.W_600 if is_selected else ft.FontWeight.NORMAL
                ),
            ], spacing=12),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor=ft.Colors.with_opacity(0.1, CorporateColors.PRIMARY) if is_selected else None,
            border_radius=8,
            on_click=lambda e, v=view_id: self._handle_menu_click(v),
            ink=True,
            data=view_id
        )
        
        return btn
    
    def _create_run_section(self):
        """Crear sección de Run Pipeline"""
        self.run_button = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.PLAY_ARROW, size=18),
                ft.Text("Run Pipeline", size=13, weight=ft.FontWeight.W_600),
            ], spacing=8, tight=True),
            style=ft.ButtonStyle(
                bgcolor=CorporateColors.SECONDARY,  # Gris por defecto
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=12)
            ),
            width=200,
            disabled=True,
            on_click=self._handle_run_click
        )
        
        self.run_status_text = ft.Text(
            "Configure all parameters",
            size=11,
            color=ft.Colors.WHITE54,
            text_align=ft.TextAlign.CENTER
        )
        
        return ft.Container(
            content=ft.Column([
                self.run_button,
                self.run_status_text
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            padding=20
        )
    
    def _handle_menu_click(self, view_id):
        """Handler interno para click en menú"""
        # Actualizar vista actual
        old_view = self.current_view
        self.current_view = view_id
        
        # Actualizar UI de botones
        self._update_button_states(old_view, view_id)
        
        # Llamar callback externo
        if self.on_view_change:
            self.on_view_change(view_id)
    
    def _handle_run_click(self, e):
        """Handler interno para click en Run Pipeline"""
        if self.on_run_click:
            self.on_run_click(e)
    
    def _update_button_states(self, old_view, new_view):
        """Actualizar estados visuales de los botones"""
        # Desmarcar botón anterior
        if old_view in self.menu_buttons:
            old_btn = self.menu_buttons[old_view]
            old_btn.bgcolor = None
            old_btn.content.controls[0].color = ft.Colors.WHITE70  # Icon
            old_btn.content.controls[1].color = ft.Colors.WHITE70  # Text
            old_btn.content.controls[1].weight = ft.FontWeight.NORMAL
        
        # Marcar botón nuevo
        if new_view in self.menu_buttons:
            new_btn = self.menu_buttons[new_view]
            new_btn.bgcolor = ft.Colors.with_opacity(0.1, CorporateColors.PRIMARY)
            new_btn.content.controls[0].color = CorporateColors.PRIMARY_LIGHT  # Icon
            new_btn.content.controls[1].color = ft.Colors.WHITE  # Text
            new_btn.content.controls[1].weight = ft.FontWeight.W_600
        
        self.page.update()
    
    def update_run_button(self, enabled, status_text=None):
        """
        Actualizar estado del botón Run Pipeline
        
        Args:
            enabled: True si el botón debe estar habilitado
            status_text: Texto opcional para mostrar bajo el botón
        """
        if self.run_button:
            self.run_button.disabled = not enabled
            self.run_button.style.bgcolor = CorporateColors.SUCCESS if enabled else CorporateColors.SECONDARY
        
        if status_text and self.run_status_text:
            self.run_status_text.value = status_text
            self.run_status_text.color = ft.Colors.WHITE70 if enabled else ft.Colors.WHITE54
        
        if self.container:
            self.page.update()
    
    def set_current_view(self, view_id):
        """Cambiar vista programáticamente"""
        if view_id != self.current_view:
            old_view = self.current_view
            self.current_view = view_id
            self._update_button_states(old_view, view_id)