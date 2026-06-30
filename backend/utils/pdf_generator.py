"""
PDF report generator - redesigned with visual score bars,
color-coded sections, cover page hero block, and clean typography.
Uses fpdf2 >= 2.7.9
"""
from __future__ import annotations
from datetime import datetime
import math
from fpdf import FPDF
from fpdf.enums import XPos, YPos


# ── Colour palette ─────────────────────────────────────────────────────────────
C = {
    "bg":         (9,   9,  11),   # not used in PDF (white bg)
    "navy":       (15,  30,  80),
    "blue":       (37,  99, 235),
    "blue_light": (59, 130, 246),
    "indigo":     (67,  56, 202),
    "purple":     (109,  40, 217),
    "green":      (5,  150,  105),
    "green_lt":   (16, 185, 129),
    "amber":      (217, 119,   6),
    "amber_lt":   (245, 158,  11),
    "red":        (185,  28,  28),
    "red_lt":     (239,  68,  68),
    "orange":     (194,  65,  12),
    "slate_900":  (15,  23,  42),
    "slate_800":  (30,  41,  59),
    "slate_700":  (51,  65,  85),
    "slate_500":  (100, 116, 139),
    "slate_300":  (203, 213, 225),
    "slate_100":  (241, 245, 249),
    "white":      (255, 255, 255),
    # tinted fill backgrounds
    "fill_blue":  (239, 246, 255),
    "fill_green": (240, 253, 244),
    "fill_amber": (255, 251, 235),
    "fill_red":   (254, 242, 242),
    "fill_purple":(245, 243, 255),
    "fill_navy":  (224, 231, 255),
}


def _rgb(name): return C[name]


def _s(text, maxlen: int = 0) -> str:
    """Sanitise text for Latin-1 PDF encoding."""
    if not text: return ""
    text = str(text)
    replacements = {
        "\u2018": "'",  "\u2019": "'",  "\u201c": '"',  "\u201d": '"',
        "\u2013": "-",  "\u2014": "-",  "\u2022": "-",  "\u2026": "...",
        "\u20b9": "Rs.","\u20ac": "EUR","\u00a3": "GBP","\u2192": "->",
        "\u2190": "<-", "\u2713": "+",  "\u2714": "+",  "\u2715": "x",
        "\u2716": "x",  "\u00b0": " deg","\u00ae": "(R)","\u2122": "(TM)",
        "\u00a9": "(C)","\u00bd": "1/2","\u00bc": "1/4","\u00be": "3/4",
        "\u00d7": "x",  "\u00f7": "/",  "\u221e": "inf","\u2248": "~",
        "\u2260": "!=", "\u2264": "<=", "\u2265": ">=", "\t": "  ",
        "\u25cf": "-",  "\u25cb": "-",  "\u2b24": "-",  "\u2023": "-",
        "\u25aa": "-",  "\u25ba": ">",
    }
    for ch, rep in replacements.items():
        text = text.replace(ch, rep)
    text = text.encode("latin-1", errors="ignore").decode("latin-1")
    if maxlen and len(text) > maxlen:
        text = text[:maxlen] + "..."
    return text.strip()


def _score_color(score, out_of=100):
    pct = score / out_of
    if pct >= 0.65: return C["green_lt"]
    if pct >= 0.40: return C["amber_lt"]
    return C["red_lt"]


def _verdict_colors(verdict):
    return {
        "Proceed": (C["green"],     C["fill_green"], C["green_lt"]),
        "Pivot":   (C["amber"],     C["fill_amber"], C["amber_lt"]),
        "Abandon": (C["red"],       C["fill_red"],   C["red_lt"]),
    }.get(verdict, (C["indigo"], C["fill_navy"], C["blue_light"]))


