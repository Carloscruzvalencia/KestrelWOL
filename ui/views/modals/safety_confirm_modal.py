"""
Modal de Confirmación de Seguridad Laboral (ui/views/modals/safety_confirm_modal.py)
Cumplimiento: Directiva 2006/42/CE & RD 1215/1997
"""

import tkinter as tk
from typing import Any, Callable, Dict, List, Optional
import customtkinter as ctk

from core.config import (
    ACCENT_AMBER,
    ACCENT_EMERALD,
    BG_CARD,
    BG_CONTAINER_DARK,
    BG_DARK,
    BG_INPUT,
    FONTS,
    HOVER_EMERALD,
    HOVER_SECONDARY,
    MODAL_SIZES,
    TEXT_MUTED,
    TEXT_PRIMARY,
)


class SafetyConfirmModal(ctk.CTkToplevel):
    """
    Diálogo modal de confirmación obligatoria previa a encendidos masivos:
    - Informa sobre los puestos que se van a encender.
    - Recuerda el retardo escalonado de 250 ms (REBT).
    - Exige certificación del operador de que la zona está despejada.
    """

    def __init__(
        self,
        parent,
        targets: List[Dict[str, Any]],
        scope_title: str,
        on_confirm: Optional[Callable[[List[Dict[str, Any]]], None]] = None
    ):
        super().__init__(parent)
        self.targets = targets
        self.scope_title = scope_title
        self.on_confirm = on_confirm

        w, h = MODAL_SIZES["safety_confirm"]
        self.title("⚠️ Confirmación de Seguridad Operativa")
        self.geometry(f"{w}x{h}")
        self.configure(fg_color=BG_DARK)

        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self) -> None:
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=8)
        card.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        ctk.CTkLabel(
            card,
            text="⚠️ PREVENCIÓN DE RIESGOS LABORALES (RD 1215/1997)",
            font=FONTS["title_section"],
            text_color=ACCENT_AMBER,
            anchor="w"
        ).pack(anchor="w", padx=16, pady=(16, 6))

        ctk.CTkLabel(
            card,
            text=f"Va a enviar una señal de encendido masivo para: {self.scope_title}",
            font=FONTS["body_bold"],
            text_color=TEXT_PRIMARY,
            anchor="w"
        ).pack(anchor="w", padx=16, pady=(0, 10))

        # Desglose de puestos
        breakdown = ctk.CTkFrame(card, fg_color=BG_CONTAINER_DARK, corner_radius=6)
        breakdown.pack(fill=tk.X, padx=16, pady=(0, 10))

        ctk.CTkLabel(
            breakdown,
            text=f"• Total de equipos a encender: {len(self.targets)} equipo(s)",
            font=FONTS["body_bold"],
            text_color=ACCENT_EMERALD,
            anchor="w"
        ).pack(anchor="w", padx=12, pady=(10, 10))

        # Aviso REBT
        elec_box = ctk.CTkFrame(card, fg_color="transparent")
        elec_box.pack(fill=tk.X, padx=16, pady=(0, 12))

        ctk.CTkLabel(
            elec_box,
            text="⚡ REBT / UNE-EN 62040: El encendido se ejecutará con retardo escalonado de 250 ms\n"
                 "entre paquetes para proteger contra picos de corriente (inrush current) en SAIs.",
            font=FONTS["caption_normal"],
            text_color="#38bdf8",
            justify="left",
            anchor="w"
        ).pack(anchor="w")

        if not self.targets:
            ctk.CTkLabel(
                card,
                text="❌ No hay equipos en la lista seleccionada.",
                font=FONTS["body_bold"],
                text_color="#f87171"
            ).pack(pady=10)

            ctk.CTkButton(
                card,
                text="Entendido",
                font=FONTS["body_normal"],
                fg_color=BG_INPUT,
                hover_color=HOVER_SECONDARY,
                text_color=TEXT_PRIMARY,
                command=self.destroy
            ).pack(side=tk.RIGHT, padx=16, pady=10)
        else:
            self.chk_safe = ctk.BooleanVar(value=False)
            chk = ctk.CTkCheckBox(
                card,
                text=" Certifico que el área física y periféricos están despejados sin operarios en riesgo",
                variable=self.chk_safe,
                font=FONTS["body_bold"],
                text_color=TEXT_PRIMARY,
                fg_color=ACCENT_EMERALD,
                hover_color=HOVER_EMERALD,
                command=self._on_check_toggle
            )
            chk.pack(anchor="w", padx=16, pady=(0, 16))

            btn_box = ctk.CTkFrame(card, fg_color="transparent")
            btn_box.pack(fill=tk.X, padx=16, pady=(0, 12))

            ctk.CTkButton(
                btn_box,
                text="Cancelar",
                font=FONTS["body_normal"],
                fg_color=BG_INPUT,
                hover_color=HOVER_SECONDARY,
                text_color=TEXT_PRIMARY,
                command=self.destroy
            ).pack(side=tk.LEFT)

            self.btn_confirm = ctk.CTkButton(
                btn_box,
                text="⚡ Confirmar y Encender",
                font=FONTS["body_bold"],
                fg_color=ACCENT_EMERALD,
                hover_color=HOVER_EMERALD,
                text_color=TEXT_PRIMARY,
                state="disabled",
                command=self._confirm
            )
            self.btn_confirm.pack(side=tk.RIGHT)

    def _on_check_toggle(self) -> None:
        if hasattr(self, "btn_confirm"):
            state = "normal" if self.chk_safe.get() else "disabled"
            self.btn_confirm.configure(state=state)

    def _confirm(self) -> None:
        self.destroy()
        if self.on_confirm:
            self.on_confirm(self.targets)

