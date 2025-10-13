import pandas as pd
import numpy as np
import os
import time
from contextlib import contextmanager

def run_business_rules(df, tables_path, logger, audit=None):
    # Guardar el prefix original
    original_prefix = logger.prefix
    # Cambiar al prefix específico del módulo
    logger.prefix = "Functions"

    df = df.copy()

    logger.debug(f"input data columns -> {df.columns.tolist()} ")

    # Helper: context manager para tracking automático
    @contextmanager
    def track(description):
        """Context manager para medir tiempo de un bloque de código"""
        start = time.time()
        try:
            yield
        finally:
            elapsed = time.time() - start
            if audit:
                audit.log_transformation(description, elapsed)
    
    # =========================================================================
    # COMPLEJIDAD: SIMPLE
    # - Solo renombres y asignaciones directas
    # - Sin merges, sin conversiones de fechas complejas
    # - Operaciones muy rápidas
    # =========================================================================

    # Renombrar columnas principales
    with track("Column renaming (batch 1)"):
        df = df.rename(columns={
            "Sex": "SEX",
            "tipo_producto": "PROD_TYPE",
            "sum_insured": "SUM_ASSURED",
            "annual_prem": "ANNUAL_PREM",
            "reins_name": "REINS",
            "comission_precentage": "COMM_PC"
        })
        logger.success("Main columns renamed")

    # Mapeo simple de sexo
    with track("SEX value mapping"):
        df["SEX"] = df["SEX"].map({"Female": 0, "Male": 1})
        logger.success("SEX mapped to numeric")

    # Mapeo simple de producto
    with track("PROD_TYPE value mapping"):
        df["PROD_TYPE"] = df["PROD_TYPE"].map({"Vitalicio": 1, "Temporal": 2})
        logger.success("PROD_TYPE mapped to numeric")

    # Asignación simple de POL_TERM_Y (sin merge)
    with track("POL_TERM_Y simple assignment"):
        df["POL_TERM_Y"] = np.where(df["PROD_TYPE"] == 1, 100, 20)
        logger.success("POL_TERM_Y assigned")

    # Mapeo simple de frecuencia
    with track("PREM_FREQ mapping"):
        freq_mapping = {
            "Mensual": 12,
            "Trimestral": 4,
            "Semestral": 2,
            "Anual": 1
        }
        df["PREM_FREQ"] = df["prem_frecuency"].map(freq_mapping)
        logger.success("PREM_FREQ mapped")

    # Selección de columnas de output
    with track("Output column selection"):
        output_vars = ["ID", "PROD_TYPE", "SEX", "POL_TERM_Y", "SUM_ASSURED", 
                        "ANNUAL_PREM", "PREM_FREQ", "REINS", "COMM_PC"]
        logger.info(f"Output variable list: {', '.join(map(str, output_vars))}")
        df_out = df[output_vars]

    # Restaurar prefix original
    logger.prefix = original_prefix
    return df_out