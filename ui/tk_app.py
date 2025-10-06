# ui/tk_app.py (Tkinter interface, class‑based)
"""Tkinter front‑end for DPF app (class version).
> Encapsula estado en clase `App` para facilitar mantenimiento.
> Ejecuta pipeline en hilo, streamea log y gestiona cierre seguro.
"""
import pathlib    # -> para trabajar con paths, sin importar el sistema operativo
import subprocess # -> Te permite ejecutar comandos del sistema desde Python, como si abrieras una terminal y escribieras comandos.
import threading  # -> threading mantiene la interfaz "viva" mientras el trabajo pesado se ejecuta en paralelo.
import yaml
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox

THIS_DIR = pathlib.Path(__file__).resolve().parent
PROGRAM_DIR = (THIS_DIR / "../program").resolve()
CONFIG_PATH = PROGRAM_DIR / "config.yaml"
PIPELINE_PATH = PROGRAM_DIR / "pipeline.py"


class App(tk.Tk): # la clase hereda de tk.Tk > hace que la clase se convierta automaticamente en una ventana con todas sus funcionalidades.
    WIDTH, HEIGHT = 700, 500

    def __init__(self):
        super().__init__()
        self.title("DPF runner") # Llama al constructor de tk.Tk
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.resizable(False, False)

        # Estado
        self.running = False

        # Valores config iniciales
        self.cfg = self._load_config()

        # Tk variables
        self.var_input = tk.StringVar(value=self.cfg["input_file"])
        self.var_output = tk.StringVar(value=self.cfg["output_file"])
        self.var_tables = tk.StringVar(value=self.cfg["tables_path"])

        # UI
        self._build_ui()

    # ---------------------------------------------------------------------
    # Config helpers
    # ---------------------------------------------------------------------
    def _load_config(self):
        if CONFIG_PATH.exists():
            return yaml.safe_load(CONFIG_PATH.read_text())  #-> Si existe el archivo config.yaml > lo carga
        return {                                            #-> Si no existe, usa valores por defecto
            "input_file": str((THIS_DIR / "../inputs/input.xlsx").resolve()),
            "output_file": str((THIS_DIR / "../outputs/output.rpt").resolve()),
            "tables_path": str((THIS_DIR / "../tables").resolve()),
        }

    def _save_config(self):
        cfg = { # ingreso de configuraicon por el usuario
            "input_file": self.var_input.get(),
            "output_file": self.var_output.get(),
            "tables_path": self.var_tables.get(),
        }
        CONFIG_PATH.write_text(yaml.dump(cfg, sort_keys=False)) # -> imprime nuevamente el .yaml sin ordenar alfabeticamente las claves

    # ---------------------------------------------------------------------
    # UI building
    # ---------------------------------------------------------------------
    def _build_ui(self):
        frm_inputs = ttk.Frame(self, padding=10)
        frm_inputs.pack(fill="x")

        def make_browse_row(label, var, is_file=True):
            row = ttk.Frame(frm_inputs)
            ttk.Label(row, text=label, width=12).pack(side="left")
            ttk.Entry(row, textvariable=var, width=65).pack(side="left", padx=5)

            def browse():
                path = filedialog.askopenfilename() if is_file else filedialog.askdirectory()
                if path:
                    var.set(path)
            ttk.Button(row, text="...", command=browse, width=3).pack(side="left")
            row.pack(fill="x", pady=3)

        make_browse_row("Input file", self.var_input, True)
        make_browse_row("Output file", self.var_output, True)
        make_browse_row("Tables location", self.var_tables, False)

        # Botones
        frm_btn = ttk.Frame(self)
        frm_btn.pack(fill="x")

        ttk.Button(frm_btn, text="▶️  Run pipeline", width=20, command=self.on_run).pack(side="left", padx=10, pady=5)
        ttk.Button(frm_btn, text="Close", width=10, command=self.on_close).pack(side="right", padx=10, pady=5)

        # Log box
        self.log_box = scrolledtext.ScrolledText(self, height=20, font=("Consolas", 9))
        self.log_box.pack(fill="both", expand=True, padx=10, pady=5)

        # Cerrar con X
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------------------------------------------------------------
    # Pipeline execution
    # ---------------------------------------------------------------------
    def on_run(self):
        if self.running: # proteccion, en caso haya algo ejecutando en ese momento - warning - no action
            messagebox.showwarning("DPF", "Pipeline already running.")
            return
        self.log_box.delete(1.0, tk.END)    #-> limpia el log box
        self._save_config()                 #-> se guarda la config ingresada por el usuario
        threading.Thread(target=self._worker, daemon=True).start() # se ejecuta la funcion _worker y si se cierra la ventana se mata el proceso

    def _worker(self):
        self.running = True # -> control de estado - para evitar paralelos
        try:
            proc = subprocess.Popen(            # -> simil abrir terminal y ejecutar python pipeline.py
                ["python", str(PIPELINE_PATH)], # -> ejecuta el pipeline.py 
                stdout=subprocess.PIPE,         # -> captura la salida standard para el log
                stderr=subprocess.STDOUT,       # -> redirige errores a stout
                text=True,                      # -> texto, no bytes
                cwd=PIPELINE_PATH.parent,       # -> directorio donde ejecutar
            )
            for line in proc.stdout:                # -> captura los logs en tiempo real
                self.log_box.insert(tk.END, line)   # -> impresion del log
                self.log_box.see(tk.END)            # -> scroll automatico en caso de extenderse
            proc.wait()                             # -> Espera a que termine
            if proc.returncode == 0:                # -> 0 == exito
                messagebox.showinfo("DPF", "Pipeline finished ✔️")
            else:                                   # -> cualquier otro numero, error
                messagebox.showerror("DPF", f"Pipeline finished with code: {proc.returncode}")
        except FileNotFoundError:
            messagebox.showerror("DPF", "pipeline.py was not found.")
        finally:
            self.running = False # -> control de estado

    # ---------------------------------------------------------------------
    # Close logic
    # ---------------------------------------------------------------------
    def on_close(self):
        if self.running:
            ok = messagebox.askyesno("Confirmation", "The pipeline is still running.\nClosing this window will stop the current prcoess.\n¿Do you still want to exit?")
            if not ok:
                return
        self.destroy()


if __name__ == "__main__":
    App().mainloop()