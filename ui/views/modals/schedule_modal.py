"""
Modal de Programación Horaria Semanal (ui/views/modals/schedule_modal.py)
KestrelWOL - CustomTkinter (Industrial Enterprise Dark Mode)
"""

import tkinter as tk
from tkinter import messagebox
from typing import Any, Callable, Dict, List, Optional
import customtkinter as ctk

from core.config import (
    ACCENT_EMERALD,
    ACCENT_ROSE,
    BG_BORDER,
    BG_BORDER_BUTTON,
    BG_BTN_SECONDARY,
    BG_CARD,
    BG_DARK,
    BG_INPUT,
    BUTTON_PRIMARY_TEXT,
    FONT_FAMILY_MONO,
    FONTS,
    HOVER_EMERALD,
    HOVER_SECONDARY,
    MODAL_SIZES,
    TEXT_DISABLED,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    UI_RADIUS,
)
from ui.components.icons import get_icon


class ScheduleModal(ctk.CTkToplevel):
    """
    Diálogo modal para configurar encendidos programados recurrentes:
    - Selector de hora 24h (HH:MM).
    - Días de la semana activos (Lun-Dom).
    """

    def __init__(
        self,
        parent,
        machine: Dict[str, Any],
        on_save_schedule: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        super().__init__(parent)
        self.machine = machine
        self.on_save_schedule = on_save_schedule

        w, h = MODAL_SIZES["schedule"]
        self.title(f"Programar Encendido: {machine.get('name')}")
        self.geometry(f"{w}x{h}")
        self.minsize(w, h)
        self.configure(fg_color=BG_DARK)

        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self) -> None:
        curr_sched = self.machine.get("schedule") or {}
        init_enabled = bool(curr_sched.get("enabled", False))
        init_time = curr_sched.get("time", "08:00")
        init_days = curr_sched.get("days", [0, 1, 2, 3, 4])

        try:
            init_h, init_m = init_time.split(":")
        except Exception:
            init_h, init_m = "08", "00"

        header = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BG_BORDER,
            corner_radius=UI_RADIUS
        )
        header.pack(fill=tk.X, padx=16, pady=(16, 10))

        ctk.CTkLabel(
            header,
            text="  Programar Encendido Automático",
            image=get_icon("clock", TEXT_PRIMARY, 15),
            compound="left",
            font=FONTS["title_section"],
            text_color=TEXT_PRIMARY,
            anchor="w"
        ).pack(anchor="w", padx=14, pady=(10, 2))

        ctk.CTkLabel(
            header,
            text=f"Equipo: {self.machine.get('name')} ({self.machine.get('ip')})",
            font=FONTS["mono_log"],
            text_color=TEXT_MUTED,
            anchor="w"
        ).pack(anchor="w", padx=14, pady=(0, 10))

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(side=tk.BOTTOM, fill=tk.X, padx=16, pady=(0, 14))

        ctk.CTkButton(
            footer,
            text="Cancelar",
            font=FONTS["body_normal"],
            fg_color=BG_BTN_SECONDARY,
            hover_color=HOVER_SECONDARY,
            border_width=1,
            border_color=BG_BORDER_BUTTON,
            text_color=TEXT_SECONDARY,
            width=0,
            height=32,
            corner_radius=UI_RADIUS,
            command=self.destroy
        ).pack(side=tk.LEFT)

        if init_enabled:
            ctk.CTkButton(
                footer,
                text="Desactivar",
                image=get_icon("trash", TEXT_MUTED, 14),
                compound="left",
                font=FONTS["body_bold"],
                fg_color=BG_BTN_SECONDARY,
                hover_color=ACCENT_ROSE,
                border_width=1,
                border_color=BG_BORDER_BUTTON,
                text_color=TEXT_MUTED,
                width=0,
                height=32,
                corner_radius=UI_RADIUS,
                command=self._disable
            ).pack(side=tk.RIGHT, padx=(6, 0))

        ctk.CTkButton(
            footer,
            text="Guardar Programación",
            image=get_icon("check", BUTTON_PRIMARY_TEXT, 14),
            compound="left",
            font=FONTS["body_bold"],
            fg_color=ACCENT_EMERALD,
            hover_color=HOVER_EMERALD,
            text_color=BUTTON_PRIMARY_TEXT,
            width=0,
            height=32,
            corner_radius=UI_RADIUS,
            command=self._save
        ).pack(side=tk.RIGHT)

        card = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BG_BORDER,
            corner_radius=UI_RADIUS
        )
        card.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 12))

        self.var_enabled = ctk.BooleanVar(value=init_enabled)
        chk_enabled = ctk.CTkCheckBox(
            card,
            text=" Habilitar programación automática para este equipo",
            variable=self.var_enabled,
            font=FONTS["body_bold"],
            text_color=TEXT_PRIMARY,
            fg_color=ACCENT_EMERALD,
            hover_color=HOVER_EMERALD,
            border_color=BG_BORDER_BUTTON,
            corner_radius=4
        )
        chk_enabled.pack(anchor="w", padx=14, pady=(14, 12))

        # 1. Selector de Hora
        ctk.CTkLabel(card, text="1. HORA DE ENCENDIDO (FORMATO 24H)", font=FONTS["micro"], text_color=TEXT_DISABLED).pack(anchor="w", padx=14, pady=(0, 6))

        time_frame = ctk.CTkFrame(card, fg_color="transparent")
        time_frame.pack(anchor="w", padx=14, pady=(0, 14))

        spin_kwargs = {
            "width": 3,
            "font": (FONT_FAMILY_MONO, 16, "bold"),
            "bg": BG_INPUT,
            "fg": TEXT_PRIMARY,
            "buttonbackground": BG_BTN_SECONDARY,
            "insertbackground": TEXT_PRIMARY,
            "highlightthickness": 1,
            "highlightbackground": BG_BORDER_BUTTON,
            "highlightcolor": ACCENT_EMERALD,
            "bd": 0,
            "justify": "center",
        }

        self.spin_h = tk.Spinbox(time_frame, from_=0, to=23, format="%02.0f", **spin_kwargs)
        self.spin_h.delete(0, "end")
        self.spin_h.insert(0, init_h)
        self.spin_h.pack(side=tk.LEFT)

        tk.Label(time_frame, text=":", font=(FONT_FAMILY_MONO, 18, "bold"), fg=TEXT_MUTED, bg=BG_CARD).pack(side=tk.LEFT, padx=6)

        self.spin_m = tk.Spinbox(time_frame, from_=0, to=59, format="%02.0f", **spin_kwargs)
        self.spin_m.delete(0, "end")
        self.spin_m.insert(0, init_m)
        self.spin_m.pack(side=tk.LEFT)

        # 2. Selector de Días
        ctk.CTkLabel(card, text="2. DÍAS DE LA SEMANA", font=FONTS["micro"], text_color=TEXT_DISABLED).pack(anchor="w", padx=14, pady=(0, 6))

        days_info = [
            ("Lunes", 0), ("Martes", 1), ("Miércoles", 2), ("Jueves", 3),
            ("Viernes", 4), ("Sábado", 5), ("Domingo", 6)
        ]
        grid_days = ctk.CTkFrame(card, fg_color="transparent")
        grid_days.pack(fill=tk.X, padx=14, pady=(0, 10))

        self.day_vars: List[ctk.BooleanVar] = []
        for idx, (day_name, day_val) in enumerate(days_info):
            var = ctk.BooleanVar(value=(day_val in init_days))
            self.day_vars.append(var)
            cb = ctk.CTkCheckBox(
                grid_days,
                text=f" {day_name}",
                variable=var,
                font=FONTS["body_normal"],
                text_color=TEXT_PRIMARY,
                fg_color=ACCENT_EMERALD,
                hover_color=HOVER_EMERALD,
                border_color=BG_BORDER_BUTTON,
                corner_radius=4
            )
            col = idx % 2
            row = idx // 2
            cb.grid(row=row, column=col, sticky="w", padx=(0, 24), pady=4)

    def _save(self) -> None:
        try:
            h = int(self.spin_h.get())
            m = int(self.spin_m.get())
            if not (0 <= h <= 23 and 0 <= m <= 59):
                raise ValueError()
            h_str, m_str = f"{h:02d}", f"{m:02d}"
        except Exception:
            messagebox.showwarning("Hora inválida", "Por favor ingresa una hora válida (00-23 y 00-59).", parent=self)
            return

        selected = [idx for idx, var in enumerate(self.day_vars) if var.get()]
        if self.var_enabled.get() and not selected:
            messagebox.showwarning("Días no seleccionados", "Debes seleccionar al menos un día.", parent=self)
            return

        sched = {
            "enabled": self.var_enabled.get(),
            "time": f"{h_str}:{m_str}",
            "days": selected
        }
        self.destroy()
        if self.on_save_schedule:
            self.on_save_schedule(sched)

    def _disable(self) -> None:
        sched = {
            "enabled": False,
            "time": f"{self.spin_h.get().zfill(2)}:{self.spin_m.get().zfill(2)}",
            "days": [idx for idx, var in enumerate(self.day_vars) if var.get()]
        }
        self.destroy()
        if self.on_save_schedule:
            self.on_save_schedule(sched)
