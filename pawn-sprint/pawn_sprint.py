"""
Pawn Sprint — a Pygame pawn-racing game with 16-bit aesthetics.
Player (White) vs AI (Black).  First pawn to reach the opposite back rank wins.
"""

import pygame
import sys
import math
import random
import time

# ─────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────
WINDOW_W, WINDOW_H = 720, 760
BOARD_ORIGIN_X, BOARD_ORIGIN_Y = 60, 60
CELL = 75                          # pixels per square
BOARD_PX = CELL * 8               # 600 px

FPS = 60
ANIM_SPEED = 6                    # pixels moved per frame during animation

# 16-bit palette
COL_BG          = (20,  20,  40)
COL_LIGHT_SQ    = (235, 210, 160)
COL_DARK_SQ     = (140,  90,  50)
COL_HIGHLIGHT   = (100, 200, 100, 160)
COL_CAPTURE     = (220,  60,  60, 160)
COL_PAWN_W      = (240, 240, 240)
COL_PAWN_W_OUT  = ( 80,  80,  80)
COL_PAWN_B      = ( 30,  30,  30)
COL_PAWN_B_OUT  = (160, 160, 160)
COL_PAWN_SHINE  = (255, 255, 255)
COL_LABEL       = (220, 200, 120)
COL_UI_BAR      = ( 30,  30,  60)
COL_TITLE       = (255, 220,  60)
COL_WIN_WHITE   = (240, 240, 200)
COL_WIN_BLACK   = ( 50,  50,  80)
COL_WIN_TEXT    = (255, 220,  60)
COL_BTN         = ( 70,  50, 120)
COL_BTN_HOV     = (120,  80, 200)
COL_BTN_TXT     = (255, 255, 220)
COL_TURN_W      = (200, 230, 255)
COL_TURN_B      = (180, 120, 255)

# Player ids
WHITE = 0
BLACK = 1

AI_THINK_DELAY = 0.5   # seconds the AI "thinks" before moving


# ─────────────────────────────────────────────
#  Utility helpers
# ─────────────────────────────────────────────
def board_to_px(col: int, row: int) -> tuple[int, int]:
    """Return the pixel centre of a board square (col, row)."""
    x = BOARD_ORIGIN_X + col * CELL + CELL // 2
    y = BOARD_ORIGIN_Y + row * CELL + CELL // 2
    return x, y


def px_to_board(px: int, py: int) -> tuple[int, int] | None:
    """Return (col, row) from a pixel click, or None if outside the board."""
    col = (px - BOARD_ORIGIN_X) // CELL
    row = (py - BOARD_ORIGIN_Y) // CELL
    if 0 <= col < 8 and 0 <= row < 8:
        return col, row
    return None


