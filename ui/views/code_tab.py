import flet as ft
import os
import pandas as pd
from datetime import datetime

class CodeTab:
    def __init__(self, page: ft.Page, state, toast):
        self.page = page
        self.state = state
        self.toast = toast
        
        # Containers principales
        self.main_container = ft.Container()
        self.content_column = ft.Column(spacing=20)
        
        # Rutas de archivos
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.functions_path = os.path.join(current_dir, "..", "..", "program", "transformers", "functions.py")
        self.backup_path = os.path.join(current_dir, "..", "..", "program", "transformers", "functions_backup.py")
        
        # Estado del editor
        self.code_content = ""
        self.code_editor = None
        
    def build_content(self):
        """Construir el contenido del tab Code"""
        self.content_column.controls.clear()
        
        # Verificar que existe el archivo
        if not os.path.exists(self.functions_path):
            self._build_file_not_found()
            return self._build_main_container()
        
        # Cargar contenido del archivo si no está cargado
        if not self.code_content:
            self._load_file_content()
        
        # Construir la interfaz
        self._build_code_interface()
        
        return self._build_main_container()
    
    def _build_file_not_found(self):
        """Construir vista cuando el archivo no existe"""
        self.content_column.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR, size=64, color=ft.Colors.RED_400),
                    ft.Text(
                        "❌ functions.py not found",
                        size=20,
                        color=ft.Colors.RED_600,
                        weight=ft.FontWeight.W_600
                    ),
                    ft.Text(
                        f"Expected path: {self.functions_path}",
                        size=12,
                        color=ft.Colors.GREY_600
                    ),
                    ft.Text(
                        "💡 Make sure your file structure is correct and the file exists.",
                        size=14,
                        color=ft.Colors.BLUE_600
                    )
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10),
                padding=40,
                alignment=ft.alignment.center
            )
        )
    
    def _load_file_content(self):
        """Cargar el contenido del archivo functions.py"""
        try:
            with open(self.functions_path, 'r', encoding='utf-8') as f:
                self.code_content = f.read()
        except Exception as e:
            self.code_content = ""
            if self.toast:
                self.toast.error(f"Error reading functions.py: {str(e)}")
    
    def _build_code_interface(self):
        """Construir la interfaz principal del editor"""
        # Controles superiores
        self._build_top_controls()
        
        # Estado del backup
        self._build_backup_status()
        
        # Editor de código
        self._build_code_editor()
        
        # Controles inferiores
        self._build_bottom_controls()
        
        # Información del archivo
        self._build_file_info()
        
        # Advertencia
        self._build_warning()
    
    def _build_top_controls(self):
        """Construir controles superiores"""
        top_buttons = ft.Row([
            ft.ElevatedButton(
                text="📁 Reload File",
                tooltip="Reload original file (lose unsaved changes)",
                on_click=self._reload_file,
                style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE)
            ),
            ft.ElevatedButton(
                text="💾 Create Backup",
                tooltip="Save current file as backup",
                on_click=self._create_backup,
                style=ft.ButtonStyle(bgcolor=ft.Colors.ORANGE_600, color=ft.Colors.WHITE)
            ),
            ft.ElevatedButton(
                text="🔄 Restore Backup",
                tooltip="Restore from backup file",
                on_click=self._restore_backup,
                style=ft.ButtonStyle(bgcolor=ft.Colors.PURPLE_600, color=ft.Colors.WHITE)
            ),
        ], spacing=10)
        
        self.content_column.controls.append(
            ft.Container(content=top_buttons, margin=ft.margin.only(bottom=10))
        )
    
    def _build_backup_status(self):
        """Construir indicador de estado del backup"""
        backup_exists = os.path.exists(self.backup_path)
        
        if backup_exists:
            backup_time = os.path.getmtime(self.backup_path)
            backup_date = datetime.fromtimestamp(backup_time).strftime('%Y-%m-%d %H:%M:%S')
            
            status_container = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.BACKUP, color=ft.Colors.GREEN),
                    ft.Text(f"📋 Backup available from: {backup_date}", color=ft.Colors.GREEN_700)
                ]),
                padding=10,
                bgcolor=ft.Colors.GREEN_50,
                border_radius=8,
                border=ft.border.all(1, ft.Colors.GREEN_200)
            )
        else:
            status_container = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.WARNING, color=ft.Colors.ORANGE),
                    ft.Text("⚠️ No backup file found", color=ft.Colors.ORANGE_700)
                ]),
                padding=10,
                bgcolor=ft.Colors.ORANGE_50,
                border_radius=8,
                border=ft.border.all(1, ft.Colors.ORANGE_200)
            )
        
        self.content_column.controls.append(status_container)
    
    def _build_code_editor(self):
        """Construir el editor de código"""
        # Header del editor
        editor_header = ft.Container(
            content=ft.Text("📝 Code Editor", size=18, weight=ft.FontWeight.W_600),
            margin=ft.margin.only(top=15, bottom=5)
        )
        
        # Editor de texto
        self.code_editor = ft.TextField(
            value=self.code_content,
            multiline=True,
            min_lines=20,
            max_lines=100,
            expand=True,
            text_style=ft.TextStyle(font_family="Courier New", size=12, color=ft.Colors.WHITE),
            border=ft.InputBorder.OUTLINE,
            border_color=ft.Colors.GREY_400,
            focused_border_color=ft.Colors.BLUE_400,
            on_change=self._on_code_change
        )
        
        editor_container = ft.Container(
            content=self.code_editor,
            height=500,
            border_radius=8,
            padding=5,
            expand=True,
            bgcolor=ft.Colors.GREY_900,  # fondo oscuro
        )
        
        self.content_column.controls.extend([
            editor_header,
            editor_container
        ])
    
    def _build_bottom_controls(self):
        """Construir controles inferiores"""
        bottom_buttons = ft.Row([
            ft.ElevatedButton(
                text="Validate Syntax",
                icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                on_click=self._validate_syntax,
                style=ft.ButtonStyle(bgcolor=ft.Colors.INDIGO_600, color=ft.Colors.WHITE)
            ),
            ft.ElevatedButton(
                text="Save Changes",
                icon=ft.Icons.SAVE,
                on_click=self._save_changes,
                style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE)
            ),
        ], spacing=10)
        
        self.content_column.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text("🔧 Actions", size=16, weight=ft.FontWeight.W_600),
                    bottom_buttons
                ], spacing=10),
                margin=ft.margin.only(top=20)
            )
        )
    
    def _build_file_info(self):
        """Construir información del archivo"""
        try:
            file_stats = os.stat(self.functions_path)
            file_size = file_stats.st_size
            file_modified = datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            lines_count = len(self.code_content.split('\n'))
            chars_count = len(self.code_content)
            
            info_content = ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text(f"📁 File size: {file_size} bytes", size=12),
                        ft.Text(f"📝 Lines: {lines_count:,}", size=12),
                    ], spacing=5),
                    ft.Column([
                        ft.Text(f"🔤 Characters: {chars_count:,}", size=12),
                        ft.Text(f"🕒 Last modified: {file_modified}", size=12),
                    ], spacing=5)
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
            ])
            
            info_expander = ft.ExpansionTile(
                title=ft.Text("📊 File Information"),
                subtitle=ft.Text("Click to view file details"),
                leading=ft.Icon(ft.Icons.INFO_OUTLINE),
                controls=[ft.Container(content=info_content, padding=15)]
            )
            
            self.content_column.controls.append(info_expander)
            
        except Exception as e:
            if self.toast:
                self.toast.error(f"Error getting file info: {str(e)}")
    
    def _build_warning(self):
        """Construir advertencia importante"""
        warning_container = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.WARNING, color=ft.Colors.AMBER),
                ft.Text(
                    "⚠️ Important: Changes will affect the next pipeline execution. Test your changes carefully!",
                    size=13,
                    color=ft.Colors.AMBER_800,
                    weight=ft.FontWeight.W_500
                )
            ]),
            padding=15,
            bgcolor=ft.Colors.AMBER_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.AMBER_200),
            margin=ft.margin.only(top=20)
        )
        
        self.content_column.controls.append(warning_container)
    
    def _build_main_container(self):
        """Construir container principal"""
        self.main_container = ft.Container(
            content=ft.Column([
                ft.Text("🔧 Code Section", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(height=1, color=ft.Colors.GREY_300),
                ft.Container(
                    content=self.content_column,
                    expand=True
                )
            ],scroll=ft.ScrollMode.AUTO),
            padding=20,
            expand=True
        )
        
        return self.main_container
    
    def _on_code_change(self, e):
        """Manejar cambios en el editor"""
        self.code_content = e.control.value
    
    def _reload_file(self, e):
        """Recargar archivo original"""
        try:
            with open(self.functions_path, 'r', encoding='utf-8') as f:
                new_content = f.read()
            
            self.code_content = new_content
            self.code_editor.value = new_content
            self.page.update()
            
            if self.toast:
                self.toast.success("✅ File reloaded!")
                
        except Exception as error:
            if self.toast:
                self.toast.success(f"❌ Error reloading: {str(error)}")
    
    def _create_backup(self, e):
        """Crear backup del archivo actual"""
        try:
            with open(self.functions_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            with open(self.backup_path, 'w', encoding='utf-8') as f:
                f.write(current_content)
            
            if self.toast:
                self.toast.success("✅ Backup created successfully!")
            
            # Refrescar para mostrar nuevo estado del backup
            self.refresh_content()
            
        except Exception as error:
            if self.toast:
                self.toast.error(f"❌ Error creating backup: {str(error)}")
    
    def _restore_backup(self, e):
        """Restaurar desde backup"""
        if not os.path.exists(self.backup_path):
            if self.toast:
                self.toast.error("❌ No backup file to restore!")
            return
        
        try:
            with open(self.backup_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            
            self.code_content = backup_content
            self.code_editor.value = backup_content
            self.page.update()
            
            if self.toast:
                self.toast.success("✅ Backup restored to editor!")
                
        except Exception as error:
            if self.toast:
                self.toast.error(f"❌ Error restoring backup: {str(error)}")
    
    def _validate_syntax(self, e):
        """Validar sintaxis del código"""
        try:
            compile(self.code_content, '<string>', 'exec')
            if self.toast:
                self.toast.success("✅ Syntax is valid! Ready to save.")
                
        except SyntaxError as error:
            error_msg = f"❌ Syntax Error on line {error.lineno}: {error.msg}"
            if error.text:
                error_msg += f"\n📍 Code: {error.text.strip()}"
            
            if self.toast:
                self.toast.error(error_msg)
                
        except Exception as error:
            if self.toast:
                self.toast.error(f"❌ Compilation Error: {str(error)}")
    
    def _save_changes(self, e):
        """Guardar cambios en el archivo"""
        # Validar sintaxis primero
        try:
            compile(self.code_content, '<string>', 'exec')
        except SyntaxError as error:
            error_msg = f"❌ Cannot save: Syntax errors found!\n📍 Line {error.lineno}: {error.msg}"
            if self.toast:
                self.toast.error(error_msg)
            return
        except Exception as error:
            if self.toast:
                self.toast.error(f"❌ Cannot save: Compilation error: {str(error)}")
            return
        
        # Si la validación pasa, guardar
        try:
            with open(self.functions_path, 'w', encoding='utf-8') as f:
                f.write(self.code_content)
            
            if self.toast:
                self.toast.success("🎉 Changes saved successfully!")
            
            # Refrescar información del archivo
            self.refresh_content()
            
        except Exception as error:
            if self.toast:
                self.toast.error(f"❌ Error saving file: {str(error)}")
    
    def _show_syntax_validation_dialog(self, is_valid, error_msg=None):
        """Mostrar diálogo con resultado de validación"""
        if is_valid:
            dialog_content = ft.Column([
                ft.Icon(ft.Icons.CHECK_CIRCLE, size=48, color=ft.Colors.GREEN),
                ft.Text("✅ Syntax is valid!", size=16, weight=ft.FontWeight.W_600),
                ft.Text("Ready to save changes.", size=14)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
            title_color = ft.Colors.GREEN
        else:
            dialog_content = ft.Column([
                ft.Icon(ft.Icons.ERROR, size=48, color=ft.Colors.RED),
                ft.Text("❌ Syntax Error Found!", size=16, weight=ft.FontWeight.W_600),
                ft.Container(
                    content=ft.Text(error_msg, size=12, selectable=True),
                    padding=10,
                    bgcolor=ft.Colors.RED_50,
                    border_radius=8,
                    width=400
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
            title_color = ft.Colors.RED
        
        dialog = ft.AlertDialog(
            title=ft.Text("Syntax Validation", color=title_color),
            content=ft.Container(content=dialog_content, width=450, height=200),
            actions=[
                ft.TextButton("OK", on_click=lambda _: self._close_dialog())
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _close_dialog(self):
        """Cerrar diálogo activo"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
    
    def refresh_content(self):
        """Método para refrescar el contenido"""
        self.build_content()
        self.page.update()
