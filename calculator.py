"""
╔══════════════════════════════════════════════════════╗
║   ANIMATED CALCULATOR MOBILE APP — Python + Kivy     ║
║   Features: Particle FX · Glow Buttons · Ripples     ║
║   Trig · History · DEG/RAD · Animated Background     ║
╚══════════════════════════════════════════════════════╝

Requirements:
    pip install kivy

Run:
    python calculator_app.py
"""

import math
import re
import random
import os

os.environ.setdefault("KIVY_NO_ENV_CONFIG", "1")
os.environ.setdefault("DISPLAY", ":0")

from kivy.config import Config
Config.set("graphics", "width",  "400")
Config.set("graphics", "height", "800")
Config.set("graphics", "resizable", "0")
Config.set("input", "mouse", "mouse,multitouch_on_demand")

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import (
    Color, Rectangle, RoundedRectangle, Ellipse,
    Line, Canvas, PushMatrix, PopMatrix, Scale, Translate,
)
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import (
    StringProperty, ListProperty, BooleanProperty, NumericProperty,
)
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout

# ── PALETTE ──────────────────────────────────────────────────────────────────
BG          = (0.04, 0.05, 0.09, 1)
DISP_BG     = (0.03, 0.04, 0.08, 1)
ACCENT      = (0.49, 0.23, 0.93, 1)
ACCENT2     = (0.02, 0.71, 0.83, 1)
BTN_DARK    = (0.10, 0.12, 0.19, 1)
BTN_MID     = (0.12, 0.14, 0.22, 1)
BTN_OP      = (0.12, 0.09, 0.25, 1)
BTN_EQ_A    = (0.30, 0.11, 0.58, 1)
BTN_EQ_B    = (0.49, 0.23, 0.93, 1)
BTN_FN      = (0.03, 0.09, 0.13, 1)
BTN_CLR     = (0.10, 0.03, 0.03, 1)
WHITE       = (0.94, 0.96, 1.00, 1)
DIM         = (0.42, 0.44, 0.50, 1)
CYAN        = (0.40, 0.91, 0.97, 1)
PURPLE_LT   = (0.65, 0.55, 0.98, 1)
RED         = (0.97, 0.44, 0.44, 1)
GREEN       = (0.29, 0.86, 0.50, 1)

GLOW_CYCLE  = [ACCENT, (0.58,0.20,0.92,1), ACCENT2, (0.53,0.33,0.98,1)]

history_log = []

# ── HELPERS ───────────────────────────────────────────────────────────────────

def lerp_color(c1, c2, t):
    return tuple(c1[i] + (c2[i] - c1[i]) * t for i in range(4))

def lighten(c, amt=0.15):
    return tuple(min(1.0, c[i] + amt) if i < 3 else c[3] for i in range(4))


# ── ANIMATED BACKGROUND ───────────────────────────────────────────────────────

