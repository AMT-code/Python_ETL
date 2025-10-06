class AppState:
    """Manejo simple del estado de la aplicación"""
    
    def __init__(self):
        self.data = {
            'validated_input': {},
            'validated_output': {},
            'validated_tables_path': '',
            'csv_files': [],
            'current_tab': 0
        }
    
    def get(self, key, default=None):
        """Obtener valor del estado"""
        return self.data.get(key, default)
    
    def set(self, key, value):
        """Establecer valor en el estado"""
        self.data[key] = value
    
    def update(self, updates_dict):
        """Actualizar múltiples valores"""
        self.data.update(updates_dict)
    
    def reset_input(self):
        """Limpiar estado de input"""
        self.data['validated_input'] = {}
    
    def reset_tables(self):
        """Limpiar estado de tables"""
        self.data['validated_tables_path'] = ''
        self.data['csv_files'] = []
    
    def reset_output(self):
        """Limpiar estado de output"""
        self.data['validated_output'] = {}