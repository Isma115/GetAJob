import sys
import os
from importlib import import_module

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import messagebox

from utils.database import get_db
from controllers import (
    CompanyController, ApplicationController, PersonalInfoController,
    TemplateController, PromptHistoryController
)
from assets.styles.theme import COLORS, apply_theme, FONT_BOLD


VIEW_CLASSES = {
    'companies': ('views.companies', 'CompaniesView'),
    'ai_prompt': ('views.ai_prompt', 'AIPromptView'),
    'cv_generator': ('views.cv_generator', 'CVGeneratorView'),
    'settings': ('views.settings', 'SettingsView'),
    'email_templates': ('views.email_templates', 'EmailTemplatesView'),
    'interview_prep': ('views.interview_prep', 'InterviewPrepView'),
}


class JobBotApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JobBot - Asistente de Búsqueda de Empleo")
        self.root.geometry("1280x820")
        self.root.minsize(1080, 680)

        apply_theme(self.root)

        self.db = get_db()

        self.controllers = {
            'company': CompanyController(),
            'application': ApplicationController(),
            'personal_info': PersonalInfoController(),
            'template': TemplateController(),
            'prompt': PromptHistoryController()
        }

        self.setup_ui()

    def setup_ui(self):
        nav = tk.Frame(self.root, bg=COLORS['secondary'], width=280)
        nav.pack(side='left', fill='y')
        nav.pack_propagate(False)

        self.nav_panel = NavigationPanel(nav, self.on_navigate)
        self.nav_panel.pack(fill='both', expand=True)

        self.content_area = tk.Frame(self.root, bg=COLORS['background'])
        self.content_area.pack(side='right', fill='both', expand=True)

        self.views = {}

        for key in VIEW_CLASSES.keys():
            self.get_view(key)

        self.show_view('companies')
    
    def _preload_views(self):
        for key in VIEW_CLASSES.keys():
            if key not in self.views:
                self.get_view(key)

    def on_navigate(self, key):
        self.nav_panel.highlight_active(key)
        self.show_view(key)

    def show_view(self, key):
        view = self.get_view(key)
        if hasattr(view, 'refresh') and getattr(view, '_has_been_shown', False):
            view.refresh()

        view._has_been_shown = True
        view.tkraise()

    def get_view(self, key):
        if key not in self.views:
            module_name, class_name = VIEW_CLASSES[key]
            module = import_module(module_name)
            view_class = getattr(module, class_name)
            view = view_class(self.content_area, self.controllers)
            view.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.views[key] = view
        return self.views[key]

    def run(self):
        self.root.mainloop()


class NavigationPanel(tk.Frame):
    def __init__(self, parent, on_navigate):
        super().__init__(parent, bg=COLORS['secondary'], width=280)
        self.on_navigate = on_navigate
        self.active_key = None
        self.nav_widgets = {}
        self.setup_ui()

    def setup_ui(self):
        brand = tk.Frame(self, bg=COLORS['secondary'])
        brand.pack(fill='x', padx=24, pady=(28, 8))

        title = tk.Label(brand, text="JobBot", bg=COLORS['secondary'],
                         fg=COLORS['text_primary'], font=('Segoe UI', 22, 'bold'))
        title.pack(anchor='w')

        subtitle = tk.Label(brand, text="Asistente de búsqueda de empleo",
                            bg=COLORS['secondary'],
                            fg=COLORS['text_secondary'], font=('Segoe UI', 12))
        subtitle.pack(anchor='w', pady=(4, 0))

        separator = tk.Frame(self, bg=COLORS['border'], height=1)
        separator.pack(fill='x', padx=24, pady=(18, 18))

        nav_items = [
            ("Empresas", "companies"),
            ("Prompt AI", "ai_prompt"),
            ("Generador CV", "cv_generator"),
            ("Plantillas de Correo", "email_templates"),
            ("Preparación Entrevistas", "interview_prep"),
            ("Configuración", "settings"),
        ]

        for text, key in nav_items:
            row = tk.Frame(self, bg=COLORS['secondary'], cursor='hand2')
            row.pack(fill='x', padx=14, pady=3)

            accent = tk.Frame(row, bg=COLORS['secondary'], width=4)
            accent.pack(side='left', fill='y')

            label = tk.Label(row, text=text, bg=COLORS['secondary'],
                             fg=COLORS['text_secondary'],
                             font=FONT_BOLD,
                             anchor='w', padx=16, pady=14,
                             cursor='hand2')
            label.pack(side='left', fill='x', expand=True)

            self.nav_widgets[key] = (row, accent, label)
            for widget in (row, accent, label):
                widget.bind('<Button-1>', lambda event, k=key: self.on_navigate(k))
                widget.bind('<Enter>', lambda event, k=key: self.set_hover(k, True))
                widget.bind('<Leave>', lambda event, k=key: self.set_hover(k, False))

        self.highlight_active("companies")

    def set_hover(self, key, hovering):
        if key == self.active_key:
            return

        row, accent, label = self.nav_widgets[key]
        bg = COLORS['nav_hover'] if hovering else COLORS['secondary']
        for widget in (row, accent, label):
            widget.config(bg=bg)
        label.config(fg=COLORS['text_primary'] if hovering else COLORS['text_secondary'])

    def highlight_active(self, key):
        self.active_key = key
        for item_key, (row, accent, label) in self.nav_widgets.items():
            active = item_key == key
            bg = COLORS['nav_active'] if active else COLORS['secondary']
            accent_bg = COLORS['accent'] if active else bg
            fg = COLORS['text_primary'] if active else COLORS['text_secondary']

            row.config(bg=bg)
            accent.config(bg=accent_bg)
            label.config(bg=bg, fg=fg)


def main():
    try:
        app = JobBotApplication()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Application error:\n{str(e)}")
        raise


if __name__ == "__main__":
    main()