class AnimatedBG(Widget):
    """Draws drifting plasma orbs + floating particles on a dark canvas."""

    def __init__(self, **kw):
        super().__init__(**kw)
        self._orbs = [self._new_orb() for _ in range(6)]
        self._dots = []
        self._frame = 0
        Clock.schedule_interval(self._tick, 1 / 30)

    def _new_orb(self):
        return {
            "x": random.uniform(0, 400),
            "y": random.uniform(0, 800),
            "r": random.uniform(80, 160),
            "vx": random.uniform(-0.6, 0.6),
            "vy": random.uniform(-0.6, 0.6),
            "hue": random.choice(["purple", "cyan"]),
            "phase": random.uniform(0, math.pi * 2),
        }

    def _tick(self, dt):
        self._frame += 1
        for o in self._orbs:
            o["x"] += o["vx"]
            o["y"] += o["vy"]
            if o["x"] < -o["r"] or o["x"] > self.width + o["r"]:
                o["vx"] *= -1
            if o["y"] < -o["r"] or o["y"] > self.height + o["r"]:
                o["vy"] *= -1

        if self._frame % 5 == 0 and len(self._dots) < 60:
            self._dots.append({
                "x": random.uniform(0, self.width),
                "y": -5,
                "vx": random.uniform(-0.3, 0.3),
                "vy": random.uniform(0.4, 1.2),
                "life": 1.0,
                "size": random.uniform(1.5, 3.5),
                "col": random.choice([ACCENT, PURPLE_LT, CYAN]),
            })

        alive = []
        for d in self._dots:
            d["x"] += d["vx"]
            d["y"] += d["vy"]
            d["life"] -= 0.008
            if d["life"] > 0 and d["y"] < self.height + 10:
                alive.append(d)
        self._dots = alive

        self._redraw()

    def _redraw(self):
        self.canvas.clear()
        with self.canvas:
            # Background
            Color(*BG)
            Rectangle(pos=self.pos, size=self.size)

            # Grid lines
            Color(0.49, 0.23, 0.93, 0.04)
            step = dp(55)
            x = 0
            while x < self.width:
                Line(points=[x, 0, x, self.height], width=0.5)
                x += step
            y = 0
            while y < self.height:
                Line(points=[0, y, self.width, y], width=0.5)
                y += step

            # Orbs
            for o in self._orbs:
                pulse = 0.04 + 0.02 * math.sin(self._frame * 0.04 + o["phase"])
                if o["hue"] == "purple":
                    Color(0.49, 0.23, 0.93, pulse)
                else:
                    Color(0.02, 0.71, 0.83, pulse)
                r = o["r"]
                Ellipse(pos=(o["x"] - r, o["y"] - r), size=(r * 2, r * 2))

            # Floating dots
            for d in self._dots:
                c = d["col"]
                Color(c[0], c[1], c[2], d["life"] * 0.7)
                s = d["size"]
                Ellipse(pos=(d["x"] - s / 2, d["y"] - s / 2), size=(s, s))

