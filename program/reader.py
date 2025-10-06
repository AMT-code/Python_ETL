import pandas as pd
import os

def read_input(path, file_config=None):
    """
    Lee un archivo de input usando la configuración especificada
    
    Args:
        path (str): Ruta al archivo
        file_config (dict, optional): Configuración del archivo con 'type' y 'delimiter'
    
    Returns:
        pandas.DataFrame: DataFrame con los datos leídos
    """
    
    # Si no hay configuración específica, usar auto-detect por extensión
    if file_config is None or file_config.get('type') == 'auto':
        ext = os.path.splitext(path)[-1].lower()
        
        if ext in [".xlsx", ".xls"]:
            return pd.read_excel(path)
        elif ext == ".csv":
            return pd.read_csv(path)
        elif ext == ".parquet":
            return pd.read_parquet(path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    # Usar configuración específica
    file_type = file_config.get('type')
    
    if file_type == 'excel':
        return pd.read_excel(path)
    
    elif file_type == 'csv':
        # Usar delimitador específico si está configurado
        delimiter = file_config.get('delimiter', ',')
        return pd.read_csv(path, sep=delimiter)
    
    elif file_type == 'parquet':
        return pd.read_parquet(path)
    
    else:
        raise ValueError(f"Unsupported file type in config: {file_type}")