# ─────────────────────────────────────────────
#  Pawn drawing (16-bit style, no images needed)
# ─────────────────────────────────────────────
def draw_pawn(surface: pygame.Surface, cx: int, cy: int, player: int, scale: float = 1.0):
    r = int(CELL * 0.34 * scale)
    body_r = int(CELL * 0.22 * scale)
    base_h = int(CELL * 0.10 * scale)
    neck_h = int(CELL * 0.08 * scale)

    if player == WHITE:
        fill_c = COL_PAWN_W
        out_c  = COL_PAWN_W_OUT
        shine  = (255, 255, 255)
    else:
        fill_c = COL_PAWN_B
        out_c  = COL_PAWN_B_OUT
        shine  = (80,  80, 100)

    # base
    base_rect = pygame.Rect(cx - r, cy + body_r, r * 2, base_h)
    pygame.draw.ellipse(surface, out_c, base_rect.inflate(4, 3))
    pygame.draw.ellipse(surface, fill_c, base_rect)

    # neck
    neck_rect = pygame.Rect(cx - r // 3, cy + body_r - neck_h, (r // 3) * 2, neck_h + 2)
    pygame.draw.rect(surface, out_c, neck_rect.inflate(3, 0))
    pygame.draw.rect(surface, fill_c, neck_rect)

    # head
    head_cy = cy - int(CELL * 0.12 * scale)
    pygame.draw.circle(surface, out_c, (cx, head_cy), r + 2)
    pygame.draw.circle(surface, fill_c, (cx, head_cy), r)

    # shine
    shine_pos = (cx - r // 3, head_cy - r // 3)
    pygame.draw.circle(surface, shine, shine_pos, max(2, r // 4))


# ─────────────────────────────────────────────
#  Board state
# ─────────────────────────────────────────────
class Board:
    """
    board[row][col] = None | (player, pawn_id)
    White pawns start at row 6 (rank 2 from White's perspective).
    Black pawns start at row 1 (rank 7 from White's perspective).
    White moves toward row 0 (Black's back rank).
    Black moves toward row 7 (White's back rank).
    """

    def __init__(self):
        self.grid: list[list] = [[None] * 8 for _ in range(8)]
        self._place_pawns()

    def _place_pawns(self):
        for col in range(8):
            self.grid[6][col] = (WHITE, col)
            self.grid[1][col] = (BLACK, col)

    def get(self, col: int, row: int):
        return self.grid[row][col]

    def set(self, col: int, row: int, value):
        self.grid[row][col] = value

    def move(self, fc: int, fr: int, tc: int, tr: int):
        piece = self.grid[fr][fc]
        self.grid[tr][tc] = piece
        self.grid[fr][fc] = None

    def copy(self) -> "Board":
        import copy
        b = Board.__new__(Board)
        b.grid = [row[:] for row in self.grid]
        return b

    # ── legal move generation ──────────────────
    def legal_moves(self, player: int) -> list[tuple[int, int, int, int]]:
        """Return list of (from_col, from_row, to_col, to_row)."""
        moves = []
        direction = -1 if player == WHITE else 1
        start_row = 6   if player == WHITE else 1
        goal_row  = 0   if player == WHITE else 7

        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece is None or piece[0] != player:
                    continue
                nr = row + direction
                if not (0 <= nr < 8):
                    continue
                # forward
                if self.grid[nr][col] is None:
                    moves.append((col, row, col, nr))
                # diagonal capture
                for dc in (-1, 1):
                    nc = col + dc
                    if 0 <= nc < 8:
                        target = self.grid[nr][nc]
                        if target is not None and target[0] != player:
                            moves.append((col, row, nc, nr))
        return moves

    def check_win(self) -> int | None:
        """Return winning player id or None."""
        # White wins: any white pawn on row 0
        for col in range(8):
            p = self.grid[0][col]
            if p and p[0] == WHITE:
                return WHITE
        # Black wins: any black pawn on row 7
        for col in range(8):
            p = self.grid[7][col]
            if p and p[0] == BLACK:
                return BLACK
        # No legal moves → opponent wins
        for player in (WHITE, BLACK):
            if not self.legal_moves(player):
                return 1 - player
        return None


# ─────────────────────────────────────────────
#  AI  (minimax with alpha-beta, depth 4)
# ─────────────────────────────────────────────
INF = 10_000

def evaluate(board: Board) -> int:
    """Positive = good for BLACK (AI), negative = good for WHITE."""
    score = 0
    for row in range(8):
        for col in range(8):
            p = board.grid[row][col]
            if p is None:
                continue
            player = p[0]
            # advancement: black advances toward row 7, white toward row 0
            if player == BLACK:
                score += row * 2          # closer to row 7 = better
            else:
                score -= (7 - row) * 2   # closer to row 0 = better
    return score


def minimax(board: Board, depth: int, alpha: int, beta: int, maximising: bool) -> int:
    winner = board.check_win()
    if winner == BLACK:
        return INF - (4 - depth)
    if winner == WHITE:
        return -INF + (4 - depth)
    if depth == 0:
        return evaluate(board)

    current = BLACK if maximising else WHITE
    moves = board.legal_moves(current)
    if not moves:
        return evaluate(board)

    if maximising:
        best = -INF
        for mv in moves:
            nb = board.copy()
            nb.move(*mv)
            val = minimax(nb, depth - 1, alpha, beta, False)
            best = max(best, val)
            alpha = max(alpha, val)
            if beta <= alpha:
                break
        return best
    else:
        best = INF
        for mv in moves:
            nb = board.copy()
            nb.move(*mv)
            val = minimax(nb, depth - 1, alpha, beta, True)
            best = min(best, val)
            beta = min(beta, val)
            if beta <= alpha:
                break
        return best


def ai_best_move(board: Board) -> tuple[int, int, int, int] | None:
    moves = board.legal_moves(BLACK)
    if not moves:
        return None
    best_val = -INF
    best_mv  = None
    # slight randomisation among equal moves to avoid robotic play
    random.shuffle(moves)
    for mv in moves:
        nb = board.copy()
        nb.move(*mv)
        val = minimax(nb, 4, -INF, INF, False)
        if val > best_val:
            best_val = val
            best_mv  = mv
    return best_mv


# ─────────────────────────────────────────────
#  Animation helper
# ─────────────────────────────────────────────
class PawnAnim:
    """Smooth linear animation for one pawn."""

    def __init__(self, player: int, start_px: tuple, end_px: tuple):
        self.player   = player
        self.sx, self.sy = start_px
        self.ex, self.ey = end_px
        self.x = float(self.sx)
        self.y = float(self.sy)
        self.done = False
        dist = math.hypot(self.ex - self.sx, self.ey - self.sy)
        self.steps = max(1, int(dist / ANIM_SPEED))
        self.t = 0

    def update(self):
        self.t += 1
        progress = min(self.t / self.steps, 1.0)
        # ease-in-out
        eased = progress * progress * (3 - 2 * progress)
        self.x = self.sx + (self.ex - self.sx) * eased
        self.y = self.sy + (self.ey - self.sy) * eased
        if self.t >= self.steps:
            self.done = True

    def draw(self, surface: pygame.Surface):
        draw_pawn(surface, int(self.x), int(self.y), self.player)


# ─────────────────────────────────────────────
#  Button helper
# ─────────────────────────────────────────────
class Button:
    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font):
        self.rect  = rect
        self.text  = text
        self.font  = font
        self.hover = False

    def draw(self, surface: pygame.Surface):
        colour = COL_BTN_HOV if self.hover else COL_BTN
        pygame.draw.rect(surface, colour, self.rect, border_radius=8)
        pygame.draw.rect(surface, COL_TITLE, self.rect, 2, border_radius=8)
        lbl = self.font.render(self.text, True, COL_BTN_TXT)
        surface.blit(lbl, lbl.get_rect(center=self.rect.center))

    def update(self, mx: int, my: int):
        self.hover = self.rect.collidepoint(mx, my)

    def clicked(self, event: pygame.event.Event) -> bool:
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


# ─────────────────────────────────────────────
#  Game class
# ─────────────────────────────────────────────
class PawnSprint:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pawn Sprint  ♟  16-bit Edition")
        self.screen  = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock   = pygame.time.Clock()

        # fonts — try a retro-ish font, fall back to default
        self.font_big   = pygame.font.SysFont("couriernew", 38, bold=True)
        self.font_med   = pygame.font.SysFont("couriernew", 22, bold=True)
        self.font_small = pygame.font.SysFont("couriernew", 16)

        self._new_game()

    # ── game state reset ───────────────────────
    def _new_game(self):
        self.board        = Board()
        self.turn         = WHITE          # WHITE always goes first
        self.selected     = None           # (col, row) of selected pawn
        self.legal_targets: list[tuple] = []
        self.anim: PawnAnim | None = None
        self.winner       = None
        self.ai_pending   = False
        self.ai_move_time = 0.0            # when to actually execute AI move

        self.btn_restart  = Button(
            pygame.Rect(WINDOW_W // 2 - 100, WINDOW_H - 52, 200, 40),
            "NEW GAME",
            self.font_med,
        )

    # ── helpers ────────────────────────────────
    def _legal_for(self, col: int, row: int) -> list[tuple[int, int, int, int]]:
        all_moves = self.board.legal_moves(self.turn)
        return [m for m in all_moves if m[0] == col and m[1] == row]

    def _apply_move(self, fc: int, fr: int, tc: int, tr: int):
        """Start animation for move; board state updated when anim finishes."""
        self._pending_move = (fc, fr, tc, tr)
        start_px = board_to_px(fc, fr)
        end_px   = board_to_px(tc, tr)
        player   = self.board.get(fc, fr)[0]
        self.anim = PawnAnim(player, start_px, end_px)
        self.selected = None
        self.legal_targets = []

    def _finish_move(self):
        fc, fr, tc, tr = self._pending_move
        self.board.move(fc, fr, tc, tr)
        self.anim = None
        # check win
        w = self.board.check_win()
        if w is not None:
            self.winner = w
            return
        # switch turn
        self.turn = 1 - self.turn
        # if it's now the AI's turn, schedule it
        if self.turn == BLACK:
            self.ai_pending   = True
            self.ai_move_time = time.time() + AI_THINK_DELAY

    # ── event handling ─────────────────────────
    def handle_events(self):
        mx, my = pygame.mouse.get_pos()
        self.btn_restart.update(mx, my)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    self._new_game()
                    return

            if self.btn_restart.clicked(event):
                self._new_game()
                return

            # board click — only when it is the human's turn and no anim running
            if (event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and self.turn == WHITE
                    and self.anim is None
                    and self.winner is None):

                sq = px_to_board(event.pos[0], event.pos[1])
                if sq is None:
                    self.selected = None
                    self.legal_targets = []
                    continue

                col, row = sq

                # clicked on a legal target → execute move
                target_move = next(
                    (m for m in self.legal_targets if m[2] == col and m[3] == row),
                    None
                )
                if target_move:
                    self._apply_move(*target_move)
                    continue

                # clicked on own pawn → select it
                piece = self.board.get(col, row)
                if piece and piece[0] == WHITE:
                    self.selected = (col, row)
                    self.legal_targets = self._legal_for(col, row)
                else:
                    self.selected = None
                    self.legal_targets = []

    # ── update ─────────────────────────────────
    def update(self):
        if self.anim:
            self.anim.update()
            if self.anim.done:
                self._finish_move()
            return

        if self.ai_pending and time.time() >= self.ai_move_time and self.winner is None:
            self.ai_pending = False
            mv = ai_best_move(self.board)
            if mv:
                self._apply_move(*mv)
            else:
                # AI has no moves → White wins
                self.winner = WHITE

    # ── drawing ────────────────────────────────
    def draw(self):
        self.screen.fill(COL_BG)
        self._draw_board()
        self._draw_highlights()
        self._draw_pieces()
        if self.anim:
            self.anim.draw(self.screen)
        self._draw_ui()
        if self.winner is not None:
            self._draw_victory()
        pygame.display.flip()

    def _draw_board(self):
        for row in range(8):
            for col in range(8):
                colour = COL_LIGHT_SQ if (col + row) % 2 == 0 else COL_DARK_SQ
                rect = pygame.Rect(
                    BOARD_ORIGIN_X + col * CELL,
                    BOARD_ORIGIN_Y + row * CELL,
                    CELL, CELL
                )
                pygame.draw.rect(self.screen, colour, rect)

        # border
        board_rect = pygame.Rect(BOARD_ORIGIN_X, BOARD_ORIGIN_Y, BOARD_PX, BOARD_PX)
        pygame.draw.rect(self.screen, COL_LABEL, board_rect, 3)

        # rank & file labels
        files = "abcdefgh"
        for i in range(8):
            # file labels (bottom)
            lbl = self.font_small.render(files[i], True, COL_LABEL)
            self.screen.blit(lbl, (
                BOARD_ORIGIN_X + i * CELL + CELL // 2 - lbl.get_width() // 2,
                BOARD_ORIGIN_Y + BOARD_PX + 4
            ))
            # rank labels (left)
            lbl = self.font_small.render(str(8 - i), True, COL_LABEL)
            self.screen.blit(lbl, (
                BOARD_ORIGIN_X - lbl.get_width() - 5,
                BOARD_ORIGIN_Y + i * CELL + CELL // 2 - lbl.get_height() // 2,
            ))

    def _draw_highlights(self):
        if not self.selected:
            return
        # selected square
        sc, sr = self.selected
        sel_surf = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
        sel_surf.fill((255, 230, 50, 120))
        self.screen.blit(sel_surf, (
            BOARD_ORIGIN_X + sc * CELL,
            BOARD_ORIGIN_Y + sr * CELL
        ))
        # legal targets
        for m in self.legal_targets:
            tc, tr = m[2], m[3]
            is_capture = self.board.get(tc, tr) is not None
            hl_surf = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
            if is_capture:
                hl_surf.fill(COL_CAPTURE)
            else:
                hl_surf.fill(COL_HIGHLIGHT)
            self.screen.blit(hl_surf, (
                BOARD_ORIGIN_X + tc * CELL,
                BOARD_ORIGIN_Y + tr * CELL
            ))

    def _draw_pieces(self):
        anim_start_sq = None
        if self.anim:
            # don't draw the piece at its source square while animating
            fc, fr, tc, tr = self._pending_move
            anim_start_sq = (fc, fr)

        for row in range(8):
            for col in range(8):
                piece = self.board.get(col, row)
                if piece is None:
                    continue
                if anim_start_sq and (col, row) == anim_start_sq:
                    continue
                cx, cy = board_to_px(col, row)
                draw_pawn(self.screen, cx, cy, piece[0])

    def _draw_ui(self):
        # top bar
        pygame.draw.rect(self.screen, COL_UI_BAR, (0, 0, WINDOW_W, 56))
        title = self.font_big.render("PAWN SPRINT", True, COL_TITLE)
        self.screen.blit(title, (WINDOW_W // 2 - title.get_width() // 2, 8))

        # turn indicator
        if self.winner is None:
            if self.turn == WHITE:
                t_colour = COL_TURN_W
                t_text   = "YOUR TURN (White ♙)"
            else:
                t_colour = COL_TURN_B
                t_text   = "AI THINKING...  (Black ♟)"
            turn_lbl = self.font_small.render(t_text, True, t_colour)
            self.screen.blit(turn_lbl, (
                WINDOW_W // 2 - turn_lbl.get_width() // 2,
                WINDOW_H - 30
            ))

        # restart button
        self.btn_restart.draw(self.screen)

        # help text
        help_t = self.font_small.render("R = restart   ESC = quit", True, (120, 120, 160))
        self.screen.blit(help_t, (WINDOW_W - help_t.get_width() - 10, WINDOW_H - 30))

    def _draw_victory(self):
        # semi-transparent overlay
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        panel_w, panel_h = 440, 240
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        if self.winner == WHITE:
            panel.fill((220, 220, 180, 230))
            name_text = "WHITE WINS!"
            sub_text  = "Your pawn crossed the board!"
        else:
            panel.fill((40, 30, 80, 230))
            name_text = "BLACK WINS!"
            sub_text  = "The AI outraced you this time."

        px = WINDOW_W // 2 - panel_w // 2
        py = WINDOW_H // 2 - panel_h // 2
        self.screen.blit(panel, (px, py))

        # pixelated border
        for offset, col in [(4, COL_TITLE), (2, (200, 200, 255))]:
            pygame.draw.rect(self.screen, col,
                             (px - offset, py - offset, panel_w + offset * 2, panel_h + offset * 2),
                             offset, border_radius=6)

        win_lbl = self.font_big.render(name_text, True, COL_WIN_TEXT)
        self.screen.blit(win_lbl, (
            WINDOW_W // 2 - win_lbl.get_width() // 2,
            py + 30
        ))

        sub_lbl = self.font_med.render(sub_text, True, COL_LABEL)
        self.screen.blit(sub_lbl, (
            WINDOW_W // 2 - sub_lbl.get_width() // 2,
            py + 100
        ))

        # pawn icon
        draw_pawn(self.screen,
                  WINDOW_W // 2,
                  py + 165,
                  self.winner, scale=1.5)

        # "press R or click NEW GAME" hint
        hint = self.font_small.render("Press R or click NEW GAME to play again", True, (180, 180, 180))
        self.screen.blit(hint, (
            WINDOW_W // 2 - hint.get_width() // 2,
            py + panel_h - 30
        ))

    # ── main loop ─────────────────────────────
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    PawnSprint().run()