class GlowButton(Button):
    """Rounded button with press animation, ripple flash, and optional glow."""

    btn_color   = ListProperty([0.10, 0.12, 0.19, 1])
    glow_color  = ListProperty([0.49, 0.23, 0.93, 0])
    text_color  = ListProperty([0.94, 0.96, 1.00, 1])

    def __init__(self, btn_bg, txt_col, glow, **kw):
        super().__init__(**kw)
        self.btn_color  = list(btn_bg)
        self.text_color = list(txt_col)
        self.glow_color = list(glow[:3]) + [0.0]
        self._base_col  = list(btn_bg)
        self._glow_col  = list(glow)
        self.background_normal   = ""
        self.background_down     = ""
        self.background_color    = (0, 0, 0, 0)
        self.font_name = "Roboto"
        self.font_size  = dp(13)
        self.bold       = True
        self.color      = self.text_color
        self.bind(pos=self._redraw, size=self._redraw,
                  btn_color=self._redraw, glow_color=self._redraw)
        self._redraw()

    def _redraw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            # Glow halo
            ga = self.glow_color[3] if len(self.glow_color) > 3 else 0
            if ga > 0.01:
                gc = self._glow_col
                Color(gc[0], gc[1], gc[2], ga * 0.35)
                rg = dp(8)
                RoundedRectangle(
                    pos=(self.x - rg, self.y - rg),
                    size=(self.width + rg * 2, self.height + rg * 2),
                    radius=[dp(14)],
                )
            # Button face
            Color(*self.btn_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
            # Top highlight streak
            Color(1, 1, 1, 0.04)
            RoundedRectangle(
                pos=(self.x + dp(4), self.y + self.height * 0.55),
                size=(self.width - dp(8), self.height * 0.38),
                radius=[dp(8)],
            )

    def on_press(self):
        light = lighten(self._base_col, 0.20)
        anim = Animation(btn_color=light, duration=0.07)
        anim.start(self)
        # glow surge
        anim2 = Animation(glow_color=list(self._glow_col[:3]) + [1.0], duration=0.07)
        anim2.start(self)

    def on_release(self):
        anim = Animation(btn_color=self._base_col, duration=0.18)
        anim.start(self)
        anim2 = Animation(glow_color=list(self._glow_col[:3]) + [0.0], duration=0.3)
        anim2.start(self)
        # scale pop
        anim3 = (
            Animation(size_hint_y=0.88, duration=0.06) +
            Animation(size_hint_y=1.0,  duration=0.10)
        )
        anim3.start(self)


class DisplayPanel(RelativeLayout):

    expr_text    = StringProperty("")
    result_text  = StringProperty("0")
    preview_text = StringProperty("")

    def __init__(self, **kw):
        super().__init__(**kw)
        self._glow_idx   = 0
        self._border_col = list(ACCENT)

        self._bg_rect  = None
        self._border   = None

        with self.canvas.before:
            self._border_color_inst = Color(*ACCENT)
            self._border_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(12)]
            )
            Color(*DISP_BG)
            self._inner_rect = RoundedRectangle(
                pos=(self.x + dp(2), self.y + dp(2)),
                size=(self.width - dp(4), self.height - dp(4)),
                radius=[dp(10)],
            )

        self.bind(pos=self._redraw, size=self._redraw)

        # Labels
        self._expr = Label(
            text="", font_name="Roboto", font_size=dp(10),
            color=DIM, halign="right", valign="middle", size_hint=(1, None),
            height=dp(18), pos_hint={"x": 0, "top": 1},
            padding=(dp(14), 0),
        )
        self._expr.bind(size=self._expr.setter("text_size"))
        self.add_widget(self._expr)

        self._result = Label(
            text="0", font_name="Roboto", font_size=dp(36),
            color=WHITE, halign="right", valign="middle",
            size_hint=(1, None), height=dp(56),
            pos_hint={"x": 0, "top": 0.72},
            padding=(dp(14), 0),
        )
        self._result.bind(size=self._result.setter("text_size"))
        self.add_widget(self._result)

        self._preview = Label(
            text="", font_name="Roboto", font_size=dp(11),
            color=PURPLE_LT, halign="right", valign="middle",
            size_hint=(1, None), height=dp(18),
            pos_hint={"x": 0, "top": 0.34},
            padding=(dp(14), 0),
        )
        self._preview.bind(size=self._preview.setter("text_size"))
        self.add_widget(self._preview)

        Clock.schedule_interval(self._pulse_border, 0.18)

    def _redraw(self, *_):
        self._border_rect.pos  = self.pos
        self._border_rect.size = self.size
        self._inner_rect.pos   = (self.x + dp(2), self.y + dp(2))
        self._inner_rect.size  = (self.width - dp(4), self.height - dp(4))

    def _pulse_border(self, dt):
        col = GLOW_CYCLE[self._glow_idx % len(GLOW_CYCLE)]
        self._border_color_inst.rgba = col
        self._glow_idx += 1

    def set_texts(self, expr="", result="0", preview=""):
        self._expr.text    = expr
        self._result.text  = result
        self._preview.text = preview
        n = len(result)
        self._result.font_size = dp(36) if n < 10 else dp(26) if n < 16 else dp(16)

    def flash(self, color=GREEN):
        def do(dt):
            self._result.color = color
            Clock.schedule_once(lambda _: setattr(self._result, "color", WHITE), 0.35)
        Clock.schedule_once(do, 0)

    def roll_in(self, final_text, color=WHITE):
        self._result.color   = CYAN
        self._result.opacity = 0
        anim = Animation(opacity=1, duration=0.2)
        anim.start(self._result)
        Clock.schedule_once(lambda _: setattr(self._result, "color", color), 0.2)

