import flet as ft
import pandas as pd
import os

def create_data_preview(df: pd.DataFrame, file_path: str, file_type: str, max_rows: int = 10):
    """Crear preview de datos reutilizable para diferentes tabs"""
    
    # Información del archivo
    file_info = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text(f"📁 File: {os.path.basename(file_path)}", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(f"📊 Shape: {df.shape[0]:,} rows × {df.shape[1]} columns", size=14),
            ]),
            ft.Row([
                ft.Text(f"📋 Type: {file_type.upper()}", size=12, color=ft.Colors.BLUE_600),
                ft.Text(f"💾 Size: {os.path.getsize(file_path) / 1024:.1f} KB", size=12, color=ft.Colors.BLUE_600),
            ])
        ]),
        padding=10,
        bgcolor=ft.Colors.BLUE_50,
        border_radius=8
    )
    
    # Crear tabla de datos con scroll horizontal y vertical
    preview_rows = []
    
    # Data rows (máximo según max_rows)
    for i in range(min(max_rows, len(df))):
        row_cells = []
        for col in df.columns:
            value = str(df.iloc[i][col])
            # Truncar valores muy largos para mejor visualización
            if len(value) > 50:
                value = value[:47] + "..."
            row_cells.append(ft.DataCell(ft.Text(value, size=12)))
        preview_rows.append(ft.DataRow(cells=row_cells))
    
    # Crear tabla
    data_table = ft.DataTable(
        columns=[ft.DataColumn(ft.Text(str(col), weight=ft.FontWeight.BOLD, size=10)) for col in df.columns],
        rows=preview_rows,
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=8,
        data_row_max_height=35,
    )
    
    # Container scrolleable en ambas direcciones
    scrollable_table = ft.Container(
        content=ft.Row([
            data_table
        ], scroll=ft.ScrollMode.ALWAYS),  # Scroll horizontal
        height=460,  # Altura fija mayor para acomodar más filas
        expand=True,  # Expandir horizontalmente
        padding=10,
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=8,
    )
    
    return ft.Column([
        file_info,
        scrollable_table,
    ], spacing=10, expand=True)

def create_config_item(label: str, value: str):
    """Crear un item de configuración para el sidebar"""
    icon = "✅" if "❌" not in value else "❌"
    color = ft.Colors.GREEN_600 if "❌" not in value else ft.Colors.RED_600
    
    return ft.Row([
        ft.Text(f"{label}:", weight=ft.FontWeight.BOLD, size=12),
        ft.Text(f"{icon} {value.replace('❌ ', '').replace('✅ ', '')}", 
                color=color, size=12, expand=True)
    ], tight=True)