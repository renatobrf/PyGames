"""
Flight Radar v2 - 16-bit inspired ATC radar game
Controls:
  A / Enter - Accept the approaching aircraft  (+10 pts, streak bonus)
  D         - Deny / reroute the aircraft      (+5 pts)
  Tab       - Cycle selection between approaching aircraft
  Q / ESC   - Quit

Score system (v2):
  Accept (land)   : +10 base points  × streak multiplier
  Deny (reroute)  : +5  points       (no streak)
  Incident        : -20 points, streak reset
  Streak bonus    : every 5 consecutive accepts → +25 bonus pts
  Accuracy        : cleared / (cleared + incidents) × 100 %
"""

import pygame
import math
import random
import sys

# ── Constants ────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 800, 700          # extra 50 px at bottom for score bar
FPS = 60

# Radar geometry (same as v1)
RADAR_CX, RADAR_CY = WIDTH // 2, HEIGHT // 2 - 55
RADAR_RADIUS = 270

# 16-bit phosphor green palette
BLACK        = (0,   0,   0)
DARK_GREEN   = (0,   40,  0)
MED_GREEN    = (0,   100, 20)
GREEN        = (0,   200, 60)
BRIGHT_GREEN = (100, 255, 120)
WHITE_GREEN  = (180, 255, 180)
DIM_GREEN    = (0,   60,  10)
UI_GREEN     = (0,   180, 50)
ALERT_GREEN  = (180, 255, 80)
RED_ALERT    = (220, 60,  60)

# v2 score colors
SCORE_GOLD   = (255, 215, 50)
SCORE_SILVER = (160, 200, 160)
SCORE_DIM    = (60,  80,  60)
SCORE_RED    = (200, 50,  50)
SCORE_STREAK = (255, 180, 0)

# Aircraft state machine
STATE_APPROACHING = "approaching"
STATE_LANDING     = "landing"
STATE_REROUTING   = "rerouting"
STATE_GONE        = "gone"

# Scoring values
PTS_ACCEPT   = 10
PTS_DENY     = 5
PTS_INCIDENT = -20
PTS_STREAK   = 25      # bonus every STREAK_MILESTONE consecutive accepts
STREAK_MILESTONE = 5

CALLSIGNS = [
    "TAM3271", "GOL1045", "AZU4892", "LAT7603", "AMX2214",
    "DAL0931", "UAL5578", "BAW2360", "KLM7744", "LAN8821",
    "AFR0117", "IBE6301", "QFA001",  "SWR100",  "DLH400",
]


