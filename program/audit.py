import os
import time
from datetime import datetime


class AuditLogger:
    """Sistema de auditoría para registrar métricas de performance del pipeline"""
    
    def __init__(self, log_dir="../logs"):
        self.log_dir = log_dir
        self.log_path = None
        self.start_time = None
        self.metrics = {}
        
        # Asegurar que existe el directorio
        os.makedirs(log_dir, exist_ok=True)
    
    def start_audit(self, config):
        """Iniciar auditoría de una ejecución"""
        self.start_time = time.time()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_path = os.path.join(self.log_dir, f"{timestamp}_audit.txt")
        
        # Inicializar métricas
        self.metrics = {
            'input_file': config.get('input_file', 'unknown'),
            'output_file': config.get('output_file', 'unknown'),
            'tables_path': config.get('tables_path', 'unknown'),
            'input_rows': 0,
            'input_columns': 0,
            'output_rows': 0,
            'output_columns': 0,
            'runtime_total': 0,
            'runtime_reading': 0,
            'runtime_transformations': 0,
            'runtime_writing': 0,
            'transformations_count': 0,
            'transformations_complexity': 'unknown',
            'status': 'started'
        }
        
        # Escribir header del audit
        self._write_line("=" * 80)
        self._write_line("PIPELINE EXECUTION AUDIT")
        self._write_line("=" * 80)
        self._write_line(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._write_line(f"Input File: {self.metrics['input_file']}")
        self._write_line(f"Output File: {self.metrics['output_file']}")
        self._write_line(f"Tables Path: {self.metrics['tables_path']}")
        self._write_line("=" * 80)
        self._write_line("")
    
    def log_reading_start(self):
        """Marcar inicio de lectura de input"""
        self.metrics['reading_start'] = time.time()
        self._write_line("[PHASE] Starting INPUT READING...")
    
    def log_reading_end(self, rows, columns):
        """Marcar fin de lectura de input"""
        if 'reading_start' in self.metrics:
            self.metrics['runtime_reading'] = time.time() - self.metrics['reading_start']
        self.metrics['input_rows'] = rows
        self.metrics['input_columns'] = columns
        
        self._write_line(f"[PHASE] INPUT READING completed")
        self._write_line(f"  ├─ Rows read: {rows:,}")
        self._write_line(f"  ├─ Columns: {columns}")
        self._write_line(f"  └─ Time: {self.metrics['runtime_reading']:.3f}s")
        self._write_line("")
    
    def log_transformations_start(self):
        """Marcar inicio de transformaciones"""
        self.metrics['transformations_start'] = time.time()
        self._write_line("[PHASE] Starting TRANSFORMATIONS...")
    
    def log_transformation(self, name, execution_time=None):
        """Registrar una transformación individual"""
        self.metrics['transformations_count'] += 1
        if execution_time:
            self._write_line(f"  ├─ {name}: {execution_time:.3f}s")
        else:
            self._write_line(f"  ├─ {name}")
    
    def log_transformations_end(self):
        """Marcar fin de transformaciones"""
        if 'transformations_start' in self.metrics:
            self.metrics['runtime_transformations'] = time.time() - self.metrics['transformations_start']
        
        # Calcular complejidad basada en tiempo y cantidad de transformaciones
        complexity = self._calculate_complexity()
        self.metrics['transformations_complexity'] = complexity
        
        self._write_line(f"[PHASE] TRANSFORMATIONS completed")
        self._write_line(f"  ├─ Total transformations: {self.metrics['transformations_count']}")
        self._write_line(f"  ├─ Complexity: {complexity}")
        self._write_line(f"  └─ Time: {self.metrics['runtime_transformations']:.3f}s")
        self._write_line("")
    
    def log_writing_start(self):
        """Marcar inicio de escritura de output"""
        self.metrics['writing_start'] = time.time()
        self._write_line("[PHASE] Starting OUTPUT WRITING...")
    
    def log_writing_end(self, rows, columns):
        """Marcar fin de escritura de output"""
        if 'writing_start' in self.metrics:
            self.metrics['runtime_writing'] = time.time() - self.metrics['writing_start']
        self.metrics['output_rows'] = rows
        self.metrics['output_columns'] = columns
        
        self._write_line(f"[PHASE] OUTPUT WRITING completed")
        self._write_line(f"  ├─ Rows written: {rows:,}")
        self._write_line(f"  ├─ Columns: {columns}")
        self._write_line(f"  └─ Time: {self.metrics['runtime_writing']:.3f}s")
        self._write_line("")
    
    def end_audit(self, status='success', error_message=None):
        """Finalizar auditoría"""
        self.metrics['runtime_total'] = time.time() - self.start_time
        self.metrics['status'] = status
        
        self._write_line("=" * 80)
        self._write_line("EXECUTION SUMMARY")
        self._write_line("=" * 80)
        self._write_line(f"Status: {status.upper()}")
        if error_message:
            self._write_line(f"Error: {error_message}")
        self._write_line("")
        
        # Performance summary
        self._write_line("PERFORMANCE METRICS:")
        self._write_line(f"  ├─ Total Runtime: {self.metrics['runtime_total']:.3f}s")
        self._write_line(f"  ├─ Reading Time: {self.metrics['runtime_reading']:.3f}s ({self._percentage(self.metrics['runtime_reading'], self.metrics['runtime_total']):.1f}%)")
        self._write_line(f"  ├─ Transformation Time: {self.metrics['runtime_transformations']:.3f}s ({self._percentage(self.metrics['runtime_transformations'], self.metrics['runtime_total']):.1f}%)")
        self._write_line(f"  └─ Writing Time: {self.metrics['runtime_writing']:.3f}s ({self._percentage(self.metrics['runtime_writing'], self.metrics['runtime_total']):.1f}%)")
        self._write_line("")
        
        # Data throughput
        if self.metrics['input_rows'] > 0:
            throughput = self.metrics['input_rows'] / self.metrics['runtime_total']
            self._write_line("THROUGHPUT:")
            self._write_line(f"  ├─ Rows/second: {throughput:,.0f}")
            self._write_line(f"  └─ Time per 1M rows: {(1_000_000 / throughput):.2f}s (estimated)")
        self._write_line("")
        
        # Transformation complexity analysis
        self._write_line("TRANSFORMATION ANALYSIS:")
        self._write_line(f"  ├─ Total transformations: {self.metrics['transformations_count']}")
        self._write_line(f"  ├─ Complexity level: {self.metrics['transformations_complexity']}")
        self._write_line(f"  └─ Avg time per transformation: {self.metrics['runtime_transformations'] / max(1, self.metrics['transformations_count']):.3f}s")
        self._write_line("")
        
        # Data quality
        self._write_line("DATA QUALITY:")
        self._write_line(f"  ├─ Input rows: {self.metrics['input_rows']:,}")
        self._write_line(f"  ├─ Output rows: {self.metrics['output_rows']:,}")
        row_diff = self.metrics['input_rows'] - self.metrics['output_rows']
        if row_diff != 0:
            self._write_line(f"  ├─ Row difference: {row_diff:,} ({self._percentage(row_diff, self.metrics['input_rows']):.2f}%)")
        self._write_line(f"  └─ Column transformation: {self.metrics['input_columns']} → {self.metrics['output_columns']}")
        self._write_line("")
        
        self._write_line("=" * 80)
        self._write_line(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._write_line("=" * 80)
    
    def _calculate_complexity(self):
        """Calcular complejidad de las transformaciones basado en tiempo y cantidad"""
        count = self.metrics['transformations_count']
        total_time = self.metrics['runtime_transformations']
        time_per_transform = total_time / max(1, count)
        
        # Criterios de complejidad más realistas para cálculos actuariales
        # Consideramos tanto la cantidad de transformaciones como el tiempo promedio
        
        # SIMPLE: Pocas transformaciones básicas (renombres, asignaciones directas)
        if count <= 10 and time_per_transform < 0.5:
            return "SIMPLE"
        
        # MEDIUM: Transformaciones típicas con algunos joins/merges
        # Ej: 10-25 transformaciones con tiempos razonables
        elif count <= 25 and time_per_transform < 1.5:
            return "MEDIUM"
        
        # COMPLEX: Muchas transformaciones o algunas operaciones pesadas
        # Ej: 25-40 transformaciones, o transformaciones con joins múltiples
        elif count <= 40 and time_per_transform < 3.0:
            return "COMPLEX"
        
        # VERY COMPLEX: Procesos muy elaborados con muchas etapas
        # Ej: >40 transformaciones o tiempos muy altos por operación
        else:
            return "VERY COMPLEX"
    
    def _percentage(self, part, total):
        """Calcular porcentaje"""
        return (part / total * 100) if total > 0 else 0
    
    def _write_line(self, line):
        """Escribir línea al archivo de audit"""
        if self.log_path:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(line + '\n')