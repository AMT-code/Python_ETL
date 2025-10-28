import flet as ft
import os
import pandas as pd


class OutputsTab:
    """Tab 3: Output Parameters """

    def __init__(self, page, state, toast, update_sidebar=None):
        self.page = page
        self.state = state
        self.toast = toast
        self.update_sidebar = update_sidebar

        # Referencias para Tab 3 - Output
        self.output_path_field = ft.Ref[ft.TextField]()
        self.csv_checkbox = ft.Ref[ft.Checkbox]()
        self.rpt_checkbox = ft.Ref[ft.Checkbox]()
        self.output_status = ft.Ref[ft.Text]()

    def build_content(self):
        """Construir el contenido del tab"""
        return ft.Container(
            content=ft.Column([
                ft.Text("Output Configuration", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.TextField(
                    label="Output file location",
                    hint_text="e.g., outputs/results.csv, C:/path/to/output.rpt",
                    helper_text="Where to save the processed file",
                    expand=False,
                    on_change=self.validate_output,
                    ref=self.output_path_field
                ),
                
                ft.Row([ft.Text("File Format", size=16, weight=ft.FontWeight.BOLD),
                    ft.Checkbox(
                        label="CSV (.csv)",
                        value=False,
                        on_change=self.on_format_change,
                        ref=self.csv_checkbox
                    ),
                    ft.Checkbox(
                        label="RPT (.rpt)",
                        value=False,
                        on_change=self.on_format_change,
                        ref=self.rpt_checkbox
                    ),
                ]),

                ft.Text("", color=ft.Colors.BLUE_600, ref=self.output_status),
            ], spacing=20),
            padding=20
        )

    def on_format_change(self, e):
    # Solo uno puede estar seleccionado
        if e.control == self.csv_checkbox.current and e.control.value:
            self.rpt_checkbox.current.value = False
        elif e.control == self.rpt_checkbox.current and e.control.value:
            self.csv_checkbox.current.value = False
        self.page.update()
        self.validate_output(None)

    def validate_output(self, e):
        output_path = self.output_path_field.current.value
        csv_selected = self.csv_checkbox.current.value
        rpt_selected = self.rpt_checkbox.current.value

        if csv_selected and rpt_selected:
            self.output_status.current.value = "❌ Please select only one file format"
            self.state.reset_output()
        elif csv_selected:
            selected_format = ".csv"
        elif rpt_selected:
            selected_format = ".rpt"
        else:
            selected_format = None

        if output_path and selected_format:
            # Agregar extensión si falta
            if not output_path.lower().endswith(selected_format):
                base_path = os.path.splitext(output_path)[0]
                final_output_path = base_path + selected_format
            else:
                final_output_path = output_path
            
            output_dir = os.path.dirname(final_output_path)
            if output_dir and not os.path.exists(output_dir):
                self.output_status.current.value = f"⚠️ Directory '{output_dir}' doesn't exist. It will be created when running the pipeline."
            else:
                self.output_status.current.value = f"✅ Output configured: {final_output_path} ({selected_format.upper()})"
            self.state.set('validated_output', {
                "path": final_output_path,
                "file_type": selected_format
            })
        elif output_path and not selected_format:
            self.output_status.current.value = "⚠️ Please select a file format"
            self.state.reset_output()
        elif selected_format and not output_path:
            self.output_status.current.value = "⚠️ Please enter an output path"
            self.state.reset_output()
        else:
            self.output_status.current.value = "🚧 Configure output file and format"
            self.state.reset_output()

        self.update_sidebar()
        self.page.update()
