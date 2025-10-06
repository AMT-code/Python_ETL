from .functions import *
import os

def apply_transformations(df, config, logger, script_dir):
    # Guardar el prefix original
    original_prefix = logger.prefix
    # Cambiar al prefix específico del módulo
    logger.prefix = "Engine"

    logger.info("Beginning of transformations")

    # Construir ruta relativa al script
    tables_path = os.path.join(script_dir, "..", config["tables_path"])
    
    df = run_business_rules(df, tables_path, logger)

    logger.info("End of transformations")
    
    # Restaurar prefix original
    logger.prefix = original_prefix
    return df
