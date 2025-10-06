import flet as ft
import time
import threading

class Toast:
    """Sistema de Toast simple y escalable para Flet"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.toast_container = ft.Container(
            visible=False,
            alignment=ft.Alignment(0, 0.8),  # Posición: centro-abajo
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            animate_offset=ft.Animation(300, ft.AnimationCurve.BOUNCE_OUT),
        )
        
        # Agregar el contenedor al overlay de la página
        self.page.overlay.append(self.toast_container)
    
    def show(self, message: str, toast_type: str = "info", duration: int = 3):
        """
        Muestra un toast
        
        Args:
            message (str): Mensaje a mostrar
            toast_type (str): 'success', 'error', 'warning', 'info'
            duration (int): Duración en segundos
        """
        
        # Colores e iconos según el tipo
        configs = {
            "success": {"color": ft.Colors.GREEN_600, "icon": ft.Icons.CHECK_CIRCLE, "icon_color": ft.Colors.WHITE},
            "error": {"color": ft.Colors.RED_600, "icon": ft.Icons.ERROR, "icon_color": ft.Colors.WHITE},
            "warning": {"color": ft.Colors.ORANGE_600, "icon": ft.Icons.WARNING, "icon_color": ft.Colors.WHITE},
            "info": {"color": ft.Colors.BLUE_600, "icon": ft.Icons.INFO, "icon_color": ft.Colors.WHITE},
        }
        
        config = configs.get(toast_type, configs["info"])
        
        # Crear contenido del toast
        self.toast_container.content = ft.Container(
            content=ft.Row([
                ft.Icon(config["icon"], color=config["icon_color"], size=20),
                ft.Text(
                    message, 
                    color=ft.Colors.WHITE, 
                    weight=ft.FontWeight.BOLD,
                    size=14
                ),
            ], 
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER
            ),
            bgcolor=config["color"],
            padding=ft.Padding(left=20, top=12, right=20, bottom=12),
            border_radius=25,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.BLACK26,
                offset=ft.Offset(0, 2)
            ),
        )
        
        # Mostrar con animación
        self.toast_container.visible = True
        self.toast_container.offset = ft.Offset(0, 0)
        self.toast_container.opacity = 1.0
        self.page.update()
        
        # Auto-ocultar después del tiempo especificado
        def hide_toast():
            time.sleep(duration)
            self.toast_container.offset = ft.Offset(0, 0.2)
            self.toast_container.opacity = 0.0
            self.page.update()
            time.sleep(0.5)  # Esperar que termine la animación
            self.toast_container.visible = False
            self.page.update()
        
        threading.Thread(target=hide_toast, daemon=True).start()

# === EJEMPLO DE USO ===

def main(page: ft.Page):
    page.title = "Sistema Toast Simple"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    # Inicializar el sistema de toast
    toast = Toast(page)
    
    # Funciones de ejemplo
    def show_success(e):
        toast.show("¡Operación completada exitosamente!", "success")
    
    def show_error(e):
        toast.show("Error: No se pudo completar la operación", "error")
    
    def show_warning(e):
        toast.show("Advertencia: Revisa los datos ingresados", "warning")
    
    def show_info(e):
        toast.show("Información: Proceso iniciado correctamente", "info")
    
    def show_custom(e):
        toast.show("Toast personalizado con duración de 5 segundos", "info", 5)
    
    # Simulación de operaciones comunes en tu app
    def simulate_save(e):
        toast.show("Guardando datos...", "info", 1)
        
        def complete_save():
            time.sleep(1.5)
            toast.show("¡Datos guardados correctamente!", "success")
        
        threading.Thread(target=complete_save, daemon=True).start()
    
    def simulate_delete(e):
        toast.show("Eliminando elemento...", "warning", 1)
        
        def complete_delete():
            time.sleep(1.5)
            toast.show("Elemento eliminado", "error")
        
        threading.Thread(target=complete_delete, daemon=True).start()
    
    # UI
    page.add(
        ft.Column([
            ft.Text("🍞 Sistema Toast Simple y Escalable", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Reemplazo perfecto para SnackBar", size=16, color=ft.Colors.GREY_700),
            ft.Divider(height=20),
            
            # Botones básicos
            ft.Text("Tipos básicos:", weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.ElevatedButton("✅ Éxito", on_click=show_success, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
                ft.ElevatedButton("❌ Error", on_click=show_error, bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Row([
                ft.ElevatedButton("⚠️ Advertencia", on_click=show_warning, bgcolor=ft.Colors.ORANGE_600, color=ft.Colors.WHITE),
                ft.ElevatedButton("ℹ️ Info", on_click=show_info, bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE),
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Divider(),
            
            # Ejemplos prácticos
            ft.Text("Simulación de operaciones:", weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.ElevatedButton("💾 Simular Guardar", on_click=simulate_save, bgcolor=ft.Colors.INDIGO_600, color=ft.Colors.WHITE),
                ft.ElevatedButton("🗑️ Simular Eliminar", on_click=simulate_delete, bgcolor=ft.Colors.PURPLE_600, color=ft.Colors.WHITE),
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Divider(),
            ft.ElevatedButton("⏱️ Toast 5 segundos", on_click=show_custom, bgcolor=ft.Colors.TEAL_600, color=ft.Colors.WHITE),
            
        ], 
        spacing=15,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

# === VERSIÓN PARA INTEGRAR EN TU APP ===

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

"""
=== CÓMO USAR EN TU APP ===

1. Copia la clase SimpleToast a tu proyecto

2. En tu función main, inicialízala:
   toast = SimpleToast(page)

3. Úsala en cualquier lugar:
   toast.success("¡Datos guardados!")
   toast.error("Error al conectar")
   toast.warning("Revisa los campos")
   toast.info("Proceso completado")
"""

if __name__ == "__main__":
    ft.app(target=main)