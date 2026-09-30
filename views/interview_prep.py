import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import messagebox
from assets.styles.theme import (
    COLORS, create_label, create_button, create_card,
    create_entry, create_text
)

class InterviewPrepView(tk.Frame):
    def __init__(self, parent, controllers):
        super().__init__(parent, bg=COLORS['background'])
        self.controllers = controllers
        self.company_controller = controllers['company']
        self.setup_ui()

    def setup_ui(self):
        header = tk.Frame(self, bg=COLORS['background'])
        header.pack(fill='x', padx=16, pady=(16, 8))

        create_label(header, "Preparación para Entrevistas", 'heading').pack(side='left')

        content = tk.Frame(self, bg=COLORS['background'])
        content.pack(fill='both', expand=True, padx=16, pady=(0, 16))

        left = tk.Frame(content, bg=COLORS['background'])
        left.pack(side='left', fill='both', expand=True)

        right = tk.Frame(content, bg=COLORS['background'])
        right.pack(side='left', fill='both', expand=True, padx=(16, 0))

        self.common_questions_panel(left)
        self.notes_panel(right)

    def common_questions_panel(self, parent):
        card = create_card(parent)
        card.pack(fill='both', expand=True)

        tk.Label(card, text="Preguntas Comunes", bg=COLORS['surface'],
                fg=COLORS['text_primary'], font=('Segoe UI', 15, 'bold')).pack(
                anchor='w', padx=12, pady=12)

        questions = [
            ("Cuéntame sobre ti", "Respuesta de más de 400 caracteres"),
            ("¿Por qué esta empresa?", "Investigar la misión y valores de la empresa"),
            ("Tu mayor fortaleza", "Habilidades técnicas + Blandas"),
            ("Tu debilidad", "Cómo la superas"),
            ("¿Por qué deberíamos contratarte?", "Propuesta de valor"),
            ("Expectativas de salario", "Investigación de mercado + rango"),
            ("¿Dónde te ves en 5 años?", "Alineación profesional"),
            ("Describe un proyecto desafiante", "Método STAR situación/tarea/acción/resultado"),
            ("Desafío técnico de codificación", "Practicar en LeetCode/HackerRank"),
            ("Preguntas de diseño de sistemas", "Escalabilidad, APIs, bases de datos"),
        ]

        list_frame = tk.Frame(card, bg=COLORS['surface'])
        list_frame.pack(fill='both', expand=True, padx=12, pady=(0, 12))

        canvas = tk.Canvas(list_frame, bg=COLORS['surface'], highlightthickness=0)
        scroll_y = tk.Scrollbar(list_frame, orient='vertical', command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=COLORS['surface'])
        scroll_window = canvas.create_window((0, 0), window=scroll_frame, anchor='nw')

        canvas.configure(yscrollcommand=scroll_y.set)
        canvas.pack(side='left', fill='both', expand=True)
        scroll_y.pack(side='right', fill='y')

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
        scroll_frame.bind('<Configure>', on_configure)

        for i, (question, tip) in enumerate(questions):
            q_frame = tk.Frame(scroll_frame, bg=COLORS['surface'])
            q_frame.pack(fill='x', padx=8, pady=4)

            num = tk.Label(q_frame, text=f"{i+1}.", bg=COLORS['surface'],
                          fg=COLORS['primary'], font=('Segoe UI', 12, 'bold'))
            num.pack(side='left', padx=(0, 4))

            text_col = tk.Frame(q_frame, bg=COLORS['surface'])
            text_col.pack(side='left', fill='x', expand=True)

            tk.Label(text_col, text=question, bg=COLORS['surface'],
                    fg=COLORS['text_primary'], font=('Segoe UI', 12)).pack(anchor='w')

            tk.Label(text_col, text=tip, bg=COLORS['surface'],
                    fg=COLORS['text_secondary'], font=('Segoe UI', 10)).pack(anchor='w')

        btn_row = tk.Frame(card, bg=COLORS['surface'])
        btn_row.pack(fill='x', padx=12, pady=(0, 12))

        copy_btn = create_button(btn_row, "Copiar Todas las Preguntas",
                                 self.copy_questions, 'primary')
        copy_btn.pack(side='left', padx=4)

    def notes_panel(self, parent):
        card = create_card(parent)
        card.pack(fill='both', expand=True)

        tk.Label(card, text="Mis Notas", bg=COLORS['surface'],
                fg=COLORS['text_primary'], font=('Segoe UI', 15, 'bold')).pack(
                anchor='w', padx=12, pady=12)

        row1 = tk.Frame(card, bg=COLORS['surface'])
        row1.pack(fill='x', padx=12, pady=(0, 8))
        tk.Label(row1, text="Empresa a preparar:", bg=COLORS['surface'],
                fg=COLORS['text_secondary']).pack(anchor='w')
        companies = self.company_controller.get_all_companies()
        self.company_combo = tk.ttk.Combobox(row1, values=["Seleccionar..."] + [c.name for c in companies],
                                             state='readonly')
        self.company_combo.pack(fill='x', pady=(4, 0))
        self.company_combo.current(0)

        row2 = tk.Frame(card, bg=COLORS['surface'])
        row2.pack(fill='both', expand=True, padx=12, pady=(0, 12))

        self.notes_text = tk.Text(row2, bg=COLORS['background'],
                                   fg=COLORS['text_primary'],
                                   font=('Consolas', 12),
                                   relief='flat',
                                   insertbackground=COLORS['text_primary'],
                                   wrap='word')
        self.notes_text.pack(fill='both', expand=True)

        placeholder = """Mis Notas de Entrevista:

Investigación de la Empresa:
-

Puntos Clave a Mencionar:
-

Preguntas a Hacer:
-

Acciones de Seguimiento:
-
"""
        self.notes_text.insert('1.0', placeholder)

        btn_row = tk.Frame(card, bg=COLORS['surface'])
        btn_row.pack(fill='x', padx=12, pady=(0, 12))

        save_btn = create_button(btn_row, "Guardar Notas",
                                 self.save_notes, 'primary')
        save_btn.pack(side='left', padx=4)

        clear_btn = create_button(btn_row, "Limpiar", self.clear_notes, 'secondary')
        clear_btn.pack(side='left', padx=4)

    def copy_questions(self):
        questions_text = """PREGUNTAS COMUNES DE ENTREVISTA:

1. Cuéntame sobre ti
   - Mantenlo bajo 2 minutos, historial profesional + propuesta de valor

2. ¿Por qué esta empresa?
   - Investigar: misión, valores, noticias recientes, productos

3. Tu mayor fortaleza
   - Habilidad técnica + cómo benefició a tu equipo/proyecto

4. Tu debilidad
   - Debilidad real + cómo la estás superando

5. ¿Por qué deberíamos contratarte?
   - 3 cualidades clave que coinciden con la descripción del puesto

6. Expectativas de salario
   - Investigación de mercado, tener un rango listo

7. ¿Dónde te ves en 5 años?
   - Alineado con oportunidades de crecimiento de la empresa

8. Describe un proyecto desafiante (Método STAR)
   - Situación: contexto
   - Tarea: tu responsabilidad
   - Acción: lo que hiciste
   - Resultado: resultado/impacto

9. Desafío Técnico/Codificación
   - Practicar estructuras de datos y algoritmos
   - LeetCode, HackerRank, Codewars

10. Diseño de Sistemas
    - Pensar en voz alta: escalabilidad, APIs, bases de datos, microservicios
"""
        self.clipboard_clear()
        self.clipboard_append(questions_text)
        messagebox.showinfo("Éxito", "¡Preguntas copiadas!")

    def save_notes(self):
        company = self.company_combo.get()
        if company == "Seleccionar...":
            messagebox.showwarning("Advertencia", "Seleccione una empresa primero")
            return
        notes = self.notes_text.get('1.0', 'end')
        messagebox.showinfo("Guardado", f"Notas guardadas para {company}")

    def clear_notes(self):
        self.notes_text.delete('1.0', 'end')
        self.notes_text.insert('1.0', "Mis Notas de Entrevista:\n\n-\n")
