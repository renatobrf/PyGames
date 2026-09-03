import pygame
import random
import sys

# -----------------------------
# Configuration
# -----------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60
TITLE = "My Little Cat - Escape the House!"

# 16-bit Color Palette
BG_COLOR = (20, 12, 28)  # Dark purple background
FLOOR_COLOR = (101, 67, 33)  # Brown wood floor
WALL_COLOR = (139, 90, 43)  # Lighter brown walls
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 177, 76)
RED = (237, 28, 36)
YELLOW = (255, 242, 0)
BLUE = (63, 72, 204)
ORANGE = (255, 127, 39)
PINK = (255, 174, 201)
GRAY = (127, 127, 127)
DARK_GRAY = (64, 64, 64)
LIGHT_BLUE = (153, 217, 234)
PURPLE = (163, 73, 164)

# Game Settings
GRAVITY = 0.8
JUMP_STRENGTH = -15
PLAYER_SPEED = 5
PLAYER_SIZE = 30
LIVES = 3

# -----------------------------
# Initialize Pygame
# -----------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Fonts
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)
font_tiny = pygame.font.Font(None, 24)

# -----------------------------
# Player Class
# -----------------------------
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.lives = LIVES
        self.invincible = 0
        
    def update(self, platforms):
        # Apply gravity
        self.vel_y += GRAVITY
        
        # Horizontal movement
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True
            
        # Jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Check boundaries
        if self.x < 0:
            self.x = 0
        if self.x > WIDTH - self.width:
            self.x = WIDTH - self.width
            
        # Platform collision
        self.on_ground = False
        for platform in platforms:
            if self.check_collision(platform):
                # Landing on top
                if self.vel_y > 0 and self.y + self.height - self.vel_y <= platform.y:
                    self.y = platform.y - self.height
                    self.vel_y = 0
                    self.on_ground = True
                # Hitting from below
                elif self.vel_y < 0 and self.y - self.vel_y >= platform.y + platform.height:
                    self.y = platform.y + platform.height
                    self.vel_y = 0
                # Side collision
                else:
                    if self.vel_x > 0:
                        self.x = platform.x - self.width
                    elif self.vel_x < 0:
                        self.x = platform.x + platform.width
        
        # Floor collision
        if self.y >= HEIGHT - 50 - self.height:
            self.y = HEIGHT - 50 - self.height
            self.vel_y = 0
            self.on_ground = True
            
        # Update invincibility
        if self.invincible > 0:
            self.invincible -= 1
    
    def check_collision(self, obj):
        return (self.x < obj.x + obj.width and
                self.x + self.width > obj.x and
                self.y < obj.y + obj.height and
                self.y + self.height > obj.y)
    
    def take_damage(self):
        if self.invincible == 0:
            self.lives -= 1
            self.invincible = 120  # 2 seconds of invincibility
            return True
        return False
    
    def draw(self, screen):
        # Draw cat body (simple rectangle with ears)
        if self.invincible % 10 < 5 or self.invincible == 0:
            # Body
            pygame.draw.rect(screen, ORANGE, (self.x, self.y, self.width, self.height))
            # Ears
            ear_size = 8
            pygame.draw.polygon(screen, ORANGE, [
                (self.x + 5, self.y),
                (self.x + 5, self.y - ear_size),
                (self.x + 12, self.y)
            ])
            pygame.draw.polygon(screen, ORANGE, [
                (self.x + self.width - 5, self.y),
                (self.x + self.width - 5, self.y - ear_size),
                (self.x + self.width - 12, self.y)
            ])
            # Eyes
            eye_y = self.y + 10
            if self.facing_right:
                pygame.draw.circle(screen, BLACK, (int(self.x + 18), eye_y), 3)
                pygame.draw.circle(screen, BLACK, (int(self.x + 25), eye_y), 3)
            else:
                pygame.draw.circle(screen, BLACK, (int(self.x + 5), eye_y), 3)
                pygame.draw.circle(screen, BLACK, (int(self.x + 12), eye_y), 3)
            # Tail
            tail_x = self.x if self.facing_right else self.x + self.width
            pygame.draw.line(screen, ORANGE, (tail_x, self.y + self.height - 5),
                           (tail_x + (-15 if self.facing_right else 15), self.y + self.height - 15), 4)

# -----------------------------
# Platform Class
# -----------------------------
class Platform:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)

# -----------------------------
# Obstacle Class
# -----------------------------
class Obstacle:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)

# -----------------------------
# Collectible Class
# -----------------------------
class Collectible:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.collected = False
    
    def draw(self, screen):
        if not self.collected:
            # Draw a fish treat
            pygame.draw.ellipse(screen, LIGHT_BLUE, (self.x, self.y, self.width, self.height))
            pygame.draw.circle(screen, BLACK, (int(self.x + 6), int(self.y + 10)), 2)
            pygame.draw.polygon(screen, LIGHT_BLUE, [
                (self.x + self.width, self.y + 10),
                (self.x + self.width + 8, self.y + 5),
                (self.x + self.width + 8, self.y + 15)
            ])