# ══════════════════════════════════════════════════════════════════════════════
class _PDF(FPDF):

    def __init__(self, idea: str, score: int, verdict: str):
        super().__init__()
        self.idea    = _s(idea, 100)
        self.score   = score
        self.verdict = verdict
        self.set_auto_page_break(auto=True, margin=22)
        self.set_margins(18, 18, 18)

    # ── Header / Footer ───────────────────────────────────────────────────────
    def header(self):
        if self.page_no() == 1:
            return  # cover page has its own header
        # thin top bar
        self.set_fill_color(*C["navy"])
        self.rect(0, 0, 210, 10, "F")
        self.set_font("Helvetica", "B", 7)
        self.set_text_color(*C["slate_300"])
        self.set_y(2)
        self.cell(0, 6, "STARTUP SIMULATOR  |  CONFIDENTIAL ANALYSIS REPORT", align="C")
        self.set_y(12)
        self.set_text_color(*C["slate_900"])

    def footer(self):
        self.set_y(-14)
        self.set_draw_color(*C["slate_300"])
        self.set_line_width(0.3)
        self.line(18, self.get_y(), 192, self.get_y())
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*C["slate_500"])
        self.cell(0, 8,
            f"Page {self.page_no()}  |  {self.idea[:50]}  |  Generated {datetime.now().strftime('%d %b %Y')}",
            align="C")

    # ── Layout primitives ─────────────────────────────────────────────────────
    def gap(self, h=4):
        self.ln(h)

    def hline(self, color="slate_300", width=0.3):
        self.set_draw_color(*C[color])
        self.set_line_width(width)
        self.line(18, self.get_y(), 192, self.get_y())
        self.ln(4)

    def section_header(self, number: str, title: str):
        """Full-width coloured section banner."""
        self.gap(4)
        # left accent bar
        self.set_fill_color(*C["navy"])
        self.rect(18, self.get_y(), 4, 10, "F")
        # number chip
        self.set_fill_color(*C["blue"])
        self.rect(24, self.get_y(), 14, 10, "F")
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*C["white"])
        self.set_xy(24, self.get_y() + 1)
        self.cell(14, 8, number, align="C")
        # title
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*C["navy"])
        self.set_xy(41, self.get_y())
        self.cell(0, 10, _s(title))
        self.ln(14)
        self.set_text_color(*C["slate_900"])

    def subsection(self, title: str, color="blue"):
        self.gap(3)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*C[color])
        self.cell(0, 5, _s(title).upper(),
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*C[color])
        self.set_line_width(0.5)
        self.line(18, self.get_y(), 80, self.get_y())
        self.ln(4)
        self.set_text_color(*C["slate_900"])

    def body_text(self, text: str, color="slate_900"):
        self.set_font("Helvetica", size=10)
        self.set_text_color(*C[color])
        self.multi_cell(0, 5.5, _s(text),
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.gap(3)

    def kv_block(self, label: str, value: str,
                 fill_color="fill_blue", label_color="blue",
                 border_color="blue_light"):
        """Coloured card: label + body."""
        if not value: return
        self.gap(2)
        y0 = self.get_y()
        # measure text height
        lines = self.get_string_width(_s(value)) / 174
        est_h = max(18, int(lines) * 6 + 20)
        self.set_fill_color(*C[fill_color])
        self.set_draw_color(*C[border_color])
        self.set_line_width(0.4)
        # left accent
        self.set_fill_color(*C[border_color])
        self.rect(18, y0, 3, est_h, "F")
        self.set_fill_color(*C[fill_color])
        self.rect(21, y0, 171, est_h, "F")
        self.set_xy(25, y0 + 3)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*C[label_color])
        self.cell(0, 5, _s(label).upper(),
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_x(25)
        self.set_font("Helvetica", size=10)
        self.set_text_color(*C["slate_900"])
        self.multi_cell(166, 5.5, _s(value),
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.gap(4)

    def bullet_list(self, label: str, items: list,
                    dot_color="blue", fill_color="fill_blue",
                    border_color="blue_light"):
        if not items: return
        self.gap(2)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*C[dot_color])
        self.cell(0, 5, _s(label).upper(),
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.gap(1)
        for item in items[:8]:
            txt = _s(str(item), 280)
            if not txt: continue
            y0 = self.get_y()
            # dot
            self.set_fill_color(*C[dot_color])
            self.ellipse(19, y0 + 3.5, 2, 2, "F")
            self.set_x(24)
            self.set_font("Helvetica", size=10)
            self.set_text_color(*C["slate_900"])
            self.multi_cell(168, 5.5, txt,
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_draw_color(*C["slate_300"])
            self.set_line_width(0.2)
            self.line(24, self.get_y(), 192, self.get_y())
            self.gap(1)
        self.gap(3)

    # ── Visual elements ───────────────────────────────────────────────────────
    def score_bar(self, label: str, value: int, out_of: int = 20, width: int = 160):
        """Horizontal bar with label, filled bar, value."""
        pct   = min(value / out_of, 1.0)
        color = _score_color(value, out_of)
        y     = self.get_y()
        # label
        self.set_font("Helvetica", size=9)
        self.set_text_color(*C["slate_700"])
        self.set_xy(18, y)
        self.cell(52, 6, _s(label))
        # bg bar
        self.set_fill_color(*C["slate_100"])
        self.rect(72, y + 1.5, width, 4, "F")
        # filled bar
        self.set_fill_color(*color)
        if pct > 0:
            self.rect(72, y + 1.5, width * pct, 4, "F")
        # value
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*color)
        self.set_xy(72 + width + 3, y)
        self.cell(0, 6, f"{value}/{out_of}")
        self.ln(8)

    def big_score_hero(self, score: int, verdict: str, one_liner: str):
        """Large score display box for cover page."""
        dark, light, accent = _verdict_colors(verdict)
        y0 = self.get_y()
        h  = 48
        # background
        self.set_fill_color(*light)
        self.rect(18, y0, 174, h, "F")
        # left stripe
        self.set_fill_color(*dark)
        self.rect(18, y0, 6, h, "F")
        # score number
        self.set_font("Helvetica", "B", 52)
        self.set_text_color(*dark)
        self.set_xy(30, y0 + 4)
        self.cell(42, 20, str(score))
        # /100
        self.set_font("Helvetica", size=12)
        self.set_text_color(*C["slate_500"])
        self.set_xy(74, y0 + 12)
        self.cell(0, 8, "/ 100  VIABILITY SCORE")
        # verdict badge
        self.set_fill_color(*dark)
        self.rect(74, y0 + 24, 36, 10, "F")
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*C["white"])
        self.set_xy(74, y0 + 25)
        self.cell(36, 8, verdict.upper(), align="C")
        # one-liner
        if one_liner:
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(*C["slate_700"])
            self.set_xy(116, y0 + 24)
            self.multi_cell(70, 5, f'"{_s(one_liner, 120)}"')
        self.set_y(y0 + h + 8)

    def mini_score_box(self, score: int, verdict: str):
        """Compact score for conclusion page."""
        dark, light, accent = _verdict_colors(verdict)
        y0 = self.get_y()
        self.set_fill_color(*light)
        self.rect(18, y0, 174, 20, "F")
        self.set_fill_color(*dark)
        self.rect(18, y0, 4, 20, "F")
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(*dark)
        self.set_xy(26, y0 + 2)
        self.cell(30, 16, str(score))
        self.set_font("Helvetica", size=10)
        self.set_text_color(*C["slate_500"])
        self.set_xy(58, y0 + 4)
        self.cell(0, 6, "/ 100")
        self.set_xy(58, y0 + 11)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*dark)
        self.cell(0, 6, f"Verdict: {verdict}")
        self.ln(26)

    def investor_gauge(self, inv_score: int):
        """Circular-ish gauge drawn with arcs via rect segments."""
        cx, cy, r = 105, self.get_y() + 22, 18
        total_segs = 20
        filled     = round(inv_score / 10 * total_segs)
        color      = _score_color(inv_score, 10)
        for i in range(total_segs):
            angle  = math.pi + (math.pi * i / total_segs)
            x = cx + r * math.cos(angle) - 1.5
            y2 = cy + r * math.sin(angle) - 1.5
            c2 = color if i < filled else C["slate_100"]
            self.set_fill_color(*c2)
            self.ellipse(x, y2, 3, 3, "F")
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(*color)
        self.set_xy(cx - 12, cy - 6)
        self.cell(24, 10, f"{inv_score}/10", align="C")
        self.set_font("Helvetica", size=8)
        self.set_text_color(*C["slate_500"])
        self.set_xy(cx - 20, cy + 6)
        self.cell(40, 6, "INVESTOR CONFIDENCE", align="C")
        self.ln(cy - self.get_y() + 30)

    def two_col_bullets(self, label_l, items_l, label_r, items_r,
                        color_l="green", color_r="red"):
        """Side-by-side bullet lists."""
        y0   = self.get_y()
        midx = 106
        # left
        self.set_xy(18, y0)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*C[color_l])
        self.cell(86, 5, _s(label_l).upper(),
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        for item in (items_l or [])[:5]:
            self.set_x(18)
            self.set_fill_color(*C[color_l])
            self.ellipse(19, self.get_y() + 3, 2, 2, "F")
            self.set_x(24)
            self.set_font("Helvetica", size=9)
            self.set_text_color(*C["slate_900"])
            self.multi_cell(80, 5, _s(str(item), 160),
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.gap(1)
        y_end_l = self.get_y()
        # right
        self.set_xy(midx, y0)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*C[color_r])
        self.cell(86, 5, _s(label_r).upper(),
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        for item in (items_r or [])[:5]:
            self.set_x(midx)
            self.set_fill_color(*C[color_r])
            self.ellipse(midx + 1, self.get_y() + 3, 2, 2, "F")
            self.set_x(midx + 6)
            self.set_font("Helvetica", size=9)
            self.set_text_color(*C["slate_900"])
            self.multi_cell(80, 5, _s(str(item), 160),
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.gap(1)
        self.set_y(max(self.get_y(), y_end_l) + 4)

    def checklist_row(self, text: str, done: bool):
        clr = C["green_lt"] if done else C["slate_300"]
        sym = "+" if done else "-"
        tc  = C["slate_900"] if done else C["slate_500"]
        y   = self.get_y()
        self.set_fill_color(*clr)
        self.rect(18, y + 1, 6, 6, "F")
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*C["white"])
        self.set_xy(18, y + 1)
        self.cell(6, 6, sym, align="C")
        self.set_x(27)
        self.set_font("Helvetica", size=10)
        self.set_text_color(*tc)
        self.multi_cell(165, 6, _s(text),
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*C["slate_300"])
        self.set_line_width(0.2)
        self.line(18, self.get_y(), 192, self.get_y())
        self.gap(1)

    def timeline_block(self, steps: list):
        """3-phase horizontal timeline."""
        if not steps: return
        colors = [C["blue"], C["green"], C["amber"]]
        labels = ["Days 1-30", "Days 31-60", "Days 61-90"]
        y0     = self.get_y()
        w      = 56
        for i, step in enumerate(steps[:3]):
            x = 18 + i * (w + 3)
            # header
            self.set_fill_color(*colors[i])
            self.rect(x, y0, w, 9, "F")
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(*C["white"])
            self.set_xy(x, y0 + 1)
            self.cell(w, 7, labels[i], align="C")
            # body
            self.set_fill_color(*C["slate_100"])
            body_h = 28
            self.rect(x, y0 + 9, w, body_h, "F")
            self.set_font("Helvetica", size=8)
            self.set_text_color(*C["slate_900"])
            self.set_xy(x + 2, y0 + 11)
            self.multi_cell(w - 4, 4.5, _s(str(step), 160))
        self.set_y(y0 + 42)

    def dimension_bars(self, bd: dict, total: int):
        """Visual score bars for 5 dimensions."""
        if not bd: return
        items = [
            ("Problem Strength",    bd.get("problem_strength", 0)),
            ("Market Opportunity",  bd.get("market_opportunity", 0)),
            ("Competitive Position",bd.get("competitive_position", 0)),
            ("Team Execution",      bd.get("team_execution", 0)),
            ("Financial Viability", bd.get("financial_viability", 0)),
        ]
        self.gap(2)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*C["navy"])
        self.cell(0, 6, f"Score Breakdown - Total: {total}/100",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.gap(2)
        for label, val in items:
            self.score_bar(label, val, out_of=20, width=110)
        self.gap(2)

    def market_size_bars(self, market_text: str):
        """Parse TAM/SAM/SOM and draw visual bars."""
        import re
        parts = re.findall(r'\$([0-9.]+)\s*([BMKbmk])', market_text or "")
        if len(parts) < 2: return
        names  = ["TAM", "SAM", "SOM"]
        mults  = {"B": 1000, "M": 1, "K": 0.001}
        values = []
        for n, u in parts[:3]:
            values.append(float(n) * mults.get(u.upper(), 1))
        max_v  = max(values) if values else 1
        colors = [C["blue"], C["indigo"], C["purple"]]
        self.gap(2)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*C["navy"])
        self.cell(0, 6, "Market Size Visualised",

                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.gap(2)
        for i, val in enumerate(values):
            label = names[i]
            pct   = val / max_v if max_v else 0
            y     = self.get_y()
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(*C["slate_700"])
            self.set_xy(18, y)
            self.cell(14, 6, label)
            self.set_fill_color(*C["slate_100"])
            self.rect(34, y + 1, 130, 5, "F")
            self.set_fill_color(*colors[i])
            if pct > 0:
                self.rect(34, y + 1, 130 * pct, 5, "F")
            raw_n, raw_u = parts[i]
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(*colors[i])
            self.set_xy(168, y)
            self.cell(0, 6, f"${raw_n}{raw_u.upper()}")
            self.ln(9)
        self.gap(2)

    def competitor_bars(self, details: list):
        """Horizontal funding bars for competitors."""
        if not details: return
        import re
        names, funds, raw_labels = [], [], []
        for d in details[:6]:
            m = re.search(r'\$([0-9.]+)\s*([BMKbmk])', d.get("funding", ""))
            if m:
                names.append(_s(d.get("name", "?"), 22))
                mults = {"B": 1000, "M": 1, "K": 0.001}
                funds.append(float(m.group(1)) * mults.get(m.group(2).upper(), 1))
                raw_labels.append(f"${m.group(1)}{m.group(2).upper()}")
        if not funds: return
        max_f  = max(funds)
        colors = [C["blue"], C["indigo"], C["purple"],
                  C["blue_light"], C["amber"], C["green"]]
        self.gap(2)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*C["navy"])
        self.cell(0, 6, "Competitor Funding Raised",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.gap(2)
        for i, (name, fund) in enumerate(zip(names, funds)):
            pct = fund / max_f if max_f else 0
            y   = self.get_y()
            self.set_font("Helvetica", size=9)
            self.set_text_color(*C["slate_700"])
            self.set_xy(18, y)
            self.cell(38, 6, name)
            self.set_fill_color(*C["slate_100"])
            self.rect(58, y + 1, 110, 5, "F")
            self.set_fill_color(*colors[i % len(colors)])
            if pct > 0:
                self.rect(58, y + 1, 110 * pct, 5, "F")
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(*colors[i % len(colors)])
            self.set_xy(172, y)
            self.cell(0, 6, raw_labels[i])
            self.ln(9)
        self.gap(2)

    def cover_toc(self, sections: list):
        """Two-column table of contents."""
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*C["slate_500"])
        self.cell(0, 5, "CONTENTS",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.gap(2)
        half = math.ceil(len(sections) / 2)
        left = sections[:half]
        right = sections[half:]
        y0 = self.get_y()
        for i, s in enumerate(left):
            self.set_xy(18, y0 + i * 7)
            self.set_fill_color(*C["fill_navy"])
            self.rect(18, y0 + i * 7, 86, 6, "F")
            self.set_font("Helvetica", size=9)
            self.set_text_color(*C["navy"])
            self.set_x(21)
            self.cell(83, 6, _s(s))
        for i, s in enumerate(right):
            self.set_xy(108, y0 + i * 7)
            self.set_fill_color(*C["fill_navy"])
            self.rect(108, y0 + i * 7, 84, 6, "F")
            self.set_font("Helvetica", size=9)
            self.set_text_color(*C["navy"])
            self.set_x(111)
            self.cell(81, 6, _s(s))
        rows = max(len(left), len(right))
        self.set_y(y0 + rows * 7 + 6)


# ══════════════════════════════════════════════════════════════════════════════
def generate_pdf(report: dict) -> bytes:
    idea = report.get("idea", "Startup Analysis")
    f    = report.get("founder",      {}) or {}
    m    = report.get("market",       {}) or {}
    c    = report.get("competitor",   {}) or {}
    cu   = report.get("customer",     {}) or {}
    inv  = report.get("investor",     {}) or {}
    fl   = report.get("failure",      {}) or {}
    ip   = report.get("india_policy", {}) or {}
    j    = report.get("judge",        {}) or {}

    score   = j.get("final_score", 0) or 0
    verdict = j.get("verdict", "Pivot") or "Pivot"
    dark, light, accent = _verdict_colors(verdict)

    pdf = _PDF(idea, score, verdict)

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 1 - COVER
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()

    # Full-width navy hero
    pdf.set_fill_color(*C["navy"])
    pdf.rect(0, 0, 210, 68, "F")

    # Accent stripe
    pdf.set_fill_color(*accent)
    pdf.rect(0, 64, 210, 4, "F")

    # Report type label
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*C["slate_300"])
    pdf.set_xy(18, 14)
    pdf.cell(0, 6, "STARTUP VIABILITY REPORT  |  AI-POWERED ANALYSIS")

    # Main title
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(*C["white"])
    pdf.set_xy(18, 26)
    pdf.multi_cell(174, 10, _s(idea, 120))

    # Date and ID
    pdf.set_font("Helvetica", size=8)
    pdf.set_text_color(*C["slate_300"])
    pdf.set_xy(18, 56)
    pdf.cell(0, 6,
        f"Generated: {datetime.now().strftime('%d %B %Y')}  |  ID: {report.get('id', '')}")

    pdf.set_y(78)

    # Big score hero
    pdf.big_score_hero(score, verdict, j.get("one_line_verdict", ""))

    pdf.gap(6)
    pdf.hline("slate_300")

    # Table of contents
    toc = [
        "1. Executive Summary", "2. Founder Analysis",
        "3. Market Analysis",   "4. Competitor Analysis",
        "5. Customer Intel",    "6. Investor Assessment",
        "7. Failure Analysis",  "8. India Policy & Schemes",
        "9. Action Plan",       "10. Conclusion",
    ]
    pdf.cover_toc(toc)

    pdf.gap(4)
    pdf.hline("slate_300")
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*C["slate_500"])
    pdf.multi_cell(0, 5,
        "Disclaimer: AI-generated for informational purposes only. "
        "Verify all data independently before business or investment decisions.",
        new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 2 - EXECUTIVE SUMMARY
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_header("1", "Executive Summary")

    # Dimension bars
    pdf.dimension_bars(j.get("scoring_breakdown", {}), score)
    pdf.hline()

    pdf.kv_block("Summary", j.get("summary", ""),
                 fill_color="fill_navy", label_color="navy", border_color="blue")
    pdf.kv_block("Go-To-Market Strategy", j.get("go_to_market", ""),
                 fill_color="fill_blue", label_color="blue", border_color="blue_light")
    pdf.bullet_list("Top Recommendations", j.get("recommendations", []),
                    dot_color="green", fill_color="fill_green", border_color="green_lt")

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 3 - FOUNDER
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_header("2", "Founder Analysis")

    pdf.kv_block("Problem Being Solved", f.get("problem", ""),
                 fill_color="fill_navy", label_color="navy", border_color="blue")
    pdf.kv_block("Target Market", f.get("target_market", ""),
                 fill_color="fill_blue", label_color="blue", border_color="blue_light")
    pdf.kv_block("Minimum Viable Product (MVP)", f.get("mvp", ""),
                 fill_color="fill_purple", label_color="purple", border_color="purple")
    pdf.kv_block("Unique Value Proposition", f.get("unique_value_proposition", ""),
                 fill_color="fill_green", label_color="green", border_color="green_lt")
    pdf.kv_block("Problem Evidence", f.get("problem_evidence", ""),
                 fill_color="fill_amber", label_color="amber", border_color="amber_lt")
    pdf.kv_block("Founder-Market Fit Required", f.get("founder_market_fit", ""),
                 fill_color="fill_blue", label_color="blue", border_color="blue_light")
    pdf.bullet_list("Similar Companies", f.get("similar_companies", []),
                    dot_color="indigo")
    pdf.bullet_list("Critical Success Factors", f.get("success_factors", []),
                    dot_color="green", fill_color="fill_green", border_color="green_lt")

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 4 - MARKET
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_header("3", "Market Analysis")

    # Visual market size bars
    pdf.market_size_bars(m.get("market_size", ""))
    pdf.hline()

    pdf.kv_block("Market Size - TAM / SAM / SOM", m.get("market_size", ""),
                 fill_color="fill_navy", label_color="navy", border_color="blue")
    pdf.kv_block("Growth Rate (CAGR)", m.get("growth_rate", ""),
                 fill_color="fill_green", label_color="green", border_color="green_lt")
    pdf.kv_block("Why Now", m.get("why_now", ""),
                 fill_color="fill_amber", label_color="amber", border_color="amber_lt")
    pdf.bullet_list("Market Statistics", m.get("market_statistics", []),
                    dot_color="blue")
    pdf.bullet_list("Key Opportunities", m.get("opportunities", []),
                    dot_color="green", fill_color="fill_green", border_color="green_lt")
    pdf.bullet_list("Market Trends", m.get("trends", []),
                    dot_color="purple", fill_color="fill_purple", border_color="purple")
    pdf.bullet_list("Revenue Models", m.get("revenue_models", []),
                    dot_color="indigo")
    pdf.bullet_list("Target Segments", m.get("target_segments", []),
                    dot_color="blue")

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 5 - COMPETITOR
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_header("4", "Competitor Analysis")

    # Visual competitor funding bars
    pdf.competitor_bars(c.get("competitor_details", []))
    pdf.hline()

    pdf.kv_block("Market Map", c.get("market_map", ""),
                 fill_color="fill_navy", label_color="navy", border_color="blue")
    pdf.kv_block("Competitive Advantage / Moat", c.get("competitive_advantage", ""),
                 fill_color="fill_blue", label_color="blue", border_color="blue_light")
    pdf.kv_block("Positioning Strategy", c.get("positioning_strategy", ""),
                 fill_color="fill_purple", label_color="purple", border_color="purple")
    pdf.bullet_list("Market Gaps - Underserved Needs", c.get("gaps", []),
                    dot_color="amber", fill_color="fill_amber", border_color="amber_lt")

    # Competitor deep-dives
    details = c.get("competitor_details", []) or []
    if details:
        pdf.hline()
        pdf.subsection("Competitor Deep-Dives", color="navy")
        for d in details[:4]:
            pdf.gap(2)
            pdf.set_fill_color(*C["fill_navy"])
            pdf.rect(18, pdf.get_y(), 174, 8, "F")
            pdf.set_fill_color(*C["navy"])
            pdf.rect(18, pdf.get_y(), 3, 8, "F")
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*C["navy"])
            pdf.set_x(24)
            name_line = f"{_s(d.get('name',''), 30)}  -  {_s(d.get('funding',''), 20)}"
            pdf.cell(0, 8, name_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.two_col_bullets(
                "Strengths", d.get("strengths", []),
                "Weaknesses", d.get("weaknesses", []),
                color_l="green", color_r="red"
            )
            if d.get("how_to_beat"):
                pdf.kv_block("Strategy to Win", d["how_to_beat"],
                             fill_color="fill_green", label_color="green",
                             border_color="green_lt")

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 6 - CUSTOMER
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_header("5", "Customer Intelligence")

    # Persona cards
    personas = cu.get("personas", []) or []
    if personas:
        pdf.subsection("User Personas", color="purple")
        for p in personas[:4]:
            pdf.gap(1)
            pdf.set_fill_color(*C["fill_purple"])
            pdf.rect(18, pdf.get_y(), 174, 4, "F")
            pdf.set_fill_color(*C["purple"])
            pdf.rect(18, pdf.get_y(), 3, 4, "F")
            pdf.set_y(pdf.get_y() + 2)
            pdf.set_x(24)
            pdf.set_font("Helvetica", size=9)
            pdf.set_text_color(*C["slate_900"])
            pdf.multi_cell(168, 5, _s(str(p), 260),
                           new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.gap(2)

    pdf.hline()
    pdf.two_col_bullets(
        "Pain Points (User's Voice)", cu.get("pain_points", []),
        "Acquisition Channels",       cu.get("acquisition_channels", []),
        color_l="amber", color_r="blue"
    )
    pdf.hline()
    pdf.kv_block("Willingness to Pay", cu.get("willingness_to_pay", ""),
                 fill_color="fill_green", label_color="green", border_color="green_lt")
    pdf.kv_block("Early Adopter Profile", cu.get("early_adopter_profile", ""),
                 fill_color="fill_blue", label_color="blue", border_color="blue_light")
    pdf.kv_block("Customer Journey", cu.get("customer_journey", ""),
                 fill_color="fill_navy", label_color="navy", border_color="blue")
    pdf.bullet_list("Community Insights", cu.get("community_insights", []),
                    dot_color="purple", fill_color="fill_purple", border_color="purple")

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 7 - INVESTOR
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_header("6", "Investor Assessment")

    # Gauge + summary side by side
    y0 = pdf.get_y()
    pdf.investor_gauge(inv.get("investment_score", 0) or 0)
    y_after_gauge = pdf.get_y()

    pdf.set_xy(88, y0)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*C["blue"])
    pdf.cell(0, 5, "INVESTMENT SCORE GUIDE",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    for rng, lbl, clr in [
        ("1-3", "Pass - not fundable yet",       "red_lt"),
        ("4-6", "Interested - needs proof",       "amber_lt"),
        ("7-8", "Ready to fund",                  "green_lt"),
        ("9-10","Exceptional opportunity",         "green"),
    ]:
        pdf.set_x(88)
        pdf.set_fill_color(*C[clr])
        pdf.rect(88, pdf.get_y() + 1, 6, 4, "F")
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*C["slate_700"])
        pdf.set_x(97)
        pdf.cell(0, 6, f"{rng}  {lbl}",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(max(pdf.get_y(), y_after_gauge))
    pdf.hline()

    pdf.kv_block("Funding Stage", inv.get("funding_stage", ""),
                 fill_color="fill_navy", label_color="navy", border_color="blue")
    pdf.kv_block("Suggested Raise", inv.get("suggested_raise", ""),
                 fill_color="fill_blue", label_color="blue", border_color="blue_light")
    pdf.kv_block("Exit Potential", inv.get("exit_potential", ""),
                 fill_color="fill_green", label_color="green", border_color="green_lt")
    pdf.kv_block("Investor Concerns", inv.get("concerns", ""),
                 fill_color="fill_amber", label_color="amber", border_color="amber_lt")

    pdf.two_col_bullets(
        "Investment Strengths", inv.get("strengths", []),
        "Key Risks",            inv.get("risks", []),
        color_l="green", color_r="red"
    )
    pdf.hline()
    pdf.bullet_list("Relevant VCs - From Research", inv.get("relevant_investors", []),
                    dot_color="purple", fill_color="fill_purple", border_color="purple")
    pdf.bullet_list("Real Funding Examples", inv.get("funding_examples", []),
                    dot_color="amber", fill_color="fill_amber", border_color="amber_lt")
    pdf.bullet_list("Key Metrics Investors Will Demand",
                    inv.get("key_metrics_for_investors", []),
                    dot_color="blue")

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 8 - FAILURE
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_header("7", "Failure Analysis")

    pdf.kv_block("Biggest Single Risk", fl.get("biggest_single_risk", ""),
                 fill_color="fill_red", label_color="red", border_color="red_lt")
    pdf.kv_block("Runway Analysis", fl.get("runway_analysis", ""),
                 fill_color="fill_amber", label_color="amber", border_color="amber_lt")
    pdf.hline()
    pdf.two_col_bullets(
        "Failure Modes - Causal Chains", fl.get("failure_modes", []),
        "Mitigation Strategies",         fl.get("mitigation_strategies", []),
        color_l="red", color_r="green"
    )
    pdf.hline()
    pdf.bullet_list("Real Companies That Failed Here", fl.get("failed_companies", []),
                    dot_color="amber", fill_color="fill_amber", border_color="amber_lt")
    pdf.two_col_bullets(
        "Critical Success Factors", fl.get("critical_success_factors", []),
        "Pivot Options",            fl.get("pivot_options", []),
        color_l="green", color_r="blue"
    )

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 9 - INDIA POLICY
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_header("8", "India Policy, Schemes & Incentives")

    pdf.kv_block("DPIIT / Startup India Eligibility",
                 ip.get("startup_india_eligibility", ""),
                 fill_color="fill_amber", label_color="orange", border_color="amber_lt")
    pdf.hline()
    pdf.two_col_bullets(
        "DPIIT Benefits",   ip.get("dpiit_benefits", []),
        "Tax Benefits",     ip.get("tax_benefits", []),
        color_l="orange", color_r="green"
    )
    pdf.bullet_list("Government Schemes - With Amounts",
                    ip.get("government_schemes", []),
                    dot_color="orange", fill_color="fill_amber", border_color="amber_lt")
    pdf.bullet_list("Grants and Subsidies", ip.get("grants_and_subsidies", []),
                    dot_color="amber")
    pdf.hline()
    pdf.bullet_list("Indian VCs Active in This Space", ip.get("indian_vcs", []),
                    dot_color="purple", fill_color="fill_purple", border_color="purple")
    pdf.two_col_bullets(
        "Accelerators & Incubators", ip.get("accelerators_incubators", []),
        "State-Level Incentives",    ip.get("state_incentives", []),
        color_l="blue", color_r="orange"
    )
    pdf.hline()
    pdf.bullet_list("Regulatory Requirements", ip.get("regulatory_requirements", []),
                    dot_color="red", fill_color="fill_red", border_color="red_lt")

    # Compliance checklist
    pdf.subsection("Compliance Checklist", color="orange")
    for item in (ip.get("compliance_checklist", []) or []):
        pdf.checklist_row(str(item), done=False)

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 10 - ACTION PLAN
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_header("9", "90-Day Action Plan")

    # Timeline visual
    pdf.timeline_block(j.get("action_plan_90_days", []))
    pdf.hline()

    # Detailed steps
    pdf.subsection("Detailed Steps", color="blue")
    colors_cycle = ["blue", "green", "amber"]
    for i, step in enumerate(j.get("action_plan_90_days", []) or []):
        clr = colors_cycle[i % 3]
        lbl = ["Days 1-30", "Days 31-60", "Days 61-90"][i % 3]
        pdf.gap(2)
        pdf.set_fill_color(*C[clr])
        pdf.rect(18, pdf.get_y(), 28, 7, "F")
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*C["white"])
        pdf.set_xy(18, pdf.get_y() + 1)
        pdf.cell(28, 5, lbl, align="C")
        pdf.set_x(50)
        pdf.set_font("Helvetica", size=9)
        pdf.set_text_color(*C["slate_900"])
        lines = _s(str(step), 300).split(":", 1)
        txt = (lines[0].strip() + ": " + lines[1].strip()) if len(lines) > 1 else lines[0]
        pdf.multi_cell(142, 5.5, txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.gap(2)

    pdf.hline()
    pdf.bullet_list("Key Metrics to Track Weekly", j.get("key_metrics", []),
                    dot_color="green", fill_color="fill_green", border_color="green_lt")

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 11 - CONCLUSION
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_header("10", "Conclusion")

    pdf.mini_score_box(score, verdict)

    pdf.kv_block("Summary", j.get("summary", ""),
                 fill_color="fill_navy", label_color="navy", border_color="blue")
    if j.get("one_line_verdict"):
        pdf.kv_block("One-Line Verdict", j["one_line_verdict"],
                     fill_color="fill_purple", label_color="purple", border_color="purple")
    pdf.hline()

    # Investment readiness checklist
    pdf.subsection("Investment Readiness Checklist", color="green")
    checks = [
        ("Problem validated with 20+ customer interviews",
         bool(f.get("problem_evidence"))),
        ("Market size quantified with data sources",
         bool(m.get("market_size") and "$" in str(m.get("market_size", "")))),
        ("Competitive moat clearly defined",
         bool(c.get("competitive_advantage"))),
        ("Willingness-to-pay validated with real users",
         bool(cu.get("willingness_to_pay"))),
        ("MVP scoped and buildable within 60 days",
         bool(f.get("mvp"))),
        ("DPIIT recognition obtained",
         "yes" in str(ip.get("startup_india_eligibility", "")).lower()),
        ("90-day plan with measurable milestones",
         bool(j.get("action_plan_90_days"))),
        ("Target investors identified",
         bool(inv.get("relevant_investors"))),
    ]
    for text, done in checks:
        pdf.checklist_row(text, done)

    pdf.hline()
    pdf.bullet_list("Final Recommendations", j.get("recommendations", []),
                    dot_color="blue", fill_color="fill_blue", border_color="blue_light")
    pdf.hline()

    # India footnote
    if ip.get("startup_india_eligibility"):
        pdf.set_fill_color(*C["fill_amber"])
        pdf.rect(18, pdf.get_y(), 174, 14, "F")
        pdf.set_fill_color(*C["amber"])
        pdf.rect(18, pdf.get_y(), 3, 14, "F")
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*C["orange"])
        pdf.set_x(24)
        pdf.cell(0, 5, "INDIA OPPORTUNITY",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_x(24)
        pdf.set_font("Helvetica", size=9)
        pdf.set_text_color(*C["slate_900"])
        snippet = _s(str(ip.get("startup_india_eligibility", ""))[:200])
        pdf.multi_cell(168, 5, snippet, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.gap(8)

    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*C["slate_500"])
    pdf.multi_cell(0, 5,
        "Disclaimer: This report is AI-generated for informational purposes only. "
        "All market data, funding figures, and company information should be "
        "independently verified before making any business or investment decisions.",
        new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    return bytes(pdf.output())