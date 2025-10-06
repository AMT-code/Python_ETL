import yaml
import os
import sys
import time
from reader import read_input
from writer import write_csv, write_rpt
from logger import Logger
from transformers.engine import apply_transformations

# 0. logger init
# Detectar si se ejecuta desde subprocess (sin terminal interactiva)
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
    log.success(f"Setting input file location: {config['input_file']}")
    # Log configuración del archivo de input si existe
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

    if input_file.startswith("input"):  # Ruta relativa al proyecto
        input_path = os.path.join(script_dir, "..", input_file)
    else:                               # Ruta absoluta
        input_path = input_file
    
    # Obtener configuración del archivo de input
    input_file_config = config.get('input_file_config', None)
    
    df = read_input(input_path, file_config=input_file_config)
    log.success(f"{len(df)} lines read")
    
    # Log adicional sobre cómo se leyó el archivo
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
    exit()

# 3. applying transformation
try:
    df = apply_transformations(df, config, log, script_dir)
except Exception as e:
    log.critical(f"Error during transformations: {e} --> PROCESS ENDED")
    exit()

# 4. printing output
try:
    output_path = "../" + config["output_file"]
    output_file = os.path.basename(output_path)
    ext = os.path.splitext(output_path)[-1].lower()
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
except Exception as e:
    log.critical(f"Error during output saving: {e}")
    exit()

# 999. logger ends
runtime = time.time() - start_time  # <-- Calcula el runtime
log.info(f"Pipeline runtime: {runtime:.2f} seconds")  # <-- Imprime el runtime
log.info("=== PIPELINE ENDING ===")