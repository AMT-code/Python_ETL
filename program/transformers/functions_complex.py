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
    # COMPLEJIDAD: COMPLEX
    # - Incluye todas las transformaciones de MEDIUM
    # - Agrega validaciones, cálculos derivados y agregaciones
    # - Más merges y operaciones condicionales complejas
    # =========================================================================

    # Mapear sexo
    with track("SEX mapping"):
        df["Sex"] = df["Sex"].map({"Female": 0, "Male": 1})
        df = df.rename(columns={"Sex":"SEX"})
        logger.success("SEX mapped")

    # Validación de datos de entrada
    with track("Input data validation"):
        # Validar que no haya valores nulos en columnas críticas
        critical_cols = ['ID', 'SEX', 'inception_date', 'birth_date']
        null_counts = df[critical_cols].isnull().sum()
        if null_counts.sum() > 0:
            logger.warning(f"Found null values in critical columns")
        logger.success("Input validation completed")

    # pol_term_y con merge
    with track("POL_TERM_Y assignment + merge"):
        idx_map = pd.read_csv(os.path.join(tables_path, "temp_idx_map.csv"))
        df = df.merge(idx_map, how="left", left_on="temp_idx", right_on="idx")
        df.loc[df["tipo_producto"] == "Vitalicio", "POL_TERM_Y"] = 100
        logger.success("POL_TERM_Y correctly assigned")

    # prod type column
    with track("PROD_TYPE mapping"):
        df = df.rename(columns={"tipo_producto":"PROD_TYPE"})
        df["PROD_TYPE"] = df["PROD_TYPE"].map({"Vitalicio":1, "Temporal":2})
        logger.success("PROD_TYPE column correctly assigned")

    # date conversions (más elaboradas)
    with track("Date conversions and calculations"):
        df["inception_date"] = pd.to_datetime(df["inception_date"], format='%d/%m/%Y')
        df["birth_date"] = pd.to_datetime(df["birth_date"], format='%d/%m/%Y')
        df["ENTRY_YEAR"] = df["inception_date"].dt.year
        df["ENTRY_MTH"] = df["inception_date"].dt.month
        df["ENTRY_DAY"] = df["inception_date"].dt.day  # Extra
        df["AGE_AT_ENTRY"] = (df["inception_date"] - df["birth_date"]).dt.days // 365
        logger.success("date conversions correctly done")

    # Cálculo de edad actual y duración del contrato
    with track("Age and duration calculations"):
        from datetime import datetime
        current_date = datetime.now()
        df["CURRENT_AGE"] = ((current_date - df["birth_date"]).dt.days // 365)
        df["CONTRACT_DURATION_YEARS"] = ((current_date - df["inception_date"]).dt.days // 365)
        logger.success("Age and duration calculated")

    # Clasificación por rangos de edad
    with track("Age range classification"):
        df["AGE_RANGE"] = pd.cut(df["AGE_AT_ENTRY"], 
                                    bins=[0, 25, 35, 45, 55, 65, 100],
                                    labels=["0-25", "26-35", "36-45", "46-55", "56-65", "65+"])
        logger.success("Age ranges classified")

    # sum assured
    with track("SUM_ASSURED assignment"):
        df["SUM_ASSURED"] = df["sum_insured"]
        logger.success("SUM_ASSURED column correctly assigned")

    # annual prem
    with track("ANNUAL_PREM assignment"):
        df["ANNUAL_PREM"] = df["annual_prem"]
        logger.success("ANNUAL_PREM column correctly assigned")

    # Cálculo de ratio prima/suma asegurada
    with track("Premium ratio calculation"):
        df["PREM_SA_RATIO"] = (df["ANNUAL_PREM"] / df["SUM_ASSURED"] * 100).round(4)
        logger.success("Premium ratio calculated")

    # tariff grp
    with track("TARIFF merge"):
        tariff_map = pd.read_csv(os.path.join(tables_path, "tariff_map.csv"))
        df = df.merge(tariff_map, on="tariff_grp", how="left")
        logger.success("TARIFF column correctly assigned")

    # currency map
    with track("CURRENCY merge"):
        currency_map = pd.read_csv(os.path.join(tables_path, "currency_map.csv"))
        df = df.merge(currency_map, on="country", how="left")
        logger.success("CURRENCY column correctly assigned")

    # prem freq
    with track("PREM_FREQ mapping"):
        freq_mapping = {
            "Mensual": 12,
            "Trimestral": 4,
            "Semestral": 2,
            "Anual": 1
        }
        df["PREM_FREQ"] = df["prem_frecuency"].map(freq_mapping)
        logger.success("PREM_FREQ column correctly assigned")

    # reins company
    with track("REINS rename"):
        df = df.rename(columns={"reins_name":"REINS"})
    
    # comm pc
    with track("COMM_PC rename"):
        df = df.rename(columns={"comission_precentage":"COMM_PC"})

    # Cálculo de comisión en valor absoluto
    with track("Commission amount calculation"):
        df["COMM_AMOUNT"] = (df["ANNUAL_PREM"] * df["COMM_PC"] / 100).round(2)
        logger.success("Commission amount calculated")

    # Clasificación de riesgo simple
    with track("Risk classification"):
        conditions = [
            (df["AGE_AT_ENTRY"] < 30) & (df["PROD_TYPE"] == 2),
            (df["AGE_AT_ENTRY"] >= 30) & (df["AGE_AT_ENTRY"] < 50),
            (df["AGE_AT_ENTRY"] >= 50) & (df["PROD_TYPE"] == 1)
        ]
        choices = ["LOW", "MEDIUM", "HIGH"]
        df["RISK_CLASS"] = np.select(conditions, choices, default="MEDIUM")
        logger.success("Risk classification completed")

    # Agregación por país (ejemplo de operación más pesada)
    with track("Country aggregation statistics"):
        country_stats = df.groupby('country').agg({
            'SUM_ASSURED': 'mean',
            'ANNUAL_PREM': 'mean',
            'ID': 'count'
        }).reset_index()
        country_stats.columns = ['country', 'AVG_SA_BY_COUNTRY', 'AVG_PREM_BY_COUNTRY', 'COUNT_BY_COUNTRY']
        df = df.merge(country_stats, on='country', how='left')
        logger.success("Country statistics merged")

    # Validación de datos de salida
    with track("Output data validation"):
        # Verificar que no haya valores negativos en campos monetarios
        monetary_cols = ['SUM_ASSURED', 'ANNUAL_PREM', 'COMM_AMOUNT']
        for col in monetary_cols:
            if (df[col] < 0).any():
                logger.warning(f"Negative values found in {col}")
        logger.success("Output validation completed")

    # output variables selection (más columnas que MEDIUM)
    with track("Output column selection"):
        output_vars = ["ID", "PROD_TYPE", "SEX", "POL_TERM_Y", "ENTRY_YEAR", "ENTRY_MTH", 
                        "AGE_AT_ENTRY", "CURRENT_AGE", "AGE_RANGE", "TARIFF", "CURRENCY", 
                        "SUM_ASSURED", "ANNUAL_PREM", "PREM_SA_RATIO", "PREM_FREQ", 
                        "REINS", "COMM_PC", "COMM_AMOUNT", "RISK_CLASS"]
        logger.info(f"Output variable list: {', '.join(map(str, output_vars))}")
        df_out = df[output_vars]

    # Restaurar prefix original
    logger.prefix = original_prefix
    return df_out