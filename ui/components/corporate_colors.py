"""
Paleta de colores corporativa para ETL Pipeline Tool
Estilo: Profesional, sobrio, tipo aplicación de escritorio
"""

class CorporateColors:
    """Paleta de colores corporativa"""
    
    # Colores principales
    PRIMARY = "#1E3A8A"           # Azul oscuro corporativo
    PRIMARY_LIGHT = "#3B82F6"     # Azul claro (hover, selección)
    PRIMARY_DARK = "#1E293B"      # Azul muy oscuro
    
    # Colores secundarios
    SECONDARY = "#64748B"         # Gris azulado
    SECONDARY_LIGHT = "#94A3B8"   # Gris claro
    
    # Fondos
    BACKGROUND = "#F8FAFC"        # Gris muy claro (fondo general)
    SURFACE = "#FFFFFF"           # Blanco (cards, contenedores)
    SIDEBAR_BG = "#0F172A"        # Gris oscuro (sidebar)
    
    # Texto
    TEXT_PRIMARY = "#0F172A"      # Texto principal (casi negro)
    TEXT_SECONDARY = "#64748B"    # Texto secundario (gris)
    TEXT_DISABLED = "#94A3B8"     # Texto deshabilitado
    
    # Bordes y separadores
    BORDER = "#E2E8F0"            # Bordes sutiles
    DIVIDER = "#CBD5E1"           # Divisores
    
    # Estados
    SUCCESS = "#059669"           # Verde (éxito)
    WARNING = "#D97706"           # Naranja (advertencia)
    ERROR = "#DC2626"             # Rojo (error)
    INFO = "#0EA5E9"              # Azul claro (información)
    
    # Interacciones
    HOVER = "#F1F5F9"             # Hover sutil
    SELECTED = "#EFF6FF"          # Elemento seleccionado
    FOCUS = "#DBEAFE"             # Focus
    
    # Overlay
    OVERLAY_BG = "#00000080"      # Negro semi-transparente (overlays)
    
    @classmethod
    def with_opacity(cls, color, opacity):
        """Helper para agregar opacidad a un color"""
        import flet as ft
        return ft.Colors.with_opacity(opacity, color)