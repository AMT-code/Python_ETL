import flet as ft
import os
import glob
import datetime

class LogTab:
    """Tab para leer y mostrar archivos de log del pipeline"""
    
    def __init__(self, page, state, toast):
        self.page = page
        self.state = state
        self.toast = toast
        
        # Referencias a elementos de UI
        self.log_files_dropdown = ft.Ref[ft.Dropdown]()
        self.log_content_text = ft.Ref[ft.Text]()
        self.log_container = ft.Ref[ft.Container]()
        self.refresh_button = ft.Ref[ft.ElevatedButton]()
        self.filter_checkbox = ft.Ref[ft.Checkbox]()
        self.level_filter_dropdown = ft.Ref[ft.Dropdown]()
        self.line_numbers_checkbox = ft.Ref[ft.Checkbox]()
        self.stats_container = ft.Ref[ft.Container]()
        
        # Estado interno
        self.current_log_content = ""
        self.log_dir = self.get_log_directory()
    
    def get_log_directory(self):
        """Obtener directorio de logs"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "..", "..", "logs")
    
    def build_content(self):
        """Construir el contenido del tab"""
        return ft.Container(
            content=ft.Column([
                ft.Text("Pipeline Logs", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),

                # Selector de archivo de log y refresh button
                ft.Row([
                    ft.Dropdown(
                        label="Select a log file",
                        hint_text="No log files available",
                        width=300,
                        on_change=self.log_file_selected,
                        ref=self.log_files_dropdown
                    ),
                    ft.ElevatedButton(
                        "Refresh",
                        icon=ft.Icons.REFRESH,
                        on_click=self.refresh_log_files,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.BLUE_GREY
                        ),
                        ref=self.refresh_button
                    )
                ], spacing=10),

                # Controles de visualización - Filtros, dropdown levels, line numbers
                ft.Row([
                    ft.Checkbox(
                        label="Filter by log level",
                        on_change=self.toggle_filter,
                        ref=self.filter_checkbox
                    ),
                    ft.Dropdown(
                        label="Levels",
                        width=200,
                        visible=False,
                        options=[
                            ft.dropdown.Option("ALL", "All levels"),
                            ft.dropdown.Option("DEBUG", "Debug"),
                            ft.dropdown.Option("INFO", "Info"),
                            ft.dropdown.Option("SUCCESS", "Success"),
                            ft.dropdown.Option("WARNING", "Warning"),
                            ft.dropdown.Option("ERROR", "Error"),
                            ft.dropdown.Option("CRITICAL", "Critical"),
                        ],
                        value="ALL",
                        on_change=self.apply_filter,
                        ref=self.level_filter_dropdown
                    ),
                    ft.Checkbox(
                        label="Show line numbers",
                        on_change=self.toggle_line_numbers,
                        ref=self.line_numbers_checkbox
                    )
                ], spacing=10),
                
                # Container principal de contenido del log
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Select a log file to view its contents or refresh the list",
                            color=ft.Colors.GREY_100,
                            size=14
                        )
                    ], scroll=ft.ScrollMode.AUTO),
                    expand=True,
                    padding=15,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    bgcolor=ft.Colors.GREY_700,
                    ref=self.log_container
                ),
                
                # Estadísticas del log (inicialmente oculto)
                ft.Container(
                    visible=False,
                    ref=self.stats_container
                )
                
            ], spacing=15, expand=True),
            padding=20
        )
    
    def refresh_log_files(self, e=None):
        """Buscar archivos de log y actualizar dropdown"""
        if not os.path.exists(self.log_dir):
            self.log_files_dropdown.current.options = []
            self.log_files_dropdown.current.hint_text = "Log directory doesn't exist yet"
            self.log_files_dropdown.current.value = None
            self.show_no_logs_message()
            self.page.update()
            return
        
        # Buscar archivos .txt en el directorio de logs
        log_files = glob.glob(os.path.join(self.log_dir, "*.txt"))
        
        if not log_files:
            self.log_files_dropdown.current.options = []
            self.log_files_dropdown.current.hint_text = "No log files found"
            self.log_files_dropdown.current.value = None
            self.show_no_logs_message()
            self.page.update()
            return
        
        # Ordenar por fecha de modificación (más recientes primero)
        log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        log_filenames = [os.path.basename(f) for f in log_files]
        
        # Actualizar dropdown
        self.log_files_dropdown.current.options = [
            ft.dropdown.Option(filename, filename) for filename in log_filenames
        ]
        self.log_files_dropdown.current.hint_text = f"{len(log_filenames)} log files available"
        
        # Si no hay selección, seleccionar el más reciente
        if not self.log_files_dropdown.current.value and log_filenames:
            self.log_files_dropdown.current.value = log_filenames[0]
            self.load_log_file(log_filenames[0])
        
        self.page.update()
    
    def show_no_logs_message(self):
        """Mostrar mensaje cuando no hay logs"""
        self.log_container.current.content = ft.Column([
            ft.Icon(ft.Icons.DESCRIPTION, size=64, color=ft.Colors.GREY_400),
            ft.Text("No log files found", size=16, color=ft.Colors.GREY_600),
            ft.Text("Run the pipeline first to generate logs", size=12, color=ft.Colors.GREY_500)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
        
        self.stats_container.current.visible = False
    
    def log_file_selected(self, e):
        """Manejar selección de archivo de log"""
        selected_file = e.control.value
        if selected_file:
            self.load_log_file(selected_file)
    
    def load_log_file(self, filename):
        """Cargar y mostrar contenido del archivo de log"""
        log_path = os.path.join(self.log_dir, filename)
        
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                self.current_log_content = f.read()
            
            # Obtener estadísticas del archivo
            file_stats = os.stat(log_path)
            file_time = datetime.datetime.fromtimestamp(file_stats.st_mtime)
            file_size = file_stats.st_size
            
            # Mostrar información del archivo y contenido
            self.display_log_content()
            self.show_log_stats(filename, file_time, file_size)
            
            self.toast.success(f"Log file loaded: {filename}")
            
        except Exception as ex:
            self.toast.error(f"Error reading log file: {str(ex)}")
            self.show_error_message(str(ex))
    
    def display_log_content(self):
        """Mostrar el contenido del log con filtros aplicados"""
        content = self.current_log_content
        
        # Aplicar filtro de nivel si está habilitado
        if self.filter_checkbox.current.value:
            selected_level = self.level_filter_dropdown.current.value
            if selected_level != "ALL":
                filtered_lines = []
                for line in content.split('\n'):
                    if f"[{selected_level}]" in line:
                        filtered_lines.append(line)
                content = '\n'.join(filtered_lines)
        
        # Agregar números de línea si está habilitado
        if self.line_numbers_checkbox.current.value and content:
            lines = content.split('\n')
            numbered_lines = [f"{i+1:4d}: {line}" for i, line in enumerate(lines)]
            content = '\n'.join(numbered_lines)
        
        # Crear elementos de texto por línea para mejor renderizado
        log_widgets = []
        if content:
            lines = content.split('\n')
            for line in lines[:500]:  # Limitar para performance
                log_widgets.append(self.create_log_line_widget(line))
        else:
            log_widgets.append(ft.Text("No content matches the current filter", 
                                    color=ft.Colors.GREY_500, size=12))
        
        # Actualizar container
        self.log_container.current.content = ft.Column(
            controls=log_widgets,
            scroll=ft.ScrollMode.AUTO,
            spacing=1
        )
        
        self.page.update()
    
    def create_log_line_widget(self, line: str) -> ft.Text:
        """Crear widget para una línea de log con colores"""
        color = ft.Colors.WHITE
        
        # Determinar color según nivel
        if "[ERROR]" in line or "[CRITICAL]" in line:
            color = ft.Colors.RED_300
        elif "[WARNING]" in line:
            color = ft.Colors.ORANGE_300
        elif "[SUCCESS]" in line:
            color = ft.Colors.GREEN_300
        elif "[INFO]" in line:
            color = ft.Colors.LIGHT_BLUE_300
        elif "[DEBUG]" in line:
            color = ft.Colors.YELLOW_200
        
        return ft.Text(
            line,
            color=color,
            size=11,
            font_family="Consolas,Monaco,monospace",
            selectable=True
        )
    
    def show_log_stats(self, filename: str, file_time: datetime.datetime, file_size: int):
        """Mostrar estadísticas del archivo de log"""
        lines = self.current_log_content.split('\n')
        total_lines = len(lines)
        
        # Contar por nivel
        level_counts = {}
        for level in ['DEBUG', 'INFO', 'SUCCESS', 'WARNING', 'ERROR', 'CRITICAL']:
            count = sum(1 for line in lines if f"[{level}]" in line)
            if count > 0:
                level_counts[level] = count
        
        # Crear widgets de estadísticas
        stats_widgets = [
            ft.Text(f"File: {filename}", weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Text(f"Created: {file_time.strftime('%Y-%m-%d %H:%M:%S')}", size=12, color=ft.Colors.GREY_200),
                ft.Text(f"Size: {file_size} bytes", size=12, color=ft.Colors.GREY_200),
                ft.Text(f"Lines: {total_lines}", size=12, color=ft.Colors.GREY_200),
            ], spacing=20),
        ]
        
        if level_counts:
            level_texts = [f"{level}: {count}" for level, count in level_counts.items()]
            stats_widgets.append(
                ft.Text(f"Levels: {', '.join(level_texts)}", size=12, color=ft.Colors.GREY_300)
            )
        
        self.stats_container.current.content = ft.Container(
            content=ft.Column(stats_widgets, spacing=5),
            padding=10,
            border=ft.border.all(1, ft.Colors.GREY_600),
            border_radius=8,
            bgcolor=ft.Colors.GREY_700
        )
        self.stats_container.current.visible = True
        
        self.page.update()
    
    def show_error_message(self, error_message: str):
        """Mostrar mensaje de error"""
        self.log_container.current.content = ft.Column([
            ft.Icon(ft.Icons.ERROR, size=64, color=ft.Colors.RED_400),
            ft.Text("Error loading log file", size=16, color=ft.Colors.RED_400),
            ft.Text(error_message, size=12, color=ft.Colors.GREY_400)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
        
        self.stats_container.current.visible = False
        self.page.update()
    
    def toggle_filter(self, e):
        """Toggle filtro de nivel"""
        is_enabled = e.control.value
        self.level_filter_dropdown.current.visible = is_enabled
        
        if not is_enabled:
            self.level_filter_dropdown.current.value = "ALL"
        
        self.page.update()
        
        # Re-aplicar display si hay contenido cargado
        if self.current_log_content:
            self.display_log_content()
    
    def apply_filter(self, e):
        """Aplicar filtro de nivel"""
        if self.current_log_content:
            self.display_log_content()
    
    def toggle_line_numbers(self, e):
        """Toggle números de línea"""
        if self.current_log_content:
            self.display_log_content()
    
    def initialize(self):
        """Inicializar el tab (llamar después de que se construya la UI)"""
        self.refresh_log_files()