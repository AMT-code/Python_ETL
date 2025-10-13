import pandas as pd
import numpy as np
import os
import time
from contextlib import contextmanager
from datetime import datetime

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
    # COMPLEJIDAD: VERY COMPLEX
    # - Todas las transformaciones de COMPLEX
    # - Múltiples merges con tablas auxiliares
    # - Cálculos actuariales avanzados
    # - Window functions y operaciones iterativas
    # - Simulaciones y proyecciones
    # =========================================================================

    # Mapear sexo
    with track("SEX mapping"):
        df["Sex"] = df["Sex"].map({"Female": 0, "Male": 1})
        df = df.rename(columns={"Sex":"SEX"})
        logger.success("SEX mapped")

    # Validación exhaustiva de entrada
    with track("Comprehensive input validation"):
        critical_cols = ['ID', 'SEX', 'inception_date', 'birth_date', 'sum_insured', 'annual_prem']
        null_counts = df[critical_cols].isnull().sum()
        duplicate_ids = df['ID'].duplicated().sum()
        logger.info(f"Null values: {null_counts.sum()}, Duplicates: {duplicate_ids}")
        logger.success("Comprehensive validation completed")

    # pol_term_y con merge
    with track("POL_TERM_Y assignment + merge"):
        idx_map = pd.read_csv(os.path.join(tables_path, "temp_idx_map.csv"))
        df = df.merge(idx_map, how="left", left_on="temp_idx", right_on="idx")
        df.loc[df["tipo_producto"] == "Vitalicio", "POL_TERM_Y"] = 100
        logger.success("POL_TERM_Y correctly assigned")

    # prod type
    with track("PROD_TYPE mapping"):
        df = df.rename(columns={"tipo_producto":"PROD_TYPE"})
        df["PROD_TYPE"] = df["PROD_TYPE"].map({"Vitalicio":1, "Temporal":2})
        logger.success("PROD_TYPE mapped")

    # date conversions avanzadas
    with track("Advanced date conversions"):
        df["inception_date"] = pd.to_datetime(df["inception_date"], format='%d/%m/%Y')
        df["birth_date"] = pd.to_datetime(df["birth_date"], format='%d/%m/%Y')
        df["ENTRY_YEAR"] = df["inception_date"].dt.year
        df["ENTRY_MTH"] = df["inception_date"].dt.month
        df["ENTRY_DAY"] = df["inception_date"].dt.day
        df["ENTRY_QUARTER"] = df["inception_date"].dt.quarter
        df["ENTRY_WEEK"] = df["inception_date"].dt.isocalendar().week
        df["AGE_AT_ENTRY"] = (df["inception_date"] - df["birth_date"]).dt.days // 365
        logger.success("Advanced date conversions completed")

    # Cálculos de edad y duración
    with track("Age and duration calculations"):
        current_date = datetime.now()
        df["CURRENT_AGE"] = ((pd.Timestamp(current_date) - df["birth_date"]).dt.days // 365)
        df["CONTRACT_DURATION_YEARS"] = ((pd.Timestamp(current_date) - df["inception_date"]).dt.days // 365)
        df["REMAINING_YEARS"] = df["POL_TERM_Y"] - df["CONTRACT_DURATION_YEARS"]
        df["REMAINING_YEARS"] = df["REMAINING_YEARS"].clip(lower=0)
        logger.success("Age and duration calculated")

    # Clasificaciones múltiples
    with track("Multiple classifications"):
        # Age range
        df["AGE_RANGE"] = pd.cut(df["AGE_AT_ENTRY"], 
                                bins=[0, 25, 35, 45, 55, 65, 100],
                                labels=["0-25", "26-35", "36-45", "46-55", "56-65", "65+"])
        # Sum assured range
        df["SA_RANGE"] = pd.cut(df["sum_insured"],
                                bins=[0, 50000, 100000, 250000, 500000, float('inf')],
                                labels=["0-50K", "50-100K", "100-250K", "250-500K", "500K+"])
        logger.success("Multiple classifications completed")

    # sum assured y premium
    with track("Financial variables assignment"):
        df["SUM_ASSURED"] = df["sum_insured"]
        df["ANNUAL_PREM"] = df["annual_prem"]
        logger.success("Financial variables assigned")

    # Ratios y métricas financieras avanzadas
    with track("Advanced financial metrics"):
        df["PREM_SA_RATIO"] = (df["ANNUAL_PREM"] / df["SUM_ASSURED"] * 100).round(4)
        df["SA_TO_AGE_RATIO"] = (df["SUM_ASSURED"] / df["AGE_AT_ENTRY"]).round(2)
        df["TOTAL_PREM_EXPECTED"] = (df["ANNUAL_PREM"] * df["POL_TERM_Y"]).round(2)
        df["PROFIT_MARGIN"] = (df["ANNUAL_PREM"] - (df["ANNUAL_PREM"] * 0.3)).round(2)  # Simplificado
        logger.success("Advanced financial metrics calculated")

    # Multiple merges
    with track("TARIFF merge"):
        tariff_map = pd.read_csv(os.path.join(tables_path, "tariff_map.csv"))
        df = df.merge(tariff_map, on="tariff_grp", how="left")
        logger.success("TARIFF merged")

    with track("CURRENCY merge"):
        currency_map = pd.read_csv(os.path.join(tables_path, "currency_map.csv"))
        df = df.merge(currency_map, on="country", how="left")
        logger.success("CURRENCY merged")

    # prem freq
    with track("PREM_FREQ mapping"):
        freq_mapping = {"Mensual": 12, "Trimestral": 4, "Semestral": 2, "Anual": 1}
        df["PREM_FREQ"] = df["prem_frecuency"].map(freq_mapping)
        logger.success("PREM_FREQ mapped")

    # Cálculo de prima mensual equivalente
    with track("Monthly premium calculation"):
        df["MONTHLY_PREM"] = (df["ANNUAL_PREM"] / 12).round(2)
        logger.success("Monthly premium calculated")

    # reins y comm
    with track("REINS and COMM columns"):
        df = df.rename(columns={"reins_name":"REINS", "comission_precentage":"COMM_PC"})
        df["COMM_AMOUNT"] = (df["ANNUAL_PREM"] * df["COMM_PC"] / 100).round(2)
        df["NET_PREM"] = (df["ANNUAL_PREM"] - df["COMM_AMOUNT"]).round(2)
        logger.success("REINS and commission processed")

    # Clasificación de riesgo compleja con múltiples factores
    with track("Complex risk classification"):
        risk_scores = np.zeros(len(df))
        # Factor edad
        risk_scores += np.where(df["AGE_AT_ENTRY"] < 30, 0, 
                        np.where(df["AGE_AT_ENTRY"] < 50, 1, 2))
        # Factor producto
        risk_scores += np.where(df["PROD_TYPE"] == 1, 1, 0)
        # Factor suma asegurada
        risk_scores += np.where(df["SUM_ASSURED"] > 250000, 1, 0)
        # Factor ratio prima
        risk_scores += np.where(df["PREM_SA_RATIO"] < 0.5, 0, 1)
        
        df["RISK_SCORE"] = risk_scores
        df["RISK_CLASS"] = pd.cut(risk_scores, bins=[-1, 1, 3, 5], labels=["LOW", "MEDIUM", "HIGH"])
        logger.success("Complex risk classification completed")

    # Agregaciones por múltiples dimensiones
    with track("Multi-dimensional aggregations"):
        # Por país
        country_stats = df.groupby('country').agg({
            'SUM_ASSURED': ['mean', 'sum', 'count'],
            'ANNUAL_PREM': ['mean', 'sum'],
            'RISK_SCORE': 'mean'
        }).reset_index()
        country_stats.columns = ['country', 'AVG_SA_COUNTRY', 'TOTAL_SA_COUNTRY', 'COUNT_COUNTRY',
                                'AVG_PREM_COUNTRY', 'TOTAL_PREM_COUNTRY', 'AVG_RISK_COUNTRY']
        df = df.merge(country_stats, on='country', how='left')
        
        # Por rango de edad
        age_stats = df.groupby('AGE_RANGE').agg({
            'ANNUAL_PREM': 'mean',
            'SUM_ASSURED': 'mean'
        }).reset_index()
        age_stats.columns = ['AGE_RANGE', 'AVG_PREM_AGE', 'AVG_SA_AGE']
        df = df.merge(age_stats, on='AGE_RANGE', how='left')
        logger.success("Multi-dimensional aggregations completed")

    # Window functions - Ranking dentro de grupos
    with track("Window functions - Rankings"):
        df['PREM_RANK_BY_COUNTRY'] = df.groupby('country')['ANNUAL_PREM'].rank(method='dense', ascending=False)
        df['SA_RANK_BY_AGE'] = df.groupby('AGE_RANGE')['SUM_ASSURED'].rank(method='dense', ascending=False)
        logger.success("Window functions applied")

    # Cálculo de percentiles por grupo
    with track("Percentile calculations by group"):
        df['PREM_PERCENTILE'] = df.groupby('country')['ANNUAL_PREM'].transform(
            lambda x: (x.rank() / len(x) * 100).round(1)
        )
        logger.success("Percentile calculations completed")

    # Detección de outliers
    with track("Outlier detection"):
        # Usando IQR method
        Q1_prem = df['ANNUAL_PREM'].quantile(0.25)
        Q3_prem = df['ANNUAL_PREM'].quantile(0.75)
        IQR_prem = Q3_prem - Q1_prem
        df['IS_PREM_OUTLIER'] = ((df['ANNUAL_PREM'] < (Q1_prem - 1.5 * IQR_prem)) | 
                                  (df['ANNUAL_PREM'] > (Q3_prem + 1.5 * IQR_prem))).astype(int)
        
        Q1_sa = df['SUM_ASSURED'].quantile(0.25)
        Q3_sa = df['SUM_ASSURED'].quantile(0.75)
        IQR_sa = Q3_sa - Q1_sa
        df['IS_SA_OUTLIER'] = ((df['SUM_ASSURED'] < (Q1_sa - 1.5 * IQR_sa)) | 
                                (df['SUM_ASSURED'] > (Q3_sa + 1.5 * IQR_sa))).astype(int)
        logger.success("Outlier detection completed")

    # Proyección de valores futuros (simulación simple)
    with track("Future value projections"):
        # Proyectar valor del contrato a 10 años con tasa de interés asumida
        assumed_rate = 0.05
        years_to_project = 10
        df['PROJECTED_VALUE_10Y'] = (df['TOTAL_PREM_EXPECTED'] * 
                                      ((1 + assumed_rate) ** years_to_project)).round(2)
        logger.success("Future projections calculated")

    # Cálculo de score de rentabilidad
    with track("Profitability scoring"):
        # Score basado en múltiples factores normalizados
        prem_score = (df['ANNUAL_PREM'] - df['ANNUAL_PREM'].mean()) / df['ANNUAL_PREM'].std()
        duration_score = (df['CONTRACT_DURATION_YEARS'] - df['CONTRACT_DURATION_YEARS'].mean()) / df['CONTRACT_DURATION_YEARS'].std()
        risk_score_norm = (df['RISK_SCORE'] - df['RISK_SCORE'].mean()) / df['RISK_SCORE'].std()
        
        df['PROFITABILITY_SCORE'] = (prem_score * 0.5 + 
                                      duration_score * 0.3 - 
                                      risk_score_norm * 0.2).round(3)
        logger.success("Profitability scoring completed")

    # Segmentación avanzada de clientes
    with track("Advanced customer segmentation"):
        # Usar KMeans conceptualmente (simulado con bins para no agregar sklearn)
        df['VALUE_SEGMENT'] = pd.qcut(df['TOTAL_PREM_EXPECTED'], 
                                        q=4, 
                                        labels=['BRONZE', 'SILVER', 'GOLD', 'PLATINUM'],
                                        duplicates='drop')
        logger.success("Customer segmentation completed")

    # output variables selection (máximo número de columnas)
    with track("Comprehensive output selection"):
        output_vars = [
            "ID", "PROD_TYPE", "SEX", "POL_TERM_Y", "ENTRY_YEAR", "ENTRY_MTH", 
            "AGE_AT_ENTRY", "CURRENT_AGE", "AGE_RANGE", "TARIFF", "CURRENCY",
            "SUM_ASSURED", "SA_RANGE", "ANNUAL_PREM", "MONTHLY_PREM", 
            "PREM_SA_RATIO", "TOTAL_PREM_EXPECTED", "PREM_FREQ",
            "REINS", "COMM_PC", "COMM_AMOUNT", "NET_PREM",
            "RISK_SCORE", "RISK_CLASS", "PROFITABILITY_SCORE", "VALUE_SEGMENT",
            "PREM_RANK_BY_COUNTRY", "IS_PREM_OUTLIER", "IS_SA_OUTLIER"
        ]
        logger.info(f"Output: {len(output_vars)} variables selected")
        df_out = df[output_vars]

    # Validación exhaustiva de salida
    with track("Comprehensive output validation"):
        monetary_cols = ['SUM_ASSURED', 'ANNUAL_PREM', 'COMM_AMOUNT', 'NET_PREM', 'MONTHLY_PREM']
        validation_passed = True
        for col in monetary_cols:
            if (df[col] < 0).any():
                logger.warning(f"Negative values in {col}")
                validation_passed = False
        
        if df[output_vars].isnull().sum().sum() > 0:
            logger.warning("Null values found in output")
            validation_passed = False
        
        if validation_passed:
            logger.success("All output validations passed")
        else:
            logger.warning("Some validations failed - review data quality")

    # output variables selection (máximo número de columnas)
    with track("Comprehensive output selection"):
        output_vars = [
            "ID", "PROD_TYPE", "SEX", "POL_TERM_Y", "ENTRY_YEAR", "ENTRY_MTH", 
            "AGE_AT_ENTRY", "CURRENT_AGE", "AGE_RANGE", "TARIFF", "CURRENCY",
            "SUM_ASSURED", "SA_RANGE", "ANNUAL_PREM", "MONTHLY_PREM", 
            "PREM_SA_RATIO", "TOTAL_PREM_EXPECTED", "PREM_FREQ",
            "REINS", "COMM_PC", "COMM_AMOUNT", "NET_PREM",
            "RISK_SCORE", "RISK_CLASS", "PROFITABILITY_SCORE", "VALUE_SEGMENT",
            "PREM_RANK_BY_COUNTRY", "IS_PREM_OUTLIER", "IS_SA_OUTLIER"
        ]
        logger.info(f"Output: {len(output_vars)} variables selected")
        df_out = df[output_vars]

    # Validación exhaustiva de salida
    with track("Comprehensive output validation"):
        monetary_cols = ['SUM_ASSURED', 'ANNUAL_PREM', 'COMM_AMOUNT', 'NET_PREM', 'MONTHLY_PREM']
        validation_passed = True
        for col in monetary_cols:
            if (df[col] < 0).any():
                logger.warning(f"Negative values in {col}")
                validation_passed = False
        
        if df[output_vars].isnull().sum().sum() > 0:
            logger.warning("Null values found in output")
            validation_passed = False
        
        if validation_passed:
            logger.success("All output validations passed")
        else:
            logger.warning("Some validations failed - review data quality")

    # Restaurar prefix original
    logger.prefix = original_prefix
    return df_out