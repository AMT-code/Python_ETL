import flet as ft
# ui aux
from toast import SimpleToast
from loading_overlay import LoadingOverlay
from state import AppState
# views aux
from views.input_tab import InputTab
from views.tables_tab import TablesTab
from views.output_tab import OutputsTab
from views.code_tab import CodeTab
from views.log_tab import LogTab
from views.results_tab import ResultsTab
from views.sidebar import SideBar

class ETLPipelineApp:
    """Main App set up"""
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        self.init_state()
        # Inicializar toast y loading DESPUÉS de setup_page
        self.toast = SimpleToast(self.page)
        self.loading = LoadingOverlay(self.page)
        self.sidebar = SideBar(page=self.page, state=self.state, toast=self.toast, loading=self.loading)
        self.input_tab = InputTab(page=self.page, state=self.state, toast=self.toast, update_sidebar=self.sidebar.update_sidebar)
        self.tables_tab = TablesTab(page=self.page, state=self.state, toast=self.toast, update_sidebar=self.sidebar.update_sidebar)
        self.outputs_tab = OutputsTab(page=self.page, state=self.state, toast=self.toast, update_sidebar=self.sidebar.update_sidebar)
        self.code_tab = CodeTab(page=self.page, state=self.state, toast=self.toast)
        self.log_tab = LogTab(page=self.page, state=self.state, toast=self.toast)
        self.results_tab = ResultsTab(page=self.page, state=self.state, toast=self.toast)
        self.build_ui()
    
    def setup_page(self):
        """Configuración inicial de la página"""
        self.page.title = "ETL Pipeline tool"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.bgcolor = ft.Colors.BLUE_GREY_50
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_min_width = 800
        self.page.window_min_height = 600
        
        # Configurar colores del tema
        self.page.theme = ft.Theme(
            primary_swatch=ft.Colors.BLUE,
        )

    def init_state(self):
        """Inicializar el estado de la aplicación"""
        self.state = AppState()

    """UI Components building"""
    def build_ui(self):
        """Construir la interfaz de usuario"""
        # Crear las tabs
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="📁 Input Parameters",
                    content=self.build_input_tab()
                ),
                ft.Tab(
                    text="📊 Tables Parameters", 
                    content=self.build_tables_tab()
                ),
                ft.Tab(
                    text="💾 Output Parameters",
                    content=self.build_output_tab()
                ),
                ft.Tab(
                    text="⚙️ Code View",
                    content=self.build_code_tab()
                ),
                ft.Tab(
                    text="📋 Log",
                    content=self.build_log_tab()
                ),
                ft.Tab(
                    text="✅ Results",
                    content=self.build_results_tab()
                )
            ],
            on_change=self.tab_changed
        )
        
        # Crear el sidebar
        sidebar = self.build_sidebar()
        
        # Layout principal
        main_content = ft.Row([
            # Sidebar
            ft.Container(
                content=sidebar,
                width=300,
                bgcolor=ft.Colors.BLUE_GREY_100,
                padding=20,
                border_radius=10
            ),
            # Contenido principal
            ft.Container(
                content=self.tabs,
                expand=True,
                padding=20
            )
        ], expand=True)
        
        # Agregar todo a la página
        self.page.add(
            ft.Container(
                content=main_content,
                expand=True,
                padding=10
            )
        )
    
    def build_input_tab(self):
        """Tab 1: Input Parameters"""
        return self.input_tab.build_content()
    
    def build_tables_tab(self):
        """Tab 2: Tables Parameters - Funcionalidad completa"""
        return self.tables_tab.build_content()
    
    def build_output_tab(self):
        """Tab 3: Output Parameters"""
        return self.outputs_tab.build_content()
    
    def build_code_tab(self):
        """Tab Code - Editor de funciones"""
        return self.code_tab.build_content()

    def build_log_tab(self):
        """Tab 5: Log"""
        return self.log_tab.build_content()

    def build_results_tab(self):
        """Tab 6: Results - Placeholder por ahora"""
        return self.results_tab.build_content()

    def build_sidebar(self):
        """Tab 3: Output Parameters - Placeholder por ahora"""
        return self.sidebar.build_content()

    # Event handlers
    def tab_changed(self, e):
        """Manejar cambio de tab"""
        self.state.set('current_tab', e.control.selected_index)
        print(f"Cambiado a tab: {e.control.selected_index}")
    

def main(page: ft.Page):
    app = ETLPipelineApp(page)


if __name__ == "__main__":
    ft.app(target=main)