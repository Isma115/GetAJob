import sys
import os
import html
import json
import queue
import re
import threading
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import messagebox, filedialog
from models.company import Company
from assets.styles.theme import (
    COLORS, create_label, create_button, create_card,
    create_entry, create_text, create_combobox, STATUS_COLORS,
    FONT_HEADING, FONT_PRIMARY
)
from controllers.company_controller import CompanyController

class CompaniesView(tk.Frame):
    def __init__(self, parent, controllers):
        super().__init__(parent, bg=COLORS['background'])
        self.controllers = controllers
        self.controller = controllers['company']
        self.current_edit_id = None
        self.locator_running = False
        self.locator_cancelled = False
        self.setup_ui()

    def setup_ui(self):
        self.list_view = tk.Frame(self, bg=COLORS['background'])
        self.list_view.pack(fill='both', expand=True)

        toolbar = tk.Frame(self.list_view, bg=COLORS['background'])
        toolbar.pack(fill='x', padx=16, pady=(16, 8))

        create_label(toolbar, "Empresas", 'heading').pack(side='left')

        add_btn = create_button(toolbar, "+ Añadir Empresa", self.show_add_form, 'primary')
        add_btn.pack(side='right')

        locate_btn = create_button(toolbar, "Localizar Empresas", self.show_locator_config_modal, 'secondary')
        locate_btn.pack(side='right', padx=(0, 8))

        prompt_btn = create_button(toolbar, "Prompt Búsqueda", self.show_search_prompt_modal, 'secondary')
        prompt_btn.pack(side='right', padx=(0, 8))

        self.search_entry = create_entry(toolbar, placeholder="Buscar empresas...")
        self.search_entry.pack(side='right', padx=16)
        self.search_entry.bind('<KeyRelease>', self.on_search)

        filter_frame = tk.Frame(self.list_view, bg=COLORS['background'])
        filter_frame.pack(fill='x', padx=16, pady=(0, 8))

        create_label(filter_frame, "Filtrar por:").pack(side='left', padx=(0, 8))

        self.type_filter = create_combobox(filter_frame, ["Todos los Tipos"] + self.controller.get_job_types())
        self.type_filter.pack(side='left', padx=8)
        self.type_filter.bind('<<ComboboxSelected>>', self.on_filter_change)

        self.status_filter = create_combobox(filter_frame, ["Todos los Estados"] + self.controller.get_statuses())
        self.status_filter.pack(side='left', padx=8)
        self.status_filter.bind('<<ComboboxSelected>>', self.on_filter_change)

        self.table_frame = tk.Frame(self.list_view, bg=COLORS['background'])
        self.table_frame.pack(fill='both', expand=True, padx=16, pady=(0, 16))

        self.form_frame = tk.Frame(self.list_view, bg=COLORS['background'])
        self.setup_locator_view()
        self.populate_table()

    def setup_locator_view(self):
        self.locator_view = tk.Frame(self, bg=COLORS['background'])

        locator_toolbar = tk.Frame(self.locator_view, bg=COLORS['background'])
        locator_toolbar.pack(fill='x', padx=16, pady=(16, 8))

        back_btn = create_button(locator_toolbar, "Volver Atrás", self.hide_locator_view, 'secondary')
        back_btn.pack(side='left')

        text_wrap = tk.Frame(self.locator_view, bg=COLORS['background'])
        text_wrap.pack(fill='both', expand=True, padx=16, pady=(0, 16))

        self.locator_text = create_text(text_wrap, height=30, width=100)
        self.locator_text.pack(side='left', fill='both', expand=True)

        locator_scroll = tk.Scrollbar(text_wrap, orient='vertical',
                                      command=self.locator_text.yview)
        locator_scroll.pack(side='right', fill='y')
        self.locator_text.configure(yscrollcommand=locator_scroll.set)

    def show_locator_config_modal(self):
        parent = self.winfo_toplevel()
        modal = tk.Toplevel(parent)
        modal.title("Localizar Empresas")
        modal.configure(bg=COLORS['background'])
        modal.transient(parent)
        modal.grab_set()
        modal.resizable(False, False)

        modal.withdraw()
        modal.update_idletasks()

        w, h = 560, 430
        sw = modal.winfo_screenwidth()
        sh = modal.winfo_screenheight()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        if pw <= 1:
            pw, px = sw, 0
        if ph <= 1:
            ph, py = sh, 0
        x = max(0, min(px + (pw - w) // 2, sw - w))
        y = max(0, min(py + (ph - h) // 2, sh - h))
        modal.geometry(f"{w}x{h}+{x}+{y}")
        modal.deiconify()

        header = tk.Frame(modal, bg=COLORS['surface'], height=56)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Label(header, text="Localizar Empresas", bg=COLORS['surface'],
                 fg=COLORS['text_primary'], font=FONT_HEADING).pack(side='left', padx=16)
        close_btn = create_button(header, "X", modal.destroy, 'danger')
        close_btn.pack(side='right', padx=8)

        form = create_card(modal)
        form.pack(fill='both', expand=True, padx=16, pady=16)

        entries = {}
        placeholders = {
            'sector': 'Sector a buscar *',
            'location': 'Ubicación',
            'api_key': 'API key (opcional si existe variable de entorno)',
            'google_cx': 'ID buscador Google cx',
            'limit': '10',
        }

        field_keys = ['sector', 'location', 'api_key', 'google_cx', 'limit']

        for key in field_keys:
            row = tk.Frame(form, bg=COLORS['surface'])
            row.pack(fill='x', padx=16, pady=6)
            entry = create_entry(row, placeholder=placeholders[key])
            entry.pack(fill='x')
            entries[key] = entry

        provider_row = tk.Frame(form, bg=COLORS['surface'])
        provider_row.pack(fill='x', padx=16, pady=7)
        tk.Label(provider_row, text="Proveedor", bg=COLORS['surface'],
                 fg=COLORS['text_secondary'], font=('Segoe UI', 11)).pack(anchor='w')
        provider_combo = create_combobox(provider_row, ['Google Custom Search', 'Bing Web Search'])
        provider_combo.pack(fill='x')
        provider_combo.set('Google Custom Search')

        mode_row = tk.Frame(form, bg=COLORS['surface'])
        mode_row.pack(fill='x', padx=16, pady=7)
        tk.Label(mode_row, text="Modalidad", bg=COLORS['surface'],
                 fg=COLORS['text_secondary'], font=('Segoe UI', 11)).pack(anchor='w')
        mode_combo = create_combobox(mode_row, ['Cualquiera', 'Remoto', 'Onsite', 'Híbrido'])
        mode_combo.pack(fill='x')
        mode_combo.set('Cualquiera')

        def start_search():
            sector = self._entry_value(entries['sector'], placeholders['sector'])
            if not sector:
                messagebox.showwarning("Campo obligatorio",
                                       "Define el sector de empresa que quieres buscar.",
                                       parent=modal)
                return

            limit_text = self._entry_value(entries['limit'], placeholders['limit'])
            try:
                limit = int(limit_text or "10")
            except ValueError:
                messagebox.showwarning("Número no válido",
                                       "El número de resultados debe ser un entero.",
                                       parent=modal)
                return

            criteria = {
                'sector': sector,
                'location': self._entry_value(entries['location'], placeholders['location']),
                'work_mode': mode_combo.get() if mode_combo.get() != 'Cualquiera' else '',
                'provider': provider_combo.get(),
                'api_key': self._entry_value(entries['api_key'], placeholders['api_key']),
                'google_cx': self._entry_value(entries['google_cx'], placeholders['google_cx']),
                'limit': max(1, min(limit, 20)),
            }
            modal.destroy()
            self.show_locator_view(criteria)

        btn_row = tk.Frame(modal, bg=COLORS['background'])
        btn_row.pack(fill='x', padx=16, pady=(0, 16))
        create_button(btn_row, "Iniciar búsqueda", start_search, 'primary').pack(side='left', padx=4)
        create_button(btn_row, "Cancelar", modal.destroy, 'secondary').pack(side='left', padx=4)

        modal.bind('<Escape>', lambda e: modal.destroy())

    def show_search_prompt_modal(self):
        parent = self.winfo_toplevel()
        modal = tk.Toplevel(parent)
        modal.title("Prompt Búsqueda")
        modal.configure(bg=COLORS['background'])
        modal.transient(parent)
        modal.grab_set()
        modal.resizable(False, False)

        modal.withdraw()
        modal.update_idletasks()

        w, h = 520, 350
        sw = modal.winfo_screenwidth()
        sh = modal.winfo_screenheight()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        if pw <= 1:
            pw, px = sw, 0
        if ph <= 1:
            ph, py = sh, 0
        x = max(0, min(px + (pw - w) // 2, sw - w))
        y = max(0, min(py + (ph - h) // 2, sh - h))
        modal.geometry(f"{w}x{h}+{x}+{y}")
        modal.deiconify()

        header = tk.Frame(modal, bg=COLORS['surface'], height=56)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Label(header, text="Prompt Búsqueda", bg=COLORS['surface'],
                 fg=COLORS['text_primary'], font=FONT_HEADING).pack(side='left', padx=16)
        close_btn = create_button(header, "X", modal.destroy, 'danger')
        close_btn.pack(side='right', padx=8)

        form = create_card(modal)
        form.pack(fill='both', expand=True, padx=16, pady=16)

        entries = {}
        placeholders = {
            'sector': 'Sector a buscar *',
            'company_count': 'Número de empresas *',
            'location': 'Ubicación de las empresas',
        }

        field_keys = ['sector', 'company_count', 'location']

        for key in field_keys:
            row = tk.Frame(form, bg=COLORS['surface'])
            row.pack(fill='x', padx=16, pady=7)
            entry = create_entry(row, placeholder=placeholders[key])
            entry.pack(fill='x')
            entries[key] = entry

        mode_row = tk.Frame(form, bg=COLORS['surface'])
        mode_row.pack(fill='x', padx=16, pady=8)
        tk.Label(mode_row, text="Modalidad", bg=COLORS['surface'],
                 fg=COLORS['text_secondary'], font=('Segoe UI', 11)).pack(anchor='w')
        mode_combo = create_combobox(mode_row, ['Cualquiera', 'Remoto', 'Onsite', 'Híbrido'])
        mode_combo.pack(fill='x')
        mode_combo.set('Cualquiera')

        def copy_prompt():
            sector = self._entry_value(entries['sector'], placeholders['sector'])
            if not sector:
                messagebox.showwarning("Campo obligatorio",
                                       "Define el sector de empresa que quieres buscar.",
                                       parent=modal)
                return

            count_text = self._entry_value(entries['company_count'], placeholders['company_count'])
            try:
                company_count = int(count_text)
            except ValueError:
                messagebox.showwarning("Número no válido",
                                       "El número de empresas debe ser un entero.",
                                       parent=modal)
                return

            if company_count < 1:
                messagebox.showwarning("Número no válido",
                                       "El número de empresas debe ser mayor que cero.",
                                       parent=modal)
                return

            criteria = {
                'sector': sector,
                'company_count': company_count,
                'location': self._entry_value(entries['location'], placeholders['location']),
                'work_mode': mode_combo.get() if mode_combo.get() != 'Cualquiera' else '',
            }
            prompt = self._build_ai_search_prompt(criteria)
            self.clipboard_clear()
            self.clipboard_append(prompt)
            self.update()
            modal.destroy()
            messagebox.showinfo("Prompt copiado",
                                "El prompt de búsqueda se ha copiado al portapapeles.")

        btn_row = tk.Frame(modal, bg=COLORS['background'])
        btn_row.pack(fill='x', padx=16, pady=(0, 16))
        create_button(btn_row, "Copiar Prompt", copy_prompt, 'primary').pack(side='left', padx=4)
        create_button(btn_row, "Cancelar", modal.destroy, 'secondary').pack(side='left', padx=4)

        modal.bind('<Escape>', lambda e: modal.destroy())

    def show_locator_view(self, criteria):
        self.hide_form()
        self.locator_cancelled = False
        self.locator_criteria = criteria
        self.list_view.pack_forget()
        self.locator_view.pack(fill='both', expand=True)
        self.start_company_locator(criteria)

    def hide_locator_view(self):
        self.locator_cancelled = True
        self.locator_view.pack_forget()
        self.list_view.pack(fill='both', expand=True)

    def start_company_locator(self, criteria):
        if self.locator_running:
            return

        self.locator_text.delete('1.0', 'end')
        self.locator_text.insert('end', self._format_locator_header(criteria))

        self.locator_running = True
        self.locator_queue = queue.Queue()
        worker = threading.Thread(
            target=self._run_company_locator,
            args=(criteria, self.locator_queue),
            daemon=True
        )
        worker.start()
        self.after(100, self._poll_locator_queue)

    def _poll_locator_queue(self):
        while not self.locator_queue.empty():
            kind, payload = self.locator_queue.get()
            if kind == 'result' and not self.locator_cancelled:
                self.locator_text.insert('end', payload)
                self.locator_text.see('end')
            elif kind == 'message' and not self.locator_cancelled:
                self.locator_text.insert('end', payload + "\n")
                self.locator_text.see('end')
            elif kind == 'done':
                self.locator_running = False
                if not self.locator_cancelled:
                    self.locator_text.insert('end', "\nRastreo finalizado.\n")
                    self.locator_text.see('end')
                return

        if self.locator_running:
            self.after(100, self._poll_locator_queue)

    def _run_company_locator(self, criteria, result_queue):
        try:
            results = self._search_companies_web(criteria)
        except ValueError as error:
            result_queue.put(('message', f"No se puede iniciar la búsqueda: {error}"))
            result_queue.put(('done', None))
            return
        except Exception as error:
            result_queue.put(('message', f"No se pudo completar la búsqueda: {error}"))
            result_queue.put(('done', None))
            return

        if not results:
            result_queue.put(('message', "No se encontraron empresas para esos criterios."))
            result_queue.put(('done', None))
            return

        seen = set()
        for result in results:
            if self.locator_cancelled:
                break

            url = result.get('url', '')
            identity = self._result_identity(result)
            if identity in seen:
                continue
            seen.add(identity)

            combined_text = " ".join([
                result.get('title', ''),
                result.get('snippet', ''),
            ])
            page_text = self._fetch_page_text(url) if url else ""
            if page_text:
                combined_text = f"{combined_text} {page_text}"

            data = self._extract_company_data(combined_text, url)
            data.update({
                'name': self._extract_name_from_search_result(result.get('title', ''), url) or data.get('name', ''),
                'industry': data.get('industry') or criteria['sector'],
                'job_title': self._extract_job_title(result.get('title', ''), result.get('snippet', '')),
                'location': data.get('location') or criteria.get('location', ''),
                'work_mode': data.get('work_mode') or criteria.get('work_mode', ''),
                'notes': self._build_locator_notes(result, criteria),
            })
            result_queue.put(('result', self._format_locator_company(data)))

        result_queue.put(('done', None))

    def _search_companies_web(self, criteria):
        provider = criteria.get('provider', '')
        if provider == 'Google Custom Search':
            return self._search_google(criteria)
        if provider == 'Bing Web Search':
            return self._search_bing(criteria)
        raise ValueError("Proveedor no reconocido.")

    def _search_google(self, criteria):
        api_key = criteria.get('api_key') or os.environ.get('GOOGLE_SEARCH_API_KEY')
        cx = criteria.get('google_cx') or os.environ.get('GOOGLE_SEARCH_ENGINE_ID')
        if not api_key:
            raise ValueError("falta GOOGLE_SEARCH_API_KEY o una API key en el formulario.")
        if not cx:
            raise ValueError("falta GOOGLE_SEARCH_ENGINE_ID o el ID cx en el formulario.")

        results = []
        limit = criteria.get('limit', 10)
        for start in range(1, limit + 1, 10):
            params = {
                'key': api_key,
                'cx': cx,
                'q': self._build_locator_query(criteria),
                'num': min(10, limit - len(results)),
                'start': start,
                'lr': 'lang_es',
                'gl': 'es',
            }
            payload = self._get_json("https://customsearch.googleapis.com/customsearch/v1", params)
            results.extend([
                {
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                }
                for item in payload.get('items', [])
            ])
            if len(results) >= limit or not payload.get('items'):
                break
        return results[:limit]

    def _search_bing(self, criteria):
        api_key = criteria.get('api_key') or os.environ.get('BING_SEARCH_API_KEY')
        if not api_key:
            raise ValueError("falta BING_SEARCH_API_KEY o una API key en el formulario.")

        params = {
            'q': self._build_locator_query(criteria),
            'count': min(criteria.get('limit', 10), 20),
            'mkt': 'es-ES',
            'responseFilter': 'Webpages',
        }
        payload = self._get_json(
            "https://api.bing.microsoft.com/v7.0/search",
            params,
            headers={'Ocp-Apim-Subscription-Key': api_key}
        )
        return [
            {
                'title': item.get('name', ''),
                'url': item.get('url', ''),
                'snippet': item.get('snippet', ''),
            }
            for item in payload.get('webPages', {}).get('value', [])
        ]

    def _get_json(self, endpoint, params, headers=None):
        url = f"{endpoint}?{urlencode(params)}"
        request_headers = {'User-Agent': 'Mozilla/5.0 (JobBot Company Locator)'}
        if headers:
            request_headers.update(headers)
        request = Request(url, headers=request_headers)
        try:
            with urlopen(request, timeout=10) as response:
                charset = response.headers.get_content_charset() or 'utf-8'
                body = response.read().decode(charset, errors='ignore')
            return json.loads(body)
        except HTTPError as error:
            body = error.read().decode('utf-8', errors='ignore')
            raise ValueError(f"la API respondió HTTP {error.code}: {body[:220]}") from error
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            raise ValueError(str(error)) from error

    def _build_locator_query(self, criteria):
        parts = [
            criteria['sector'],
            'empresas',
            'empleo',
            'contacto',
        ]
        if criteria.get('location'):
            parts.append(criteria['location'])
        if criteria.get('work_mode'):
            parts.append(criteria['work_mode'])
        return " ".join(parts)

    def _format_locator_header(self, criteria):
        return (
            "Búsqueda:\n"
            f"Sector: {criteria.get('sector', '')}\n"
            f"Ubicación: {criteria.get('location', '') or 'Cualquiera'}\n"
            f"Modalidad: {criteria.get('work_mode', '') or 'Cualquiera'}\n"
            f"Proveedor: {criteria.get('provider', '')}\n\n"
            "Resultados:\n\n"
        )

    def _entry_value(self, entry, placeholder):
        value = entry.get().strip()
        return "" if value == placeholder else value

    def _build_ai_search_prompt(self, criteria):
        location_line = criteria.get('location') or 'Sin restricción de ubicación'
        work_mode_line = criteria.get('work_mode') or 'Cualquier modalidad'
        target_csv = f"empresas_{self._slugify(criteria['sector'])}.csv"
        headers = [
            'Nombre de la Empresa',
            'A qué se dedica',
            'Puesto',
            'Ubicación',
            'Modalidad',
            'Persona de contacto',
            'Email de contacto',
            'Teléfono de contacto',
            'URL del Puesto',
            'Notas',
        ]

        return f"""Actúa como un agente de código con capacidad de búsqueda web y generación de archivos.

Objetivo:
Investiga empresas reales del sector indicado y genera un archivo CSV con empresas potenciales para búsqueda de empleo.

Parámetros de búsqueda:
- Sector: {criteria['sector']}
- Número objetivo de empresas: {criteria['company_count']}
- Ubicación: {location_line}
- Modalidad: {work_mode_line}
- CSV de trabajo: localizar automáticamente si existe; si no existe, crear {target_csv}

Tarea:
1. Antes de buscar empresas, recorre el directorio de trabajo y todos sus subdirectorios para localizar un CSV existente de empresas.
2. Considera como CSV de empresas cualquier .csv que tenga columnas compatibles con el formato indicado abajo o un nombre relacionado con empresas.
3. Si encuentras varios CSV candidatos, usa el más específico para el sector "{criteria['sector']}" si existe; si no, usa el CSV candidato más reciente.
4. Si encuentras un CSV existente, léelo primero, conserva sus filas y úsalo como lista de empresas ya conocidas.
5. Si no encuentras ningún CSV válido, crea uno nuevo llamado {target_csv} en el directorio de trabajo.
6. Busca en internet empresas reales que encajen con el sector y la ubicación indicada, priorizando fuentes verificables como webs oficiales, páginas de empleo, directorios empresariales, LinkedIn público, portales de ofertas y páginas de contacto.
7. Recupera hasta {criteria['company_count']} empresas nuevas distintas. Si no puedes llegar a ese número con calidad razonable, incluye solo las que puedas verificar.
8. Deduplica contra el CSV existente y contra los nuevos resultados por dominio web, nombre comercial, email, teléfono y URL.
9. No inventes datos. Cuando no encuentres un campo, deja la celda vacía.
10. Para cada empresa intenta obtener nombre, actividad, puesto u oferta relacionada, ubicación, modalidad, contacto, email, teléfono, URL fuente y notas breves.
11. Escribe el resultado en el CSV de trabajo, añadiendo las empresas nuevas a las ya existentes sin duplicarlas.

Formato exacto del CSV:
Usa estas columnas y este orden:
{', '.join(headers)}

Reglas de contenido:
- "Nombre de la Empresa": nombre comercial de la empresa.
- "A qué se dedica": sector, producto o actividad principal.
- "Puesto": puesto encontrado o tipo de perfil que suele contratar; deja vacío si no está claro.
- "Ubicación": ciudad, país o remoto si la fuente lo indica.
- "Modalidad": solo usa Remoto, Onsite, Híbrido o vacío.
- "Persona de contacto": nombre de reclutador o contacto si aparece públicamente.
- "Email de contacto": email público verificable.
- "Teléfono de contacto": teléfono público verificable.
- "URL del Puesto": URL de oferta, careers page o página oficial más útil.
- "Notas": resumen corto con la fuente usada y cualquier dato relevante para contactar.

Entrega:
- Crea o actualiza el CSV de trabajo en UTF-8.
- Al finalizar, muestra la ruta del archivo creado o actualizado, el número de empresas que ya existían, el número de empresas nuevas añadidas y el total final.
- Si usas comandos, evita modificar archivos ajenos a este CSV.
"""

    def _slugify(self, value):
        slug = re.sub(r'[^a-zA-Z0-9]+', '_', value.strip().lower())
        return slug.strip('_') or 'busqueda'

    def _result_identity(self, result):
        url = result.get('url', '')
        parsed = urlparse(url)
        host = parsed.netloc.replace('www.', '').lower()
        return host or result.get('title', '').strip().lower()

    def _extract_name_from_search_result(self, title, url):
        clean_title = re.sub(r'\s+', ' ', title or '').strip()
        separators = [' | ', ' - ', ' – ', ' — ', ': ']
        for separator in separators:
            if separator in clean_title:
                first, last = clean_title.split(separator, 1)
                if len(first) <= 45:
                    return first.strip()
                if len(last) <= 45:
                    return last.strip()
        return self._extract_name_from_url(url)

    def _extract_job_title(self, title, snippet):
        text = f"{title} {snippet}"
        patterns = [
            r'\b(?:buscamos|se busca|oferta de empleo:?|empleo:?|vacante:?)\s+([^.|,\-–—]{4,80})',
            r'\b(software engineer|data engineer|data scientist|developer|desarrollador[a]?|programador[a]?|consultor[a]?|analista|devops|qa engineer)\b',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1) if match.groups() else match.group(0)
                return re.sub(r'\s+', ' ', value).strip().title()
        return ""

    def _build_locator_notes(self, result, criteria):
        notes = [
            f"Fuente: {result.get('url', '')}",
            f"Consulta: {self._build_locator_query(criteria)}",
        ]
        snippet = result.get('snippet', '').strip()
        if snippet:
            notes.append(f"Resumen: {snippet}")
        return "\n".join(notes)

    def _fetch_page_text(self, url):
        try:
            request = Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (JobBot Company Locator)'
            })
            with urlopen(request, timeout=6) as response:
                charset = response.headers.get_content_charset() or 'utf-8'
                raw = response.read(250000)
            markup = raw.decode(charset, errors='ignore')
            return self._html_to_text(markup)
        except (HTTPError, URLError, TimeoutError, ValueError):
            return ""

    def _html_to_text(self, markup):
        markup = re.sub(r'(?is)<(script|style).*?>.*?</\1>', ' ', markup)
        title = self._first_match(r'(?is)<title[^>]*>(.*?)</title>', markup)
        meta_description = self._first_match(
            r'(?is)<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
            markup
        )
        text = re.sub(r'(?s)<[^>]+>', ' ', markup)
        parts = [title, meta_description, text]
        return html.unescape(" ".join(part for part in parts if part))

    def _extract_company_data(self, text, url):
        normalized = re.sub(r'\s+', ' ', text).strip()
        email = self._first_match(
            r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',
            normalized,
            re.IGNORECASE
        )
        phone = self._first_match(
            r'(?:(?:\+34|0034)\s*)?[6789]\d{2}[\s.-]?\d{3}[\s.-]?\d{3}',
            normalized
        )
        work_mode = self._detect_work_mode(normalized)
        industry = self._detect_industry(normalized)
        location = self._detect_location(normalized)
        name = self._extract_name_from_url(url)

        return {
            'name': name,
            'industry': industry,
            'job_title': "",
            'location': location,
            'work_mode': work_mode,
            'contact_name': "",
            'contact_email': email,
            'contact_phone': phone,
            'notes': f"Fuente: {url}"
        }

    def _detect_work_mode(self, text):
        lowered = text.lower()
        if any(term in lowered for term in ('híbrido', 'hibrido', 'hybrid')):
            return "Híbrido"
        if any(term in lowered for term in ('remoto', 'remote', 'teletrabajo')):
            return "Remoto"
        if any(term in lowered for term in ('presencial', 'onsite', 'oficina')):
            return "Onsite"
        return ""

    def _detect_industry(self, text):
        lowered = text.lower()
        industries = [
            ('software', 'Software'),
            ('inteligencia artificial', 'Inteligencia Artificial'),
            ('data', 'Datos'),
            ('cloud', 'Cloud'),
            ('ciberseguridad', 'Ciberseguridad'),
            ('fintech', 'Fintech'),
            ('salud', 'Salud'),
            ('energía', 'Energía'),
            ('energia', 'Energía'),
            ('consultoría', 'Consultoría'),
            ('consultoria', 'Consultoría'),
            ('marketing', 'Marketing'),
            ('ecommerce', 'Ecommerce'),
        ]
        for needle, label in industries:
            if needle in lowered:
                return label
        return ""

    def _detect_location(self, text):
        cities = [
            'Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Bilbao', 'Málaga',
            'Malaga', 'Zaragoza', 'Murcia', 'Alicante', 'Valladolid', 'Granada',
            'A Coruña', 'Coruña', 'Santander', 'Pamplona'
        ]
        for city in cities:
            if re.search(rf'\b{re.escape(city)}\b', text, re.IGNORECASE):
                return 'Málaga' if city == 'Malaga' else city
        return ""

    def _extract_name_from_url(self, url):
        parsed = urlparse(url)
        host = parsed.netloc.replace('www.', '')
        if not host:
            return ""
        name = host.split('.')[0].replace('-', ' ').replace('_', ' ')
        return name.title()

    def _first_match(self, pattern, text, flags=0):
        match = re.search(pattern, text, flags)
        if not match:
            return ""
        value = match.group(1) if match.groups() else match.group(0)
        return re.sub(r'\s+', ' ', value).strip()

    def _format_locator_company(self, data):
        fields = [
            ("Nombre de la Empresa", data.get('name', "")),
            ("A qué se dedica", data.get('industry', "")),
            ("Puesto", data.get('job_title', "")),
            ("Ubicación", data.get('location', "")),
            ("Modalidad", data.get('work_mode', "")),
            ("Persona de contacto", data.get('contact_name', "")),
            ("Email de contacto", data.get('contact_email', "")),
            ("Teléfono de contacto", data.get('contact_phone', "")),
            ("Notas", data.get('notes', "")),
        ]
        lines = [f"{label}: {value or ''}" for label, value in fields]
        return "\n".join(lines) + "\n\n" + ("-" * 72) + "\n\n"

    def on_search(self, event=None):
        self.refresh_table(self.get_visible_companies())

    def on_filter_change(self, event=None):
        self.refresh_table(self.get_visible_companies())

    def get_visible_companies(self):
        query = self.search_entry.get()
        if query and query != "Buscar empresas...":
            empresas = self.controller.search_companies(query)
        else:
            empresas = self.controller.get_all_companies()

        job_type = self.type_filter.get()
        if job_type and job_type != "Todos los Tipos":
            empresas = [e for e in empresas if e.job_type == job_type]

        status = self.status_filter.get()
        if status and status != "Todos los Estados":
            empresas = [e for e in empresas if e.status == status]

        return empresas

    def populate_table(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        header_frame = tk.Frame(self.table_frame, bg=COLORS['surface'])
        header_frame.pack(fill='x', padx=1)

        headers = ["Nombre", "Puesto", "Tipo", "Ubicación", "Estado", "Contactada", "Acciones"]
        self.table_widths = [20, 20, 14, 14, 10, 12, 15]

        for i, (h, w) in enumerate(zip(headers, self.table_widths)):
            tk.Label(header_frame, text=h, bg=COLORS['secondary'],
                    fg=COLORS['text_primary'], font=('Segoe UI', 11, 'bold'),
                    width=w).pack(side='left', padx=1, pady=1)

        scroll_canvas = tk.Canvas(self.table_frame, bg=COLORS['background'],
                                  highlightthickness=0)
        scroll_frame = tk.Frame(scroll_canvas, bg=COLORS['background'])
        scroll_window = scroll_canvas.create_window((0, 0), window=scroll_frame,
                                                     anchor='nw')

        scroll_y = tk.Scrollbar(self.table_frame, orient='vertical',
                                command=scroll_canvas.yview)
        scroll_y.pack(side='right', fill='y')
        scroll_canvas.configure(yscrollcommand=scroll_y.set)

        scroll_canvas.pack(side='left', fill='both', expand=True)
        self.scroll_frame = scroll_frame
        self.scroll_canvas = scroll_canvas

        def on_configure(event):
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox('all'))
        scroll_frame.bind('<Configure>', on_configure)

        self.refresh_table(self.controller.get_all_companies())

    def refresh_table(self, empresas):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not empresas:
            row_frame = tk.Frame(self.scroll_frame, bg=COLORS['background'])
            row_frame.pack(fill='x', padx=1, pady=1)
            tk.Label(row_frame, text="No se encontraron empresas", bg=COLORS['background'],
                    fg=COLORS['text_secondary']).pack(pady=20)
            return

        for empresa in empresas:
            row_bg = COLORS['contacted_row'] if empresa.contacted else COLORS['surface']
            row_frame = tk.Frame(self.scroll_frame, bg=row_bg)
            row_frame.pack(fill='x', padx=1, pady=1)

            data = [empresa.name, empresa.job_title, empresa.job_type,
                    empresa.location, empresa.status]

            for i, item in enumerate(data):
                color = COLORS['text_primary']
                if item == empresa.status:
                    color = STATUS_COLORS.get(empresa.status, COLORS['text_primary'])
                tk.Label(row_frame, text=item or "-", bg=row_bg,
                        fg=color, width=self.table_widths[i]).pack(
                        side='left', padx=1, pady=4)

            contact_text = "Contactada" if empresa.contacted else "Marcar"
            contact_style = 'contacted' if empresa.contacted else 'secondary'
            contact_btn = create_button(row_frame, contact_text,
                                        lambda e=empresa: self.toggle_contacted(e),
                                        contact_style)
            contact_btn.pack(side='left', padx=1, pady=4)

            actions = tk.Frame(row_frame, bg=row_bg)
            actions.pack(side='left', padx=1, pady=4)

            edit_btn = create_button(actions, "Editar",
                                     lambda e=empresa: self.show_edit_form(e),
                                     'primary')
            edit_btn.pack(side='left', padx=2)

            delete_btn_exp = (lambda eid=empresa.id: self.delete_company(eid))
            delete_btn = create_button(actions, "Elim", delete_btn_exp, 'danger')
            delete_btn.pack(side='left', padx=2)

        self.scroll_canvas.update_idletasks()
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox('all'))

    def show_add_form(self):
        self.current_edit_id = None
        self._open_add_modal()

    def _open_add_modal(self):
        parent = self.winfo_toplevel()
        modal = tk.Toplevel(parent)
        modal.title("Añadir Empresa")
        modal.configure(bg=COLORS['background'])
        modal.transient(parent)
        modal.grab_set()
        modal.resizable(False, False)

        modal.withdraw()
        modal.update_idletasks()

        w, h = 520, 620
        sw = modal.winfo_screenwidth()
        sh = modal.winfo_screenheight()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        if pw <= 1:
            pw, px = sw, 0
        if ph <= 1:
            ph, py = sh, 0
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        x = max(0, min(x, sw - w))
        y = max(0, min(y, sh - h))
        modal.geometry(f"{w}x{h}+{x}+{y}")
        modal.deiconify()

        header = tk.Frame(modal, bg=COLORS['surface'], height=56)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Label(header, text="Añadir Empresa", bg=COLORS['surface'],
                 fg=COLORS['text_primary'], font=FONT_HEADING).pack(side='left', padx=16)
        close_btn = create_button(header, "X", modal.destroy, 'danger')
        close_btn.pack(side='right', padx=8)

        tk.Label(modal, text="Introduce los datos básicos de contacto de la empresa.",
                 bg=COLORS['background'], fg=COLORS['text_secondary'],
                 font=FONT_PRIMARY).pack(anchor='w', padx=16, pady=(12, 4))

        form = create_card(modal)
        form.pack(fill='both', expand=True, padx=16, pady=(4, 12))

        left_col = tk.Frame(form, bg=COLORS['surface'])
        left_col.pack(side='left', fill='both', expand=True, padx=12, pady=12)
        right_col = tk.Frame(form, bg=COLORS['surface'])
        right_col.pack(side='left', fill='both', expand=True, padx=12, pady=12)

        entries = {}
        fields = [
            ("Nombre de la Empresa *", "name", left_col, 'entry'),
            ("A qué se dedica", "industry", left_col, 'entry'),
            ("Puesto", "job_title", left_col, 'entry'),
            ("Ubicación", "location", left_col, 'entry'),
            ("Modalidad", "work_mode", left_col, 'combo'),
            ("Persona de contacto", "contact_name", right_col, 'entry'),
            ("Email de contacto", "contact_email", right_col, 'entry'),
            ("Teléfono de contacto", "contact_phone", right_col, 'entry'),
        ]

        for label_text, key, parent, kind in fields:
            row = tk.Frame(parent, bg=COLORS['surface'])
            row.pack(fill='x', pady=4)
            if kind == 'entry':
                entry = create_entry(row, placeholder=label_text.split(' *')[0])
                entry.pack(fill='x')
                entries[key] = entry
            else:
                tk.Label(row, text=label_text, bg=COLORS['surface'],
                         fg=COLORS['text_secondary'], font=('Segoe UI', 11)).pack(anchor='w')
                combo = create_combobox(row, ['', 'Remoto', 'Onsite', 'Híbrido'])
                combo.pack(fill='x')
                entries[key] = combo

        notes_text = create_text(left_col, height=4, width=30)
        notes_text.pack(fill='x', pady=4)

        def save():
            name = entries['name'].get().strip()
            if not name or name == "Nombre de la Empresa":
                messagebox.showwarning("Campo obligatorio",
                                      "El nombre de la empresa es obligatorio.", parent=modal)
                return
            empresa = Company(
                name=name,
                job_title=entries['job_title'].get().strip(),
                job_type="",
                location=entries['location'].get().strip(),
                work_mode=entries['work_mode'].get(),
                industry=entries['industry'].get().strip(),
                notes=notes_text.get('1.0', 'end').strip(),
                status="lista_deseos",
                contacted=False,
                contact_name=entries['contact_name'].get().strip(),
                contact_email=entries['contact_email'].get().strip(),
                contact_phone=entries['contact_phone'].get().strip(),
            )
            self.controller.add_company(empresa)
            self.populate_table()
            self.type_filter['values'] = ["Todos los Tipos"] + self.controller.get_job_types()
            modal.destroy()

        btn_row = tk.Frame(modal, bg=COLORS['background'])
        btn_row.pack(fill='x', padx=16, pady=(0, 16))
        create_button(btn_row, "Guardar Empresa", save, 'primary').pack(side='left', padx=4)
        create_button(btn_row, "Cancelar", modal.destroy, 'secondary').pack(side='left', padx=4)

        modal.bind('<Escape>', lambda e: modal.destroy())

    def show_edit_form(self, empresa):
        self.current_edit_id = empresa.id
        self._show_form(empresa)

    def _show_form(self, empresa=None):
        for widget in self.form_frame.winfo_children():
            widget.destroy()

        self.current_contacted = bool(empresa.contacted) if empresa else False
        self.form_frame.pack(fill='both', expand=True, padx=16, pady=(0, 16))

        title = "Añadir Empresa" if empresa is None else f"Editar Empresa - {empresa.name}"
        create_label(self.form_frame, title, 'heading').pack(anchor='w', pady=(8, 16))

        form_card = create_card(self.form_frame)
        form_card.pack(fill='x', pady=(0, 16))

        left_col = tk.Frame(form_card, bg=COLORS['surface'])
        left_col.pack(side='left', fill='both', expand=True, padx=16, pady=16)

        right_col = tk.Frame(form_card, bg=COLORS['surface'])
        right_col.pack(side='left', fill='both', expand=True, padx=16, pady=16)

        fields = [
            ("Nombre de la Empresa", "name", left_col),
            ("Puesto", "job_title", left_col),
            ("Tipo de Trabajo", "job_type", left_col),
            ("Ubicación", "location", left_col),
            ("Modalidad", "work_mode", left_col),
            ("Industria", "industry", left_col),
            ("Tamaño de Empresa", "company_size", right_col),
            ("Salario Mínimo", "salary_min", right_col),
            ("Salario Máximo", "salary_max", right_col),
            ("URL del Puesto", "job_url", right_col),
            ("Persona de contacto", "contact_name", right_col),
            ("Email de contacto", "contact_email", right_col),
            ("Teléfono de contacto", "contact_phone", right_col),
        ]

        self.entries = {}
        for label_text, key, parent in fields:
            row = tk.Frame(parent, bg=COLORS['surface'])
            row.pack(fill='x', pady=4)
            tk.Label(row, text=label_text, bg=COLORS['surface'],
                    fg=COLORS['text_secondary'], font=('Segoe UI', 11)).pack(anchor='w')
            entry = create_entry(row, placeholder=label_text)
            entry.pack(fill='x')
            self.entries[key] = entry
            if empresa and getattr(empresa, key):
                entry.insert(0, getattr(empresa, key))
                entry.config(fg=COLORS['text_primary'])

        status_row = tk.Frame(right_col, bg=COLORS['surface'])
        status_row.pack(fill='x', pady=4)
        tk.Label(status_row, text="Estado", bg=COLORS['surface'],
                fg=COLORS['text_secondary'], font=('Segoe UI', 11)).pack(anchor='w')
        self.status_combo = create_combobox(status_row, self.controller.get_statuses())
        self.status_combo.pack(fill='x')
        if empresa and empresa.status:
            self.status_combo.set(empresa.status)

        notes_row = tk.Frame(left_col, bg=COLORS['surface'])
        notes_row.pack(fill='x', pady=4)
        tk.Label(notes_row, text="Notas", bg=COLORS['surface'],
                fg=COLORS['text_secondary'], font=('Segoe UI', 11)).pack(anchor='w')
        self.notes_text = create_text(notes_row, height=3, width=40)
        self.notes_text.pack()
        if empresa and empresa.notes:
            self.notes_text.insert('1.0', empresa.notes)

        btn_row = tk.Frame(self.form_frame, bg=COLORS['background'])
        btn_row.pack(fill='x')

        save_btn = create_button(btn_row, "Guardar Empresa",
                                 lambda: self.save_company(empresa is not None),
                                 'primary')
        save_btn.pack(side='left', padx=4)

        cancel_btn = create_button(btn_row, "Cancelar", self.hide_form, 'secondary')
        cancel_btn.pack(side='left', padx=4)

    def hide_form(self):
        self.form_frame.pack_forget()
        self.current_edit_id = None

    def save_company(self, is_edit):
        empresa = Company(
            name=self.entries['name'].get(),
            job_title=self.entries['job_title'].get(),
            job_type=self.entries['job_type'].get(),
            location=self.entries['location'].get(),
            work_mode=self.entries['work_mode'].get(),
            company_size=self.entries['company_size'].get(),
            salary_min=self.entries['salary_min'].get(),
            salary_max=self.entries['salary_max'].get(),
            industry=self.entries['industry'].get(),
            job_url=self.entries['job_url'].get(),
            notes=self.notes_text.get('1.0', 'end').strip(),
            status=self.status_combo.get(),
            contacted=getattr(self, 'current_contacted', False),
            contact_name=self.entries['contact_name'].get(),
            contact_email=self.entries['contact_email'].get(),
            contact_phone=self.entries['contact_phone'].get(),
        )

        if is_edit and self.current_edit_id:
            empresa.id = self.current_edit_id
            self.controller.update_company(empresa)
        else:
            self.controller.add_company(empresa)

        self.hide_form()
        self.populate_table()
        self.type_filter['values'] = ["Todos los Tipos"] + self.controller.get_job_types()

    def toggle_contacted(self, empresa):
        self.controller.set_contacted(empresa.id, not empresa.contacted)
        self.refresh_table(self.get_visible_companies())

    def delete_company(self, empresa_id):
        if messagebox.askyesno("Eliminar Empresa", "¿Estás seguro de que quieres eliminar esta empresa?"):
            self.controller.delete_company(empresa_id)
            self.populate_table()