class HistoryPanel(ScrollView):
    def __init__(self, on_restore, on_clear, **kw):
        super().__init__(**kw)
        self.do_scroll_x = False
        self._on_restore = on_restore
        self._on_clear   = on_clear
        self._container  = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=dp(2),
            padding=[dp(10), dp(6)],
        )
        self._container.bind(minimum_height=self._container.setter("height"))
        self.add_widget(self._container)

    def refresh(self):
        self._container.clear_widgets()
        hdr = BoxLayout(size_hint_y=None, height=dp(24))
        lbl = Label(text="HISTORY",font_name="Roboto",
                    font_size=dp(9), color=CYAN, halign="left",
                    size_hint_x=0.7)
        lbl.bind(size=lbl.setter("text_size"))
        clr = Button(text="CLEAR", font_name="Roboto",
                     font_size=dp(9), color=DIM,
                     background_normal="", background_color=(0, 0, 0, 0),
                     size_hint_x=0.3)
        clr.bind(on_release=lambda _: self._on_clear())
        hdr.add_widget(lbl)
        hdr.add_widget(clr)
        self._container.add_widget(hdr)

        if not history_log:
            self._container.add_widget(
                Label(text="No history yet.", font_name="Roboto",
                      font_size=dp(9), color=DIM, size_hint_y=None, height=dp(22))
            )
            return
        for entry in history_log[:12]:
            val = entry.split("=")[-1].strip()
            row = Button(
                text=entry, font_name="Roboto", font_size=dp(9),
                color=DIM, halign="right",
                background_normal="", background_color=(0, 0, 0, 0),
                size_hint_y=None, height=dp(20),
            )
            row.bind(size=row.setter("text_size"))
            row.bind(on_release=lambda _, v=val: self._on_restore(v))
            self._container.add_widget(row)
