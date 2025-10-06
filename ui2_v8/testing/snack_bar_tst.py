import flet as ft
import time
import asyncio

def main(page: ft.Page):
    page.title = "SnackBar Workarounds"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT  # Forzar tema claro
    
    # === WORKAROUND 1: SnackBar usando overlay (como AlertDialog) ===
    def show_snackbar_overlay(e):
        # Crear SnackBar manualmente en overlay
        snackbar_container = ft.Container(
            content=ft.Row([
                ft.Text("¡Mensaje usando overlay!", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                ft.TextButton("OK", style=ft.ButtonStyle(color=ft.Colors.WHITE)),
            ]),
            bgcolor=ft.Colors.RED_400,
            padding=ft.Padding(left=15, top=10, right=15, bottom=10),
            border_radius=5,
            margin=ft.Margin(left=10, right=10, bottom=10, top=0),
            animate_position=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            bottom=0,
            left=0,
            right=0,
        )
        
        # Agregar al overlay
        page.overlay.append(snackbar_container)
        page.update()
        
        # Auto-ocultar después de 3 segundos
        def hide_snackbar():
            time.sleep(3)
            if snackbar_container in page.overlay:
                page.overlay.remove(snackbar_container)
                page.update()
        
        import threading
        threading.Thread(target=hide_snackbar, daemon=True).start()
    
    # === WORKAROUND 2: BottomSheet como alternativa ===
    def show_bottom_sheet(e):
        def close_bs(e):
            bs.open = False
            page.update()
        
        bs = ft.BottomSheet(
            ft.Container(
                ft.Column([
                    ft.Text("Mensaje usando BottomSheet", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Esta es una alternativa al SnackBar que sí funciona"),
                    ft.Row([
                        ft.ElevatedButton("Cerrar", on_click=close_bs),
                    ], alignment=ft.MainAxisAlignment.END)
                ],
                tight=True,
                ),
                padding=20,
            ),
            open=True,
        )
        page.overlay.append(bs)
        page.update()
    
    # === WORKAROUND 3: Contenedor animado personalizado ===
    notification_container = ft.Container(
        visible=False,
        bgcolor=ft.Colors.GREEN_400,
        padding=15,
        border_radius=10,
        margin=ft.Margin(left=20, right=20, bottom=20, top=0),
        animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        animate_offset=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        offset=ft.Offset(0, 1),  # Inicialmente fuera de pantalla
    )
    
    def show_custom_notification(e):
        notification_container.content = ft.Row([
            ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE),
            ft.Text("¡Notificación personalizada!", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        ])
        notification_container.visible = True
        notification_container.offset = ft.Offset(0, 0)  # Mover a posición visible
        notification_container.opacity = 1.0
        page.update()
        
        # Auto-ocultar
        def hide_notification():
            time.sleep(3)
            notification_container.offset = ft.Offset(0, 1)
            notification_container.opacity = 0.0
            page.update()
            time.sleep(0.5)  # Esperar animación
            notification_container.visible = False
            page.update()
        
        import threading
        threading.Thread(target=hide_notification, daemon=True).start()
    
    # === WORKAROUND 4: Intentar SnackBar con configuración específica ===
    def try_snackbar_fixed(e):
        try:
            # Limpiar cualquier snackbar anterior
            page.snack_bar = None
            page.update()
            
            # Crear con configuración específica
            page.snack_bar = ft.SnackBar(
                content=ft.Text("¿Funciona con configuración específica?", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.BLUE_400,
                behavior=ft.SnackBarBehavior.FIXED,  # Comportamiento fijo
                width=400,
                action="OK",
                action_color=ft.Colors.WHITE,
                duration=5000,
                open=True,
            )
            page.update()
            
        except Exception as ex:
            print(f"Error: {ex}")
    
    # === WORKAROUND 5: Toast-like usando Container flotante ===
    toast_container = ft.Container(visible=False)
    
    def show_toast(message: str, color: str = ft.Colors.BLACK87):
        toast_container.content = ft.Container(
            content=ft.Text(message, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            bgcolor=color,
            padding=ft.Padding(left=20, top=10, right=20, bottom=10),
            border_radius=25,
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )
        toast_container.visible = True
        page.update()
        
        def hide_toast():
            time.sleep(2)
            toast_container.visible = False
            page.update()
        
        import threading
        threading.Thread(target=hide_toast, daemon=True).start()
    
    def show_toast_success(e):
        show_toast("✅ Operación exitosa", ft.Colors.GREEN_600)
    
    def show_toast_error(e):
        show_toast("❌ Error encontrado", ft.Colors.RED_600)
    
    def show_toast_info(e):
        show_toast("ℹ️ Información importante", ft.Colors.BLUE_600)
    
    # UI Principal
    content = ft.Column([
        ft.Text("🛠️ SnackBar Workarounds para Windows", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Dado que SnackBar no funciona, aquí tienes alternativas:", size=14, color=ft.Colors.GREY_700),
        ft.Divider(),
        
        # Botones de prueba
        ft.Text("Alternativas funcionales:", weight=ft.FontWeight.BOLD),
        ft.ElevatedButton(
            "1. Overlay Manual",
            on_click=show_snackbar_overlay,
            bgcolor=ft.Colors.RED_600,
            color=ft.Colors.WHITE,
            width=250
        ),
        ft.ElevatedButton(
            "2. BottomSheet",
            on_click=show_bottom_sheet,
            bgcolor=ft.Colors.ORANGE_600,
            color=ft.Colors.WHITE,
            width=250
        ),
        ft.ElevatedButton(
            "3. Notificación Animada",
            on_click=show_custom_notification,
            bgcolor=ft.Colors.GREEN_600,
            color=ft.Colors.WHITE,
            width=250
        ),
        
        ft.Divider(),
        ft.Text("Toasts personalizados:", weight=ft.FontWeight.BOLD),
        ft.Row([
            ft.ElevatedButton("✅ Éxito", on_click=show_toast_success, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
            ft.ElevatedButton("❌ Error", on_click=show_toast_error, bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
            ft.ElevatedButton("ℹ️ Info", on_click=show_toast_info, bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE),
        ], alignment=ft.MainAxisAlignment.CENTER),
        
        ft.Divider(),
        ft.Text("Intentar SnackBar original (probablemente no funcione):", weight=ft.FontWeight.BOLD),
        ft.ElevatedButton(
            "4. SnackBar con Config Específica",
            on_click=try_snackbar_fixed,
            bgcolor=ft.Colors.PURPLE_600,
            color=ft.Colors.WHITE,
            width=250
        ),
        
        # Contenedor para toasts
        toast_container,
    ],
    spacing=10,
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    scroll=ft.ScrollMode.AUTO,
    )
    
    # Stack para contenedor de notificación flotante
    page.add(
        ft.Stack([
            content,
            ft.Container(
                content=notification_container,
                alignment=ft.Alignment(-1, 1),  # Bottom left
            )
        ])
    )

if __name__ == "__main__":
    print("Iniciando workarounds para SnackBar...")
    ft.app(target=main)