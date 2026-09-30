import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import messagebox
from assets.styles.theme import (
    COLORS, create_label, create_button, create_card,
    create_entry, create_text, create_combobox
)

class EmailTemplatesView(tk.Frame):
    def __init__(self, parent, controllers):
        super().__init__(parent, bg=COLORS['background'])
        self.controllers = controllers
        self.info_controller = controllers['personal_info']
        self.company_controller = controllers['company']
        self.setup_ui()

    def setup_ui(self):
        header = tk.Frame(self, bg=COLORS['background'])
        header.pack(fill='x', padx=16, pady=(16, 8))

        create_label(header, "Plantillas de Correo", 'heading').pack(side='left')

        content = tk.Frame(self, bg=COLORS['background'])
        content.pack(fill='both', expand=True, padx=16, pady=(0, 16))

        left = tk.Frame(content, bg=COLORS['background'])
        left.pack(side='left', fill='both', expand=True)

        right = tk.Frame(content, bg=COLORS['background'])
        right.pack(side='left', fill='both', expand=True, padx=(16, 0))

        self.template_selector(left)
        self.email_preview(right)

    def template_selector(self, parent):
        card = create_card(parent)
        card.pack(fill='both', expand=True)

        tk.Label(card, text="Seleccionar Tipo de Plantilla", bg=COLORS['surface'],
                fg=COLORS['text_primary'], font=('Segoe UI', 15, 'bold')).pack(
                anchor='w', padx=12, pady=12)

        templates = [
            ("Seguimiento de Solicitud", "followup"),
            ("Agradecimiento de Entrevista", "thankyou"),
            ("Consulta de Networking", "networking"),
            ("Solicitud de Referido", "referral"),
        ]

        self.email_type = tk.StringVar(value="followup")

        for text, key in templates:
            rb = tk.Radiobutton(card, text=text, variable=self.email_type,
                          value=key, bg=COLORS['surface'],
                          fg=COLORS['text_primary'], selectcolor=COLORS['primary'])
            rb.pack(anchor='w', padx=24, pady=4)

        form_frame = tk.Frame(card, bg=COLORS['surface'])
        form_frame.pack(fill='x', padx=12, pady=16)

        row1 = tk.Frame(form_frame, bg=COLORS['surface'])
        row1.pack(fill='x', pady=4)
        tk.Label(row1, text="Empresa", bg=COLORS['surface'],
                fg=COLORS['text_secondary']).pack(anchor='w')
        companies = self.company_controller.get_all_companies()
        self.company_combo = create_combobox(row1, ["Seleccionar..."] + [c.name for c in companies])
        self.company_combo.pack(fill='x', pady=(4, 8))

        row2 = tk.Frame(form_frame, bg=COLORS['surface'])
        row2.pack(fill='x', pady=4)
        tk.Label(row2, text="Correo del Destinatario", bg=COLORS['surface'],
                fg=COLORS['text_secondary']).pack(anchor='w')
        self.recipient_email = create_entry(row2, placeholder="reclutador@empresa.com")
        self.recipient_email.pack(fill='x', pady=(4, 8))

        row3 = tk.Frame(form_frame, bg=COLORS['surface'])
        row3.pack(fill='x', pady=4)
        tk.Label(row3, text="Línea de Asunto", bg=COLORS['surface'],
                fg=COLORS['text_secondary']).pack(anchor='w')
        self.subject = create_entry(row3, placeholder="Asunto del correo")
        self.subject.pack(fill='x', pady=(4, 8))

        row4 = tk.Frame(form_frame, bg=COLORS['surface'])
        row4.pack(fill='x', pady=4)
        tk.Label(row4, text="Mensaje Personalizado", bg=COLORS['surface'],
                fg=COLORS['text_secondary']).pack(anchor='w')
        self.custom_msg = create_text(row4, height=3, width=40)
        self.custom_msg.pack(pady=(4, 8))

        btn_row = tk.Frame(card, bg=COLORS['surface'])
        btn_row.pack(fill='x', padx=12, pady=(0, 12))

        generate_btn = create_button(btn_row, "Generar Correo",
                                     self.generate_email, 'primary')
        generate_btn.pack(side='left', padx=4)

        clear_btn = create_button(btn_row, "Limpiar", self.clear_form, 'secondary')
        clear_btn.pack(side='left', padx=4)

    def email_preview(self, parent):
        card = create_card(parent)
        card.pack(fill='both', expand=True)

        tk.Label(card, text="Vista Previa del Correo", bg=COLORS['surface'],
                fg=COLORS['text_primary'], font=('Segoe UI', 15, 'bold')).pack(
                anchor='w', padx=12, pady=12)

        self.subject_preview = tk.Label(card, text="Asunto: ",
                                        bg=COLORS['surface'],
                                        fg=COLORS['text_secondary'])
        self.subject_preview.pack(anchor='w', padx=12, pady=(0, 4))

        text_frame = tk.Frame(card, bg=COLORS['background'])
        text_frame.pack(fill='both', expand=True, padx=12, pady=(0, 12))

        scroll_y = tk.Scrollbar(text_frame)
        scroll_y.pack(side='right', fill='y')

        self.email_text = tk.Text(text_frame, bg=COLORS['surface'],
                                  fg=COLORS['text_primary'],
                                  font=('Consolas', 12),
                                  relief='flat',
                                  insertbackground=COLORS['text_primary'],
                                  yscrollcommand=scroll_y.set,
                                  wrap='word')
        self.email_text.pack(side='left', fill='both', expand=True)
        scroll_y.config(command=self.email_text.yview)

        btn_row = tk.Frame(card, bg=COLORS['surface'])
        btn_row.pack(fill='x', padx=12, pady=(0, 12))

        copy_btn = create_button(btn_row, "Copiar al Portapapeles",
                                 self.copy_email, 'success')
        copy_btn.pack(side='left', padx=4)

    def generate_email(self):
        info = self.info_controller.get_personal_info()
        if not info:
            messagebox.showwarning("Advertencia", "Por favor agregue su información personal en Configuración")
            return

        company = self.company_combo.get()
        email_type = self.email_type.get()
        subject = self.subject.get()
        custom = self.custom_msg.get('1.0', 'end').strip()

        if email_type == "followup":
            self.generate_followup(info, company, subject, custom)
        elif email_type == "thankyou":
            self.generate_thankyou(info, company, subject, custom)
        elif email_type == "networking":
            self.generate_networking(info, subject, custom)
        elif email_type == "referral":
            self.generate_referral(info, subject, custom)

    def generate_followup(self, info, company, subject, custom):
        subject_text = subject or f"Siguiendo Mi Solicitud - Para {company}"
        self.subject_preview.config(text=f"Asunto: {subject_text}")

        company_display = company if company != 'Seleccionar...' else '[Nombre de la Empresa]'
        body = f"""Hola,

Espero que este correo le encuentre bien. Quería hacer seguimiento a mi solicitud para el puesto en {company_display}.

{"Estoy muy entusiasmado con la oportunidad de contribuir a su equipo." if not custom else custom}

Le agradecería mucho cualquier actualización sobre el calendario de contratación o información adicional que pueda necesitar de mi parte.

Gracias por su tiempo y consideración.

Atentamente,
{info.name}
{info.email}
{info.phone}"""

        self.email_text.delete('1.0', 'end')
        self.email_text.insert('1.0', body)

    def generate_thankyou(self, info, company, subject, custom):
        subject_text = subject or f"Gracias - Entrevista para {company}"
        self.subject_preview.config(text=f"Asunto: {subject_text}")

        company_display = company if company != 'Seleccionar...' else '[Empresa]'
        body = f"""Hola,

Gracias por tomarse el tiempo de hablar conmigo hoy sobre el puesto en {company_display}.

{"Disfruté conocer más sobre el equipo y el emocionante trabajo que se realiza en la empresa." if not custom else custom}

Estoy muy interesado en la oportunidad y creo que mis habilidades y experiencia serían una gran opción para el rol.

No dude en contactarme si necesita información adicional.

Atentamente,
{info.name}
{info.email}
{info.phone}"""

        self.email_text.delete('1.0', 'end')
        self.email_text.insert('1.0', body)

    def generate_networking(self, info, subject, custom):
        subject_text = subject or "Solicitud de Contacto"
        self.subject_preview.config(text=f"Asunto: {subject_text}")

        body = f"""Hola,

Espero que esté bien. Vi su perfil y me impresiona su trayectoria profesional.

{"Actualmente estoy explorando oportunidades en desarrollo de software y me encantaría conectar." if not custom else custom}

Si tiene tiempo para una breve llamada o puede compartir algún conocimiento sobre la industria, lo agradecería mucho.

Gracias por su tiempo.

Atentamente,
{info.name}
{info.email}
{info.phone}"""

        self.email_text.delete('1.0', 'end')
        self.email_text.insert('1.0', body)

    def generate_referral(self, info, subject, custom):
        subject_text = subject or f"Solicitud de Referido - {info.name}"
        self.subject_preview.config(text=f"Asunto: {subject_text}")

        company_name = self.company_combo.get() if self.company_combo.get() != 'Seleccionar...' else '[Empresa]'

        body = f"""Hola,

Espero que este mensaje le encuentre bien. Estoy buscando activamente nuevas oportunidades en desarrollo de software y noté que {company_name} tiene un equipo al que me encantaría unirme.

{"Confío en que mi experiencia traería valor al equipo y estaría agradecido por cualquier referido que pueda proporcionar." if not custom else custom}

He adjuntado mi currículum para su referencia. Por favor, hágame saber si tiene alguna pregunta.

Gracias por su apoyo.

Atentamente,
{info.name}
{info.email}
{info.phone}"""

        self.email_text.delete('1.0', 'end')
        self.email_text.insert('1.0', body)

    def copy_email(self):
        text = self.email_text.get('1.0', 'end').strip()
        if not text:
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Éxito", "¡Correo copiado!")

    def clear_form(self):
        self.company_combo.set("Seleccionar...")
        self.recipient_email.delete(0, 'end')
        self.subject.delete(0, 'end')
        self.custom_msg.delete('1.0', 'end')
        self.email_text.delete('1.0', 'end')
        self.subject_preview.config(text="Asunto: ")
