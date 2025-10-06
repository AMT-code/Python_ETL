import flet as ft
from views.components import create_config_item
from core.pipeline_runner import run_pipeline


class SideBar:
    """Construir el sidebar con controles del pipeline y resumen de configuración"""

    def __init__(self, page, state, toast, loading):
        self.page = page
        self.state = state
        self.toast = toast
        self.loading = loading

        # Referencias para SideBar
        self.run_button = ft.Ref[ft.ElevatedButton]()
        self.run_button_warning = ft.Ref[ft.Text]()
        self.config_items = ft.Ref[ft.Column]()
        self.log_container = ft.Ref[ft.Container]()

    def build_content(self):
        """Construir el sidebar con controles del pipeline y resumen de configuración"""
        # Llamar a update_sidebar cada vez que se navega entre tabs
        self.page.on_resize = lambda _: self.update_sidebar()
        self.page.on_route_change = lambda _: self.update_sidebar()
        
        return ft.Column([
            ft.Text("Pipeline Control", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            # Botón principal
            ft.ElevatedButton(
                "▶️ Run Pipeline",
                width=200,
                height=50,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.GREY,  # Inicialmente gris
                    shape=ft.RoundedRectangleBorder(radius=10)
                ),
                on_click=lambda _: run_pipeline(self),  # Pasar self completo
                disabled=True,  # Inicialmente deshabilitado
                ref=self.run_button
            ),

            ft.Text("⚠️ Complete all configuration tabs first", color=ft.Colors.ORANGE_600, ref=self.run_button_warning),
            ft.Divider(),
            
            # Current Configuration
            ft.Text("📋 Current Configuration", size=16, weight=ft.FontWeight.BOLD),
            
            ft.Container(
                content=ft.Column([
                    create_config_item("Input File", "⛔ Not set"),
                    create_config_item("Tables Path", "⛔ Not set"),
                    create_config_item("Output File", "⛔ Not set"),
                ], 
                ref=self.config_items),
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_500),
                border_radius=8,
                bgcolor=ft.Colors.BLUE_GREY_100
            ),

            ft.Divider(),
            ft.Container(
                content=ft.Column([]),
                ref=self.log_container
            )               
        ], spacing=10)

    def update_sidebar(self):
        """Actualizar estado del sidebar"""
        # Verificar si todos los parámetros están configurados
        input_ok = bool(self.state.get('validated_input', {}).get('path'))
        tables_ok = bool(self.state.get('validated_tables_path'))
        output_ok = bool(self.state.get('validated_output', {}).get('path'))
        config_complete = input_ok and tables_ok and output_ok

        # Actualizar botón
        self.run_button.current.disabled = not config_complete
        self.run_button.current.style = ft.ButtonStyle(bgcolor=ft.Colors.GREEN if config_complete else ft.Colors.GREY)
        self.run_button_warning.current.visible = not config_complete
        self.page.update()

        # Actualizar resumen de configuración
        config_data = {
            "Input File": self.state.get('validated_input', {}).get('path', "⛔ Not set"),
            "Tables Path": self.state.get('validated_tables_path') or "⛔ Not set",
            "Output File": self.state.get('validated_output', {}).get('path', "⛔ Not set"),
        }
        self.config_items.current.controls = [
            create_config_item(key, value) for key, value in config_data.items()
        ]
        self.page.update()