# interface.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
from backend import MoteurRAM 

class IDE(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("RAM Machine Environment - Projet M1 Computability")
        self.geometry("1100x750")

        # Initialisation des variables
        self.current_registers = {'PC': 1, 'R0': 0, 'R1': 0, 'Acc': 0}

        # --- Styles globaux ---
        style = ttk.Style()
        style.theme_use('clam') 

        # --- STRUCTURE PRINCIPALE (PanedWindow Vertical) ---
        self.main_split = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self.main_split.pack(fill=tk.BOTH, expand=True)

        # --- PARTIE HAUTE (PanedWindow Horizontal) ---
        self.top_split = ttk.PanedWindow(self.main_split, orient=tk.HORIZONTAL)
        self.main_split.add(self.top_split, weight=4)

        # 1. GAUCHE : Système d'onglets (Notebook)
        self.notebook = ttk.Notebook(self.top_split)
        self.top_split.add(self.notebook, weight=3)

        # 2. DROITE : Panneau Latéral (Debug & Registres)
        self.debug_frame = ttk.LabelFrame(self.top_split, text="Contrôle & Registres")
        self.top_split.add(self.debug_frame, weight=1) 
        self.create_debug_panel()

        # --- PARTIE BASSE : Output ---
        self.output_frame = ttk.LabelFrame(self.main_split, text="Sortie / Output / PRINT")
        self.main_split.add(self.output_frame, weight=1)

        # Barre d'outils pour la console (Bouton Clear)
        self.console_toolbar = ttk.Frame(self.output_frame)
        self.console_toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
        
        # Le bouton Clear
        self.btn_clear = ttk.Button(self.console_toolbar, text="Effacer la console (Clear)", command=self.clear_output)
        self.btn_clear.pack(side=tk.RIGHT)

        # Console noire
        self.output_text = tk.Text(self.output_frame, height=8, bg="#f0f0f0", fg="black", state='disabled', font=("Menlo", 11))
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Initialisation ---
        self.create_menus()
        self.new_file()

    # =========================================================================
    # GESTION DES MENUS
    # =========================================================================
    def create_menus(self):
        menubar = tk.Menu(self)

        # Menu File
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Nouveau", command=self.new_file)
        file_menu.add_command(label="Ouvrir...", command=self.open_file)
        file_menu.add_command(label="Enregistrer", command=self.save_file)
        file_menu.add_separator()
        
        # Fermer l'onglet
        file_menu.add_command(label="Fermer l'onglet", command=self.close_current_tab)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.quit)
        menubar.add_cascade(label="Fichier", menu=file_menu)

        # Menu Run
        run_menu = tk.Menu(menubar, tearoff=0)
        run_menu.add_command(label="Vérifier la Syntaxe", command=self.check_syntax) 
        run_menu.add_separator()
        run_menu.add_command(label="Exécuter (Run)", command=self.run_full_program)
        menubar.add_cascade(label="Exécution", menu=run_menu)

        # Menu Bibliothèque (LIB)
        lib_menu = tk.Menu(menubar, tearoff=0)
        lib_menu.add_command(label="Insérer PRINT", command=lambda: self.insert_snippet("PRINT \"Texte\";"))
        lib_menu.add_separator()
        lib_menu.add_command(label="Insérer FOPEN", command=lambda: self.insert_snippet("R1 = FOPEN \"data.txt\";"))
        lib_menu.add_command(label="Insérer FREAD", command=lambda: self.insert_snippet("R2 = FREAD R1;"))
        menubar.add_cascade(label="Bibliothèque (LIB)", menu=lib_menu)

        # Menu Help
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="À propos / Aide", command=self.show_help)
        menubar.add_cascade(label="Aide", menu=help_menu)

        self.config(menu=menubar)

    def show_help(self):
        msg = (
            "Projet Computability - Machine RAM\n"
            "Guide d'utilisation :\n\n"
            "1. RUN : Vérifiez la syntaxe avant d'exécuter.\n"
            "2. DEB : Utilisez le panneau de droite pour le pas-à-pas.\n"
            "3. LIB : Insérez des fonctions spéciales via le menu Bibliothèque."
        )
        messagebox.showinfo("Aide du Projet", msg)

    # =========================================================================
    # ÉDITEUR, ONGLETS ET COLORATION
    # =========================================================================
    def new_file(self):
        editor_frame = ttk.Frame(self.notebook)
        text_area = tk.Text(editor_frame, wrap="none", undo=True, font=("Menlo", 12)) 
        
        # Configuration des couleurs
        text_area.tag_configure("kw", foreground="blue", font=("Menlo", 12, "bold"))
        text_area.tag_configure("lib", foreground="#008000", font=("Menlo", 12, "bold"))
        text_area.tag_configure("reg", foreground="purple")
        text_area.tag_configure("num", foreground="#cc0000")
        text_area.tag_configure("str", foreground="#e68a00")
        text_area.tag_configure("com", foreground="grey", font=("Menlo", 12, "italic"))

        text_area.bind("<KeyRelease>", lambda e: self.highlight_syntax(text_area))

        vsb = ttk.Scrollbar(editor_frame, orient="vertical", command=text_area.yview)
        text_area.configure(yscrollcommand=vsb.set)
        text_area.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.notebook.add(editor_frame, text="Sans titre")
        self.notebook.select(editor_frame)

    # Fonction pour fermer l'onglet actif
    def close_current_tab(self):
        try:
            # Récupère l'identifiant de l'onglet actuel
            current_tab_id = self.notebook.select()
            if current_tab_id:
                self.notebook.forget(current_tab_id)
                
                # Si on a tout fermé, on recrée un onglet vide pour pas laisser l'IDE vide
                if not self.notebook.tabs():
                    self.new_file()
        except:
            pass

    def highlight_syntax(self, text_widget):
        for tag in ["kw", "lib", "reg", "num", "str", "com"]:
            text_widget.tag_remove(tag, "1.0", tk.END)

        self.apply_regex(text_widget, r"\b(if|then|gotof|gotob)\b", "kw")
        self.apply_regex(text_widget, r"\b(PRINT|FOPEN|FREAD|FWRITE)\b", "lib")
        self.apply_regex(text_widget, r"\bR\d+\b", "reg")
        self.apply_regex(text_widget, r"\b\d+\b", "num")
        self.apply_regex(text_widget, r"\".*?\"", "str")
        self.apply_regex(text_widget, r"(#|;).*$", "com")

    def apply_regex(self, widget, pattern, tag):
        start = "1.0"
        while True:
            pos = widget.search(pattern, start, stopindex=tk.END, count=tk.IntVar(), regexp=True)
            if not pos: break
            count = tk.IntVar()
            widget.search(pattern, pos, stopindex=tk.END, count=count, regexp=True)
            end = f"{pos}+{count.get()}c"
            widget.tag_add(tag, pos, end)
            start = end

    def insert_snippet(self, code_snippet):
        text_widget = self.get_current_text_widget()
        if text_widget:
            text_widget.insert(tk.INSERT, code_snippet)
            self.highlight_syntax(text_widget)

    # =========================================================================
    # PANNEAU DE DÉBOGAGE
    # =========================================================================
    def create_debug_panel(self):
        btn_frame = ttk.Frame(self.debug_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        self.btn_step = ttk.Button(btn_frame, text="Step (Pas à pas)", command=self.debug_step)
        self.btn_step.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.btn_reset = ttk.Button(btn_frame, text="Reset", command=self.debug_reset)
        self.btn_reset.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        columns = ("reg", "val")
        self.tree = ttk.Treeview(self.debug_frame, columns=columns, show="headings", height=20)
        self.tree.heading("reg", text="Registre")
        self.tree.heading("val", text="Valeur")
        self.tree.column("reg", width=80, anchor=tk.CENTER)
        self.tree.column("val", width=100, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.update_register_view()

    def update_register_view(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for reg, val in self.current_registers.items():
            self.tree.insert("", tk.END, values=(reg, val))

    # =========================================================================
    # CONNEXION AU BACKEND
    # =========================================================================
    def get_current_text_widget(self):
        try:
            tab = self.notebook.nametowidget(self.notebook.select())
            for child in tab.winfo_children():
                if isinstance(child, tk.Text): return child
        except: return None
        return None

    def get_code(self):
        text_widget = self.get_current_text_widget()
        return text_widget.get("1.0", tk.END) if text_widget else ""

    def log(self, text):
        self.output_text.configure(state='normal')
        self.output_text.insert(tk.END, f"{text}\n")
        self.output_text.see(tk.END)
        self.output_text.configure(state='disabled')

    # Fonction pour vider la console
    def clear_output(self):
        self.output_text.configure(state='normal')
        self.output_text.delete("1.0", tk.END)
        self.output_text.configure(state='disabled')

    def check_syntax(self):
        code = self.get_code()
        ok, msg = MoteurRAM.verifier_syntaxe(code)
        if ok:
            messagebox.showinfo("Syntaxe", msg)
            self.log("[Syntaxe] Vérification OK")
        else:
            messagebox.showerror("Erreur Syntaxe", msg)
            self.log(f"[Syntaxe] Erreur : {msg}")

    def run_full_program(self):
        code = self.get_code()
        val = simpledialog.askinteger("Entrée", "Valeur pour R0 (Input):")
        if val is None: return

        self.log(f"--- Lancement (R0={val}) ---")
        resultat = MoteurRAM.executer_tout(code, val)
        self.log(resultat)

    def debug_step(self):
        code = self.get_code()
        self.current_registers = MoteurRAM.executer_pas_a_pas(code, self.current_registers)
        self.update_register_view()
        self.log(f"[Debug] Step exécuté. PC -> {self.current_registers.get('PC', '?')}")

    def debug_reset(self):
        val = simpledialog.askinteger("Debug Initialisation", "Valeur de départ pour R0 :", initialvalue=0)
        if val is None: val = 0
        self.current_registers = {'PC': 1, 'R0': val, 'R1': 0, 'Acc': 0}
        self.update_register_view()
        self.log(f"[Debug] Reset effectué. R0 = {val}. Prêt à démarrer.")

    # --- Fichiers ---
    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("RAM", "*.ram"), ("All", "*.*")])
        if path:
            with open(path, "r") as f: content = f.read()
            self.new_file()
            txt = self.get_current_text_widget()
            txt.insert("1.0", content)
            self.notebook.tab("current", text=os.path.basename(path))
            self.highlight_syntax(txt)

    def save_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".ram")
        if path:
            with open(path, "w") as f: f.write(self.get_code())
            self.notebook.tab("current", text=os.path.basename(path))