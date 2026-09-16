"""
Binary Panel v2 — IBM Punched Card Simulator
Visual style: classic 1970s/80s IBM 80-column punched card (manila / cream stock).

Layout:
  • One card per character row (8 cards stacked vertically, fanned slightly).
  • Each card shows 8 hole positions (bit 7 → bit 0, MSB left).
  • A punched hole  = bit 1  →  dark oval cutout with shadow + paper-edge highlight.
  • An intact position = bit 0  →  faint embossed oval impression on the card stock.
  • IBM-style red top stripe, column numbers, card serial, and keypunch font labels.
  • Confetti/chad particles fall when a new hole is punched.

Controls:
  TYPE      – add character (max 8)
  BACKSPACE – remove last character
  ENTER     – clear / reset
  ESC       – quit
"""

import pygame
import sys
import math
import random

# ─── Screen & timing ─────────────────────────────────────────────────────────
SCREEN_W = 980
SCREEN_H = 780
FPS      = 60
TITLE    = "Binary Panel v2 — Punched Card ASCII Encoder"

# ─── Card geometry ────────────────────────────────────────────────────────────
ROWS         = 8        # cards (one per character)
COLS         = 8        # holes per card (= 8 bits)

CARD_W       = 620      # width of one card in pixels
CARD_H       = 62       # height of one card
CARD_RADIUS  = 6        # rounded-corner radius
CARD_X       = 180      # left edge of card stack
CARD_Y0      = 80       # top of first card
CARD_SPACING = 76       # vertical pitch between cards

HOLE_RX      = 13       # hole oval half-width
HOLE_RY      = 18       # hole oval half-height
HOLE_COL0    = 90       # x of first hole centre inside the card
HOLE_PITCH   = 68       # horizontal pitch between holes

# ─── Colours — aged paper / manila palette ───────────────────────────────────
C_BG            = (45,  38,  28)    # dark walnut desk background
C_BG_GRAIN      = (50,  43,  32)    # subtle grain lines on desk
C_CARD_BODY     = (220, 208, 168)   # manila card stock
C_CARD_SHADOW   = (100, 88,  60)    # drop shadow under card
C_CARD_EDGE_LT  = (240, 230, 195)   # top-edge highlight (thickness illusion)
C_CARD_EDGE_DK  = (180, 165, 125)   # bottom-edge shadow
C_STRIPE_RED    = (190, 40,  30)    # IBM red top stripe
C_STRIPE_TEXT   = (255, 235, 220)   # text printed on red stripe
C_HOLE_VOID     = (22,  16,  8)     # punched-through darkness
C_HOLE_EDGE_LT  = (255, 248, 230)   # paper edge highlight around hole
C_HOLE_EDGE_DK  = (140, 125, 90)    # paper edge shadow around hole
C_INTACT_OVAL   = (205, 194, 155)   # embossed unpunched oval
C_INTACT_HIGH   = (230, 222, 185)   # highlight on embossed oval
C_PRINT_DARK    = (60,  45,  20)    # printed text on card (IBM ink)
C_PRINT_MID     = (100, 80,  45)    # mid tone printed text
C_PRINT_LIGHT   = (160, 140, 95)    # faint printed text / column numbers
C_ACTIVE_TINT   = (255, 220, 100)   # amber tint for active card highlight
C_CHAD          = (220, 208, 168)   # confetti chad colour (card stock)
C_CHAD2         = (200, 185, 140)   # slightly darker chad
C_UI_BG         = (30,  24,  16)    # header / footer bar
C_UI_TEXT       = (210, 180, 120)   # header text
C_UI_DIM        = (120, 100, 65)    # dim UI text
C_UI_ACCENT     = (230, 160, 60)    # amber accent
C_CURSOR_BAR    = (230, 200, 100)   # input cursor
C_PUNCH_FLASH   = (255, 240, 200)   # brief white flash when hole is punched


