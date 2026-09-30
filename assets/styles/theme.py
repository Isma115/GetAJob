COLORS = {
    'primary': '#2563eb',
    'secondary': '#172033',
    'accent': '#10b981',
    'warning': '#f59e0b',
    'error': '#ef4444',
    'background': '#111827',
    'surface': '#1f2937',
    'surface_alt': '#243244',
    'text_primary': '#f8fafc',
    'text_secondary': '#a7b3c6',
    'text_preview': '#d8e0ee',
    'border': '#334155',
    'hover': '#26364a',
    'nav_active': '#2d5bff',
    'nav_hover': '#223049',
    'success': '#10b981',
    'contacted_row': '#173f35',
    'contacted_button': '#256f5a',
}

FONT_PRIMARY = ("Segoe UI", 13)
FONT_BOLD = ("Segoe UI", 13, "bold")
FONT_HEADING = ("Segoe UI", 18, "bold")
FONT_MONO = ("Consolas", 12)

STATUS_COLORS = {
    'lista_deseos': '#2563eb',
    'solicitado': '#f59e0b',
    'entrevista': '#8b5cf6',
    'oferta': '#10b981',
    'rechazado': '#ef4444'
}

def apply_theme(window):
    window.configure(bg=COLORS['background'])
    window.option_add('*Font', FONT_PRIMARY)
    window.option_add('*Button.relief', 'flat')
    window.option_add('*Button.borderWidth', 0)
    window.option_add('*Button.highlightThickness', 0)

    try:
        from tkinter import ttk
        style = ttk.Style(window)
        style.theme_use('clam')
        style.configure(
            'TCombobox',
            fieldbackground=COLORS['surface'],
            background=COLORS['surface'],
            foreground=COLORS['text_primary'],
            arrowcolor=COLORS['text_primary'],
            bordercolor=COLORS['border'],
            lightcolor=COLORS['border'],
            darkcolor=COLORS['border'],
            font=FONT_PRIMARY
        )
        style.map(
            'TCombobox',
            fieldbackground=[('readonly', COLORS['surface'])],
            foreground=[('readonly', COLORS['text_primary'])],
            background=[('readonly', COLORS['surface'])]
        )
    except Exception:
        pass

def create_button(parent, text, command, style='primary'):
    colors = {
        'primary': COLORS['primary'],
        'secondary': COLORS['surface'],
        'danger': COLORS['error'],
        'success': COLORS['success'],
        'contacted': COLORS['contacted_button']
    }
    from tkinter import Label
    bg = colors.get(style, colors['primary'])
    normal_bg = bg
    hover_bg = COLORS['hover'] if style == 'secondary' else COLORS['nav_active']

    btn = Label(parent, text=text,
                bg=normal_bg,
                fg=COLORS['text_primary'],
                font=FONT_PRIMARY,
                padx=16, pady=8,
                cursor='hand2')

    def on_enter(_event):
        btn.config(bg=hover_bg)

    def on_leave(_event):
        btn.config(bg=normal_bg)

    def on_press(_event):
        btn.config(bg=COLORS['border'])

    def on_release(_event):
        btn.config(bg=hover_bg)
        command()

    btn.bind('<Enter>', on_enter)
    btn.bind('<Leave>', on_leave)
    btn.bind('<ButtonPress-1>', on_press)
    btn.bind('<ButtonRelease-1>', on_release)
    return btn

def create_entry(parent, textvariable=None, placeholder=""):
    from tkinter import Entry, Frame
    entry = Entry(parent, textvariable=textvariable,
                   bg=COLORS['surface'],
                   fg=COLORS['text_primary'],
                   font=FONT_PRIMARY,
                   relief='flat',
                   insertbackground=COLORS['text_primary'],
                   highlightcolor=COLORS['primary'],
                   highlightthickness=1)
    if placeholder:
        entry.insert(0, placeholder)
        entry.config(fg=COLORS['text_secondary'])
        def on_focus(e):
            if entry.get() == placeholder:
                entry.delete(0, 'end')
                entry.config(fg=COLORS['text_primary'])
        def on_blur(e):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg=COLORS['text_secondary'])
        entry.bind('<FocusIn>', on_focus)
        entry.bind('<FocusOut>', on_blur)
    return entry

def create_text(parent, height=10, width=50):
    from tkinter import Text, Frame
    text = Text(parent, height=height, width=width,
                bg=COLORS['surface'],
                fg=COLORS['text_primary'],
                font=FONT_PRIMARY,
                relief='flat',
                insertbackground=COLORS['text_primary'],
                highlightcolor=COLORS['primary'],
                highlightthickness=1)
    return text

def create_label(parent, text, style='normal'):
    from tkinter import Label
    fonts = {
        'normal': FONT_PRIMARY,
        'heading': FONT_HEADING,
        'mono': FONT_MONO
    }
    label = Label(parent, text=text,
                   bg=COLORS['background'],
                   fg=COLORS['text_primary'],
                   font=fonts.get(style, FONT_PRIMARY))
    return label

def create_card(parent):
    from tkinter import Frame
    card = Frame(parent, bg=COLORS['surface'],
                 relief='flat', bd=0,
                 highlightthickness=1,
                 highlightbackground=COLORS['border'])
    return card

def create_combobox(parent, values, textvariable=None):
    from tkinter import ttk
    combo = ttk.Combobox(parent, textvariable=textvariable,
                         values=values, state='readonly')
    return combo
