from __future__ import annotations

import logging
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .calibration import calibration_from_config
from .config import (
    CONFIG_FILES,
    RuntimeConfig,
    export_backup,
    export_profile,
    import_backup,
    import_profile,
    list_profiles,
    load_config,
    load_profile,
    save_config_file,
    save_profile,
)
from .paths import ensure_portable_tree, log_path


class ConfiguratorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.home = ensure_portable_tree()
        self.logger = configure_logging(self.home)
        self.config = load_config(self.home)
        self.vars: dict[tuple[str, str], tk.StringVar] = {}
        self.profile_name = tk.StringVar(value="Novo_Perfil")
        self.status = tk.StringVar(value=f"Pasta portatil: {self.home}")
        self.root.title("Configurador - Optotipos Profissional")
        self.root.geometry("980x680")
        self.build_ui()

    def build_ui(self) -> None:
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.build_screen_tab(notebook)
        self.build_distance_tab(notebook)
        self.build_inversion_tab(notebook)
        self.build_profiles_tab(notebook)
        self.build_backup_tab(notebook)
        self.build_shortcuts_tab(notebook)

        footer = ttk.Frame(self.root)
        footer.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Label(footer, textvariable=self.status).pack(side="left")
        ttk.Button(footer, text="Salvar tudo", command=self.save_all).pack(side="right", padx=4)
        ttk.Button(footer, text="Recarregar", command=self.reload).pack(side="right", padx=4)

    def build_screen_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Tela e monitores")
        group = ttk.LabelFrame(frame, text="Tela fisica e resolucao")
        group.pack(fill="x", padx=12, pady=12)
        self.field(group, "Tela.txt", "Polegadas", "Polegadas", 0)
        self.field(group, "Tela.txt", "LarguraTelaMM", "Largura da tela (mm)", 1)
        self.field(group, "Tela.txt", "AlturaTelaMM", "Altura da tela (mm)", 2)
        self.field(group, "Tela.txt", "ResolucaoLargura", "Resolucao horizontal", 3)
        self.field(group, "Tela.txt", "ResolucaoAltura", "Resolucao vertical", 4)
        ttk.Button(group, text="Detectar resolucao atual", command=self.detect_resolution).grid(row=5, column=1, sticky="w", padx=8, pady=8)

        monitor_group = ttk.LabelFrame(frame, text="Modo de exibicao")
        monitor_group.pack(fill="x", padx=12, pady=12)
        self.combo(monitor_group, "Monitores.txt", "Modo", "Modo", ("TelaUnica", "DuasTelas", "Espelhamento"), 0)
        self.field(monitor_group, "Monitores.txt", "MonitorExaminador", "Monitor examinador", 1)
        self.field(monitor_group, "Monitores.txt", "MonitorTeste", "Monitor de testes", 2)
        self.combo(monitor_group, "Exibicao.txt", "Fundo", "Fundo", ("branco", "preto"), 3)
        self.combo(monitor_group, "Exibicao.txt", "TelaCheia", "Tela cheia", ("ON", "OFF"), 4)
        self.combo(monitor_group, "Exibicao.txt", "BarraFerramentas", "Barra de ferramentas", ("ON", "OFF"), 5)
        self.field(monitor_group, "Exibicao.txt", "Brilho", "Brilho (%)", 6)
        self.field(monitor_group, "Exibicao.txt", "Luminancia", "Luminancia (%)", 7)

    def build_distance_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Distancia e escala")
        group = ttk.LabelFrame(frame, text="Distancia de exame")
        group.pack(fill="x", padx=12, pady=12)
        self.field(group, "Distancia.txt", "Distancia", "Distancia", 0)
        self.combo(group, "Distancia.txt", "Unidade", "Unidade", ("m", "cm", "mm"), 1)

        scale = ttk.LabelFrame(frame, text="Assistente de calibracao da regua")
        scale.pack(fill="both", expand=True, padx=12, pady=12)
        self.field(scale, "Escala.txt", "FatorEscala", "Fator de escala", 0)
        self.field(scale, "Escala.txt", "Polegadas", "Polegadas", 1)
        self.field(scale, "Escala.txt", "LarguraTelaMM", "Largura da tela (mm)", 2)
        self.field(scale, "Escala.txt", "AlturaTelaMM", "Altura da tela (mm)", 3)
        ttk.Label(scale, text="A linha abaixo representa 100 mm. Ajuste ate coincidir com uma regua real.").grid(row=4, column=0, columnspan=3, sticky="w", padx=8, pady=(12, 4))
        self.ruler = tk.Canvas(scale, height=110, background="white", highlightthickness=1, highlightbackground="#cccccc")
        self.ruler.grid(row=5, column=0, columnspan=3, sticky="ew", padx=8, pady=8)
        scale.columnconfigure(1, weight=1)
        buttons = ttk.Frame(scale)
        buttons.grid(row=6, column=0, columnspan=3, sticky="w", padx=8, pady=8)
        ttk.Button(buttons, text="-0.5%", command=lambda: self.adjust_scale(0.995)).pack(side="left", padx=3)
        ttk.Button(buttons, text="+0.5%", command=lambda: self.adjust_scale(1.005)).pack(side="left", padx=3)
        ttk.Button(buttons, text="Salvar escala", command=self.save_all).pack(side="left", padx=3)
        self.ruler.bind("<Configure>", lambda _event: self.draw_ruler())
        self.draw_ruler()

    def build_inversion_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Inversao")
        group = ttk.LabelFrame(frame, text="Inversao e rotacao")
        group.pack(fill="x", padx=12, pady=12)
        self.combo(group, "Inversao.txt", "Horizontal", "Espelhamento horizontal", ("OFF", "ON"), 0)
        self.combo(group, "Inversao.txt", "Vertical", "Espelhamento vertical", ("OFF", "ON"), 1)
        self.combo(group, "Inversao.txt", "Rotacao", "Rotacao", ("0", "90", "180", "270"), 2)
        self.combo(group, "Exibicao.txt", "Filtro", "Filtro padrao", ("Nenhum", "Vermelho", "Verde", "Azul", "Polarizado", "Anaglifo"), 3)

    def build_profiles_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Perfis")
        left = ttk.Frame(frame)
        left.pack(side="left", fill="both", expand=True, padx=12, pady=12)
        right = ttk.Frame(frame)
        right.pack(side="left", fill="y", padx=12, pady=12)
        self.profile_list = tk.Listbox(left, height=18)
        self.profile_list.pack(fill="both", expand=True)
        ttk.Label(right, text="Nome do perfil").pack(anchor="w")
        ttk.Entry(right, textvariable=self.profile_name, width=30).pack(fill="x", pady=4)
        ttk.Button(right, text="Salvar perfil", command=self.save_profile_clicked).pack(fill="x", pady=4)
        ttk.Button(right, text="Carregar selecionado", command=self.load_profile_clicked).pack(fill="x", pady=4)
        ttk.Button(right, text="Exportar selecionado", command=self.export_profile_clicked).pack(fill="x", pady=4)
        ttk.Button(right, text="Importar perfil", command=self.import_profile_clicked).pack(fill="x", pady=4)
        self.refresh_profiles()

    def build_backup_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Backup")
        ttk.Label(frame, text="Exporta todas as configuracoes e perfis para BackupCalibracao.opt.").pack(anchor="w", padx=12, pady=(20, 8))
        ttk.Button(frame, text="Exportar Configuracao", command=self.export_backup_clicked).pack(anchor="w", padx=12, pady=6)
        ttk.Button(frame, text="Importar Configuracao", command=self.import_backup_clicked).pack(anchor="w", padx=12, pady=6)

    def build_shortcuts_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Atalhos")
        group = ttk.LabelFrame(frame, text="Teclado e controle")
        group.pack(fill="x", padx=12, pady=12)
        for row, key in enumerate(("ConfiguracoesAvancadas", "ProximoTeste", "TesteAnterior", "Aumentar", "Diminuir", "Aleatorio")):
            self.field(group, "Atalhos.txt", key, key, row)

    def field(self, parent: ttk.Frame, file_name: str, key: str, label: str, row: int) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=8, pady=5)
        var = self.var(file_name, key)
        ttk.Entry(parent, textvariable=var, width=24).grid(row=row, column=1, sticky="w", padx=8, pady=5)

    def combo(self, parent: ttk.Frame, file_name: str, key: str, label: str, values: tuple[str, ...], row: int) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=8, pady=5)
        var = self.var(file_name, key)
        ttk.Combobox(parent, textvariable=var, values=values, state="readonly", width=22).grid(row=row, column=1, sticky="w", padx=8, pady=5)

    def var(self, file_name: str, key: str) -> tk.StringVar:
        variable_key = (file_name, key)
        if variable_key not in self.vars:
            self.vars[variable_key] = tk.StringVar(value=self.config.get(file_name, key, ""))
        return self.vars[variable_key]

    def detect_resolution(self) -> None:
        self.var("Tela.txt", "ResolucaoLargura").set(str(self.root.winfo_screenwidth()))
        self.var("Tela.txt", "ResolucaoAltura").set(str(self.root.winfo_screenheight()))
        self.status.set("Resolucao detectada.")

    def adjust_scale(self, multiplier: float) -> None:
        variable = self.var("Escala.txt", "FatorEscala")
        try:
            value = float(variable.get().replace(",", "."))
        except ValueError:
            value = 1.0
        variable.set(f"{value * multiplier:.4f}")
        self.draw_ruler()

    def draw_ruler(self) -> None:
        if not hasattr(self, "ruler"):
            return
        self.ruler.delete("all")
        width = max(self.ruler.winfo_width(), 600)
        try:
            config = self.preview_config()
            calibration = calibration_from_config(config)
            pixels = calibration.pixels_per_mm_x * 100
        except Exception:
            pixels = 320
        x1 = max(30, (width - pixels) / 2)
        x2 = min(width - 30, x1 + pixels)
        y = 55
        self.ruler.create_line(x1, y, x2, y, fill="black", width=5)
        self.ruler.create_line(x1, y - 18, x1, y + 18, fill="black", width=3)
        self.ruler.create_line(x2, y - 18, x2, y + 18, fill="black", width=3)
        self.ruler.create_text((x1 + x2) / 2, y + 32, text="100 mm", fill="black", font=("Arial", 14, "bold"))

    def preview_config(self) -> RuntimeConfig:
        values = {file_name: dict(self.config.values[file_name]) for file_name in CONFIG_FILES}
        for (file_name, key), variable in self.vars.items():
            values[file_name][key] = variable.get()
        return RuntimeConfig(root=self.home, values=values)

    def save_all(self) -> None:
        grouped: dict[str, dict[str, str]] = {file_name: {} for file_name in CONFIG_FILES}
        for (file_name, key), variable in self.vars.items():
            grouped[file_name][key] = variable.get()
        for file_name, values in grouped.items():
            if values:
                save_config_file(file_name, values, self.home)
        self.config = load_config(self.home)
        self.status.set("Configuracoes salvas.")
        self.logger.info("Configuracoes salvas")

    def reload(self) -> None:
        self.config = load_config(self.home)
        for (file_name, key), variable in self.vars.items():
            variable.set(self.config.get(file_name, key, ""))
        self.draw_ruler()
        self.refresh_profiles()
        self.status.set("Configuracoes recarregadas.")

    def refresh_profiles(self) -> None:
        self.profile_list.delete(0, tk.END)
        for profile in list_profiles(self.home):
            self.profile_list.insert(tk.END, profile.name)

    def selected_profile(self) -> str | None:
        selection = self.profile_list.curselection()
        if not selection:
            return None
        return self.profile_list.get(selection[0])

    def save_profile_clicked(self) -> None:
        self.save_all()
        path = save_profile(self.profile_name.get(), self.home)
        self.refresh_profiles()
        self.status.set(f"Perfil salvo: {path.name}")

    def load_profile_clicked(self) -> None:
        name = self.selected_profile()
        if not name:
            messagebox.showwarning("Perfis", "Selecione um perfil.")
            return
        load_profile(name, self.home)
        self.reload()
        self.status.set(f"Perfil carregado: {name}")

    def export_profile_clicked(self) -> None:
        name = self.selected_profile()
        if not name:
            messagebox.showwarning("Perfis", "Selecione um perfil.")
            return
        destination = filedialog.asksaveasfilename(defaultextension=".ini", initialfile=name, filetypes=[("Perfil INI", "*.ini")])
        if destination:
            export_profile(name, Path(destination), self.home)
            self.status.set("Perfil exportado.")

    def import_profile_clicked(self) -> None:
        source = filedialog.askopenfilename(filetypes=[("Perfil INI", "*.ini")])
        if source:
            imported = import_profile(Path(source), self.home)
            self.refresh_profiles()
            self.status.set(f"Perfil importado: {imported.name}")

    def export_backup_clicked(self) -> None:
        destination = filedialog.asksaveasfilename(defaultextension=".opt", initialfile="BackupCalibracao.opt", filetypes=[("Backup Optotipos", "*.opt")])
        if destination:
            path = export_backup(Path(destination), self.home)
            self.status.set(f"Backup exportado: {path.name}")

    def import_backup_clicked(self) -> None:
        source = filedialog.askopenfilename(filetypes=[("Backup Optotipos", "*.opt")])
        if source:
            import_backup(Path(source), self.home)
            self.reload()
            self.status.set("Backup importado.")


def configure_logging(root: Path) -> logging.Logger:
    logger = logging.getLogger("configurador")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path("Configurador.txt", root), encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.info("Configurador iniciado")
    return logger


def run() -> None:
    root = tk.Tk()
    ConfiguratorApp(root)
    root.mainloop()