# ─── Chad / confetti particles ───────────────────────────────────────────────
class Chad:
    """A tiny paper disc ejected when a hole is punched."""
    __slots__ = ("x", "y", "vx", "vy", "rot", "vrot", "alpha", "size", "color")

    def __init__(self, x: float, y: float):
        self.x    = x
        self.y    = y
        self.vx   = random.uniform(-3.0, 3.0)
        self.vy   = random.uniform(-5.0, -1.0)
        self.rot  = random.uniform(0, 360)
        self.vrot = random.uniform(-8, 8)
        self.alpha = 255
        self.size  = random.randint(4, 9)
        self.color = random.choice([C_CHAD, C_CHAD2,
                                    (240, 228, 185), (190, 175, 130)])

    def update(self):
        self.vy   += 0.25          # gravity
        self.x    += self.vx
        self.y    += self.vy
        self.rot  += self.vrot
        self.alpha = max(0, self.alpha - 5)

    @property
    def alive(self) -> bool:
        return self.alpha > 0 and self.y < SCREEN_H + 20


# ─── Core logic ──────────────────────────────────────────────────────────────
def to_binary_rows(text: str) -> list:
    """Convert up to 8 characters to a list of 8 bit-lists (MSB first)."""
    rows = []
    for i in range(8):
        if i < len(text):
            code = ord(text[i]) & 0xFF
            bits = [(code >> (7 - b)) & 1 for b in range(8)]
        else:
            bits = [0] * 8
        rows.append(bits)
    return rows


def hole_center(card_x: int, card_y: int, col: int) -> tuple:
    """Return pixel centre of hole at (col) on a card whose top-left is (card_x, card_y)."""
    cx = card_x + HOLE_COL0 + col * HOLE_PITCH
    cy = card_y + CARD_H // 2 + 4   # slightly below mid (real IBM cards had zones above)
    return cx, cy


# ─── Drawing helpers ─────────────────────────────────────────────────────────
def draw_desk_texture(surface: pygame.Surface):
    """Draw a subtle wood-grain desk background."""
    surface.fill(C_BG)
    for gy in range(0, SCREEN_H, 6):
        shade = random.randint(-4, 4)
        c = (
            max(0, min(255, C_BG_GRAIN[0] + shade)),
            max(0, min(255, C_BG_GRAIN[1] + shade)),
            max(0, min(255, C_BG_GRAIN[2] + shade)),
        )
        pygame.draw.line(surface, c, (0, gy), (SCREEN_W, gy), 1)


def draw_oval(surface: pygame.Surface, cx: int, cy: int, rx: int, ry: int, color, width=0):
    rect = pygame.Rect(cx - rx, cy - ry, rx * 2, ry * 2)
    pygame.draw.ellipse(surface, color, rect, width)


def draw_punched_hole(surface: pygame.Surface, cx: int, cy: int, pulse: float):
    """
    Draw a punched-through hole.
    pulse 0→1: brief bright flash around rim as hole is freshly punched.
    """
    # Paper fibre edge — light arc (top-left) and dark arc (bottom-right)
    draw_oval(surface, cx, cy, HOLE_RX + 3, HOLE_RY + 3, C_HOLE_EDGE_DK)
    draw_oval(surface, cx - 1, cy - 1, HOLE_RX + 2, HOLE_RY + 2, C_HOLE_EDGE_LT)

    # The void
    draw_oval(surface, cx, cy, HOLE_RX, HOLE_RY, C_HOLE_VOID)

    # Inner highlight on the near edge of the paper wall
    draw_oval(surface, cx, cy - 2, HOLE_RX - 3, HOLE_RY - 5, C_HOLE_EDGE_LT, width=1)

    # Punch flash (freshly punched)
    if pulse < 1.0:
        flash_a = int(200 * (1.0 - pulse))
        flash_surf = pygame.Surface((HOLE_RX * 4, HOLE_RY * 4), pygame.SRCALPHA)
        ell_rect = pygame.Rect(HOLE_RX, HOLE_RY, HOLE_RX * 2, HOLE_RY * 2)
        pygame.draw.ellipse(flash_surf,
                            (*C_PUNCH_FLASH, flash_a), ell_rect, 3)
        surface.blit(flash_surf, (cx - HOLE_RX * 2, cy - HOLE_RY * 2),
                     special_flags=pygame.BLEND_RGBA_ADD)


