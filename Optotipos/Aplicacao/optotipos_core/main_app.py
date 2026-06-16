from __future__ import annotations

import logging
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import messagebox, ttk
except ModuleNotFoundError:  # pragma: no cover - Windows builds include Tkinter.
    tk = None
    messagebox = None
    ttk = None

from .calibration import calibration_from_config
from .catalog import TESTS, categories, tests_by_category
from .config import RuntimeConfig, load_config, save_config_file
from .desktop_shortcut import ensure_desktop_shortcut
from .paths import ensure_portable_tree, log_path
from .rendering import RenderOptions, RenderState, SNELLEN_DENOMINATORS, render_test
from .wireless import RemoteServer


@dataclass(frozen=True)
class MonitorRect:
    x: int
    y: int
    width: int
    height: int

    def geometry(self) -> str:
        return f"{self.width}x{self.height}+{self.x}+{self.y}"


@dataclass(frozen=True)
class DisplayWindowPlan:
    title: str
    monitor: MonitorRect
    fullscreen: bool
    horizontal_mirror: bool = False
    vertical_mirror: bool = False


@dataclass(frozen=True)
class MonitorLayoutPlan:
    requested_mode: str
    effective_mode: str
    main_monitor: MonitorRect
    main_fullscreen: bool
    display_windows: tuple[DisplayWindowPlan, ...]
    horizontal_mirror: bool = False
    vertical_mirror: bool = False
    fallback_reason: str = ""

    @property
    def total_canvases(self) -> int:
        return 1 + len(self.display_windows)


def detect_monitors(root: tk.Tk) -> list[MonitorRect]:
    if tk is None:
        return [MonitorRect(0, 0, 1280, 720)]
    if sys.platform == "win32":
        try:
            return detect_windows_monitors()
        except Exception:
            pass

    virtual_width = max(root.winfo_vrootwidth(), root.winfo_screenwidth())
    virtual_height = max(root.winfo_vrootheight(), root.winfo_screenheight())
    virtual_x = root.winfo_vrootx()
    virtual_y = root.winfo_vrooty()
    screen_width = max(root.winfo_screenwidth(), 1)
    if virtual_width > screen_width:
        count = max(1, round(virtual_width / screen_width))
        return [MonitorRect(virtual_x + index * screen_width, virtual_y, screen_width, virtual_height) for index in range(count)]
    return [MonitorRect(virtual_x, virtual_y, virtual_width, virtual_height)]


def detect_windows_monitors() -> list[MonitorRect]:
    import ctypes
    from ctypes import wintypes

    monitors: list[MonitorRect] = []

    class RECT(ctypes.Structure):
        _fields_ = [
            ("left", ctypes.c_long),
            ("top", ctypes.c_long),
            ("right", ctypes.c_long),
            ("bottom", ctypes.c_long),
        ]

    monitor_enum_proc = ctypes.WINFUNCTYPE(
        ctypes.c_int,
        wintypes.HMONITOR,
        wintypes.HDC,
        ctypes.POINTER(RECT),
        wintypes.LPARAM,
    )

    def callback(_monitor, _dc, rect, _data):
        monitors.append(MonitorRect(rect.contents.left, rect.contents.top, rect.contents.right - rect.contents.left, rect.contents.bottom - rect.contents.top))
        return 1

    ctypes.windll.user32.EnumDisplayMonitors(0, 0, monitor_enum_proc(callback), 0)
    return monitors or [MonitorRect(0, 0, 1920, 1080)]


def bounded_monitor(monitors: list[MonitorRect], index: int) -> MonitorRect:
    if not monitors:
        return MonitorRect(0, 0, 1280, 720)
    return monitors[max(0, min(index, len(monitors) - 1))]