# -----------------------------
# Exit Door Class
# -----------------------------
class ExitDoor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 80
    
    def draw(self, screen):
        pygame.draw.rect(screen, (101, 67, 33), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 3)
        pygame.draw.circle(screen, YELLOW, (int(self.x + 40), int(self.y + 40)), 5)

# -----------------------------
# Level Data
# -----------------------------
def create_level_1():
    """Living Room"""
    platforms = [
        Platform(100, 450, 150, 20, (139, 90, 43)),  # Coffee table
        Platform(350, 380, 120, 20, (101, 67, 33)),  # Sofa
        Platform(550, 320, 100, 20, (64, 64, 64)),   # TV stand
        Platform(200, 250, 80, 20, (139, 90, 43)),   # Shelf
    ]
    obstacles = [
        Obstacle(130, 420, 30, 30, RED),  # Vase on coffee table
        Obstacle(400, 350, 25, 30, PURPLE),  # Book on sofa
    ]
    collectibles = [
        Collectible(120, 420),
        Collectible(380, 350),
        Collectible(570, 290),
    ]
    exit_door = ExitDoor(700, HEIGHT - 50 - 80)
    return platforms, obstacles, collectibles, exit_door, "Living Room"

def create_level_2():
    """Kitchen"""
    platforms = [
        Platform(50, 400, 120, 20, GRAY),      # Counter
        Platform(250, 350, 100, 20, GRAY),     # Island
        Platform(450, 300, 130, 20, GRAY),     # Upper counter
        Platform(650, 250, 100, 20, (101, 67, 33)),  # Cabinet
    ]
    obstacles = [
        Obstacle(80, 370, 25, 30, RED),   # Knife block
        Obstacle(280, 320, 30, 30, BLUE), # Pot
        Obstacle(480, 270, 25, 30, GREEN), # Plant
    ]
    collectibles = [
        Collectible(100, 370),
        Collectible(300, 320),
        Collectible(500, 270),
        Collectible(680, 220),
    ]
    exit_door = ExitDoor(730, HEIGHT - 50 - 80)
    return platforms, obstacles, collectibles, exit_door, "Kitchen"

def create_level_3():
    """Bedroom"""
    platforms = [
        Platform(80, 420, 200, 20, PURPLE),    # Bed
        Platform(350, 350, 100, 20, (139, 90, 43)),  # Dresser
        Platform(520, 280, 90, 20, (101, 67, 33)),   # Nightstand
        Platform(200, 200, 120, 20, GRAY),     # Wardrobe top
    ]
    obstacles = [
        Obstacle(150, 390, 30, 30, PINK),  # Pillow
        Obstacle(380, 320, 25, 30, RED),   # Lamp
        Obstacle(540, 250, 30, 30, BLUE),  # Clock
    ]
    collectibles = [
        Collectible(150, 390),
        Collectible(390, 320),
        Collectible(550, 250),
        Collectible(240, 170),
    ]
    exit_door = ExitDoor(700, HEIGHT - 50 - 80)
    return platforms, obstacles, collectibles, exit_door, "Bedroom"

