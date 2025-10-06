import pandas as pd
import numpy as np
import os

def run_business_rules(df, tables_path, logger):
    # Guardar el prefix original
    original_prefix = logger.prefix
    # Cambiar al prefix específico del módulo
    logger.prefix = "Functions"

    df = df.copy()

    # --> debugger <--
    # logger.debug(f"input data types:\n {df.info()} ")
    # logger.debug(f"input data head lines=> {df.head(2)} ")
    logger.debug(f"input data columns=> {df.columns.tolist()} ")

    # mapear sexo
    df["Sex"] = df["Sex"].map({"Female": 0, "Male": 1})
    df = df.rename(columns={"Sex":"SEX"})
    logger.success("SEX mapped")

    # pol_term_y
    idx_map = pd.read_csv(os.path.join(tables_path, "temp_idx_map.csv"))
    df = df.merge(idx_map, how="left", left_on="temp_idx", right_on="idx")

    df.loc[df["tipo_producto"] == "Vitalicio", "POL_TERM_Y"] = 100
    logger.success("POL_TERM_Y correctly assigned")

    # prod type column
    df = df.rename(columns={"tipo_producto":"PROD_TYPE"})
    df["PROD_TYPE"] = df["PROD_TYPE"].map({"Vitalicio":1, "Temporal":2})
    logger.success("PROD_TYPE column correctly assigned")

    # date conversions
    df["inception_date"] = pd.to_datetime(df["inception_date"], format='%d/%m/%Y')
    df["birth_date"] = pd.to_datetime(df["birth_date"], format='%d/%m/%Y')

    df["ENTRY_YEAR"] = df["inception_date"].dt.year
    df["ENTRY_MTH"] = df["inception_date"].dt.month
    df["AGE_AT_ENTRY"] = (df["inception_date"] - df["birth_date"]).dt.days // 365
    logger.success("date conversions correctly done")

    # sum assured
    df["SUM_ASSURED"] = df["sum_insured"]
    logger.success("SUM_ASSURED column correctly assigned")

    # annual prem
    df["ANNUAL_PREM"] = df["annual_prem"]
    logger.success("ANNUAL_PREM column correctly assigned")

    # tariff grp
    tariff_map = pd.read_csv(os.path.join(tables_path, "tariff_map.csv"))
    df = df.merge(tariff_map, on="tariff_grp", how="left")
    logger.success("TARIFF column correctly assigned")

    # currency map
    currency_map = pd.read_csv(os.path.join(tables_path, "currency_map.csv"))
    df = df.merge(currency_map, on="country", how="left")
    logger.success("CURRENCY column correctly assigned")

    # prem freq
    freq_mapping = {
    "Mensual": 12,
    "Trimestral": 4,
    "Semestral": 2,
    "Anual": 1
    }
    df["PREM_FREQ"] = df["prem_frecuency"].map(freq_mapping)
    logger.success("PREM_FREQ column correctly assigned")

    # reins company
    df = df.rename(columns={"reins_name":"REINS"})
    
    # comm pc
    df = df.rename(columns={"comission_precentage":"COMM_PC"})

    # -> debugger <-
    # df["TST"] = np.where(df["SEX"] == 0, "TESTING", "TST")
    # logger.debug(df.info())

    # output variables selection
    output_vars = ["ID", "PROD_TYPE", "SEX", "POL_TERM_Y","ENTRY_YEAR", "ENTRY_MTH", "AGE_AT_ENTRY", "TARIFF", "CURRENCY", "SUM_ASSURED", "ANNUAL_PREM","PREM_FREQ", "REINS", "COMM_PC"]
    logger.info(f"Output variable list: {', '.join(map(str, output_vars))}")
    df_out = df[output_vars]

    # Restaurar prefix original
    logger.prefix = original_prefix
    return df_out