class CalculatorWidget(FloatLayout):

    BUTTONS = [
        [("sin", BTN_FN, CYAN,     ACCENT2),  ("cos", BTN_FN, CYAN,   ACCENT2),
         ("tan", BTN_FN, CYAN,     ACCENT2),  ("log", BTN_FN, CYAN,   ACCENT2),
         ("ln",  BTN_FN, CYAN,     ACCENT2)],
        [("√",   BTN_FN, CYAN,     ACCENT2),  ("x²",  BTN_FN, CYAN,   ACCENT2),
         ("xʸ",  BTN_FN, CYAN,     ACCENT2),  ("π",   BTN_FN, CYAN,   ACCENT2),
         ("e",   BTN_FN, CYAN,     ACCENT2)],
        [("1/x", BTN_FN, CYAN,     ACCENT2),  ("(",   BTN_MID, WHITE, ACCENT),
         (")",   BTN_MID, WHITE,   ACCENT),   ("%",   BTN_OP,  PURPLE_LT, ACCENT),
         ("AC",  BTN_CLR, RED,     RED)],
        [("7",   BTN_DARK, WHITE,  ACCENT),   ("8",   BTN_DARK, WHITE, ACCENT),
         ("9",   BTN_DARK, WHITE,  ACCENT),   ("⌫",   BTN_MID,  RED,  RED),
         ("÷",   BTN_OP,   PURPLE_LT, ACCENT)],
        [("4",   BTN_DARK, WHITE,  ACCENT),   ("5",   BTN_DARK, WHITE, ACCENT),
         ("6",   BTN_DARK, WHITE,  ACCENT),   ("+",   BTN_OP,   PURPLE_LT, ACCENT),
         ("−",   BTN_OP,   PURPLE_LT, ACCENT)],
        [("1",   BTN_DARK, WHITE,  ACCENT),   ("2",   BTN_DARK, WHITE, ACCENT),
         ("3",   BTN_DARK, WHITE,  ACCENT),   ("×",   BTN_OP,   PURPLE_LT, ACCENT),
         ("±",   BTN_MID,  WHITE, ACCENT)],
        [("0",   BTN_DARK, WHITE,  ACCENT),   ("00",  BTN_DARK, DIM,   ACCENT),
         (".",   BTN_MID,  WHITE,  ACCENT),   ("ANS", BTN_MID,  DIM,   ACCENT),
         ("=",   BTN_EQ_A, WHITE,  ACCENT)],
    ]

    def __init__(self, **kw):
        super().__init__(**kw)
        self.expression    = ""
        self.just_computed = False
        self.deg_mode      = True
        self._hist_open    = False

        self._build()
        Window.bind(on_key_down=self._key_down)


    def _build(self):
        self._bg = AnimatedBG(size_hint=(1, 1))
        self.add_widget(self._bg)

        main = BoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
            padding=[dp(10), dp(8)],
            spacing=dp(4),
        )
        self.add_widget(main)
        tbar = BoxLayout(size_hint_y=None, height=dp(32), spacing=dp(6))
        title_lbl = Label(
            text="Yoooo Babe",font_name="Roboto", font_size=dp(15),
            bold=True, color=PURPLE_LT, halign="left", size_hint_x=0.4,
        )
        title_lbl.bind(size=title_lbl.setter("text_size"))
        tbar.add_widget(title_lbl)

        self._deg_btn = self._small_btn("DEG", CYAN, self._toggle_deg)
        self._hist_btn = self._small_btn("HIST", DIM, self._toggle_hist)
        spacer = Widget()
        tbar.add_widget(spacer)
        tbar.add_widget(self._deg_btn)
        tbar.add_widget(self._hist_btn)
        main.add_widget(tbar)

        self._disp = DisplayPanel(size_hint=(1, None), height=dp(100))
        main.add_widget(self._disp)

        self._hist = HistoryPanel(
            on_restore=self._restore_hist,
            on_clear=self._clear_hist,
            size_hint=(1, None), height=dp(110),
            do_scroll_x=False,
        )
        with self._hist.canvas.before:
            Color(0.05, 0.06, 0.12, 0.95)
            self._hist_bg = RoundedRectangle(
                pos=self._hist.pos, size=self._hist.size, radius=[dp(8)]
            )
        self._hist.bind(pos=self._upd_hist_bg, size=self._upd_hist_bg)
        self._hist.opacity = 0
        self._hist.disabled = True
        main.add_widget(self._hist)

        # Button grid
        grid = GridLayout(
            cols=5, rows=7,
            spacing=dp(5),
            size_hint=(1, 1),
        )
        for row in self.BUTTONS:
            for (label, bg, fg, glow) in row:
                b = GlowButton(
                    btn_bg=bg, txt_col=fg, glow=glow,
                    text=label,
                )
                b.bind(on_release=lambda inst, l=label: self._handle(l))
                grid.add_widget(b)
        main.add_widget(grid)

    def _small_btn(self, text, col, cb):
        btn = Button(
            text=text,font_name="Roboto", font_size=dp(9),
            color=col, size_hint=(None, 1), width=dp(46),
            background_normal="", background_down="",
            background_color=(0, 0, 0, 0),
        )
        with btn.canvas.before:
            Color(0.12, 0.14, 0.22, 1)
            self._sb_rect = RoundedRectangle(
                pos=btn.pos, size=btn.size, radius=[dp(4)]
            )

        def _upd(*_):
            self._sb_rect.pos  = btn.pos
            self._sb_rect.size = btn.size

        btn.bind(pos=_upd, size=_upd, on_release=lambda _: cb())
        return btn

    def _upd_hist_bg(self, *_):
        self._hist_bg.pos  = self._hist.pos
        self._hist_bg.size = self._hist.size

    def _handle(self, action):
        expr = self.expression
        if action == "AC":
            self.expression = ""; self.just_computed = False
            self._disp.flash(RED)
        elif action == "⌫":
            self.expression = expr[:-1]
        elif action == "=":
            self._evaluate(); return
        elif action == "NEG" or action == "±":
            self.expression = f"-({expr})" if expr else "-"
        elif action == "ANS":
            if history_log:
                last = history_log[0].split("=")[-1].strip()
                self.expression = last if self.just_computed else expr + last
        elif action == "π":
            self.expression = "π" if self.just_computed else expr + "π"
            self.just_computed = False
        elif action == "e":
            self.expression = "e" if self.just_computed else expr + "e"
            self.just_computed = False
        elif action == "x²":
            self.expression += "²"; self.just_computed = False
        elif action == "xʸ":
            self.expression += "^"; self.just_computed = False
        elif action == "1/x":
            self.expression = f"1/({expr})" if (self.just_computed and expr) else expr + "1/"
            self.just_computed = False
        elif action in ("sin", "cos", "tan", "log", "ln", "√"):
            if self.just_computed and expr:
                self.expression = f"{action}({expr})"
            else:
                self.expression = expr + f"{action}("
            self.just_computed = False
        else:
            if self.just_computed and action not in "+-×−÷/":
                self.expression = action
            else:
                self.expression += action
            self.just_computed = False
        self._update_display()

    def _evaluate(self):
        if not self.expression:
            return
        try:
            result, formatted = self._compute(self.expression)
            history_log.insert(0, f"{self.expression} = {formatted}")
            if len(history_log) > 20:
                history_log.pop()
            self._disp.set_texts(expr=self.expression, result=formatted, preview="")
            self._disp.roll_in(formatted)
            self._disp.flash(GREEN)
            self.expression    = formatted
            self.just_computed = True
            if self._hist_open:
                self._hist.refresh()
        except Exception:
            self._shake()
            self._disp.flash(RED)
            self._disp.set_texts(expr="", result="Error", preview="")
            self._disp._result.color = RED
            self.expression = ""; self.just_computed = False
            Clock.schedule_once(
                lambda _: self._disp.set_texts(result="0") or
                          setattr(self._disp._result, "color", WHITE), 0.8
            )

    def _compute(self, raw):
        expr = raw
        expr = expr.replace("π", str(math.pi)).replace("e", str(math.e))
        expr = expr.replace("²", "**2").replace("^", "**")
        if self.deg_mode:
            for fn in ("sin", "cos", "tan"):
                expr = expr.replace(f"{fn}(", f"math.{fn}(math.radians(")
            # close extra parens
            expr += ")" * expr.count("math.radians(")
        else:
            for fn in ("sin", "cos", "tan"):
                expr = expr.replace(f"{fn}(", f"math.{fn}(")
        expr = expr.replace("log(", "math.log10(").replace("ln(", "math.log(")
        expr = expr.replace("√(", "math.sqrt(")
        expr = expr.replace("÷", "/").replace("×", "*").replace("−", "-")
        result = eval(expr, {"__builtins__": {}}, {"math": math})  # noqa: S307
        if isinstance(result, float):
            if result == int(result) and abs(result) < 1e15:
                formatted = str(int(result))
            else:
                formatted = f"{result:.10g}"
        else:
            formatted = str(result)
        return result, formatted

    def _update_display(self):
        text = self.expression or "0"
        preview = ""
        if self.expression and not self.just_computed:
            try:
                _, v = self._compute(self.expression)
                preview = f"= {v}"
            except Exception:
                pass
        expr_txt = self.expression if self.just_computed else ""
        self._disp.set_texts(expr=expr_txt, result=text, preview=preview)

    def _shake(self):
        orig_x = self.x
        seq = Animation(x=orig_x + dp(10), duration=0.04) + \
              Animation(x=orig_x - dp(10), duration=0.04) + \
              Animation(x=orig_x + dp(7),  duration=0.04) + \
              Animation(x=orig_x - dp(7),  duration=0.04) + \
              Animation(x=orig_x,          duration=0.04)
        seq.start(self)
    def _toggle_deg(self):
        self.deg_mode = not self.deg_mode
        self._deg_btn.text = "DEG" if self.deg_mode else "RAD"
        self._deg_btn.color = CYAN if self.deg_mode else DIM

    def _toggle_hist(self):
        self._hist_open = not self._hist_open
        if self._hist_open:
            self._hist.refresh()
            self._hist.opacity  = 1
            self._hist.disabled = False
            self._hist_btn.color = CYAN
        else:
            self._hist.opacity  = 0
            self._hist.disabled = True
            self._hist_btn.color = DIM

    def _restore_hist(self, val):
        self.expression = val; self.just_computed = False
        self._update_display()

    def _clear_hist(self):
        history_log.clear()
        self._hist.refresh()

    def _key_down(self, window, key, scancode, codepoint, modifiers):
        if codepoint in "0123456789.+-*/()%":
            self._handle(codepoint)
        elif key == 13:   # Enter
            self._handle("=")
        elif key == 8:    # Backspace
            self._handle("⌫")
        elif key == 27:   # Escape
            self._handle("AC")


class CalcApp(App):
    title = "Tera Paisa Khatam"

    def build(self):
        Window.clearcolor = BG
        return CalculatorWidget()


if __name__ == "__main__":
    CalcApp().run()