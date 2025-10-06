import os
from datetime import datetime
from enum import Enum

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class Colors:
    # Códigos ANSI para colores
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Colores de texto
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Colores brillantes
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'

def get_log_path():
    # Obtener el directorio donde está logger.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(script_dir, "..", "logs")
    
    os.makedirs(logs_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return os.path.join(logs_dir, f"{ts}.txt")

class Logger:
    def __init__(self, prefix="", use_colors=True):
        self.prefix = prefix
        self.log_path = get_log_path()
        self.use_colors = use_colors
        
        # Mapeo de niveles a colores
        self.level_colors = {
            LogLevel.DEBUG: Colors.CYAN,
            LogLevel.INFO: Colors.BLUE,
            LogLevel.SUCCESS: Colors.GREEN,
            LogLevel.WARNING: Colors.YELLOW,
            LogLevel.ERROR: Colors.RED,
            LogLevel.CRITICAL: Colors.BRIGHT_RED + Colors.BOLD
        }

    def log(self, message: str, level: LogLevel = LogLevel.INFO):
        ts = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{ts}] | [{level.value}] | {self.prefix} | {message}"
        
        # Guardar en archivo SIN colores
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"{log_line}\n")
        
        # Mostrar en consola CON colores
        if self.use_colors and level in self.level_colors:
            colored_level = f"{self.level_colors[level]}[{level.value}]{Colors.RESET}"
            colored_line = f"[{ts}] | {colored_level} | {self.prefix} | {message}"
            print(colored_line)
        else:
            print(log_line)

    # Métodos de conveniencia
    def debug(self, message: str):
        self.log(message, LogLevel.DEBUG)
    
    def info(self, message: str):
        self.log(message, LogLevel.INFO)
    
    def success(self, message: str):
        self.log(message, LogLevel.SUCCESS)
    
    def warning(self, message: str):
        self.log(message, LogLevel.WARNING)
    
    def error(self, message: str):
        self.log(message, LogLevel.ERROR)
    
    def critical(self, message: str):
        self.log(message, LogLevel.CRITICAL)