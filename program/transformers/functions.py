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
    """    
    =========================================================================
    HOW TO USE: Para trackear una transformación en el audit, usa:
    
        with track("Descripción de la transformación"):
            # Tu código aquí
            df["NUEVA_COL"] = df["VIEJA"] * 2
            logger.success("Transformación exitosa")
    
    El tracking es automático: mide el tiempo y lo registra en audit.txt
    Si no quieres trackear algo, simplemente no uses "with track()"
    =========================================================================
    """

    # =================================================================
    # TRANSFORMACIONES 
    # =================================================================

    # mapear sexo
    with track("SEX mapping"):
        df["Sex"] = df["Sex"].map({"Female": 0, "Male": 1})
        df = df.rename(columns={"Sex":"SEX"})
        logger.success("SEX mapped")

    # pol_term_y
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

    # date conversions
    with track("Date conversions (3 columns)"):
        df["inception_date"] = pd.to_datetime(df["inception_date"], format='%d/%m/%Y')
        df["birth_date"] = pd.to_datetime(df["birth_date"], format='%d/%m/%Y')
        df["ENTRY_YEAR"] = df["inception_date"].dt.year
        df["ENTRY_MTH"] = df["inception_date"].dt.month
        df["AGE_AT_ENTRY"] = (df["inception_date"] - df["birth_date"]).dt.days // 365
        logger.success("date conversions correctly done")

    # sum assured
    with track("SUM_ASSURED assignment"):
        df["SUM_ASSURED"] = df["sum_insured"]
        logger.success("SUM_ASSURED column correctly assigned")

    # annual prem
    with track("ANNUAL_PREM assignment"):
        df["ANNUAL_PREM"] = df["annual_prem"]
        logger.success("ANNUAL_PREM column correctly assigned")

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

    # -> debugger <-
    # df["TST"] = np.where(df["SEX"] == 0, "TESTING", "TST")
    # logger.debug(df.info())

    # output variables selection
    with track("Output column selection"):
        output_vars = ["ID", "PROD_TYPE", "SEX", "POL_TERM_Y","ENTRY_YEAR", "ENTRY_MTH", "AGE_AT_ENTRY", "TARIFF", "CURRENCY", "SUM_ASSURED", "ANNUAL_PREM","PREM_FREQ", "REINS", "COMM_PC"]
        logger.info(f"Output variable list: {', '.join(map(str, output_vars))}")
        df_out = df[output_vars]

    # Restaurar prefix original
    logger.prefix = original_prefix
    return df_out