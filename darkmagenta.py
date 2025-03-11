import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

CONFIG_FILE = "config.json"

def load_config():
    """Carga la configuración desde el archivo JSON."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config
        except Exception as e:
            print("Error al cargar la configuración:", e)
    return {}

def save_config(config):
    """Guarda la configuración en el archivo JSON."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print("Error al guardar la configuración:", e)

def select_folder():
    """Abre un diálogo para seleccionar una carpeta y actualiza el entry correspondiente."""
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder_path)
        # Guardar la carpeta seleccionada en la configuración
        config = load_config()
        config["last_folder"] = folder_path
        save_config(config)

def search_only():
    """Busca la cadena en todos los archivos de la carpeta (y subcarpetas) sin reemplazarla.
    Por cada ocurrencia encontrada, se muestra la línea y columna."""
    folder = folder_entry.get()
    search_term = search_entry.get()
    
    if not folder:
        messagebox.showwarning("Advertencia", "Por favor, seleccione una carpeta.")
        return
    if not search_term:
        messagebox.showwarning("Advertencia", "Por favor, ingrese la cadena a buscar.")
        return

    # Limpiar el área de reporte
    report_text.delete(1.0, tk.END)
    
    total_files = 0
    total_occurrences = 0
    report = ""

    # Recorrer la carpeta y subcarpetas de forma recursiva
    for root_dir, _, files in os.walk(folder):
        for filename in files:
            file_path = os.path.join(root_dir, filename)
            total_files += 1
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
            except UnicodeDecodeError:
                # Ignorar archivos binarios sin error.
                continue
            except Exception as e:
                report += f"Error al leer {file_path}: {str(e)}\n"
                continue

            file_occurrences = []
            # Buscar ocurrencias en cada línea
            for line_num, line in enumerate(lines, start=1):
                start_index = 0
                while True:
                    index = line.find(search_term, start_index)
                    if index == -1:
                        break
                    # Se registra la ocurrencia (línea y columna, ambas a partir de 1)
                    file_occurrences.append((line_num, index + 1))
                    total_occurrences += 1
                    start_index = index + len(search_term)
            
            if file_occurrences:
                report += f"\nArchivo: {file_path}\n"
                for occ in file_occurrences:
                    report += f"  Línea {occ[0]}, Columna {occ[1]}\n"

    report += f"\nTotal de archivos analizados: {total_files}\n"
    report += f"Total de ocurrencias encontradas: {total_occurrences}\n"
    report_text.insert(tk.END, report)

def search_and_replace():
    """Busca y reemplaza la cadena en todos los archivos de la carpeta (y subcarpetas)."""
    folder = folder_entry.get()
    search_term = search_entry.get()
    replace_term = replace_entry.get()
    
    if not folder:
        messagebox.showwarning("Advertencia", "Por favor, seleccione una carpeta.")
        return
    if not search_term:
        messagebox.showwarning("Advertencia", "Por favor, ingrese la cadena a buscar.")
        return

    # Limpiar el área de reporte
    report_text.delete(1.0, tk.END)
    
    total_files = 0
    total_occurrences = 0
    modified_files = 0
    report = ""

    # Recorrer la carpeta y subcarpetas de forma recursiva
    for root_dir, _, files in os.walk(folder):
        for filename in files:
            file_path = os.path.join(root_dir, filename)
            total_files += 1
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
            except UnicodeDecodeError:
                # Ignorar archivos binarios
                continue
            except Exception as e:
                report += f"Error al leer {file_path}: {str(e)}\n"
                continue

            count = content.count(search_term)
            if count > 0:
                total_occurrences += count
                new_content = content.replace(search_term, replace_term)
                try:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(new_content)
                    modified_files += 1
                    report += f"{file_path}: {count} ocurrencia(s) reemplazada(s)\n"
                except Exception as e:
                    report += f"Error al escribir en {file_path}: {str(e)}\n"

    report += f"\nTotal de archivos analizados: {total_files}\n"
    report += f"Total de ocurrencias encontradas y reemplazadas: {total_occurrences}\n"
    report += f"Total de archivos modificados: {modified_files}\n"
    report_text.insert(tk.END, report)

# Configuración de la ventana principal usando ttkbootstrap
root = ttk.Window(themename="flatly")
root.title("Buscador y Reemplazador de Texto")

frame = ttk.Frame(root, padding=10)
frame.pack(fill="both", expand=True)

# Selección de carpeta
folder_label = ttk.Label(frame, text="Carpeta:")
folder_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
folder_entry = ttk.Entry(frame, width=50)
folder_entry.grid(row=0, column=1, padx=5, pady=5)
folder_button = ttk.Button(frame, text="Seleccionar carpeta", command=select_folder)
folder_button.grid(row=0, column=2, padx=5, pady=5)

# Cargar la última carpeta utilizada desde el archivo de configuración
config = load_config()
if "last_folder" in config:
    folder_entry.insert(0, config["last_folder"])

# Entrada para la cadena a buscar
search_label = ttk.Label(frame, text="Cadena a buscar:")
search_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
search_entry = ttk.Entry(frame, width=50)
search_entry.grid(row=1, column=1, padx=5, pady=5)

# Entrada para la cadena de reemplazo
replace_label = ttk.Label(frame, text="Cadena de reemplazo:")
replace_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
replace_entry = ttk.Entry(frame, width=50)
replace_entry.grid(row=2, column=1, padx=5, pady=5)

# Botones para ejecutar la búsqueda o búsqueda y reemplazo
search_button = ttk.Button(frame, text="Solo Buscar", command=search_only)
search_button.grid(row=3, column=0, padx=5, pady=10)
replace_button = ttk.Button(frame, text="Buscar y Reemplazar", command=search_and_replace)
replace_button.grid(row=3, column=1, padx=5, pady=10)

# Área de reporte con scroll para mostrar resultados
report_text = scrolledtext.ScrolledText(frame, wrap="word", width=80, height=20)
report_text.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

root.mainloop()