# -----------------------------
# Game States
# -----------------------------
def draw_start_screen(screen):
    screen.fill(BG_COLOR)
    
    # Title
    title = font_large.render("MY LITTLE CAT", True, ORANGE)
    title_rect = title.get_rect(center=(WIDTH // 2, 150))
    screen.blit(title, title_rect)
    
    # Subtitle
    subtitle = font_medium.render("Escape the House!", True, WHITE)
    subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 220))
    screen.blit(subtitle, subtitle_rect)
    
    # Instructions
    instructions = [
        "Use ARROW KEYS or WASD to move",
        "SPACE or UP to jump",
        "Avoid obstacles (red items)",
        "Collect treats (fish)",
        "Reach the door to escape!",
        "",
        "Press SPACE to Start"
    ]
    
    y_offset = 300
    for line in instructions:
        text = font_tiny.render(line, True, WHITE if line != "Press SPACE to Start" else YELLOW)
        text_rect = text.get_rect(center=(WIDTH // 2, y_offset))
        screen.blit(text, text_rect)
        y_offset += 30
    
    # Draw a cute cat
    cat_x, cat_y = WIDTH // 2 - 20, 240
    pygame.draw.rect(screen, ORANGE, (cat_x, cat_y, 40, 40))
    pygame.draw.polygon(screen, ORANGE, [(cat_x + 8, cat_y), (cat_x + 8, cat_y - 10), (cat_x + 15, cat_y)])
    pygame.draw.polygon(screen, ORANGE, [(cat_x + 32, cat_y), (cat_x + 32, cat_y - 10), (cat_x + 25, cat_y)])
    pygame.draw.circle(screen, BLACK, (cat_x + 15, cat_y + 15), 3)
    pygame.draw.circle(screen, BLACK, (cat_x + 25, cat_y + 15), 3)

def draw_game_over_screen(screen, won, score, level_reached):
    screen.fill(BG_COLOR)
    
    if won:
        title = font_large.render("YOU WON!", True, GREEN)
        message = font_medium.render("The cat escaped!", True, WHITE)
    else:
        title = font_large.render("GAME OVER", True, RED)
        message = font_medium.render("The cat got caught!", True, WHITE)
    
    title_rect = title.get_rect(center=(WIDTH // 2, 150))
    screen.blit(title, title_rect)
    
    message_rect = message.get_rect(center=(WIDTH // 2, 230))
    screen.blit(message, message_rect)
    
    # Stats
    score_text = font_small.render(f"Score: {score}", True, YELLOW)
    score_rect = score_text.get_rect(center=(WIDTH // 2, 300))
    screen.blit(score_text, score_rect)
    
    level_text = font_small.render(f"Level Reached: {level_reached}", True, WHITE)
    level_rect = level_text.get_rect(center=(WIDTH // 2, 350))
    screen.blit(level_text, level_rect)
    
    # Restart instruction
    restart = font_medium.render("Press SPACE to Restart", True, YELLOW)
    restart_rect = restart.get_rect(center=(WIDTH // 2, 450))
    screen.blit(restart, restart_rect)
    
    quit_text = font_tiny.render("Press ESC to Quit", True, GRAY)
    quit_rect = quit_text.get_rect(center=(WIDTH // 2, 520))
    screen.blit(quit_text, quit_rect)

def draw_hud(screen, lives, score, level_name):
    # Lives
    lives_text = font_small.render(f"Lives: {lives}", True, RED)
    screen.blit(lives_text, (10, 10))
    
    # Score
    score_text = font_small.render(f"Score: {score}", True, YELLOW)
    screen.blit(score_text, (WIDTH - 150, 10))
    
    # Level name
    level_text = font_tiny.render(level_name, True, WHITE)
    screen.blit(level_text, (WIDTH // 2 - 50, 10))

# -----------------------------
# Main Game Loop
# -----------------------------
def main():
    game_state = "start"  # start, playing, game_over
    current_level = 1
    score = 0
    won = False
    
    # Initialize level
    platforms, obstacles, collectibles, exit_door, level_name = create_level_1()
    player = Player(50, HEIGHT - 50 - PLAYER_SIZE)
    
    running = True
    while running:
        clock.tick(FPS)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                if game_state == "start":
                    if event.key == pygame.K_SPACE:
                        game_state = "playing"
                        current_level = 1
                        score = 0
                        platforms, obstacles, collectibles, exit_door, level_name = create_level_1()
                        player = Player(50, HEIGHT - 50 - PLAYER_SIZE)
                
                elif game_state == "game_over":
                    if event.key == pygame.K_SPACE:
                        game_state = "start"
        
        # Game logic
        if game_state == "playing":
            player.update(platforms)
            
            # Check obstacle collision
            for obstacle in obstacles:
                if player.check_collision(obstacle):
                    if player.take_damage():
                        player.x = 50
                        player.y = HEIGHT - 50 - PLAYER_SIZE
                        player.vel_x = 0
                        player.vel_y = 0
            
            # Check collectible collision
            for collectible in collectibles:
                if not collectible.collected and player.check_collision(collectible):
                    collectible.collected = True
                    score += 100
            
            # Check exit door collision
            if player.check_collision(exit_door):
                if current_level < 3:
                    current_level += 1
                    score += 500
                    if current_level == 2:
                        platforms, obstacles, collectibles, exit_door, level_name = create_level_2()
                    elif current_level == 3:
                        platforms, obstacles, collectibles, exit_door, level_name = create_level_3()
                    player = Player(50, HEIGHT - 50 - PLAYER_SIZE)
                else:
                    won = True
                    score += 1000
                    game_state = "game_over"
            
            # Check if player died
            if player.lives <= 0:
                won = False
                game_state = "game_over"
            
            # Fall off screen
            if player.y > HEIGHT:
                player.take_damage()
                player.x = 50
                player.y = HEIGHT - 50 - PLAYER_SIZE
                player.vel_x = 0
                player.vel_y = 0
        
        # Drawing
        if game_state == "start":
            draw_start_screen(screen)
        
        elif game_state == "playing":
            screen.fill(BG_COLOR)
            
            # Draw floor
            pygame.draw.rect(screen, FLOOR_COLOR, (0, HEIGHT - 50, WIDTH, 50))
            
            # Draw game objects
            for platform in platforms:
                platform.draw(screen)
            for obstacle in obstacles:
                obstacle.draw(screen)
            for collectible in collectibles:
                collectible.draw(screen)
            exit_door.draw(screen)
            player.draw(screen)
            
            # Draw HUD
            draw_hud(screen, player.lives, score, level_name)
        
        elif game_state == "game_over":
            draw_game_over_screen(screen, won, score, current_level)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

# Made with Bob
