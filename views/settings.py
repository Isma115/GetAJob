import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import messagebox, filedialog
from models.application import PersonalInfo
from utils.paths import DATA_DB_PATH, DATA_DIR, EXPORTS_DIR, ensure_data_dirs
from assets.styles.theme import (
    COLORS, create_label, create_button, create_card,
    create_entry, create_text
)

class SettingsView(tk.Frame):
    def __init__(self, parent, controllers):
        super().__init__(parent, bg=COLORS['background'])
        self.controllers = controllers
        self.info_controller = controllers['personal_info']
        self.setup_ui()

    def setup_ui(self):
        header = tk.Frame(self, bg=COLORS['background'])
        header.pack(fill='x', padx=16, pady=(16, 8))

        create_label(header, "Settings", 'heading').pack(side='left')

        content = tk.Frame(self, bg=COLORS['background'])
        content.pack(fill='both', expand=True, padx=16, pady=(0, 16))

        left = tk.Frame(content, bg=COLORS['background'])
        left.pack(side='left', fill='both', expand=True)

        right = tk.Frame(content, bg=COLORS['background'])
        right.pack(side='left', fill='both', expand=True, padx=(16, 0))

        self.personal_info_panel(left)
        self.data_management_panel(right)

    def personal_info_panel(self, parent):
        card = create_card(parent)
        card.pack(fill='both', expand=True)

        tk.Label(card, text="Información Personal", bg=COLORS['surface'],
                fg=COLORS['text_primary'], font=('Segoe UI', 15, 'bold')).pack(
                anchor='w', padx=12, pady=12)

        info = self.info_controller.get_personal_info()

        form_frame = tk.Frame(card, bg=COLORS['surface'])
        form_frame.pack(fill='x', padx=12, pady=(0, 12))

        fields = [
            ("Nombre Completo", "name", info.name if info else ""),
            ("Correo Electrónico", "email", info.email if info else ""),
            ("Teléfono", "phone", info.phone if info else ""),
            ("Dirección", "address", info.address if info else ""),
            ("URL de LinkedIn", "linkedin", info.linkedin if info else ""),
            ("URL de GitHub", "github", info.github if info else ""),
            ("Sitio Web/Portafolio", "website", info.website if info else ""),
        ]

        self.settings_entries = {}

        for label_text, key, value in fields:
            row = tk.Frame(form_frame, bg=COLORS['surface'])
            row.pack(fill='x', pady=4)
            tk.Label(row, text=label_text, bg=COLORS['surface'],
                    fg=COLORS['text_secondary'], font=('Segoe UI', 11)).pack(anchor='w')
            entry = create_entry(row, placeholder=label_text)
            entry.pack(fill='x')
            if value:
                entry.insert(0, value)
            self.settings_entries[key] = entry

        btn_row = tk.Frame(card, bg=COLORS['surface'])
        btn_row.pack(fill='x', padx=12, pady=(0, 12))

        save_btn = create_button(btn_row, "Guardar Información Personal",
                                 self.save_personal_info, 'primary')
        save_btn.pack(side='left', padx=4)

    def data_management_panel(self, parent):
        card = create_card(parent)
        card.pack(fill='both', expand=True)

        tk.Label(card, text="Gestión de Datos", bg=COLORS['surface'],
                fg=COLORS['text_primary'], font=('Segoe UI', 15, 'bold')).pack(
                anchor='w', padx=12, pady=12)

        actions = tk.Frame(card, bg=COLORS['surface'])
        actions.pack(fill='x', padx=12, pady=(0, 12))

        export_btn = create_button(actions, "Exportar Base de Datos",
                                   self.export_database, 'secondary')
        export_btn.pack(fill='x', pady=4)

        import_btn = create_button(actions, "Importar Base de Datos",
                                   self.import_database, 'secondary')
        import_btn.pack(fill='x', pady=4)

        csv_btn = create_button(actions, "Exportar Empresas (CSV)",
                               self.export_companies_csv, 'secondary')
        csv_btn.pack(fill='x', pady=4)

        info_frame = tk.Frame(card, bg=COLORS['surface'])
        info_frame.pack(fill='both', expand=True, padx=12, pady=(12, 12))

        tk.Label(info_frame, text="Acerca de JobBot", bg=COLORS['surface'],
                fg=COLORS['text_primary'], font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(8, 4))

        about_text = """
JobBot v1.0

Tu estación de trabajo todo-en-uno para solicitudes de empleo.
Indexa empresas, crea CVs, rastrea solicitudes,
y consegui más entrevistas más rápido.

Datos locales guardados en:
{data_dir}

Construido con Python Tkinter.
""".format(data_dir=DATA_DIR)
        tk.Label(info_frame, text=about_text, bg=COLORS['surface'],
                fg=COLORS['text_secondary'], justify='left').pack(anchor='w')

    def save_personal_info(self):
        info = PersonalInfo(
            name=self.settings_entries['name'].get(),
            email=self.settings_entries['email'].get(),
            phone=self.settings_entries['phone'].get(),
            address=self.settings_entries['address'].get(),
            linkedin=self.settings_entries['linkedin'].get(),
            github=self.settings_entries['github'].get(),
            website=self.settings_entries['website'].get()
        )
        self.info_controller.save_personal_info(info)
        messagebox.showinfo("Éxito", "¡Información personal guardada!")

    def export_database(self):
        ensure_data_dirs()
        filepath = filedialog.asksaveasfilename(
            initialdir=EXPORTS_DIR,
            initialfile="job_assistant_backup.db",
            defaultextension=".db",
            filetypes=[("Base de Datos SQLite", "*.db")]
        )
        if filepath:
            import shutil
            shutil.copy(DATA_DB_PATH, filepath)
            messagebox.showinfo("Éxito", f"Base de datos exportada a:\n{filepath}")

    def import_database(self):
        ensure_data_dirs()
        filepath = filedialog.askopenfilename(
            initialdir=EXPORTS_DIR,
            filetypes=[("Base de Datos SQLite", "*.db")]
        )
        if filepath:
            import shutil
            shutil.copy(filepath, DATA_DB_PATH)
            messagebox.showinfo("Éxito", "¡Base de datos importada! Reinicie para aplicar los cambios.")

    def export_companies_csv(self):
        ensure_data_dirs()
        filepath = filedialog.asksaveasfilename(
            initialdir=EXPORTS_DIR,
            initialfile="empresas.csv",
            defaultextension=".csv",
            filetypes=[("Archivo CSV", "*.csv")]
        )
        if filepath:
            companies = self.controllers['company'].get_all_companies()
            import csv
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Nombre", "Puesto", "Tipo de Trabajo", "Ubicación",
                               "Modalidad", "Salario Mínimo", "Salario Máximo",
                               "Tamaño de Empresa", "Industria", "Estado",
                               "Contactada", "Notas"])
                for c in companies:
                    writer.writerow([c.name, c.job_title, c.job_type,
                                   c.location, c.work_mode, c.salary_min,
                                   c.salary_max, c.company_size, c.industry,
                                   c.status, "Sí" if c.contacted else "No", c.notes])
            messagebox.showinfo("Éxito", f"Empresas exportadas a:\n{filepath}")