# ── Aircraft Entity ───────────────────────────────────────────────────────────
class Aircraft:
    _id_counter = 0

    def __init__(self):
        Aircraft._id_counter += 1
        self.callsign = random.choice(CALLSIGNS)[:-2] + f"{random.randint(10,99)}"
        self.altitude = random.randint(180, 390) * 100   # ft
        self.speed    = random.randint(280, 520)          # kts

        # Start on the radar edge at a random angle
        self.angle = random.uniform(0, 2 * math.pi)
        self.dist  = float(RADAR_RADIUS - 5)
        self.state = STATE_APPROACHING

        self.approach_speed = random.uniform(0.25, 0.55)
        self.reroute_angle_delta = random.choice([-1, 1]) * random.uniform(0.008, 0.018)

        self.trail: list[tuple[float, float]] = []
        self.blink_timer = 0.0
        self.ttl = 0.0

        self._update_pos()

    def _update_pos(self):
        self.x = RADAR_CX + self.dist * math.cos(self.angle)
        self.y = RADAR_CY + self.dist * math.sin(self.angle)

    def polar_pos(self):
        return self.x, self.y

    def update(self, dt: float):
        self.blink_timer += dt

        if self.state == STATE_APPROACHING:
            self.dist -= self.approach_speed
            self._update_pos()
            self.trail.append((self.x, self.y))
            if len(self.trail) > 18:
                self.trail.pop(0)
            if self.dist <= 0:
                self.state = STATE_GONE
                self.ttl   = 1.5

        elif self.state == STATE_LANDING:
            self.dist -= self.approach_speed * 3.0
            self._update_pos()
            self.trail.append((self.x, self.y))
            if len(self.trail) > 12:
                self.trail.pop(0)
            if self.dist <= 0:
                self.state = STATE_GONE
                self.ttl   = 1.5

        elif self.state == STATE_REROUTING:
            self.angle += self.reroute_angle_delta
            self.dist  += self.approach_speed * 0.8
            self._update_pos()
            self.trail.append((self.x, self.y))
            if len(self.trail) > 18:
                self.trail.pop(0)
            if self.dist >= RADAR_RADIUS + 40:
                self.state = STATE_GONE
                self.ttl   = 0.0

        elif self.state == STATE_GONE:
            self.ttl -= dt

    def is_dead(self):
        return self.state == STATE_GONE and self.ttl <= 0

    def accept(self):
        if self.state == STATE_APPROACHING:
            self.state = STATE_LANDING

    def deny(self):
        if self.state == STATE_APPROACHING:
            self.state = STATE_REROUTING

    def draw(self, surface: pygame.Surface):
        if self.state == STATE_GONE:
            return

        # Phosphor trail
        for i, (tx, ty) in enumerate(self.trail):
            r = max(1, i // 4)
            color = (0, int(80 + 120 * (i / max(len(self.trail), 1))), 20)
            pygame.draw.circle(surface, color, (int(tx), int(ty)), r)

        blink = (int(self.blink_timer * 3) % 2 == 0) if self.state == STATE_APPROACHING else True

        if blink:
            ix, iy = int(self.x), int(self.y)
            if self.state == STATE_LANDING:
                col  = ALERT_GREEN
                size = 6
                cx_dir = RADAR_CX - self.x
                cy_dir = RADAR_CY - self.y
                length = math.hypot(cx_dir, cy_dir) or 1
                nx, ny = cx_dir / length, cy_dir / length
                pts = [
                    (ix + int(nx * size * 2), iy + int(ny * size * 2)),
                    (ix + int(-ny * size),    iy + int(nx * size)),
                    (ix + int(ny * size),     iy + int(-nx * size)),
                ]
                pygame.draw.polygon(surface, col, pts)
            elif self.state == STATE_REROUTING:
                pygame.draw.circle(surface, MED_GREEN, (ix, iy), 4)
                pygame.draw.circle(surface, DIM_GREEN, (ix, iy), 7, 1)
            else:
                pygame.draw.line(surface, BRIGHT_GREEN, (ix - 5, iy), (ix + 5, iy), 2)
                pygame.draw.line(surface, BRIGHT_GREEN, (ix, iy - 5), (ix, iy + 5), 2)
                pygame.draw.circle(surface, GREEN, (ix, iy), 3)

        if self.state != STATE_GONE:
            label_col = (ALERT_GREEN  if self.state == STATE_LANDING  else
                         MED_GREEN    if self.state == STATE_REROUTING else WHITE_GREEN)
            font = pygame.font.SysFont("Courier New", 10, bold=True)
            txt  = font.render(self.callsign, True, label_col)
            surface.blit(txt, (int(self.x) + 8, int(self.y) - 8))


# ── Radar Sweep ───────────────────────────────────────────────────────────────
class RadarSweep:
    def __init__(self):
        self.angle = 0.0
        self.speed = 1.2    # rad/s

    def update(self, dt: float):
        self.angle = (self.angle + self.speed * dt) % (2 * math.pi)

    def draw(self, surface: pygame.Surface):
        trail_steps = 30
        trail_span  = math.pi * 0.45

        for i in range(trail_steps):
            frac = i / trail_steps
            a    = self.angle - trail_span * (1 - frac)
            green_val = int(30 + 100 * frac)
            col  = (0, green_val, int(green_val * 0.3))

            pts = [(RADAR_CX, RADAR_CY)]
            arc_steps = 4
            for j in range(arc_steps + 1):
                aa = a + (trail_span / trail_steps) * j
                px = RADAR_CX + RADAR_RADIUS * math.cos(aa)
                py = RADAR_CY + RADAR_RADIUS * math.sin(aa)
                pts.append((px, py))
            if len(pts) >= 3:
                pygame.draw.polygon(surface, col, pts)

        ex = RADAR_CX + RADAR_RADIUS * math.cos(self.angle)
        ey = RADAR_CY + RADAR_RADIUS * math.sin(self.angle)
        pygame.draw.line(surface, GREEN, (RADAR_CX, RADAR_CY), (int(ex), int(ey)), 2)


# ── Radar background ─────────────────────────────────────────────────────────
def draw_radar_bg(surface: pygame.Surface, font_small):
    for ring in range(1, 5):
        r = RADAR_RADIUS * ring // 4
        pygame.draw.circle(surface, MED_GREEN, (RADAR_CX, RADAR_CY), r, 1)
        lbl = font_small.render(f"{ring * 25} NM", True, DIM_GREEN)
        surface.blit(lbl, (RADAR_CX + r + 2, RADAR_CY - 10))

    pygame.draw.line(surface, MED_GREEN,
                     (RADAR_CX - RADAR_RADIUS, RADAR_CY),
                     (RADAR_CX + RADAR_RADIUS, RADAR_CY), 1)
    pygame.draw.line(surface, MED_GREEN,
                     (RADAR_CX, RADAR_CY - RADAR_RADIUS),
                     (RADAR_CX, RADAR_CY + RADAR_RADIUS), 1)
    pygame.draw.circle(surface, GREEN, (RADAR_CX, RADAR_CY), RADAR_RADIUS, 2)

    compass = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
    for label, (dx, dy) in compass.items():
        px = RADAR_CX + int(dx * (RADAR_RADIUS + 14))
        py = RADAR_CY + int(dy * (RADAR_RADIUS + 14))
        txt = font_small.render(label, True, UI_GREEN)
        surface.blit(txt, (px - txt.get_width() // 2, py - txt.get_height() // 2))


# ── Score state dataclass-like container ─────────────────────────────────────
class ScoreState:
    def __init__(self):
        self.points        = 0
        self.cleared       = 0       # accepted and landed
        self.rerouted      = 0       # denied
        self.incidents     = 0       # reached center unhandled
        self.streak        = 0       # consecutive accepts
        self.best_streak   = 0
        self.elapsed       = 0.0     # total seconds played
        self.last_delta    = 0       # last point change (for animation)
        self.delta_timer   = 0.0     # how long to show the delta label

    def add_accept(self):
        self.streak += 1
        if self.streak > self.best_streak:
            self.best_streak = self.streak
        pts = PTS_ACCEPT
        bonus = 0
        if self.streak % STREAK_MILESTONE == 0:
            bonus = PTS_STREAK
        total = pts + bonus
        self.points  += total
        self.cleared += 1
        self.last_delta  = total
        self.delta_timer = 2.0
        return bonus > 0   # True if streak bonus was awarded

    def add_deny(self):
        self.rerouted += 1
        self.points   += PTS_DENY
        self.last_delta  = PTS_DENY
        self.delta_timer = 1.5
        # deny does NOT reset streak

    def add_incident(self):
        self.incidents += 1
        self.streak = 0
        self.points  = max(0, self.points + PTS_INCIDENT)
        self.last_delta  = PTS_INCIDENT
        self.delta_timer = 2.0

    def update(self, dt: float):
        self.elapsed += dt
        if self.delta_timer > 0:
            self.delta_timer -= dt

    @property
    def accuracy(self) -> float:
        total = self.cleared + self.incidents
        return (self.cleared / total * 100.0) if total > 0 else 100.0

    @property
    def elapsed_str(self) -> str:
        m = int(self.elapsed) // 60
        s = int(self.elapsed) % 60
        return f"{m:02d}:{s:02d}"


# ── Draw the top HUD bar ──────────────────────────────────────────────────────
def draw_top_bar(surface: pygame.Surface, fonts, score: ScoreState,
                 aircraft_list: list, active_idx: int):
    font_med   = fonts["med"]
    font_small = fonts["small"]

    pygame.draw.line(surface, MED_GREEN, (0, 20), (WIDTH, 20), 1)
    title = font_med.render("AIR TRAFFIC CONTROL — RADAR v2.0", True, GREEN)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 3))

    # Points top-left
    pts_txt = font_small.render(f"PTS: {score.points:>6}", True, SCORE_GOLD)
    surface.blit(pts_txt, (10, 5))

    # Incidents top-right
    inc_col = RED_ALERT if score.incidents > 0 else DIM_GREEN
    inc_txt = font_small.render(f"INCIDENTS: {score.incidents}", True, inc_col)
    surface.blit(inc_txt, (WIDTH - inc_txt.get_width() - 10, 5))

    # Traffic sidebar (right of radar)
    panel_y    = HEIGHT - 160         # top of bottom panels
    sidebar_x  = RADAR_CX + RADAR_RADIUS + 30
    approaching = [a for a in aircraft_list if a.state == STATE_APPROACHING]
    active      = approaching[active_idx % len(approaching)] if approaching else None

    surface.blit(font_small.render("── TRAFFIC ──", True, MED_GREEN), (sidebar_x, 30))
    y_off = 48
    for ac in aircraft_list:
        if ac.state == STATE_GONE:
            continue
        col = (ALERT_GREEN if (ac.state == STATE_APPROACHING and ac == active) else
               GREEN       if ac.state == STATE_LANDING                        else
               DIM_GREEN   if ac.state == STATE_REROUTING                      else MED_GREEN)
        prefix = "▶ " if ac == active else "  "
        line = font_small.render(
            f"{prefix}{ac.callsign} {ac.state[:4].upper()}", True, col)
        surface.blit(line, (sidebar_x, y_off))
        y_off += 16
        if y_off > panel_y - 10:
            break


# ── Draw the middle flight-info panel ────────────────────────────────────────
def draw_flight_panel(surface: pygame.Surface, fonts,
                      aircraft_list: list, active_idx: int):
    font_med   = fonts["med"]
    font_small = fonts["small"]

    panel_y    = HEIGHT - 160
    pygame.draw.line(surface, MED_GREEN, (0, panel_y), (WIDTH, panel_y), 1)
    pygame.draw.rect(surface, DARK_GREEN, (0, panel_y, WIDTH, 70))

    approaching = [a for a in aircraft_list if a.state == STATE_APPROACHING]
    active      = approaching[active_idx % len(approaching)] if approaching else None

    if active:
        info1 = font_med.render(
            f"FLIGHT: {active.callsign}   ALT: {active.altitude} FT   SPD: {active.speed} KTS",
            True, BRIGHT_GREEN)
        surface.blit(info1, (20, panel_y + 8))

        dist_pct = int((1 - active.dist / RADAR_RADIUS) * 100)
        info2 = font_small.render(
            f"PROXIMITY: {dist_pct}%   BEARING: {int(math.degrees(active.angle)) % 360}°",
            True, UI_GREEN)
        surface.blit(info2, (20, panel_y + 28))

        # [A] Accept
        pygame.draw.rect(surface, (0, 80, 20),  (20, panel_y + 44, 150, 20), border_radius=3)
        pygame.draw.rect(surface, GREEN,          (20, panel_y + 44, 150, 20), 1, border_radius=3)
        a_txt = font_small.render("[A] ACCEPT +10pts", True, BRIGHT_GREEN)
        surface.blit(a_txt, (20 + (150 - a_txt.get_width()) // 2, panel_y + 48))

        # [D] Deny
        pygame.draw.rect(surface, (60, 20, 0),   (180, panel_y + 44, 150, 20), border_radius=3)
        pygame.draw.rect(surface, RED_ALERT,      (180, panel_y + 44, 150, 20), 1, border_radius=3)
        d_txt = font_small.render("[D] DENY +5pts", True, RED_ALERT)
        surface.blit(d_txt, (180 + (150 - d_txt.get_width()) // 2, panel_y + 48))

        # Queue
        queue_lbl = font_small.render(
            f"QUEUE: {len(approaching)}  [TAB] next", True, DIM_GREEN)
        surface.blit(queue_lbl, (360, panel_y + 48))
    else:
        idle = font_med.render("NO INCOMING TRAFFIC — MONITORING...", True, DIM_GREEN)
        surface.blit(idle, (WIDTH // 2 - idle.get_width() // 2, panel_y + 22))


# ── Draw the score footer bar ─────────────────────────────────────────────────
def draw_score_footer(surface: pygame.Surface, fonts, score: ScoreState):
    font_med   = fonts["med"]
    font_small = fonts["small"]
    font_big   = fonts["big"]

    bar_y  = HEIGHT - 90
    bar_h  = 90

    # Background
    pygame.draw.line(surface, GREEN, (0, bar_y), (WIDTH, bar_y), 2)
    pygame.draw.rect(surface, (0, 15, 0), (0, bar_y, WIDTH, bar_h))

    # ── Column layout ──────────────────────────────────────────────────────
    # Col 1: Total points (big)
    col1_x = 20
    pts_label = font_small.render("SCORE", True, DIM_GREEN)
    surface.blit(pts_label, (col1_x, bar_y + 6))
    pts_val = font_big.render(f"{score.points:>6}", True, SCORE_GOLD)
    surface.blit(pts_val, (col1_x, bar_y + 20))

    # Floating delta
    if score.delta_timer > 0 and score.last_delta != 0:
        alpha_frac = min(1.0, score.delta_timer)
        if score.last_delta > 0:
            delta_col = tuple(int(c * alpha_frac) for c in SCORE_GOLD)
            delta_str = f"+{score.last_delta}"
        else:
            delta_col = tuple(int(c * alpha_frac) for c in SCORE_RED)
            delta_str = str(score.last_delta)
        delta_txt = font_med.render(delta_str, True, delta_col)
        # Float upward as timer decays
        float_y = bar_y + 18 - int((2.0 - score.delta_timer) * 12)
        surface.blit(delta_txt, (col1_x + 90, float_y))

    # Separator
    pygame.draw.line(surface, MED_GREEN, (165, bar_y + 8), (165, bar_y + bar_h - 8), 1)

    # ── Col 2: Cleared / Rerouted / Incidents ─────────────────────────────
    col2_x = 180
    surface.blit(font_small.render("CLEARED", True, DIM_GREEN),   (col2_x,      bar_y + 6))
    surface.blit(font_small.render("REROUTED", True, DIM_GREEN),  (col2_x + 90, bar_y + 6))
    surface.blit(font_small.render("INCIDENTS", True, DIM_GREEN), (col2_x + 185,bar_y + 6))

    cl_col  = BRIGHT_GREEN
    re_col  = UI_GREEN
    inc_col = RED_ALERT if score.incidents > 0 else SCORE_DIM

    surface.blit(font_med.render(str(score.cleared),   True, cl_col),  (col2_x,       bar_y + 22))
    surface.blit(font_med.render(str(score.rerouted),  True, re_col),  (col2_x + 90,  bar_y + 22))
    surface.blit(font_med.render(str(score.incidents), True, inc_col), (col2_x + 185, bar_y + 22))

    # Separator
    pygame.draw.line(surface, MED_GREEN, (430, bar_y + 8), (430, bar_y + bar_h - 8), 1)

    # ── Col 3: Accuracy bar ───────────────────────────────────────────────
    col3_x = 445
    acc     = score.accuracy
    acc_col = (BRIGHT_GREEN if acc >= 80 else
               ALERT_GREEN  if acc >= 50 else
               RED_ALERT)

    surface.blit(font_small.render("ACCURACY", True, DIM_GREEN), (col3_x, bar_y + 6))
    surface.blit(font_med.render(f"{acc:5.1f}%", True, acc_col), (col3_x, bar_y + 22))

    # Progress bar
    bar_w    = 150
    bar_fill = int(bar_w * acc / 100)
    pygame.draw.rect(surface, SCORE_DIM,  (col3_x, bar_y + 44, bar_w, 10), border_radius=3)
    if bar_fill > 0:
        pygame.draw.rect(surface, acc_col, (col3_x, bar_y + 44, bar_fill, 10), border_radius=3)
    pygame.draw.rect(surface, MED_GREEN,  (col3_x, bar_y + 44, bar_w, 10), 1, border_radius=3)

    # Separator
    pygame.draw.line(surface, MED_GREEN, (610, bar_y + 8), (610, bar_y + bar_h - 8), 1)

    # ── Col 4: Streak + Time ──────────────────────────────────────────────
    col4_x = 625

    # Streak
    streak_col = SCORE_STREAK if score.streak >= 3 else (
                 UI_GREEN     if score.streak >= 1 else SCORE_DIM)
    surface.blit(font_small.render("STREAK", True, DIM_GREEN), (col4_x, bar_y + 6))
    streak_val = font_med.render(f"×{score.streak}", True, streak_col)
    surface.blit(streak_val, (col4_x, bar_y + 22))

    # Streak milestone progress dots
    dot_y   = bar_y + 44
    dot_gap = 14
    for i in range(STREAK_MILESTONE):
        filled = i < (score.streak % STREAK_MILESTONE) or (
                 score.streak > 0 and score.streak % STREAK_MILESTONE == 0)
        col = SCORE_STREAK if filled else SCORE_DIM
        pygame.draw.circle(surface, col, (col4_x + i * dot_gap + 6, dot_y + 5), 5)
        pygame.draw.circle(surface, MED_GREEN, (col4_x + i * dot_gap + 6, dot_y + 5), 5, 1)

    # Best streak
    best_txt = font_small.render(f"BEST: {score.best_streak}", True, DIM_GREEN)
    surface.blit(best_txt, (col4_x + STREAK_MILESTONE * dot_gap + 10, dot_y))

    # Elapsed time (bottom-right corner)
    time_txt = font_small.render(f"TIME  {score.elapsed_str}", True, DIM_GREEN)
    surface.blit(time_txt, (WIDTH - time_txt.get_width() - 10, bar_y + bar_h - 16))


# ── Flash effect ─────────────────────────────────────────────────────────────
class FlashEffect:
    def __init__(self, x, y, color, label=""):
        self.x, self.y = x, y
        self.color  = color
        self.label  = label
        self.timer  = 1.0
        self.radius = 4

    def update(self, dt):
        self.timer  -= dt * 1.8
        self.radius += dt * 60

    def draw(self, surface, font):
        if self.timer <= 0:
            return
        col = tuple(min(255, int(c * self.timer)) for c in self.color)
        pygame.draw.circle(surface, col, (int(self.x), int(self.y)), int(self.radius), 2)
        if self.label:
            lbl = font.render(self.label, True, col)
            surface.blit(lbl, (int(self.x) - lbl.get_width() // 2,
                                int(self.y) - 30))

    def is_dead(self):
        return self.timer <= 0


# ── Streak bonus burst ────────────────────────────────────────────────────────
class StreakBurst:
    """Full-width banner that briefly flashes when a streak milestone is hit."""
    def __init__(self):
        self.timer   = 0.0
        self.message = ""

    def trigger(self, streak: int):
        self.timer   = 2.2
        self.message = f"★  STREAK ×{streak}!  +{PTS_STREAK} BONUS  ★"

    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt

    def draw(self, surface, font):
        if self.timer <= 0:
            return
        alpha = min(1.0, self.timer)
        col   = tuple(int(c * alpha) for c in SCORE_STREAK)
        txt   = font.render(self.message, True, col)
        x     = WIDTH  // 2 - txt.get_width()  // 2
        y     = HEIGHT // 2 - txt.get_height() // 2
        # Dim backing rect
        backing = pygame.Surface((txt.get_width() + 24, txt.get_height() + 10),
                                  pygame.SRCALPHA)
        backing.fill((0, 0, 0, int(180 * alpha)))
        surface.blit(backing, (x - 12, y - 5))
        surface.blit(txt, (x, y))


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Flight Radar v2 — ATC")
    clock  = pygame.time.Clock()

    fonts = {
        "big":   pygame.font.SysFont("Courier New", 26, bold=True),
        "med":   pygame.font.SysFont("Courier New", 15, bold=True),
        "small": pygame.font.SysFont("Courier New", 11),
    }

    sweep        = RadarSweep()
    aircraft: list[Aircraft]     = []
    effects:  list[FlashEffect]  = []
    score        = ScoreState()
    streak_burst = StreakBurst()

    spawn_timer    = 0.0
    spawn_interval = 5.0
    active_idx     = 0

    aircraft.append(Aircraft())

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False

                elif event.key == pygame.K_TAB:
                    approaching = [a for a in aircraft if a.state == STATE_APPROACHING]
                    if approaching:
                        active_idx = (active_idx + 1) % len(approaching)

                elif event.key in (pygame.K_a, pygame.K_RETURN):
                    approaching = [a for a in aircraft if a.state == STATE_APPROACHING]
                    if approaching:
                        ac  = approaching[active_idx % len(approaching)]
                        ac.accept()
                        got_bonus = score.add_accept()
                        effects.append(FlashEffect(ac.x, ac.y, (100, 255, 120),
                                                   f"CLEARED +{PTS_ACCEPT}"))
                        if got_bonus:
                            streak_burst.trigger(score.streak)

                elif event.key == pygame.K_d:
                    approaching = [a for a in aircraft if a.state == STATE_APPROACHING]
                    if approaching:
                        ac  = approaching[active_idx % len(approaching)]
                        ac.deny()
                        score.add_deny()
                        effects.append(FlashEffect(ac.x, ac.y, (180, 180, 50),
                                                   f"REROUTED +{PTS_DENY}"))

        # ── Spawn ─────────────────────────────────────────────────────────────
        spawn_timer += dt
        if spawn_timer >= spawn_interval:
            spawn_timer = 0.0
            if len([a for a in aircraft if not a.is_dead()]) < 6:
                aircraft.append(Aircraft())
            spawn_interval = max(2.5, spawn_interval - 0.1)

        # ── Update ────────────────────────────────────────────────────────────
        score.update(dt)
        sweep.update(dt)
        streak_burst.update(dt)

        approaching = [a for a in aircraft if a.state == STATE_APPROACHING]
        if approaching:
            active_idx = active_idx % len(approaching)
        else:
            active_idx = 0

        for ac in aircraft:
            was_approaching = (ac.state == STATE_APPROACHING)
            ac.update(dt)
            if was_approaching and ac.state == STATE_GONE:
                score.add_incident()
                effects.append(FlashEffect(RADAR_CX, RADAR_CY, (220, 60, 60), "INCIDENT!"))

        for ef in effects:
            ef.update(dt)

        aircraft = [a for a in aircraft if not a.is_dead()]
        effects  = [e for e in effects  if not e.is_dead()]

        # ── Draw ──────────────────────────────────────────────────────────────
        screen.fill(BLACK)

        # Radar
        pygame.draw.circle(screen, DARK_GREEN, (RADAR_CX, RADAR_CY), RADAR_RADIUS)
        draw_radar_bg(screen, fonts["small"])
        sweep.draw(screen)

        for ac in aircraft:
            ac.draw(screen)

        for ef in effects:
            ef.draw(screen, fonts["med"])

        # HUD layers
        draw_top_bar(screen, fonts, score, aircraft, active_idx)
        draw_flight_panel(screen, fonts, aircraft, active_idx)
        draw_score_footer(screen, fonts, score)

        # Streak burst overlay (on top of everything)
        streak_burst.draw(screen, fonts["big"])

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