def draw_intact_position(surface: pygame.Surface, cx: int, cy: int):
    """Draw an embossed (unpunched) oval impression."""
    draw_oval(surface, cx, cy, HOLE_RX + 1, HOLE_RY + 1, C_CARD_EDGE_DK)
    draw_oval(surface, cx, cy, HOLE_RX,     HOLE_RY,     C_INTACT_OVAL)
    # Tiny highlight to give embossed feel
    draw_oval(surface, cx - 1, cy - 2, HOLE_RX - 4, HOLE_RY - 6, C_INTACT_HIGH, width=1)


def draw_card(surface: pygame.Surface, fonts: dict, card_x: int, card_y: int,
              row: int, word: str, bits: list, pulses: list,
              is_active: bool, tick: int):
    """Draw one complete punched card for the given character row."""

    # ── Drop shadow ──────────────────────────────────────────────────────────
    shadow_rect = pygame.Rect(card_x + 4, card_y + 5, CARD_W, CARD_H)
    shadow_surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
    shadow_surf.fill((*C_CARD_SHADOW, 120))
    surface.blit(shadow_surf, shadow_rect.topleft)

    # ── Active card amber tint background ────────────────────────────────────
    if is_active and word:
        tint_surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
        tint_surf.fill((*C_ACTIVE_TINT, 22))
        surface.blit(tint_surf, (card_x, card_y))

    # ── Card body ─────────────────────────────────────────────────────────────
    card_rect = pygame.Rect(card_x, card_y, CARD_W, CARD_H)
    pygame.draw.rect(surface, C_CARD_BODY, card_rect, border_radius=CARD_RADIUS)

    # Simulated paper thickness: bright top edge, dark bottom edge
    pygame.draw.line(surface, C_CARD_EDGE_LT,
                     (card_x + CARD_RADIUS, card_y),
                     (card_x + CARD_W - CARD_RADIUS, card_y), 2)
    pygame.draw.line(surface, C_CARD_EDGE_DK,
                     (card_x + CARD_RADIUS, card_y + CARD_H - 1),
                     (card_x + CARD_W - CARD_RADIUS, card_y + CARD_H - 1), 2)

    # ── Top stripe (IBM-style red band) ──────────────────────────────────────
    stripe_rect = pygame.Rect(card_x, card_y, CARD_W, 14)
    pygame.draw.rect(surface, C_STRIPE_RED, stripe_rect,
                     border_top_left_radius=CARD_RADIUS,
                     border_top_right_radius=CARD_RADIUS)

    # Stripe text — card serial / character info
    if row < len(word):
        ch      = word[row]
        dec_val = ord(ch) & 0xFF
        stripe_txt = (f"COL {row + 1:02d}   "
                      f"CHAR: '{ch}'   "
                      f"DEC: {dec_val:3d}   "
                      f"HEX: {dec_val:02X}H   "
                      f"BIN: {dec_val:08b}")
    else:
        stripe_txt = f"COL {row + 1:02d}   (EMPTY)"

    st_surf = fonts["tiny"].render(stripe_txt, True, C_STRIPE_TEXT)
    surface.blit(st_surf, (card_x + 8, card_y + 1))

    # ── Column weight labels printed on card stock ────────────────────────────
    weights  = ["128", "64", "32", "16", "8", "4", "2", "1"]
    bit_lbls = ["b7",  "b6", "b5", "b4", "b3","b2","b1","b0"]
    for col in range(COLS):
        hcx, _ = hole_center(card_x, card_y, col)
        # weight above hole area
        wl = fonts["tiny"].render(weights[col], True, C_PRINT_LIGHT)
        surface.blit(wl, (hcx - wl.get_width() // 2, card_y + 15))
        # bit label below hole area
        bl = fonts["tiny"].render(bit_lbls[col], True, C_PRINT_LIGHT)
        surface.blit(bl, (hcx - bl.get_width() // 2, card_y + CARD_H - 14))

    # ── Holes ─────────────────────────────────────────────────────────────────
    for col in range(COLS):
        hcx, hcy = hole_center(card_x, card_y, col)
        bit = bits[col]
        if bit:
            draw_punched_hole(surface, hcx, hcy, pulses[col])
        else:
            draw_intact_position(surface, hcx, hcy)

    # ── Left margin: row number + character badge ─────────────────────────────
    row_lbl = fonts["small"].render(f"#{row + 1}", True, C_PRINT_MID)
    surface.blit(row_lbl, (card_x + 6, card_y + CARD_H // 2 - 7))

    if row < len(word):
        ch = word[row]
        badge_col = C_PRINT_DARK if not is_active else (140, 80, 0)
        ch_lbl = fonts["mono"].render(f"'{ch}'", True, badge_col)
        surface.blit(ch_lbl, (card_x + 30, card_y + CARD_H // 2 - 8))
    else:
        empty_lbl = fonts["small"].render("---", True, C_PRINT_LIGHT)
        surface.blit(empty_lbl, (card_x + 30, card_y + CARD_H // 2 - 6))

    # ── Right margin: decimal + hex ───────────────────────────────────────────
    if row < len(word):
        dec_val = ord(word[row]) & 0xFF
        dec_lbl = fonts["small"].render(f"{dec_val}", True, C_PRINT_MID)
        hex_lbl = fonts["tiny"].render(f"0x{dec_val:02X}", True, C_PRINT_LIGHT)
        surface.blit(dec_lbl, (card_x + CARD_W - 68, card_y + CARD_H // 2 - 10))
        surface.blit(hex_lbl, (card_x + CARD_W - 68, card_y + CARD_H // 2 + 4))

    # ── Card border outline ───────────────────────────────────────────────────
    border_col = C_UI_ACCENT if is_active and word else C_CARD_EDGE_DK
    pygame.draw.rect(surface, border_col, card_rect, 1, border_radius=CARD_RADIUS)

    # ── Notched corner (top-left cut) — classic IBM feature ───────────────────
    notch_pts = [
        (card_x,       card_y + 18),
        (card_x + 12,  card_y + 6),
        (card_x + 12,  card_y),
        (card_x,       card_y),
    ]
    pygame.draw.polygon(surface, C_BG, notch_pts)
    pygame.draw.polygon(surface, C_CARD_EDGE_DK, notch_pts, 1)

    # ── Sprocket holes — small circles on left and right edges ────────────────
    for sx_off, base_x in [(8, card_x), (-8, card_x + CARD_W)]:
        for sy_off in [CARD_H // 2]:
            scx = base_x + sx_off if sx_off > 0 else base_x + sx_off
            scy = card_y + sy_off
            pygame.draw.circle(surface, C_CARD_EDGE_DK, (scx, scy), 4)
            pygame.draw.circle(surface, C_HOLE_VOID,    (scx, scy), 3)


def draw_chad_particles(surface: pygame.Surface, chads: list):
    """Draw all live chad confetti particles."""
    for chad in chads:
        if not chad.alive:
            continue
        s = pygame.Surface((chad.size * 2, chad.size * 2), pygame.SRCALPHA)
        pts = []
        for i in range(4):
            angle = math.radians(chad.rot + i * 90)
            pts.append((
                chad.size + chad.size * 0.8 * math.cos(angle),
                chad.size + chad.size * 0.8 * math.sin(angle),
            ))
        pygame.draw.polygon(s, (*chad.color, chad.alpha), pts)
        surface.blit(s, (int(chad.x) - chad.size, int(chad.y) - chad.size),
                     special_flags=pygame.BLEND_RGBA_ADD)


def draw_ui(surface: pygame.Surface, fonts: dict,
            word: str, bits_matrix: list, tick: int,
            desk_surf: pygame.Surface):
    """Draw header, input bar, status bar and instructions."""

    # ── Header ────────────────────────────────────────────────────────────────
    pygame.draw.rect(surface, C_UI_BG, (0, 0, SCREEN_W, 52))
    pygame.draw.line(surface, C_UI_ACCENT, (0, 52), (SCREEN_W, 52), 1)

    title_surf = fonts["title"].render(TITLE, True, C_UI_ACCENT)
    surface.blit(title_surf, (18, 13))

    # Blinking feed indicator
    if (tick // 28) % 2 == 0:
        feed_col = C_UI_ACCENT
    else:
        feed_col = (80, 60, 25)
    pygame.draw.rect(surface, feed_col, (SCREEN_W - 44, 18, 16, 16), border_radius=3)
    feed_lbl = fonts["tiny"].render("FEED", True, C_UI_DIM)
    surface.blit(feed_lbl, (SCREEN_W - 70, 34))

    # ── Bottom input + instructions panel ────────────────────────────────────
    panel_y  = CARD_Y0 + ROWS * CARD_SPACING + 10
    avail_h  = SCREEN_H - panel_y - 30

    pygame.draw.line(surface, C_UI_DIM, (CARD_X - 30, panel_y),
                     (CARD_X + CARD_W + 80, panel_y), 1)

    # Prompt + typed word
    active_row = max(0, len(word) - 1) if word else 0
    prompt = fonts["mono"].render("KEYPUNCH >", True, C_UI_DIM)
    surface.blit(prompt, (CARD_X - 30, panel_y + 8))

    wx = CARD_X - 30 + prompt.get_width() + 14
    for i, ch in enumerate(word):
        col = C_UI_ACCENT if i == active_row else C_UI_TEXT
        cs = fonts["mono"].render(ch, True, col)
        surface.blit(cs, (wx + i * 22, panel_y + 8))

    # Blinking cursor
    if len(word) < 8 and (tick // 22) % 2 == 0:
        pygame.draw.rect(surface, C_CURSOR_BAR,
                         (wx + len(word) * 22, panel_y + 10, 14, 18))

    # Char count
    cc = fonts["small"].render(f"{len(word)}/8", True, C_UI_DIM)
    surface.blit(cc, (wx + 8 * 22 + 12, panel_y + 12))

    # Instructions
    instructions = [
        "TYPE  — enter a character (max 8)",
        "BKSP  — delete last character",
        "ENTER — clear card stack",
        "ESC   — quit",
    ]
    iy = panel_y + 36
    for line in instructions:
        ls = fonts["tiny"].render(line, True, C_UI_DIM)
        surface.blit(ls, (CARD_X - 30, iy))
        iy += 16

    # ── Status bar ────────────────────────────────────────────────────────────
    pygame.draw.rect(surface, C_UI_BG, (0, SCREEN_H - 28, SCREEN_W, 28))
    pygame.draw.line(surface, C_UI_DIM, (0, SCREEN_H - 28), (SCREEN_W, SCREEN_H - 28), 1)

    punched  = sum(sum(r) for r in bits_matrix)
    intact   = 64 - punched
    st_parts = [
        "IBM 029 KEYPUNCH EMULATOR",
        f"CARDS: {ROWS}",
        f"HOLES/CARD: {COLS}",
        f"PUNCHED: {punched:2d}",
        f"INTACT: {intact:2d}",
        f"WORD: \"{word}\"" if word else "WORD: (empty)",
    ]
    sx = 14
    for part in st_parts:
        ss = fonts["tiny"].render(part, True, C_UI_DIM)
        surface.blit(ss, (sx, SCREEN_H - 20))
        sx += ss.get_width() + 28


def build_fonts() -> dict:
    pygame.font.init()
    try:
        mono_name  = pygame.font.match_font(
            "couriernew,courier,consolas,lucidaconsole,dejavusansmono")
        title_font = pygame.font.Font(mono_name, 20)
        mono_font  = pygame.font.Font(mono_name, 16)
        small_font = pygame.font.Font(mono_name, 13)
        tiny_font  = pygame.font.Font(mono_name, 11)
    except Exception:
        title_font = pygame.font.SysFont("monospace", 20, bold=True)
        mono_font  = pygame.font.SysFont("monospace", 16)
        small_font = pygame.font.SysFont("monospace", 13)
        tiny_font  = pygame.font.SysFont("monospace", 11)
    return {"title": title_font, "mono": mono_font,
            "small": small_font, "tiny": tiny_font}


# ─── Pre-render stable desk texture once ─────────────────────────────────────
def make_desk_surface() -> pygame.Surface:
    surf = pygame.Surface((SCREEN_W, SCREEN_H))
    surf.fill(C_BG)
    rng = random.Random(42)          # deterministic grain
    for gy in range(0, SCREEN_H, 5):
        shade = rng.randint(-5, 5)
        c = (
            max(0, min(255, C_BG_GRAIN[0] + shade)),
            max(0, min(255, C_BG_GRAIN[1] + shade)),
            max(0, min(255, C_BG_GRAIN[2] + shade)),
        )
        pygame.draw.line(surf, c, (0, gy), (SCREEN_W, gy), 1)
    return surf


# ─── Main loop ───────────────────────────────────────────────────────────────
def run():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption(TITLE)
    clock  = pygame.time.Clock()
    fonts  = build_fonts()
    desk   = make_desk_surface()

    word        = ""
    bits_matrix = to_binary_rows(word)

    # Per-hole punch animation: 0.0 = just punched, 1.0 = steady
    hole_pulses = [[1.0] * COLS for _ in range(ROWS)]
    prev_bits   = [[0]   * COLS for _ in range(ROWS)]

    # Chad particle list
    chads: list = []

    tick = 0

    while True:
        clock.tick(FPS)
        tick += 1

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                elif event.key == pygame.K_RETURN:
                    word        = ""
                    bits_matrix = to_binary_rows(word)
                    hole_pulses = [[1.0] * COLS for _ in range(ROWS)]
                    prev_bits   = [[0]   * COLS for _ in range(ROWS)]
                    chads.clear()

                elif event.key == pygame.K_BACKSPACE:
                    if word:
                        word        = word[:-1]
                        bits_matrix = to_binary_rows(word)

                else:
                    if (event.unicode
                            and event.unicode.isprintable()
                            and len(word) < 8):
                        word        += event.unicode
                        bits_matrix  = to_binary_rows(word)

        # ── Trigger punch animation + spawn chad for newly punched holes ──────
        for r in range(ROWS):
            for c in range(COLS):
                if bits_matrix[r][c] == 1 and prev_bits[r][c] == 0:
                    hole_pulses[r][c] = 0.0
                    # Spawn chad particles at hole position
                    card_x = CARD_X
                    card_y = CARD_Y0 + r * CARD_SPACING
                    hcx, hcy = hole_center(card_x, card_y, c)
                    for _ in range(random.randint(4, 9)):
                        chads.append(Chad(hcx, hcy))
                elif bits_matrix[r][c] == 0 and prev_bits[r][c] == 1:
                    hole_pulses[r][c] = 1.0
                prev_bits[r][c] = bits_matrix[r][c]

        # ── Advance punch-flash animations ────────────────────────────────────
        for r in range(ROWS):
            for c in range(COLS):
                if bits_matrix[r][c] == 1 and hole_pulses[r][c] < 1.0:
                    hole_pulses[r][c] = min(1.0, hole_pulses[r][c] + 0.055)

        # ── Update chad particles ─────────────────────────────────────────────
        for chad in chads:
            chad.update()
        chads = [ch for ch in chads if ch.alive]

        # ── Active row ────────────────────────────────────────────────────────
        active_row = max(0, len(word) - 1) if word else -1

        # ── Render ────────────────────────────────────────────────────────────
        screen.blit(desk, (0, 0))

        # Draw cards bottom-up so top card paints last (correct overlap)
        for row in range(ROWS - 1, -1, -1):
            card_x   = CARD_X
            card_y   = CARD_Y0 + row * CARD_SPACING
            is_act   = (row == active_row)
            draw_card(screen, fonts, card_x, card_y,
                      row, word, bits_matrix[row], hole_pulses[row],
                      is_act, tick)

        # Chad particles over cards
        draw_chad_particles(screen, chads)

        # Header / footer / input UI (drawn last — always on top)
        draw_ui(screen, fonts, word, bits_matrix, tick, desk)

        pygame.display.flip()


if __name__ == "__main__":
    run()
