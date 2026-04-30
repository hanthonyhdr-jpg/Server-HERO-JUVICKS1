import os
import sys
import subprocess
import threading
import uuid
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class SmartCompilerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 Compilador Inteligente Universal")
        self.root.geometry("950x600")
        
        # Tentar maximizar
        try:
            self.root.state('zoomed')
        except:
            pass
        
        # === TEMA 100% DARK ===
        bg_main = "#121212"
        bg_card = "#1e1e1e"
        bg_input = "#2d2d2d"
        fg_text = "#e0e0e0"
        fg_accent = "#0EA5E9"
        
        self.root.configure(bg=bg_main)

        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure(".", background=bg_main, foreground=fg_text)
        style.configure("TFrame", background=bg_main)
        style.configure("TLabel", background=bg_main, foreground=fg_text, font=("Segoe UI", 10))
        style.configure("Header.TLabel", background=bg_main, foreground=fg_accent, font=("Segoe UI", 16, "bold"))
        
        style.configure("TLabelframe", background=bg_main, foreground=fg_accent, font=("Segoe UI", 10, "bold"), bordercolor="#333333")
        style.configure("TLabelframe.Label", background=bg_main, foreground=fg_accent)
        
        style.configure("TButton", background="#0284c7", foreground="white", font=("Segoe UI", 10, "bold"), padding=6, borderwidth=0)
        style.map("TButton", background=[("active", "#0369a1")])
        
        style.configure("TCheckbutton", background=bg_main, foreground=fg_text)
        style.map("TCheckbutton", background=[("active", bg_main)])
        
        style.configure("TEntry", fieldbackground=bg_input, foreground=fg_text, borderwidth=0, insertcolor="white")
        style.map("TEntry", fieldbackground=[("active", bg_input), ("focus", bg_input)])

        self.extra_datas = []
        self.show_console = tk.BooleanVar(value=False)

        self.create_widgets()

    def create_widgets(self):
        # Header
        hdr_frame = ttk.Frame(self.root)
        hdr_frame.pack(fill=tk.X, pady=(5, 0), padx=20)
        
        header = ttk.Label(hdr_frame, text="🚀 Compilador Automático Universal", style="Header.TLabel")
        header.pack(side=tk.LEFT)
        
        btn_frame_top = ttk.Frame(hdr_frame)
        btn_frame_top.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame_top, text="🤖 Auto-Detectar", command=self.auto_detect_project).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame_top, text="💾 Salvar Perfil", command=self.save_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame_top, text="📂 Carregar Perfil", command=self.load_profile).pack(side=tk.LEFT, padx=5)

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=0)

        # ================= FRAME ESQUERDO (Configurações) =================
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # --- Card 1: Informações do Sistema ---
        card1 = ttk.LabelFrame(left_frame, text="Informações do Sistema", padding=15)
        card1.pack(fill=tk.X, pady=5)

        ttk.Label(card1, text="Nome do App:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.app_name = ttk.Entry(card1, width=35)
        self.app_name.grid(row=0, column=1, sticky=tk.W, pady=2)

        ttk.Label(card1, text="Versão:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.app_version = ttk.Entry(card1, width=15)
        self.app_version.insert(0, "1.0.0")
        self.app_version.grid(row=1, column=1, sticky=tk.W, pady=2)

        ttk.Label(card1, text="Empresa:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.app_publisher = ttk.Entry(card1, width=35)
        self.app_publisher.insert(0, "Minha Empresa")
        self.app_publisher.grid(row=2, column=1, sticky=tk.W, pady=2)

        # --- Card 2: Arquivos Principais ---
        card2 = ttk.LabelFrame(left_frame, text="Arquivos Principais", padding=15)
        card2.pack(fill=tk.X, pady=10)

        # Script Principal
        ttk.Label(card2, text="Script Principal (.py):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.main_script = ttk.Entry(card2, width=28)
        self.main_script.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(card2, text="Procurar", command=self.browse_main_script, width=10).grid(row=0, column=2, pady=2)

        # Ícone
        ttk.Label(card2, text="Ícone (.ico):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.app_icon = ttk.Entry(card2, width=28)
        self.app_icon.grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(card2, text="Procurar", command=self.browse_icon, width=10).grid(row=1, column=2, pady=2)

        # Pasta de Saída
        ttk.Label(card2, text="Pasta de Saída (Destino):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.output_dir = ttk.Entry(card2, width=28)
        self.output_dir.insert(0, os.getcwd())
        self.output_dir.grid(row=2, column=1, padx=5, pady=2)
        ttk.Button(card2, text="Procurar", command=self.browse_output_dir, width=10).grid(row=2, column=2, pady=2)

        # --- Card 3: Dependências Avançadas ---
        card3 = ttk.LabelFrame(left_frame, text="Módulos Avançados (separados por vírgula)", padding=5)
        card3.pack(fill=tk.X, pady=2)
        
        ttk.Button(card3, text="📥 Auto-Preencher via requirements.txt", command=self.load_requirements).pack(anchor=tk.W, pady=(0, 2))

        ttk.Label(card3, text="Hidden Imports (Ocultos):").pack(anchor=tk.W)
        self.hidden_imports = tk.Text(card3, height=1, width=45, font=("Segoe UI", 9), bg="#2D2D2D", fg="#E0E0E0", insertbackground="white", relief="flat")
        self.hidden_imports.pack(fill=tk.X, pady=(0, 2))
        self.hidden_imports.insert(tk.END, "streamlit, pandas, pyarrow, pydoc, xlsxwriter, psycopg2, fpdf, docx")

        ttk.Label(card3, text="Collect All (Copia tudo da Lib):").pack(anchor=tk.W)
        self.collect_all = tk.Text(card3, height=1, width=45, font=("Segoe UI", 9), bg="#2D2D2D", fg="#E0E0E0", insertbackground="white", relief="flat")
        self.collect_all.pack(fill=tk.X, pady=(0, 2))
        self.collect_all.insert(tk.END, "streamlit, streamlit_drawable_canvas, pandas, pyarrow, plotly, altair")

        ttk.Label(card3, text="Excludes (Ignorar na compilação):").pack(anchor=tk.W)
        self.excludes = tk.Text(card3, height=1, width=45, font=("Segoe UI", 9), bg="#2D2D2D", fg="#E0E0E0", insertbackground="white", relief="flat")
        self.excludes.pack(fill=tk.X, pady=(0, 2))
        self.excludes.insert(tk.END, "matplotlib, notebook, IPython, tqdm, jedi, test")

        # --- Card 3.5: Opções do Executável ---
        card35 = ttk.LabelFrame(left_frame, text="Opções", padding=5)
        card35.pack(fill=tk.X, pady=2)
        
        ttk.Checkbutton(card35, text="Ocultar Janela de Console (Background)", variable=self.show_console, command=lambda: self.show_console.set(not self.show_console.get())).pack(anchor=tk.W)
        self.show_console.set(True) # Ocultar por padrão (True = sem console)

        # ================= FRAME DIREITO (Extras & Log) =================
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Card 4: Pastas Extras ---
        card4 = ttk.LabelFrame(right_frame, text="Pastas e Arquivos Extras", padding=5)
        card4.pack(fill=tk.BOTH, expand=True, pady=2)

        self.list_extras = tk.Listbox(card4, height=4, bg="#2D2D2D", fg="#E0E0E0", selectbackground="#0EA5E9", relief="flat")
        self.list_extras.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        btn_frame = ttk.Frame(card4)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="➕ Add Pasta", command=self.add_extra_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="➕ Add Arquivo", command=self.add_extra_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Remover", command=self.remove_extra).pack(side=tk.RIGHT, padx=5)

        # --- Card 5: Logs ---
        card5 = ttk.LabelFrame(right_frame, text="Console de Saída", padding=5)
        card5.pack(fill=tk.BOTH, expand=True, pady=2)
        self.log_text = tk.Text(card5, height=5, bg="#050505", fg="#00ff00", font=("Consolas", 9), insertbackground="white", relief="flat")
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # ================= BOTTOM BAR (Ações) =================
        action_frame = ttk.Frame(self.root, padding=5)
        action_frame.pack(fill=tk.X, side=tk.BOTTOM)

        ttk.Button(action_frame, text="1️⃣ Gerar .spec e .iss", command=self.generate_files, width=22).pack(side=tk.LEFT, padx=(20, 5))
        ttk.Button(action_frame, text="📂 Abrir Pasta", command=self.open_output_folder, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="2️⃣ COMPILAR SISTEMA (EXE + SETUP)", command=self.start_compilation, width=32).pack(side=tk.RIGHT, padx=20)

    # --- Funções de Navegação ---
    def open_output_folder(self):
        out_dir = self.output_dir.get().strip() or os.getcwd()
        output_folder = os.path.join(out_dir, "Output")
        dist_folder = os.path.join(out_dir, "dist")
        
        if os.path.exists(output_folder):
            os.startfile(output_folder)
        elif os.path.exists(dist_folder):
            os.startfile(dist_folder)
        elif os.path.exists(out_dir):
            os.startfile(out_dir)
        else:
            os.startfile(os.getcwd())

    def browse_output_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.output_dir.delete(0, tk.END)
            self.output_dir.insert(0, os.path.normpath(d))

    def browse_main_script(self):
        f = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if f:
            self.main_script.delete(0, tk.END)
            self.main_script.insert(0, os.path.relpath(f))

    def browse_icon(self):
        f = filedialog.askopenfilename(filetypes=[("Icon Files", "*.ico")])
        if f:
            self.app_icon.delete(0, tk.END)
            self.app_icon.insert(0, os.path.relpath(f))

    def add_extra_folder(self):
        d = filedialog.askdirectory()
        if d:
            rel_path = os.path.relpath(d)
            self.extra_datas.append((rel_path, os.path.basename(rel_path)))
            self.list_extras.insert(tk.END, f"📁 {rel_path} -> {os.path.basename(rel_path)}")

    def add_extra_file(self):
        f = filedialog.askopenfilename()
        if f:
            rel_path = os.path.relpath(f)
            self.extra_datas.append((rel_path, '.'))
            self.list_extras.insert(tk.END, f"📄 {rel_path} -> .")

    def remove_extra(self):
        sel = self.list_extras.curselection()
        if sel:
            idx = sel[0]
            self.list_extras.delete(idx)
            self.extra_datas.pop(idx)

    def log(self, msg):
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def load_requirements(self):
        f = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not f: return
        if self._parse_requirements(f):
            messagebox.showinfo("Sucesso", "Requirements.txt analisado e campos auto-preenchidos!")
            
    def _parse_requirements(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
            modules = []
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'): continue
                
                # Remover versões (ex: pandas==2.0 -> pandas)
                import re
                mod_name = re.split(r'[=><~]', line)[0].strip()
                if mod_name:
                    modules.append(mod_name)
            
            # Filtro Inteligente: Separa libs pesadas que precisam de Collect All
            heavy_libs = {'streamlit', 'pandas', 'pyarrow', 'plotly', 'altair', 'scipy', 'numpy', 'matplotlib'}
            
            collect_list = [m for m in modules if m.lower() in heavy_libs or 'streamlit' in m.lower()]
            hidden_list = [m for m in modules if m not in collect_list]
            
            if collect_list:
                self.collect_all.delete("1.0", tk.END)
                self.collect_all.insert(tk.END, ", ".join(collect_list))
                
            if hidden_list:
                self.hidden_imports.delete("1.0", tk.END)
                self.hidden_imports.insert(tk.END, ", ".join(hidden_list))
            return True
        except Exception as e:
            return False

    def auto_detect_project(self):
        cwd = os.getcwd()
        
        # 1. Detectar Script Principal
        for p_script in ["PY/launcher.py", "launcher.py", "PY/Inicio.py", "app.py", "main.py"]:
            if os.path.exists(os.path.join(cwd, p_script)):
                self.main_script.delete(0, tk.END)
                self.main_script.insert(0, p_script.replace("/", "\\"))
                break
                
        # 2. Detectar Ícone
        for p_icon in ["ICONE/ICONE.ico", "icone.ico", "icon.ico", "assets/icon.ico"]:
            if os.path.exists(os.path.join(cwd, p_icon)):
                self.app_icon.delete(0, tk.END)
                self.app_icon.insert(0, p_icon.replace("/", "\\"))
                break
                
        # 3. Detectar Pastas
        self.list_extras.delete(0, tk.END)
        self.extra_datas.clear()
        common_folders = ["PY", "DATABASE", "ICONE", "TELA", "WHATSAPP_MOTOR", "MODELOS_HTML", "CONFIG_SISTEMA", "assiname_app", "assets", "static"]
        for f in common_folders:
            if os.path.exists(os.path.join(cwd, f)) and os.path.isdir(os.path.join(cwd, f)):
                self.extra_datas.append((f, f))
                self.list_extras.insert(tk.END, f"📁 {f} -> {f}")
                
        # 4. Detectar Requirements.txt
        req_file = os.path.join(cwd, "requirements.txt")
        if os.path.exists(req_file):
            self._parse_requirements(req_file)
            
        messagebox.showinfo("Auto-Detect", "Projeto analisado com sucesso!\nOs arquivos vitais e pastas foram auto-preenchidos.")

    def save_profile(self):
        f = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")], title="Salvar Perfil do Projeto")
        if not f: return
        data = {
            "app_name": self.app_name.get(),
            "app_version": self.app_version.get(),
            "app_publisher": self.app_publisher.get(),
            "main_script": self.main_script.get(),
            "app_icon": self.app_icon.get(),
            "output_dir": self.output_dir.get(),
            "hidden_imports": self.hidden_imports.get("1.0", tk.END).strip(),
            "collect_all": self.collect_all.get("1.0", tk.END).strip(),
            "excludes": self.excludes.get("1.0", tk.END).strip(),
            "show_console": self.show_console.get(),
            "extra_datas": self.extra_datas
        }
        try:
            with open(f, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)
            messagebox.showinfo("Sucesso", "Perfil do projeto salvo com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar: {e}")

    def load_profile(self):
        f = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")], title="Carregar Perfil")
        if not f: return
        try:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
            self.app_name.delete(0, tk.END); self.app_name.insert(0, data.get("app_name", ""))
            self.app_version.delete(0, tk.END); self.app_version.insert(0, data.get("app_version", "1.0.0"))
            self.app_publisher.delete(0, tk.END); self.app_publisher.insert(0, data.get("app_publisher", ""))
            self.main_script.delete(0, tk.END); self.main_script.insert(0, data.get("main_script", ""))
            self.app_icon.delete(0, tk.END); self.app_icon.insert(0, data.get("app_icon", ""))
            self.output_dir.delete(0, tk.END); self.output_dir.insert(0, data.get("output_dir", ""))
            
            self.hidden_imports.delete("1.0", tk.END); self.hidden_imports.insert(tk.END, data.get("hidden_imports", ""))
            self.collect_all.delete("1.0", tk.END); self.collect_all.insert(tk.END, data.get("collect_all", ""))
            self.excludes.delete("1.0", tk.END); self.excludes.insert(tk.END, data.get("excludes", ""))
            
            self.show_console.set(data.get("show_console", False))
            
            self.extra_datas = data.get("extra_datas", [])
            self.list_extras.delete(0, tk.END)
            for src, dst in self.extra_datas:
                if src == dst:
                    self.list_extras.insert(tk.END, f"📁 {src} -> {dst}")
                else:
                    self.list_extras.insert(tk.END, f"📄 {src} -> {dst}")
            messagebox.showinfo("Sucesso", "Perfil carregado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar perfil: {e}")

    # --- Lógica do Compilador ---
    def get_safe_name(self):
        return self.app_name.get().replace(" ", "_").upper()

    def generate_files(self):
        name = self.app_name.get().strip()
        version = self.app_version.get().strip()
        main_script = self.main_script.get().strip()
        icon = self.app_icon.get().strip()
        publisher = self.app_publisher.get().strip()
        
        if not name or not main_script:
            messagebox.showerror("Erro", "Nome do App e Script Principal são obrigatórios!")
            return False

        safe_name = self.get_safe_name()
        
        out_dir = self.output_dir.get().strip()
        if not out_dir: out_dir = os.getcwd()
        os.makedirs(out_dir, exist_ok=True)
        
        # 1. Gerar .spec
        spec_content = self.create_spec_content(safe_name, main_script, icon)
        spec_filename = os.path.join(out_dir, f"{safe_name}.spec")
        with open(spec_filename, "w", encoding="utf-8") as f:
            f.write(spec_content)
        self.log(f"✅ {safe_name}.spec gerado em {out_dir}")

        # 2. Gerar .iss
        iss_content = self.create_iss_content(name, safe_name, version, publisher, icon, out_dir)
        iss_filename = os.path.join(out_dir, f"instalador_{safe_name}.iss")
        with open(iss_filename, "w", encoding="utf-8") as f:
            f.write(iss_content)
        self.log(f"✅ instalador_{safe_name}.iss gerado em {out_dir}")
        
        messagebox.showinfo("Sucesso", "Arquivos de configuração gerados com sucesso!")
        return True

    def create_spec_content(self, safe_name, main_script, icon):
        datas_list = []
        for src, dst in self.extra_datas:
            src = src.replace('\\', '/')
            datas_list.append(f"('{src}', '{dst}')")
        datas_str = ",\n        ".join(datas_list)
        
        imports_raw = self.hidden_imports.get("1.0", tk.END).strip()
        imports_list = [f"'{i.strip()}'" for i in imports_raw.split(",") if i.strip()]
        imports_str = ",\n        ".join(imports_list)
        
        excludes_raw = self.excludes.get("1.0", tk.END).strip()
        excludes_list = [f"'{i.strip()}'" for i in excludes_raw.split(",") if i.strip()]
        excludes_str = ",\n        ".join(excludes_list)

        collect_raw = self.collect_all.get("1.0", tk.END).strip()
        collect_list = [i.strip() for i in collect_raw.split(",") if i.strip()]
        
        collect_code = ""
        for mod in collect_list:
            safe_mod = mod.replace("-", "_").replace(".", "_")
            collect_code += f"{safe_mod}_datas, {safe_mod}_binaries, {safe_mod}_hiddenimports = collect_all('{mod}')\n"
            
        collect_datas_ext = " + ".join([f"{mod.replace('-', '_').replace('.', '_')}_datas" for mod in collect_list])
        collect_binaries_ext = " + ".join([f"{mod.replace('-', '_').replace('.', '_')}_binaries" for mod in collect_list])
        collect_hidden_ext = " + ".join([f"{mod.replace('-', '_').replace('.', '_')}_hiddenimports" for mod in collect_list])
        
        if collect_datas_ext: collect_datas_ext = " + " + collect_datas_ext
        if collect_binaries_ext: collect_binaries_ext = " + " + collect_binaries_ext
        if collect_hidden_ext: collect_hidden_ext = " + " + collect_hidden_ext

        icon_str = f"icon='{icon.replace(chr(92), '/')}'," if icon else ""
        console_bool = "False" if self.show_console.get() else "True"

        spec = f"""# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_all

sys.setrecursionlimit(2000)

{collect_code}

a = Analysis(
    ['{main_script.replace(chr(92), '/')}'],
    pathex=[],
    binaries=[]{collect_binaries_ext},
    datas=[
        {datas_str}
    ]{collect_datas_ext},
    hiddenimports=[
        {imports_str}
    ]{collect_hidden_ext},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        {excludes_str}
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{safe_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console={console_bool},
    {icon_str}
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{safe_name}',
)
"""
        return spec

    def create_iss_content(self, name, safe_name, version, publisher, icon, out_dir):
        icon_line = f"SetupIconFile={icon}" if icon else ""
        icon_icon = f"UninstallDisplayIcon={{app}}\\{safe_name}.exe" if icon else ""
        app_id = str(uuid.uuid4()).upper()
        
        # Corrige as barras para o script Inno Setup
        out_dir_inno = out_dir.replace('/', '\\')

        iss = f"""[Setup]
AppId={{{{{app_id}}}}}
AppName={name}
AppVersion={version}
AppPublisher={publisher}
DefaultDirName={{autopf}}\\{name.replace(' ', '')}
DefaultGroupName={name}
OutputDir={out_dir_inno}\\Output
OutputBaseFilename=Instalador_{safe_name}
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
{icon_line}
{icon_icon}

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Files]
Source: "{out_dir_inno}\\dist\\{safe_name}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\{name}"; Filename: "{{app}}\\{safe_name}.exe"
Name: "{{autodesktop}}\\{name}"; Filename: "{{app}}\\{safe_name}.exe"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{safe_name}.exe"; Description: "{{cm:LaunchProgram,{name}}}"; Flags: nowait postinstall skipifsilent
"""
        return iss

    def start_compilation(self):
        if not self.generate_files():
            return
            
        safe_name = self.get_safe_name()
        out_dir = self.output_dir.get().strip() or os.getcwd()
        
        spec_file = os.path.join(out_dir, f"{safe_name}.spec")
        iss_file = os.path.join(out_dir, f"instalador_{safe_name}.iss")
        
        def run_thread():
            self.log(f"🚀 Iniciando PyInstaller no diretório {out_dir}...")
            try:
                # 1. PyInstaller
                process = subprocess.Popen([sys.executable, "-m", "PyInstaller", "--clean", "-y", 
                                            "--distpath", os.path.join(out_dir, "dist"),
                                            "--workpath", os.path.join(out_dir, "build"),
                                            spec_file], 
                                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=out_dir)
                for line in process.stdout:
                    self.log(line.strip())
                process.wait()
                
                if process.returncode != 0:
                    self.log("❌ Erro no PyInstaller. Compilação abortada.")
                    return

                self.log("✅ PyInstaller concluído. Iniciando Inno Setup...")

                # 2. Inno Setup
                inno_paths = [
                    r"C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe",
                    r"C:\\Program Files\\Inno Setup 6\\ISCC.exe"
                ]
                iscc_exe = next((p for p in inno_paths if os.path.exists(p)), None)
                
                if iscc_exe:
                    process_inno = subprocess.Popen([iscc_exe, iss_file], 
                                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                    for line in process_inno.stdout:
                        self.log(line.strip())
                    process_inno.wait()
                    
                    if process_inno.returncode == 0:
                        self.log("🎉 COMPILAÇÃO FINALIZADA COM SUCESSO!")
                        self.log("O instalador está na pasta 'Output'.")
                        messagebox.showinfo("Pronto!", "Instalador gerado com sucesso na pasta Output!")
                    else:
                        self.log("❌ Erro no Inno Setup.")
                else:
                    self.log("⚠️ Inno Setup não encontrado. Instale o Inno Setup 6 para gerar o instalador final.")
                    messagebox.showwarning("Inno Setup", "Inno Setup não encontrado. O executável foi gerado na pasta dist/, mas o instalador não pôde ser criado.")

            except Exception as e:
                self.log(f"❌ ERRO GRAVE: {str(e)}")

        threading.Thread(target=run_thread, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartCompilerApp(root)
    root.mainloop()
