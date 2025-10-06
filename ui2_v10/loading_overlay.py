import flet as ft


class LoadingOverlay:
    """Overlay de carga que bloquea toda la interfaz con logs en tiempo real"""
    
    def __init__(self, page):
        self.page = page
        self.log_column = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=2,
            height=300,
            width=600
        )
        self.cancel_callback = None
        self.cancel_button = ft.ElevatedButton(
            "Cancel Pipeline",
            icon=ft.Icons.CANCEL,
            on_click=self._on_cancel_click,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREY_400,
                color=ft.Colors.BLACK,
            ),
            visible=False
        )
        
        self.container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.BLACK),
            alignment=ft.alignment.center,
            expand=True,
        )
        self.page.overlay.append(self.container)
    
    def show(self, message="Processing...", allow_cancel=False, cancel_callback=None):
        """Mostrar overlay de carga con logs en tiempo real"""
        self.log_column.controls.clear()
        self.cancel_callback = cancel_callback
        self.cancel_button.visible = allow_cancel
        
        self.container.content = ft.Container(
            content=ft.Column([
                # Header con spinner y título
                ft.Row([
                    ft.ProgressRing(width=40, height=40, stroke_width=4, color=ft.Colors.BLUE_400),
                    ft.Text(
                        message,
                        color=ft.Colors.WHITE,
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER),
                
                ft.Divider(color=ft.Colors.WHITE30),
                
                # Área de logs en tiempo real
                ft.Container(
                    content=ft.Column([
                        ft.Text("📋 Execution Logs:", color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=self.log_column,
                            bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                            border_radius=8,
                            padding=10,
                            border=ft.border.all(1, ft.Colors.BLUE_400)
                        )
                    ], spacing=5),
                    width=600
                ),
                
                # Botón de cancelación
                ft.Container(
                    content=self.cancel_button,
                    alignment=ft.alignment.center,
                    padding=ft.padding.only(top=10)
                ),
                
                # Nota informativa
                ft.Container(
                    content=ft.Text(
                        "🔒 Interface locked during execution",
                        color=ft.Colors.ORANGE_200,
                        size=11,
                        italic=True,
                        text_align=ft.TextAlign.CENTER
                    ),
                    padding=10,
                    bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.ORANGE),
                    border_radius=8,
                    margin=ft.margin.only(top=10)
                )
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            scroll=ft.ScrollMode.AUTO),
            padding=30,
            bgcolor=ft.Colors.BLUE_GREY_900,
            border_radius=15,
            border=ft.border.all(2, ft.Colors.BLUE_400),
            width=700,
        )
        self.container.visible = True
        self.page.update()
    
    def add_log(self, message, level="INFO"):
        """Agregar una línea de log en tiempo real"""
        # Determinar color según nivel
        color = ft.Colors.WHITE
        icon = "ℹ️"
        
        if "ERROR" in level or "CRITICAL" in level:
            color = ft.Colors.RED_300
            icon = "❌"
        elif "WARNING" in level:
            color = ft.Colors.ORANGE_300
            icon = "⚠️"
        elif "SUCCESS" in level:
            color = ft.Colors.GREEN_300
            icon = "✅"
        elif "DEBUG" in level:
            color = ft.Colors.YELLOW_200
            icon = "🔍"
        
        # Agregar log
        log_text = ft.Text(
            f"{icon} {message}",
            color=color,
            size=11,
            font_family="Consolas,Monaco,monospace",
            selectable=True
        )
        
        self.log_column.controls.append(log_text)
        
        # Auto-scroll al final (mantener últimos 50 logs para performance)
        if len(self.log_column.controls) > 50:
            self.log_column.controls.pop(0)
        
        # Actualizar UI
        try:
            self.page.update()
        except:
            pass  # Si la página se cerró, ignorar
    
    def hide(self):
        """Ocultar overlay de carga"""
        self.container.visible = False
        self.cancel_callback = None
        try:
            self.page.update()
        except:
            pass
    
    def _on_cancel_click(self, e):
        """Manejar click en botón de cancelación"""
        if self.cancel_callback:
            # Deshabilitar botón para evitar múltiples clicks
            self.cancel_button.disabled = True
            self.cancel_button.text = "Canceling..."
            self.page.update()
            
            # Llamar callback de cancelación
            self.cancel_callback()