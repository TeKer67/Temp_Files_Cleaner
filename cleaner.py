import os
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime, timedelta
import logging

# ================== CONFIGURACIÓN ==================

APP_NAME = "Temporary Files Cleaner"
VERSION = "1.0.0"

DAYS_THRESHOLD = 1          # Archivos más antiguos de X días
DRY_RUN_DEFAULT = True      # Siempre empieza en simulación
FORBIDDEN_EXT = (".exe", ".dll", ".sys", ".drv")

# Rutas TEMP reales y portables (sin usuario fijo)
TEMP_DIRS = [
    os.environ.get("TEMP"),
    os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Temp")
]

# Log
LOG_FILE = "cleaner.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ================== LÓGICA ==================

def is_safe_file(path):
    return not path.lower().endswith(FORBIDDEN_EXT)

def is_old_enough(path):
    try:
        return datetime.fromtimestamp(
            os.path.getmtime(path)
        ) < datetime.now() - timedelta(days=DAYS_THRESHOLD)
    except OSError:
        return False

def run_clean(dry_run=True):
    deleted = 0
    skipped = 0
    freed = 0

    output.delete("1.0", tk.END)
    mode = "SIMULACIÓN" if dry_run else "LIMPIEZA REAL"
    output.insert(tk.END, f"{APP_NAME} v{VERSION}\nModo: {mode}\n\n")
    logging.info(f"Inicio en modo {mode}")

    for base in TEMP_DIRS:
        if not base or not os.path.exists(base):
            continue

        output.insert(tk.END, f"Escaneando: {base}\n")

        for root, _, files in os.walk(base):
            for file in files:
                path = os.path.join(root, file)

                if not is_safe_file(path) or not is_old_enough(path):
                    skipped += 1
                    continue

                try:
                    size = os.path.getsize(path)
                    if not dry_run:
                        os.remove(path)

                    deleted += 1
                    freed += size

                    msg = f"{'Simulado' if dry_run else 'Borrado'}: {path}"
                    output.insert(tk.END, f"✔ {msg}\n")
                    logging.info(msg)

                except PermissionError:
                    skipped += 1
                    output.insert(tk.END, f"🔒 En uso: {path}\n")
                except OSError:
                    skipped += 1

        output.insert(tk.END, "\n")

    summary = (
        f"Resumen:\n"
        f"Archivos {'detectados' if dry_run else 'eliminados'}: {deleted}\n"
        f"Ignorados: {skipped}\n"
        f"Espacio {'estimado' if dry_run else 'liberado'}: {freed / (1024*1024):.2f} MB\n"
    )

    output.insert(tk.END, summary)
    logging.info(summary)
    messagebox.showinfo("Finalizado", summary)

# ================== GUI ==================

def start_dry_run():
    run_clean(dry_run=True)

def start_clean():
    if not messagebox.askyesno(
        "Confirmar limpieza",
        "Esto eliminará archivos temporales antiguos.\n¿Continuar?"
    ):
        return
    run_clean(dry_run=False)

root = tk.Tk()
root.title(f"{APP_NAME} v{VERSION}")
root.geometry("920x560")

frame = tk.Frame(root)
frame.pack(pady=5)

tk.Button(
    frame,
    text="Simulación (Dry-Run)",
    width=25,
    command=start_dry_run
).pack(side=tk.LEFT, padx=5)

tk.Button(
    frame,
    text="Limpiar ahora",
    width=25,
    command=start_clean
).pack(side=tk.LEFT, padx=5)

output = scrolledtext.ScrolledText(root, width=115, height=30)
output.pack(padx=10, pady=10)

root.mainloop()
