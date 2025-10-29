import flet as ft

# UI Components
from components.corporate_colors import CorporateColors
from components.corporate_titlebar import CorporateTitleBar
from components.corporate_statusbar import CorporateStatusBar
from components.corporate_sidebar import CorporateSidebar

# Core UI utilities
from toast import SimpleToast
from loading_overlay import LoadingOverlay
from state import AppState

# Views (tabs)
from views.input_tab import InputTab
from views.tables_tab import TablesTab
from views.output_tab import OutputsTab
from views.code_tab import CodeTab
from views.log_tab import LogTab
from views.results_tab import ResultsTab

# Core functionality
from core.pipeline_runner import run_pipeline


class ETLPipelineApp:
    """
    Main App - Versión Corporativa v2
    Responsabilidad: Solo ensamblar componentes y coordinar
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_view = "input"
        
        self.setup_page()
        self.init_state()
        self.init_components()
        self.init_tabs()
        self.build_ui()
    
    def setup_page(self):
        """Configuración de la página"""
        self.page.title = "ETL Pipeline Tool"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.bgcolor = CorporateColors.BACKGROUND
        self.page.padding = 0
        self.page.window_width = 1400
        self.page.window_height = 900
        self.page.window_min_width = 1200
        self.page.window_min_height = 700
        
        self.page.theme = ft.Theme(
            color_scheme_seed=CorporateColors.PRIMARY,
        )
    
    def init_state(self):
        """Inicializar estado"""
        self.state = AppState()
        self.state.set('enable_audit', True)
    
    def init_components(self):
        """Inicializar componentes de UI"""
        # Utilidades
        self.toast = SimpleToast(self.page)
        self.loading = LoadingOverlay(self.page)
        
        # Componentes corporativos
        self.titlebar = CorporateTitleBar(self.page)
        self.statusbar = CorporateStatusBar(self.page, self.state)
        self.sidebar = CorporateSidebar(
            page=self.page,
            state=self.state,
            on_view_change=self.handle_view_change,
            on_run_click=self.handle_run_pipeline
        )
        
        # Container para contenido principal
        self.main_content_container = ft.Container(
            bgcolor=ft.Colors.WHITE,
            expand=True
        )
    
    def init_tabs(self):
        """Inicializar tabs (vistas)"""
        self.tabs = {
            'input': InputTab(
                page=self.page,
                state=self.state,
                toast=self.toast,
                update_sidebar=self.update_status
            ),
            'tables': TablesTab(
                page=self.page,
                state=self.state,
                toast=self.toast,
                update_sidebar=self.update_status
            ),
            'output': OutputsTab(
                page=self.page,
                state=self.state,
                toast=self.toast,
                update_sidebar=self.update_status,
                enable_audit_control=True
            ),
            'code': CodeTab(
                page=self.page,
                state=self.state,
                toast=self.toast
            ),
            'logs': LogTab(
                page=self.page,
                state=self.state,
                toast=self.toast
            ),
            'results': ResultsTab(
                page=self.page,
                state=self.state,
                toast=self.toast
            )
        }
    
    def build_ui(self):
        """Ensamblar la UI completa"""
        # Construir componentes
        title_bar = self.titlebar.build()
        sidebar_widget = self.sidebar.build()
        status_bar = self.statusbar.build()
        
        # Cargar vista inicial
        self.load_view(self.current_view)
        
        # Layout principal
        layout = ft.Column([
            title_bar,
            ft.Row([
                sidebar_widget,
                self.main_content_container
            ], expand=True, spacing=0),
            status_bar
        ], spacing=0, expand=True)
        
        self.page.add(layout)
    
    def handle_view_change(self, view_id):
        """Handler: cambio de vista"""
        self.current_view = view_id
        self.load_view(view_id)
    
    def handle_run_pipeline(self, e):
        """Handler: ejecutar pipeline"""
        # Crear bridge para pipeline_runner
        bridge = self.create_pipeline_bridge()
        
        # Ejecutar usando el runner original
        run_pipeline(bridge)
    
    def create_pipeline_bridge(self):
        """Crear objeto bridge para pipeline_runner"""
        class PipelineBridge:
            def __init__(self, page, state, toast, loading, run_button):
                self.page = page
                self.state = state
                self.toast = toast
                self.loading = loading
                self.run_button = ft.Ref[ft.ElevatedButton]()
                self.run_button.current = run_button
        
        return PipelineBridge(
            page=self.page,
            state=self.state,
            toast=self.toast,
            loading=self.loading,
            run_button=self.sidebar.run_button
        )
    
    def load_view(self, view_id):
        """Cargar contenido de una vista"""
        # Información de la vista
        view_info = {
            "input": ("Input File Configuration", "Configure your input data source"),
            "tables": ("Tables Configuration", "Manage auxiliary tables and lookup data"),
            "output": ("Output Configuration", "Define output file format and location"),
            "code": ("Code Editor", "View and edit transformation functions"),
            "logs": ("Execution Logs", "Monitor pipeline execution history"),
            "results": ("Pipeline Results", "Review processed data output"),
        }
        
        title, subtitle = view_info.get(view_id, ("", ""))
        
        # Header
        header = self.create_view_header(title, subtitle)
        
        # Contenido del tab
        content = self.tabs[view_id].build_content()
        
        # Actualizar container principal
        self.main_content_container.content = ft.Column([
            header,
            ft.Container(
                content=content,
                padding=0,
                expand=True
            )
        ], spacing=0, expand=True)
        
        self.page.update()
    
    def create_view_header(self, title, subtitle):
        """Crear header de vista con botones condicionales"""
        # Definir qué tabs tienen botones de Save y Refresh
        has_save = self.current_view in ['input', 'tables', 'output']
        has_refresh = self.current_view in ['input', 'tables', 'output']
        
        # Construir row de botones
        action_buttons = []
        
        if has_save:
            action_buttons.append(
                ft.ElevatedButton(
                    "Save",
                    icon=ft.Icons.SAVE,
                    style=ft.ButtonStyle(
                        bgcolor=CorporateColors.PRIMARY,
                        color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=6)
                    ),
                    on_click=lambda e: self.save_current_view()
                )
            )
        
        if has_refresh:
            action_buttons.append(
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    icon_color=CorporateColors.SECONDARY,
                    tooltip="Refresh",
                    on_click=lambda e: self.refresh_current_view()
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(
                        title,
                        size=24,
                        weight=ft.FontWeight.W_700,
                        color=CorporateColors.TEXT_PRIMARY
                    ),
                    ft.Container(expand=True),
                    *action_buttons  # Agregar botones condicionalmente
                ], spacing=10),
                ft.Text(
                    subtitle,
                    size=13,
                    color=CorporateColors.TEXT_SECONDARY
                ),
            ], spacing=4),
            padding=ft.padding.symmetric(horizontal=30, vertical=20),
            border=ft.border.only(bottom=ft.BorderSide(1, CorporateColors.BORDER))
        )
    
    def refresh_current_view(self):
        """Refrescar vista actual"""
        self.load_view(self.current_view)
    
    def save_current_view(self):
        """Guardar/aplicar configuración del tab actual"""
        if self.current_view == 'input':
            # Re-validar input
            if hasattr(self.tabs['input'], 'validate_input'):
                self.tabs['input'].validate_input(None)
                self.toast.success("✅ Input configuration saved")
        
        elif self.current_view == 'tables':
            # Re-validar tables
            if hasattr(self.tabs['tables'], 'validate_tables'):
                self.tabs['tables'].validate_tables(None)
                self.toast.success("✅ Tables configuration saved")
        
        elif self.current_view == 'output':
            # Re-validar output
            if hasattr(self.tabs['output'], 'validate_output'):
                self.tabs['output'].validate_output(None)
                self.toast.success("✅ Output configuration saved")
        
        # Actualizar status después de guardar
        self.update_status()
    
    def update_status(self):
        """Actualizar status bar y botón Run Pipeline"""
        # Verificar configuración
        input_ok = bool(self.state.get('validated_input', {}).get('path'))
        tables_ok = bool(self.state.get('validated_tables_path'))
        output_ok = bool(self.state.get('validated_output', {}).get('path'))
        config_complete = input_ok and tables_ok and output_ok
        
        # Actualizar status bar
        self.statusbar.update_status()
        
        # Actualizar botón Run Pipeline
        status_text = "Ready to execute" if config_complete else "Configure all parameters"
        self.sidebar.update_run_button(enabled=config_complete, status_text=status_text)


def main(page: ft.Page):
    app = ETLPipelineApp(page)


if __name__ == "__main__":
    ft.app(target=main)