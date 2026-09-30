import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import messagebox, filedialog
from utils.paths import ensure_data_dirs
from assets.styles.theme import (
    COLORS, create_label, create_button, create_card,
    create_entry, create_text
)

class CVGeneratorView(tk.Frame):
    def __init__(self, parent, controllers):
        super().__init__(parent, bg=COLORS['background'])
        self.controllers = controllers
        self.info_controller = controllers['personal_info']
        self.setup_ui()

    def setup_ui(self):
        header = tk.Frame(self, bg=COLORS['background'])
        header.pack(fill='x', padx=16, pady=(16, 8))
        create_label(header, "Generador de CV", 'heading').pack(side='left')

        content = tk.Frame(self, bg=COLORS['background'])
        content.pack(fill='both', expand=True, padx=16, pady=(0, 16))

        left = tk.Frame(content, bg=COLORS['background'])
        left.pack(side='left', fill='both', expand=True)

        right = tk.Frame(content, bg=COLORS['background'])
        right.pack(side='left', fill='both', expand=True, padx=(16, 0))

        self.job_offer_panel(left)
        self.right_panel(right)

    def job_offer_panel(self, parent):
        card = create_card(parent)
        card.pack(fill='both', expand=True)

        tk.Label(card, text="Oferta de Trabajo", bg=COLORS['surface'],
                fg=COLORS['text_primary'], font=('Segoe UI', 15, 'bold')).pack(
                anchor='w', padx=12, pady=12)

        instructions = tk.Frame(card, bg=COLORS['surface'])
        instructions.pack(fill='x', padx=12, pady=(0, 12))
        tk.Label(instructions, text="Pega aquí el texto completo de la oferta de trabajo.",
                bg=COLORS['surface'], fg=COLORS['text_secondary']).pack(anchor='w')

        text_frame = tk.Frame(card, bg=COLORS['background'])
        text_frame.pack(fill='both', expand=True, padx=12, pady=(0, 12))

        scroll_y = tk.Scrollbar(text_frame)
        scroll_y.pack(side='right', fill='y')

        self.job_offer_text = tk.Text(text_frame,
                                       bg=COLORS['surface'],
                                       fg=COLORS['text_primary'],
                                       font=('Consolas', 10),
                                       relief='flat',
                                       insertbackground=COLORS['text_primary'],
                                       yscrollcommand=scroll_y.set,
                                       wrap='word')
        self.job_offer_text.pack(side='left', fill='both', expand=True)
        scroll_y.config(command=self.job_offer_text.yview)

        btn_row = tk.Frame(card, bg=COLORS['surface'])
        btn_row.pack(fill='x', padx=12, pady=(0, 12))

        generate_btn = create_button(btn_row, "Generar Prompt",
                                     self.generate_prompt, 'primary')
        generate_btn.pack(side='left', padx=4)

        clear_offer_btn = create_button(btn_row, "Limpiar",
                                        lambda: self.job_offer_text.delete('1.0', 'end'),
                                        'secondary')
        clear_offer_btn.pack(side='left', padx=4)

    def right_panel(self, parent):
        prompt_card = create_card(parent)
        prompt_card.pack(fill='both', expand=True, pady=(0, 8))

        tk.Label(prompt_card, text="Prompt para IA", bg=COLORS['surface'],
                fg=COLORS['text_primary'], font=('Segoe UI', 15, 'bold')).pack(
                anchor='w', padx=12, pady=12)

        prompt_text_frame = tk.Frame(prompt_card, bg=COLORS['background'])
        prompt_text_frame.pack(fill='both', expand=True, padx=12, pady=(0, 12))

        scroll_prompt = tk.Scrollbar(prompt_text_frame)
        scroll_prompt.pack(side='right', fill='y')

        self.prompt_text = tk.Text(prompt_text_frame,
                                    bg=COLORS['surface'],
                                    fg=COLORS['text_primary'],
                                    font=('Consolas', 10),
                                    relief='flat',
                                    insertbackground=COLORS['text_primary'],
                                    yscrollcommand=scroll_prompt.set,
                                    wrap='word')
        self.prompt_text.pack(side='left', fill='both', expand=True)
        scroll_prompt.config(command=self.prompt_text.yview)

        prompt_btn_row = tk.Frame(prompt_card, bg=COLORS['surface'])
        prompt_btn_row.pack(fill='x', padx=12, pady=(0, 12))

        copy_btn = create_button(prompt_btn_row, "Copiar Prompt",
                                 self.copy_prompt, 'success')
        copy_btn.pack(side='left', padx=4)

        clear_prompt_btn = create_button(prompt_btn_row, "Limpiar",
                                         lambda: self.prompt_text.delete('1.0', 'end'),
                                         'secondary')
        clear_prompt_btn.pack(side='left', padx=4)

        response_card = create_card(parent)
        response_card.pack(fill='both', expand=True, pady=(8, 0))

        tk.Label(response_card, text="Respuesta de IA", bg=COLORS['surface'],
                fg=COLORS['text_primary'], font=('Segoe UI', 15, 'bold')).pack(
                anchor='w', padx=12, pady=12)

        tk.Label(response_card, text="Pega aquí el Markdown que devuelva la IA.",
                bg=COLORS['surface'], fg=COLORS['text_secondary']).pack(anchor='w', padx=12, pady=(0, 8))

        response_text_frame = tk.Frame(response_card, bg=COLORS['background'])
        response_text_frame.pack(fill='both', expand=True, padx=12, pady=(0, 8))

        scroll_resp = tk.Scrollbar(response_text_frame)
        scroll_resp.pack(side='right', fill='y')

        self.ai_response = tk.Text(response_text_frame,
                                    bg=COLORS['surface'],
                                    fg=COLORS['text_primary'],
                                    font=('Consolas', 10),
                                    relief='flat',
                                    insertbackground=COLORS['text_primary'],
                                    yscrollcommand=scroll_resp.set,
                                    wrap='word')
        self.ai_response.pack(side='left', fill='both', expand=True)
        scroll_resp.config(command=self.ai_response.yview)

        config_frame = tk.Frame(response_card, bg=COLORS['surface'])
        config_frame.pack(fill='x', padx=12, pady=(0, 8))

        dir_frame = tk.Frame(config_frame, bg=COLORS['surface'])
        dir_frame.pack(fill='x', pady=2)
        tk.Label(dir_frame, text="Directorio", bg=COLORS['surface'],
                fg=COLORS['text_secondary']).pack(side='left', padx=(0, 8))
        self.output_dir = create_entry(dir_frame, placeholder="~/Documents/outputGAJ")
        self.output_dir.pack(side='left', fill='x', expand=True, padx=(0, 4))

        browse_btn = create_button(dir_frame, "Explorar",
                                   self.browse_directory, 'secondary')
        browse_btn.pack(side='left')

        file_frame = tk.Frame(config_frame, bg=COLORS['surface'])
        file_frame.pack(fill='x', pady=2)
        tk.Label(file_frame, text="Archivo", bg=COLORS['surface'],
                fg=COLORS['text_secondary']).pack(side='left', padx=(0, 8))
        self.filename = create_entry(file_frame, placeholder="ej., CV.pdf")
        self.filename.insert(0, "Ismael_Moraleda_Lopez.pdf")
        self.filename.pack(side='left', fill='x', expand=True)

        response_btn_row = tk.Frame(response_card, bg=COLORS['surface'])
        response_btn_row.pack(fill='x', padx=12, pady=(0, 12))

        generate_pdf_btn = create_button(response_btn_row, "Generar PDF",
                                          self.generate_pdf, 'primary')
        generate_pdf_btn.pack(side='left', padx=4)

        clear_resp_btn = create_button(response_btn_row, "Limpiar",
                                       lambda: self.ai_response.delete('1.0', 'end'),
                                       'secondary')
        clear_resp_btn.pack(side='left', padx=4)

    def show_install_instructions(self):
        card = create_card(self)
        card.pack(fill='both', expand=True, padx=16, pady=16)

        tk.Label(card, text="Configuración de Generación de PDF Requerida", bg=COLORS['surface'],
                fg=COLORS['error'], font=('Segoe UI', 16, 'bold')).pack(pady=12)

        tk.Label(card, text="Para habilitar la generación de PDF, instale reportlab:", bg=COLORS['surface'],
                fg=COLORS['text_primary']).pack(pady=8)

        install_text = """
Ejecute este comando en su terminal:

pip install reportlab

Luego reinicie la aplicación.
"""
        tk.Label(card, text=install_text, bg=COLORS['surface'],
                fg=COLORS['accent'], font=('Consolas', 13)).pack(pady=12)

    def generate_prompt(self):
        offer = self.job_offer_text.get('1.0', 'end').strip()
        if not offer:
            messagebox.showwarning("Advertencia", "Por favor pega primero una oferta de trabajo")
            return

        info = self.info_controller.get_personal_info()

        personal_data = ""
        if info:
            personal_data = f"""Información Personal:
- Nombre: {info.name or 'N/A'}
- Correo: {info.email or 'N/A'}
- Teléfono: {info.phone or 'N/A'}
- Ubicación: {info.address or 'N/A'}
- LinkedIn: {info.linkedin or 'N/A'}
- GitHub: {info.github or 'N/A'}
- Sitio Web: {info.website or 'N/A'}"""

        prompt = f"""Eres un asesor de carrera experto en CVs. A partir de la siguiente oferta de trabajo y la información personal del candidato, genera un CV profesional en formato Markdown optimizado para esta oferta concreta.

## Oferta de Trabajo

{offer}

## {personal_data}

Estructura requerida del CV:
1. **Encabezado** — Nombre completo, título profesional alineado con la oferta, ubicación, teléfono, email, LinkedIn.
2. **Resumen Profesional** — 3-4 líneas adaptadas a los requisitos de la oferta. Incluye palabras clave del anuncio.
3. **Experiencia Laboral** — Formato: *Puesto | Empresa | Fechas*. Debajo, 3-5 viñetas con logros cuantificables. Prioriza experiencias relevantes para esta oferta.
4. **Educación** — Título, institución, año.
5. **Habilidades Técnicas** — Categorizadas. Prioriza las mencionadas en la oferta.
6. **Idiomas** — Nivel por idioma.
7. **Certificaciones** (si aplica).

Formato: Markdown limpio, sin columnas, sin tablas, sin gráficos. Diseño 100% texto, máximo una página. Compatible con ATS. No incluyas explicaciones adicionales, solo el CV."""

        self.prompt_text.delete('1.0', 'end')
        self.prompt_text.insert('1.0', prompt)

    def copy_prompt(self):
        prompt = self.prompt_text.get('1.0', 'end').strip()
        if not prompt:
            messagebox.showwarning("Advertencia", "No hay prompt para copiar")
            return
        self.clipboard_clear()
        self.clipboard_append(prompt)
        messagebox.showinfo("Éxito", "¡Prompt copiado al portapapeles!")

    def browse_directory(self):
        ensure_data_dirs()
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.delete(0, 'end')
            self.output_dir.insert(0, directory)

    def parse_markdown_cv(self, md_text):
        lines = md_text.split('\n')
        sections = []
        current_section = {'title': '', 'content': []}

        for line in lines:
            if line.startswith('# ') and not current_section['content']:
                current_section['title'] = line[2:].strip()
            elif line.startswith('## '):
                if current_section['title'] or current_section['content']:
                    sections.append(current_section)
                current_section = {'title': line[2:].strip(), 'content': []}
            elif line.strip():
                current_section['content'].append(line.strip())
            elif not line.strip() and current_section['content']:
                current_section['content'].append('')

        if current_section['title'] or current_section['content']:
            sections.append(current_section)

        return sections

    def generate_pdf(self):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.enums import TA_CENTER
        except ImportError:
            self.show_install_instructions()
            messagebox.showwarning("Advertencia", "Instale reportlab para generar PDFs")
            return

        md_text = self.ai_response.get('1.0', 'end').strip()
        if not md_text:
            messagebox.showwarning("Advertencia", "Por favor pega primero la respuesta de la IA")
            return

        if not self.filename.get():
            messagebox.showwarning("Advertencia", "Por favor especifica un nombre de archivo")
            return

        filename = self.filename.get()
        if not filename.endswith('.pdf'):
            filename += '.pdf'

        output_dir = self.output_dir.get().strip()
        if not output_dir:
            output_dir = os.path.expanduser("~/Documents/outputGAJ")
        if output_dir == "~/Documents/outputGAJ":
            output_dir = os.path.expanduser("~/Documents/outputGAJ")
        ensure_data_dirs()
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, filename)

        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4,
                                    rightMargin=2*cm, leftMargin=2*cm,
                                    topMargin=2*cm, bottomMargin=2*cm)

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('CustomTitle',
                                         parent=styles['Heading1'],
                                         fontSize=24,
                                         textColor=COLORS['primary'] if isinstance(COLORS['primary'], str) and COLORS['primary'].startswith('#') else None,
                                         spaceAfter=20,
                                         alignment=TA_CENTER)

            heading_style = ParagraphStyle('CustomHeading',
                                           parent=styles['Heading2'],
                                           fontSize=14,
                                           spaceBefore=16,
                                           spaceAfter=8)

            body_data = self.parse_markdown_cv(md_text)
            story = []

            for section in body_data:
                title = section['title']
                content = section['content']

                if title == '' and content:
                    if content[0].startswith('# '):
                        story.append(Paragraph(content[0][2:], title_style))
                    else:
                        for line in content:
                            story.append(Paragraph(line, styles['Normal']))
                        story.append(Spacer(1, 12))
                elif title:
                    story.append(Paragraph(title, heading_style))
                    for line in content:
                        story.append(Paragraph(line, styles['Normal']))
                    story.append(Spacer(1, 8))

            doc.build(story)
            messagebox.showinfo("Éxito", f"¡PDF generado exitosamente!\n\nGuardado en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar PDF:\n{str(e)}")
