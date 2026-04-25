import tkinter as tk
from tkinter import font as tkfont
import math
import re

# ── Colour palette ──────────────────────────────────────────────────────────
BG          = "#0d0f1a"
PANEL       = "#151827"
DISPLAY_BG  = "#0a0c16"
ACCENT      = "#7c3aed"        # violet
ACCENT2     = "#06b6d4"        # cyan
BTN_DARK    = "#1e2235"
BTN_MID     = "#252a40"
BTN_OP      = "#2d1f4e"        # operator – violet tint
BTN_EQ      = "#4c1d95"        # equals – deep violet
BTN_FN      = "#0e2a35"        # functions – cyan tint
BTN_CLR     = "#3b0f0f"        # clear – red tint
TEXT_WHITE  = "#f0f4ff"
TEXT_DIM    = "#6b7280"
TEXT_ACCENT = "#a78bfa"
TEXT_CYAN   = "#67e8f9"
TEXT_RED    = "#f87171"

HOVER_LIFT  = 10               # brightness boost on hover

# ── History ─────────────────────────────────────────────────────────────────
history: list[str] = []


# ── Helper – lighten a hex colour ───────────────────────────────────────────
def lighten(hex_color: str, amount: int = HOVER_LIFT) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r, g, b = min(255, r+amount), min(255, g+amount), min(255, b+amount)
    return f"#{r:02x}{g:02x}{b:02x}"


# ── Round rectangle ─────────────────────────────────────────────────────────
def round_rect(canvas, x1, y1, x2, y2, radius=12, **kw):
    points = [
        x1+radius, y1,  x2-radius, y1,
        x2, y1,  x2, y1+radius,
        x2, y2-radius,  x2, y2,
        x2-radius, y2,  x1+radius, y2,
        x1, y2,  x1, y2-radius,
        x1, y1+radius,  x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kw)


