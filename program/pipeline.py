import yaml
import os
import sys
import time
from reader import read_input
from writer import write_csv, write_rpt
from logger import Logger
from audit import AuditLogger
from transformers.engine import apply_transformations

# 0. logger init
use_colors = sys.stdout.isatty()
log = Logger("Pipeline", use_colors=use_colors)

start_time = time.time()
log.info("=== PIPELINE BEGINNING ===")
script_dir = os.path.dirname(os.path.abspath(__file__))

# 1. load config
try:
    config_path = os.path.join(script_dir, "config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Verificar si audit está habilitado (después de cargar config)
    audit_enabled = config.get('enable_audit', True)
    audit = AuditLogger() if audit_enabled else None
    
    if audit_enabled:
        log.info("Audit logging: ENABLED")
        audit.start_audit(config)
    else:
        log.warning("Audit logging: DISABLED (no performance metrics will be saved)")
    
    log.success(f"Setting input file location: {config['input_file']}")
    if 'input_file_config' in config:
        input_config = config['input_file_config']
        log.info(f"Input file type: {input_config.get('type', 'auto')}")
        if input_config.get('delimiter'):
            log.info(f"Input file delimiter: \"{input_config.get('delimiter')}\"")
    else:
        log.info("Using auto-detect for input file format")
    
    log.success(f"Setting tables location: {config['tables_path']}")
    log.success(f"Setting output file location: {config['output_file']}")
except Exception as e:
    log.critical(f"Error during configuration loading: {e} --> PROCESS ENDED")
    exit()

# 2. input reading
try:
    input_file = config["input_file"]
    if input_file.startswith("input"):
        input_path = os.path.join(script_dir, "..", input_file)
    else:
        input_path = input_file
    
    input_file_config = config.get('input_file_config', None)
    
    if audit:
        audit.log_reading_start()
    
    df = read_input(input_path, file_config=input_file_config)
    
    if audit:
        audit.log_reading_end(len(df), len(df.columns))
    
    log.success(f"{len(df)} lines read")
    
    if input_file_config:
        file_type = input_file_config.get('type', 'auto')
        if file_type == 'csv' and input_file_config.get('delimiter'):
            log.info(f"File read as CSV with delimiter: \"{input_file_config.get('delimiter')}\"")
        else:
            log.info(f"File read as: {file_type}")
    else:
        log.info("File read using auto-detection")
except Exception as e:
    log.critical(f"Error during input reading: {e} --> PROCESS ENDED ")
    if audit:
        audit.end_audit(status='failed', error_message=str(e))
    exit()

# 3. applying transformation
try:
    if audit:
        audit.log_transformations_start()
    
    df = apply_transformations(df, config, log, script_dir, audit)
    
    if audit:
        audit.log_transformations_end()
except Exception as e:
    log.critical(f"Error during transformations: {e} --> PROCESS ENDED")
    if audit:
        audit.end_audit(status='failed', error_message=str(e))
    exit()

# 4. printing output
try:
    output_path = "../" + config["output_file"]
    output_file = os.path.basename(output_path)
    ext = os.path.splitext(output_path)[-1].lower()
    
    if audit:
        audit.log_writing_start()
    
    if ext == ".rpt":
        write_rpt(df, output_path)
        log.success(f"{output_file} file successfully saved")
    elif ext == ".csv":
        write_csv(df, output_path)
        log.success(f"{output_file} file successfully saved")
    else:
        warn_path = output_path + ".csv"
        log.warning(f"'{ext}' extension is not supported; the output file will use 'csv' format in: {warn_path}")
        df.to_csv(warn_path, index=False)
        log.success(f"{os.path.basename(warn_path)} .csv file successfully saved")
    
    if audit:
        audit.log_writing_end(len(df), len(df.columns))
except Exception as e:
    log.critical(f"Error during output saving: {e}")
    if audit:
        audit.end_audit(status='failed', error_message=str(e))
    exit()

# 999. logger ends
runtime = time.time() - start_time
log.info(f"Pipeline runtime: {runtime:.2f} seconds")
log.info("=== PIPELINE ENDING ===")

# Finalizar auditoría
if audit:
    audit.end_audit(status='success')