def plan_monitor_layout(
    mode: str,
    monitors: list[MonitorRect],
    examiner_index: int = 0,
    test_index: int = 0,
    fullscreen: bool = True,
    horizontal_mirror: bool = False,
    vertical_mirror: bool = False,
) -> MonitorLayoutPlan:
    available = monitors or [MonitorRect(0, 0, 1280, 720)]
    requested_mode = mode if mode in {"TelaUnica", "DuasTelas", "Espelhamento"} else "TelaUnica"

    if requested_mode == "DuasTelas":
        if len(available) < 2:
            return MonitorLayoutPlan(
                requested_mode=mode,
                effective_mode="TelaUnica",
                main_monitor=bounded_monitor(available, test_index),
                main_fullscreen=fullscreen,
                display_windows=(),
                horizontal_mirror=horizontal_mirror,
                vertical_mirror=vertical_mirror,
                fallback_reason="DuasTelas requer pelo menos dois monitores detectados.",
            )
        return MonitorLayoutPlan(
            requested_mode=mode,
            effective_mode="DuasTelas",
            main_monitor=bounded_monitor(available, examiner_index),
            main_fullscreen=False,
            display_windows=(DisplayWindowPlan("Exibicao de Testes", bounded_monitor(available, test_index), True, horizontal_mirror, vertical_mirror),),
            horizontal_mirror=horizontal_mirror,
            vertical_mirror=vertical_mirror,
        )

    if requested_mode == "Espelhamento":
        if len(available) < 2:
            return MonitorLayoutPlan(
                requested_mode=mode,
                effective_mode="TelaUnica",
                main_monitor=bounded_monitor(available, test_index),
                main_fullscreen=fullscreen,
                display_windows=(),
                horizontal_mirror=horizontal_mirror,
                vertical_mirror=vertical_mirror,
                fallback_reason="Espelhamento requer monitores adicionais detectados.",
            )
        return MonitorLayoutPlan(
            requested_mode=mode,
            effective_mode="Espelhamento",
            main_monitor=bounded_monitor(available, 0),
            main_fullscreen=fullscreen,
            display_windows=tuple(DisplayWindowPlan(f"Espelho {index}", monitor, True, horizontal_mirror, vertical_mirror) for index, monitor in enumerate(available[1:], start=1)),
            horizontal_mirror=horizontal_mirror,
            vertical_mirror=vertical_mirror,
        )

    return MonitorLayoutPlan(
        requested_mode=mode,
        effective_mode="TelaUnica",
        main_monitor=bounded_monitor(available, test_index),
        main_fullscreen=fullscreen,
        display_windows=(),
        horizontal_mirror=horizontal_mirror,
        vertical_mirror=vertical_mirror,
    )


class OptotiposApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.home = ensure_portable_tree()
        self.logger = configure_logging(self.home)
        self.config = load_config(self.home)
        self.calibration = calibration_from_config(self.config)
        self.state = RenderState()
        self.current_index = 0
        self.current_category = tk.StringVar(value=categories()[0])
        self.status_text = tk.StringVar(value="")
        self.remote = RemoteServer(self.handle_remote_command)
        self.display_windows: list[tk.Toplevel] = []
        self.display_canvases: list[tk.Canvas] = []
        self.monitors: list[MonitorRect] = []

        self.root.title("Optotipos Profissional")
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.build_ui()
        self.bind_shortcuts()
        self.apply_window_mode()
        ensure_desktop_shortcut(self.home)
        self.render()

    def build_ui(self) -> None:
        self.toolbar = ttk.Frame(self.root)
        if self.config.get_bool("Exibicao.txt", "BarraFerramentas", True):
            self.toolbar.pack(side="top", fill="x")

        ttk.Label(self.toolbar, text="Categoria").pack(side="left", padx=(8, 4))
        self.category_combo = ttk.Combobox(self.toolbar, textvariable=self.current_category, values=categories(), state="readonly", width=22)
        self.category_combo.pack(side="left", padx=4)
        self.category_combo.bind("<<ComboboxSelected>>", self.on_category_changed)

        ttk.Label(self.toolbar, text="Teste").pack(side="left", padx=(10, 4))
        self.test_combo = ttk.Combobox(self.toolbar, state="readonly", width=28)
        self.test_combo.pack(side="left", padx=4)
        self.test_combo.bind("<<ComboboxSelected>>", self.on_test_changed)
        self.refresh_test_combo()

        for label, command in (
            ("Anterior", self.previous_test),
            ("Proximo", self.next_test),
            ("Menor", self.smaller),
            ("Maior", self.bigger),
            ("Aleatorio", self.toggle_random),
            ("Modo Monitor", self.cycle_monitor_mode),
            ("Wireless", self.toggle_wireless),
            ("Configuracoes Avancadas", self.open_configurator),
        ):
            ttk.Button(self.toolbar, text=label, command=command).pack(side="left", padx=3)

        ttk.Label(self.toolbar, textvariable=self.status_text).pack(side="left", padx=12)
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(side="top", fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _event: self.render())
        self.display_canvases = [self.canvas]

    def bind_shortcuts(self) -> None:
        self.root.bind("<Right>", lambda _event: self.next_test())
        self.root.bind("<Left>", lambda _event: self.previous_test())
        self.root.bind("<plus>", lambda _event: self.bigger())
        self.root.bind("<KP_Add>", lambda _event: self.bigger())
        self.root.bind("<minus>", lambda _event: self.smaller())
        self.root.bind("<KP_Subtract>", lambda _event: self.smaller())
        self.root.bind("<r>", lambda _event: self.toggle_random())
        self.root.bind("<R>", lambda _event: self.toggle_random())
        self.root.bind("<f>", lambda _event: self.toggle_fullscreen())
        self.root.bind("<F>", lambda _event: self.toggle_fullscreen())
        self.root.bind("<b>", lambda _event: self.toggle_background())
        self.root.bind("<B>", lambda _event: self.toggle_background())
        self.root.bind("<h>", lambda _event: self.toggle_horizontal())
        self.root.bind("<H>", lambda _event: self.toggle_horizontal())
        self.root.bind("<v>", lambda _event: self.toggle_vertical())
        self.root.bind("<V>", lambda _event: self.toggle_vertical())
        self.root.bind("<Escape>", lambda _event: self.root.attributes("-fullscreen", False))
        self.root.bind("<m>", lambda _event: self.cycle_monitor_mode())
        self.root.bind("<M>", lambda _event: self.cycle_monitor_mode())
        self.root.bind("<Control-Alt-c>", lambda _event: self.open_configurator())
        self.root.bind("<Control-Alt-C>", lambda _event: self.open_configurator())
        self.canvas.bind("<Button-1>", lambda _event: self.next_test())

    def apply_window_mode(self) -> None:
        self.monitors = detect_monitors(self.root)
        mode = self.config.get("Monitores.txt", "Modo", "TelaUnica")
        layout = plan_monitor_layout(
            mode=mode,
            monitors=self.monitors,
            examiner_index=self.config.get_int("Monitores.txt", "MonitorExaminador", 0),
            test_index=self.config.get_int("Monitores.txt", "MonitorTeste", 0),
            fullscreen=self.config.get_bool("Exibicao.txt", "TelaCheia", True),
            horizontal_mirror=self.config.get_bool("Inversao.txt", "Horizontal", False),
            vertical_mirror=self.config.get_bool("Inversao.txt", "Vertical", False),
        )
        self.destroy_display_windows()
        self.display_canvases = [self.canvas]

        self.root.attributes("-fullscreen", layout.main_fullscreen)
        self.root.geometry(layout.main_monitor.geometry())
        for display in layout.display_windows:
            self.create_display_window(display.monitor, display.title, fullscreen=display.fullscreen)

    def create_display_window(self, monitor: MonitorRect, title: str, fullscreen: bool) -> None:
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry(monitor.geometry())
        window.attributes("-fullscreen", fullscreen)
        canvas = tk.Canvas(window, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.bind("<Configure>", lambda _event: self.render())
        window.bind("<Escape>", lambda _event: window.attributes("-fullscreen", False))
        self.display_windows.append(window)
        self.display_canvases.append(canvas)

    def destroy_display_windows(self) -> None:
        for window in getattr(self, "display_windows", []):
            if window.winfo_exists():
                window.destroy()
        self.display_windows = []

    def refresh_test_combo(self) -> None:
        tests = tests_by_category(self.current_category.get())
        self.test_combo["values"] = [test.name for test in tests]
        self.test_combo.current(0)
        self.current_index = TESTS.index(tests[0])

    def on_category_changed(self, _event: object | None = None) -> None:
        self.refresh_test_combo()
        self.render()

    def on_test_changed(self, _event: object | None = None) -> None:
        selected = self.test_combo.get()
        for index, test in enumerate(TESTS):
            if test.name == selected:
                self.current_index = index
                break
        self.render()

    @property
    def current_test(self):
        return TESTS[self.current_index % len(TESTS)]

    def render_options(self) -> RenderOptions:
        background_name = self.config.get("Exibicao.txt", "Fundo", "branco").lower()
        background = "black" if background_name == "preto" else "white"
        foreground = "white" if background == "black" else "black"
        return RenderOptions(
            background=background,
            foreground=foreground,
            horizontal_mirror=self.config.get_bool("Inversao.txt", "Horizontal", False),
            vertical_mirror=self.config.get_bool("Inversao.txt", "Vertical", False),
            rotation=self.config.get_int("Inversao.txt", "Rotacao", 0),
            filter_name=self.config.get("Exibicao.txt", "Filtro", "Nenhum"),
        )

    def render(self) -> None:
        if not hasattr(self, "canvas"):
            return
        self.remote.set_current_test(self.current_test.name)
        options = self.render_options()
        for canvas in self.display_canvases:
            if canvas.winfo_exists():
                render_test(canvas, self.current_test, self.calibration, self.state, options)
        mode = self.config.get("Monitores.txt", "Modo", "TelaUnica")
        self.status_text.set(f"{self.current_test.name} | {self.calibration.distance_m:g} m | {mode} ({len(self.monitors)} monitor(es))")

    def next_test(self) -> None:
        self.current_index = (self.current_index + 1) % len(TESTS)
        self.sync_combo_to_current()
        self.render()

    def previous_test(self) -> None:
        self.current_index = (self.current_index - 1) % len(TESTS)
        self.sync_combo_to_current()
        self.render()

    def sync_combo_to_current(self) -> None:
        category = self.current_test.category
        if self.current_category.get() != category:
            self.current_category.set(category)
            self.test_combo["values"] = [test.name for test in tests_by_category(category)]
        self.test_combo.set(self.current_test.name)

    def bigger(self) -> None:
        denominators = sorted(SNELLEN_DENOMINATORS)
        current = min(denominators, key=lambda value: abs(value - self.state.denominator))
        index = denominators.index(current)
        self.state.denominator = denominators[min(index + 1, len(denominators) - 1)]
        self.state.single_line = True
        self.render()

    def smaller(self) -> None:
        denominators = sorted(SNELLEN_DENOMINATORS)
        current = min(denominators, key=lambda value: abs(value - self.state.denominator))
        index = denominators.index(current)
        self.state.denominator = denominators[max(index - 1, 0)]
        self.state.single_line = True
        self.render()

    def toggle_random(self) -> None:
        self.state.randomize = not self.state.randomize
        self.state.seed += 1
        self.render()

    def toggle_fullscreen(self) -> None:
        self.root.attributes("-fullscreen", not bool(self.root.attributes("-fullscreen")))
        for window in self.display_windows:
            window.attributes("-fullscreen", not bool(window.attributes("-fullscreen")))

    def toggle_background(self) -> None:
        current = self.config.values["Exibicao.txt"].get("Fundo", "branco")
        self.config.values["Exibicao.txt"]["Fundo"] = "preto" if current.lower() == "branco" else "branco"
        self.render()

    def toggle_horizontal(self) -> None:
        current = self.config.values["Inversao.txt"].get("Horizontal", "OFF")
        self.config.values["Inversao.txt"]["Horizontal"] = "OFF" if current.upper() == "ON" else "ON"
        self.render()

    def toggle_vertical(self) -> None:
        current = self.config.values["Inversao.txt"].get("Vertical", "OFF")
        self.config.values["Inversao.txt"]["Vertical"] = "OFF" if current.upper() == "ON" else "ON"
        self.render()

    def cycle_monitor_mode(self) -> None:
        modes = ("TelaUnica", "DuasTelas", "Espelhamento")
        current = self.config.values["Monitores.txt"].get("Modo", "TelaUnica")
        next_mode = modes[(modes.index(current) + 1) % len(modes)] if current in modes else "TelaUnica"
        self.config.values["Monitores.txt"]["Modo"] = next_mode
        save_config_file("Monitores.txt", self.config.values["Monitores.txt"], self.home)
        self.apply_window_mode()
        self.render()

    def toggle_wireless(self) -> None:
        if self.remote.running:
            self.remote.stop()
            self.status_text.set("Wireless desligado")
            return
        url = self.remote.start()
        self.status_text.set(f"Wireless: {url}")
        messagebox.showinfo("Wireless", f"Controle por smartphone iniciado em:\n{url}\n\nUse dispositivos na mesma rede local.")

    def handle_remote_command(self, command: str) -> None:
        self.root.after(0, lambda: self.execute_command(command))

    def execute_command(self, command: str) -> None:
        actions = {
            "next": self.next_test,
            "prev": self.previous_test,
            "bigger": self.bigger,
            "smaller": self.smaller,
            "random": self.toggle_random,
            "fullscreen": self.toggle_fullscreen,
            "blackwhite": self.toggle_background,
            "left_occlusion": lambda: self.set_occlusion("left"),
            "right_occlusion": lambda: self.set_occlusion("right"),
            "clear_occlusion": lambda: self.set_occlusion("none"),
        }
        action = actions.get(command)
        if action:
            action()

    def set_occlusion(self, value: str) -> None:
        self.state.occlusion = value
        self.render()

    def open_configurator(self) -> None:
        candidates = [
            self.home / "Configurador.exe",
            self.home.parent / "Configurador" / "Configurador.exe",
            self.home / "Configurador.pyw",
            self.home.parent / "Configurador" / "Configurador.pyw",
        ]
        for candidate in candidates:
            if candidate.exists():
                if candidate.suffix.lower() == ".pyw":
                    subprocess.Popen([sys.executable, str(candidate)], cwd=str(candidate.parent))
                else:
                    subprocess.Popen([str(candidate)], cwd=str(candidate.parent))
                return
        messagebox.showwarning("Configurador", "Configurador.exe nao foi encontrado.")

    def close(self) -> None:
        self.remote.stop()
        self.destroy_display_windows()
        self.root.destroy()


def configure_logging(root: Path) -> logging.Logger:
    logger = logging.getLogger("optotipos")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path("Optotipos.txt", root), encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.info("Software principal iniciado")
    return logger


def run() -> None:
    if tk is None:
        raise RuntimeError("Tkinter nao esta instalado neste ambiente.")
    root = tk.Tk()
    OptotiposApp(root)
    root.mainloop()