# ── Calculator App ───────────────────────────────────────────────────────────
class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Yooooo Babe")
        self.resizable(False, False)
        self.configure(bg=BG)

        # state
        self.expression   = ""
        self.just_computed = False
        self.deg_mode     = tk.BooleanVar(value=True)   # True=DEG, False=RAD
        self.history_open = False

        self._build_ui()
        self._bind_keys()
        self.update_display()

    # ── UI construction ──────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Title bar ───────────────────────────────────────────────────────
        title_bar = tk.Frame(self, bg=BG)
        title_bar.pack(fill="x", padx=18, pady=(14, 0))

        tk.Label(title_bar, text="Yooooo Babe❤️", bg=BG,
                 fg=TEXT_ACCENT,
                 font=("Courier New", 13, "bold")).pack(side="left")

        # DEG / RAD toggle
        self.angle_btn = tk.Button(
            title_bar, textvariable=tk.StringVar(),
            bg=BTN_DARK, fg=TEXT_CYAN, relief="flat",
            font=("Courier New", 9, "bold"), padx=8, pady=2,
            cursor="hand2", bd=0, activebackground=BTN_MID,
            activeforeground=TEXT_CYAN,
            command=self._toggle_angle)
        self.angle_btn.pack(side="right", padx=(4, 0))
        self._refresh_angle_btn()

        # History button
        hist_btn = tk.Button(
            title_bar, text="⏱ HIST",
            bg=BTN_DARK, fg=TEXT_DIM, relief="flat",
            font=("Courier New", 9, "bold"), padx=8, pady=2,
            cursor="hand2", bd=0, activebackground=BTN_MID,
            activeforeground=TEXT_WHITE,
            command=self._toggle_history)
        hist_btn.pack(side="right", padx=(0, 4))

        # ── Display area ─────────────────────────────────────────────────────
        disp_frame = tk.Frame(self, bg=DISPLAY_BG,
                               highlightbackground=ACCENT,
                               highlightthickness=1)
        disp_frame.pack(fill="x", padx=14, pady=10)

        # expression label (small, top-right)
        self.expr_label = tk.Label(
            disp_frame, text="", bg=DISPLAY_BG, fg=TEXT_DIM,
            font=("Courier New", 11), anchor="e", justify="right")
        self.expr_label.pack(fill="x", padx=14, pady=(10, 0))

        # main result label
        self.result_label = tk.Label(
            disp_frame, text="0", bg=DISPLAY_BG, fg=TEXT_WHITE,
            font=("Courier New", 38, "bold"), anchor="e", justify="right")
        self.result_label.pack(fill="x", padx=14, pady=(0, 12))

        # live-preview of expression value
        self.preview_label = tk.Label(
            disp_frame, text="", bg=DISPLAY_BG, fg=TEXT_ACCENT,
            font=("Courier New", 12), anchor="e")
        self.preview_label.pack(fill="x", padx=14, pady=(0, 8))

        # ── Buttons ──────────────────────────────────────────────────────────
        btn_area = tk.Frame(self, bg=BG)
        btn_area.pack(padx=14, pady=(0, 14))

        # row definitions: (label, bg, fg, action)
        rows = [
            # Scientific row 1
            [("sin",  BTN_FN, TEXT_CYAN, "sin("),
             ("cos",  BTN_FN, TEXT_CYAN, "cos("),
             ("tan",  BTN_FN, TEXT_CYAN, "tan("),
             ("log",  BTN_FN, TEXT_CYAN, "log("),
             ("ln",   BTN_FN, TEXT_CYAN, "ln(")],
            # Scientific row 2
            [("√",   BTN_FN, TEXT_CYAN, "sqrt("),
             ("x²",  BTN_FN, TEXT_CYAN, "**2"),
             ("xʸ",  BTN_FN, TEXT_CYAN, "**"),
             ("π",   BTN_FN, TEXT_CYAN, "pi"),
             ("e",   BTN_FN, TEXT_CYAN, "e")],
            # Scientific row 3
            [("1/x", BTN_FN, TEXT_CYAN, "1/"),
             ("(",   BTN_MID, TEXT_WHITE, "("),
             (")",   BTN_MID, TEXT_WHITE, ")"),
             ("%",   BTN_OP,  TEXT_ACCENT, "%"),
             ("AC",  BTN_CLR, TEXT_RED,   "AC")],
            # Numeric rows
            [("7", BTN_DARK, TEXT_WHITE, "7"),
             ("8", BTN_DARK, TEXT_WHITE, "8"),
             ("9", BTN_DARK, TEXT_WHITE, "9"),
             ("⌫", BTN_MID,  TEXT_RED,   "BS"),
             ("÷", BTN_OP,   TEXT_ACCENT, "/")],
            [("4", BTN_DARK, TEXT_WHITE, "4"),
             ("5", BTN_DARK, TEXT_WHITE, "5"),
             ("6", BTN_DARK, TEXT_WHITE, "6"),
             ("+", BTN_OP,   TEXT_ACCENT, "+"),
             ("−", BTN_OP,   TEXT_ACCENT, "-")],
            [("1", BTN_DARK, TEXT_WHITE, "1"),
             ("2", BTN_DARK, TEXT_WHITE, "2"),
             ("3", BTN_DARK, TEXT_WHITE, "3"),
             ("×", BTN_OP,   TEXT_ACCENT, "*"),
             ("±", BTN_MID,  TEXT_WHITE,  "NEG")],
            [("0",   BTN_DARK, TEXT_WHITE, "0"),
             ("00",  BTN_DARK, TEXT_DIM,   "00"),
             (".",   BTN_MID,  TEXT_WHITE,  "."),
             ("ANS", BTN_MID,  TEXT_DIM,    "ANS"),
             ("=",   BTN_EQ,   TEXT_WHITE,  "=")],
        ]

        self._btn_refs = {}
        for r_idx, row in enumerate(rows):
            row_frame = tk.Frame(btn_area, bg=BG)
            row_frame.pack(fill="x", pady=3)
            for c_idx, (label, bg, fg, action) in enumerate(row):
                self._make_button(row_frame, label, bg, fg, action)

        # ── History panel (hidden initially) ─────────────────────────────────
        self.hist_frame = tk.Frame(self, bg=PANEL,
                                    highlightbackground=ACCENT2,
                                    highlightthickness=1)
        # not packed yet

        hist_title = tk.Frame(self.hist_frame, bg=PANEL)
        hist_title.pack(fill="x", padx=8, pady=(8, 0))
        tk.Label(hist_title, text="HISTORY", bg=PANEL, fg=TEXT_CYAN,
                 font=("Courier New", 10, "bold")).pack(side="left")
        tk.Button(hist_title, text="✕ Clear", bg=PANEL, fg=TEXT_DIM,
                  relief="flat", font=("Courier New", 9),
                  cursor="hand2", command=self._clear_history).pack(side="right")

        self.hist_list = tk.Frame(self.hist_frame, bg=PANEL)
        self.hist_list.pack(fill="both", expand=True, padx=8, pady=8)

    # ── Button factory ───────────────────────────────────────────────────────
    def _make_button(self, parent, label, bg, fg, action):
        btn = tk.Button(
            parent, text=label, width=5,
            bg=bg, fg=fg, activebackground=lighten(bg),
            activeforeground=fg,
            font=("Courier New", 13, "bold"),
            relief="flat", bd=0, cursor="hand2",
            pady=10,
            command=lambda a=action: self._handle(a))
        btn.pack(side="left", expand=True, fill="x", padx=3)
        # hover effect
        btn.bind("<Enter>", lambda e, b=btn, c=bg: b.config(bg=lighten(c, 18)))
        btn.bind("<Leave>", lambda e, b=btn, c=bg: b.config(bg=c))
        return btn

    # ── Keyboard bindings ─────────────────────────────────────────────────────
    def _bind_keys(self):
        key_map = {
            "Return": "=", "KP_Enter": "=",
            "BackSpace": "BS", "Delete": "AC",
            "Escape": "AC",
            "percent": "%",
        }
        for char in "0123456789.+-*/()":
            self.bind(char, lambda e, c=char: self._handle(c))
        for key, action in key_map.items():
            self.bind(f"<{key}>", lambda e, a=action: self._handle(a))

    # ── Core logic ────────────────────────────────────────────────────────────
    def _handle(self, action: str):
        expr = self.expression

        if action == "AC":
            self.expression = ""
            self.just_computed = False

        elif action == "BS":
            self.expression = expr[:-1]

        elif action == "=":
            self._evaluate()
            return

        elif action == "NEG":
            # wrap current expression in negation
            if expr:
                self.expression = f"-({expr})"

        elif action == "ANS":
            if history:
                # grab last result (after '=')
                last = history[-1].split("=")[-1].strip()
                if self.just_computed:
                    self.expression = last
                else:
                    self.expression += last

        elif action == "pi":
            self.expression += "π"

        elif action == "e":
            self.expression += "e"

        elif action in ("sin(", "cos(", "tan(", "log(", "ln(", "sqrt("):
            if self.just_computed and expr:
                self.expression = action + expr + ")"
            else:
                self.expression += action

        elif action == "**2":
            self.expression += "²"

        elif action == "**":
            self.expression += "^"

        elif action == "1/":
            if self.just_computed and expr:
                self.expression = f"1/({expr})"
            else:
                self.expression += "1/"

        else:
            if self.just_computed and action not in "+-*/":
                self.expression = action
            else:
                self.expression += action
            self.just_computed = False

        self.update_display()

    def _evaluate(self):
        raw = self.expression
        if not raw:
            return
        try:
            result, formatted = self._compute(raw)
            history.append(f"{raw} = {formatted}")
            self.expression = formatted
            self.just_computed = True
            self.update_display(result_override=formatted)
            self._refresh_history_panel()
        except Exception:
            self.result_label.config(text="Error", fg=TEXT_RED)
            self.expression = ""
            self.just_computed = False

    def _compute(self, raw: str):
        # pre-process display symbols → Python
        expr = raw
        expr = expr.replace("π", str(math.pi))
        expr = expr.replace("e", str(math.e))
        expr = expr.replace("²", "**2")
        expr = expr.replace("^", "**")
        expr = expr.replace("√", "math.sqrt")

        # trig / log: respect degree mode
        if self.deg_mode.get():
            expr = re.sub(r'sin\(', 'math.sin(math.radians(', expr)
            expr = re.sub(r'cos\(', 'math.cos(math.radians(', expr)
            expr = re.sub(r'tan\(', 'math.tan(math.radians(', expr)
            # each trig call now needs an extra closing paren
            # we balance by appending ')' after matching
            expr = self._balance_trig(expr)
        else:
            expr = expr.replace("sin(",  "math.sin(")
            expr = expr.replace("cos(",  "math.cos(")
            expr = expr.replace("tan(",  "math.tan(")

        expr = expr.replace("log(", "math.log10(")
        expr = expr.replace("ln(",  "math.log(")
        expr = expr.replace("sqrt(","math.sqrt(")

        result = eval(expr, {"__builtins__": {}}, {"math": math})

        # format nicely
        if isinstance(result, float):
            if result == int(result) and abs(result) < 1e15:
                formatted = str(int(result))
            else:
                formatted = f"{result:.10g}"
        else:
            formatted = str(result)
        return result, formatted

    def _balance_trig(self, expr: str) -> str:
        """Add extra ')' after each trig radians( ... ) group."""
        # We wrapped sin( → math.sin(math.radians(  so each open needs +1 close
        # Simple approach: count added 'math.radians(' and insert ')' before each
        # top-level closing paren following a radians group.
        # Easier: just let the user always close their brackets and we add the
        # extra ')' at end for each trig function used.
        count = expr.count("math.radians(")
        # We need to insert a ')' to close radians( for each occurrence.
        # Strategy: replace 'math.radians(' back to a sentinel, then handle.
        # Simplest correct approach for typical expressions:
        # append count extra ')' at the very end.
        expr += ")" * count
        return expr

    def update_display(self, result_override=None):
        display = self.expression or "0"
        # live preview
        preview = ""
        if self.expression and not self.just_computed:
            try:
                _, val = self._compute(self.expression)
                preview = f"= {val}"
            except Exception:
                preview = ""

        self.expr_label.config(text=self.expression if self.just_computed else "")
        self.result_label.config(
            text=result_override if result_override else display,
            fg=TEXT_WHITE)
        self.preview_label.config(text=preview)

        # auto-shrink font for long numbers
        length = len(result_override or display)
        size = 38 if length < 10 else 28 if length < 16 else 20
        self.result_label.config(font=("Courier New", size, "bold"))

    # ── Angle mode toggle ─────────────────────────────────────────────────────
    def _toggle_angle(self):
        self.deg_mode.set(not self.deg_mode.get())
        self._refresh_angle_btn()

    def _refresh_angle_btn(self):
        label = "DEG" if self.deg_mode.get() else "RAD"
        self.angle_btn.config(text=label)

    # ── History panel ─────────────────────────────────────────────────────────
    def _toggle_history(self):
        if self.history_open:
            self.hist_frame.pack_forget()
            self.history_open = False
        else:
            self._refresh_history_panel()
            self.hist_frame.pack(fill="x", padx=14, pady=(0, 14))
            self.history_open = True

    def _refresh_history_panel(self):
        for w in self.hist_list.winfo_children():
            w.destroy()
        if not history:
            tk.Label(self.hist_list, text="No history yet.", bg=PANEL,
                     fg=TEXT_DIM, font=("Courier New", 10)).pack(anchor="w")
            return
        for entry in reversed(history[-12:]):
            row = tk.Frame(self.hist_list, bg=PANEL)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=entry, bg=PANEL, fg=TEXT_DIM,
                     font=("Courier New", 10), anchor="w",
                     cursor="hand2").pack(side="left", fill="x", expand=True)
            # click to restore
            lbl = row.winfo_children()[0]
            val = entry.split("=")[-1].strip()
            lbl.bind("<Button-1>", lambda e, v=val: self._restore(v))

    def _restore(self, val: str):
        self.expression = val
        self.just_computed = False
        self.update_display()

    def _clear_history(self):
        history.clear()
        self._refresh_history_panel()


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = Calculator()
    app.mainloop()