import os
import pandas as pd
import pandas.api.types as ptypes

def _get_variable_type(series: pd.Series) -> str:
    """Return encoded variable type according to custom MPF‐style rules."""
    if ptypes.is_integer_dtype(series):
        return "I"
    if ptypes.is_float_dtype(series):
        return "N"
    if ptypes.is_object_dtype(series):
        max_len = series.dropna().astype(str).str.len().max()
        return f"T{max_len}"
    return "NA"

def write_rpt(df: pd.DataFrame, output_path: str) -> None:
    """Write *df* to *output_path* in custom .rpt format.

    Format rules
    ------------
    1. First line  : VARIABLE_TYPES,<encoded-types>
    2. Second line : !1,<column names>
    3. Data lines  : *,<row values>
    4. Footer      : blank line + "##END##"
    """
    # Build header lines
    types_line = ["VARIABLE_TYPES"] + [_get_variable_type(df[c]) for c in df.columns]
    header_line = ["!1"] + list(df.columns)

    # Data lines prefixed with "*"
    data_lines = df.astype(str).apply(lambda r: ["*"] + r.tolist(), axis=1)

    # Convert to CSV strings
    to_csv = lambda items: ",".join(items)
    lines = [to_csv(types_line), to_csv(header_line)] + [to_csv(row) for row in data_lines]

    # Footer
    lines += ["", "##END##"]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def write_csv(df, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
