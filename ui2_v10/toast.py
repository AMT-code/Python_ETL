import flet as ft
import time
import threading


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