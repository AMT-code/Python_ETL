import os
import re
import pandas as pd
from datetime import datetime

def parse_audit_file(filepath):
    """Extraer métricas de un archivo audit.txt"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    data = {}
    
    # Extraer información básica
    data['filename'] = os.path.basename(filepath)
    data['timestamp'] = re.search(r'Start Time: (.+)', content).group(1)
    
    # Input/Output
    data['input_file'] = re.search(r'Input File: (.+)', content).group(1)
    data['output_file'] = re.search(r'Output File: (.+)', content).group(1)
    
    # Rows
    data['input_rows'] = int(re.search(r'Rows read: ([\d,]+)', content).group(1).replace(',', ''))
    data['output_rows'] = int(re.search(r'Rows written: ([\d,]+)', content).group(1).replace(',', ''))
    
    # Columns
    data['input_columns'] = int(re.search(r'Rows read: [\d,]+\n  ├─ Columns: (\d+)', content).group(1))
    data['output_columns'] = int(re.search(r'Rows written: [\d,]+\n  ├─ Columns: (\d+)', content).group(1))
    
    # Tiempos
    data['total_runtime'] = float(re.search(r'Total Runtime: ([\d.]+)s', content).group(1))
    data['reading_time'] = float(re.search(r'Reading Time: ([\d.]+)s', content).group(1))
    data['transformation_time'] = float(re.search(r'Transformation Time: ([\d.]+)s', content).group(1))
    data['writing_time'] = float(re.search(r'Writing Time: ([\d.]+)s', content).group(1))
    
    # Porcentajes
    data['reading_pct'] = float(re.search(r'Reading Time: [\d.]+s \(([\d.]+)%\)', content).group(1))
    data['transformation_pct'] = float(re.search(r'Transformation Time: [\d.]+s \(([\d.]+)%\)', content).group(1))
    data['writing_pct'] = float(re.search(r'Writing Time: [\d.]+s \(([\d.]+)%\)', content).group(1))
    
    # Throughput
    data['throughput'] = int(re.search(r'Rows/second: ([\d,]+)', content).group(1).replace(',', ''))
    data['time_per_1m'] = float(re.search(r'Time per 1M rows: ([\d.]+)s', content).group(1))
    
    # Transformaciones
    data['transformation_count'] = int(re.search(r'Total transformations: (\d+)', content).group(1))
    data['complexity'] = re.search(r'Complexity level: (\w+)', content).group(1)
    data['avg_time_per_transform'] = float(re.search(r'Avg time per transformation: ([\d.]+)s', content).group(1))
    
    # Status
    data['status'] = re.search(r'Status: (\w+)', content).group(1)
    
    return data


def analyze_audits(logs_dir='logs'):
    """Analizar todos los archivos audit.txt en el directorio"""
    audit_files = [f for f in os.listdir(logs_dir) if f.endswith('_audit.txt')]
    
    if not audit_files:
        print("No audit files found!")
        return None
    
    # Parse todos los audits
    data_list = []
    for audit_file in audit_files:
        filepath = os.path.join(logs_dir, audit_file)
        try:
            data = parse_audit_file(filepath)
            data_list.append(data)
        except Exception as e:
            print(f"Error parsing {audit_file}: {e}")
    
    # Crear DataFrame
    df = pd.DataFrame(data_list)
    
    # Ordenar por timestamp
    df = df.sort_values('timestamp')
    
    return df


def generate_summary_report(df, output_file='zzz_audit_analysis/audit_summary_report.txt'):
    """Generar reporte consolidado"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("CONSOLIDATED AUDIT REPORT\n")
        f.write("=" * 100 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Executions: {len(df)}\n")
        f.write(f"Date Range: {df['timestamp'].min()} to {df['timestamp'].max()}\n")
        f.write("=" * 100 + "\n\n")
        
        # Resumen por tamaño de dataset
        f.write("PERFORMANCE BY DATA SIZE\n")
        f.write("-" * 100 + "\n")
        f.write(f"{'Rows':<15} {'Count':<8} {'Avg Runtime':<15} {'Avg Throughput':<20} {'Time per 1M':<15}\n")
        f.write("-" * 100 + "\n")
        
        grouped = df.groupby('input_rows').agg({
            'input_rows': 'count',
            'total_runtime': 'mean',
            'throughput': 'mean',
            'time_per_1m': 'mean'
        }).rename(columns={'input_rows': 'count'})
        
        for idx, row in grouped.iterrows():
            f.write(f"{idx:>14,} {int(row['count']):<8} {row['total_runtime']:>13.2f}s {row['throughput']:>17,.0f} r/s {row['time_per_1m']:>13.2f}s\n")
        
        f.write("\n\n")
        
        # Análisis de fases (promedio)
        f.write("AVERAGE TIME DISTRIBUTION BY PHASE\n")
        f.write("-" * 100 + "\n")
        avg_reading_pct = df['reading_pct'].mean()
        avg_transform_pct = df['transformation_pct'].mean()
        avg_writing_pct = df['writing_pct'].mean()
        
        f.write(f"  ├─ Reading:        {avg_reading_pct:>6.1f}% (avg: {df['reading_time'].mean():.3f}s)\n")
        f.write(f"  ├─ Transformation: {avg_transform_pct:>6.1f}% (avg: {df['transformation_time'].mean():.3f}s)\n")
        f.write(f"  └─ Writing:        {avg_writing_pct:>6.1f}% (avg: {df['writing_time'].mean():.3f}s)\n")
        f.write("\n")
        f.write(f"⚠️  BOTTLENECK: {'Writing' if avg_writing_pct > avg_transform_pct and avg_writing_pct > avg_reading_pct else 'Transformation' if avg_transform_pct > avg_reading_pct else 'Reading'}\n")
        
        f.write("\n\n")
        
        # Complejidad
        f.write("COMPLEXITY ANALYSIS\n")
        f.write("-" * 100 + "\n")
        complexity_counts = df['complexity'].value_counts()
        for complexity, count in complexity_counts.items():
            f.write(f"  {complexity}: {count} executions\n")
        
        f.write("\n\n")
        
        # Throughput trends
        f.write("THROUGHPUT TRENDS\n")
        f.write("-" * 100 + "\n")
        f.write(f"  ├─ Maximum:  {df['throughput'].max():>12,.0f} rows/s (at {df.loc[df['throughput'].idxmax(), 'input_rows']:,} rows)\n")
        f.write(f"  ├─ Minimum:  {df['throughput'].min():>12,.0f} rows/s (at {df.loc[df['throughput'].idxmin(), 'input_rows']:,} rows)\n")
        f.write(f"  └─ Average:  {df['throughput'].mean():>12,.0f} rows/s\n")
        
        f.write("\n\n")
        
        # Escalabilidad
        f.write("SCALABILITY PROJECTION\n")
        f.write("-" * 100 + "\n")
        avg_time_per_1m = df['time_per_1m'].mean()
        f.write(f"  Based on current performance ({avg_time_per_1m:.2f}s per 1M rows):\n\n")
        
        projections = [5, 10, 20, 50, 100]
        for million in projections:
            estimated_time = million * avg_time_per_1m
            minutes = estimated_time / 60
            f.write(f"  {million:>3}M rows → {estimated_time:>8.1f}s ({minutes:>6.1f} min)\n")
        
        f.write("\n")
        f.write("=" * 100 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 100 + "\n")
    
    print(f"✅ Summary report generated: {output_file}")


def generate_comparison_csv(df, output_file='zzz_audit_analysis/audit_comparison.csv'):
    """Generar CSV para análisis externo (Excel)"""
    
    # Seleccionar columnas clave
    comparison_df = df[[
        'timestamp', 'input_rows', 'output_rows',
        'total_runtime', 'reading_time', 'transformation_time', 'writing_time',
        'throughput', 'time_per_1m', 'complexity',
        'transformation_count', 'avg_time_per_transform'
    ]].copy()
    
    # Renombrar para claridad
    comparison_df.columns = [
        'Timestamp', 'Input Rows', 'Output Rows',
        'Total Runtime (s)', 'Reading (s)', 'Transformation (s)', 'Writing (s)',
        'Throughput (rows/s)', 'Time per 1M (s)', 'Complexity',
        'Transform Count', 'Avg Time per Transform (s)'
    ]
    
    comparison_df.to_csv(output_file, index=False)
    print(f"✅ Comparison CSV generated: {output_file}")


if __name__ == "__main__":
    print("Analyzing audit files...")
    df = analyze_audits()
    
    if df is not None:
        print(f"Found {len(df)} audit files\n")
        
        # Generar reportes
        generate_summary_report(df)
        generate_comparison_csv(df)
        
        # Mostrar preview
        print("\nPreview of data:")
        print(df[['input_rows', 'total_runtime', 'throughput', 'complexity']].to_string())
    else:
        print("No data to analyze")