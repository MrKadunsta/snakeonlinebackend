import pygame
import random
import time
import asyncio  # For pygbag

# Initialize Pygame
pygame.init()

# Set favicon safely
try:
    img = pygame.image.load("favicon.png")
    pygame.display.set_icon(img)
except:
    pass

# Monitor dimensions
monitor_info = pygame.display.Info()
monitor_width = monitor_info.current_w
monitor_height = monitor_info.current_h

# Variables
activate_game_over = True
score = 0
initial_pixel_size = 40
tx = []
ty = []
a = 0
b = 0
x = 0
y = 0
sprite_rect = None
play_button_hitbox = pygame.Rect(0, 0, 0, 0)

# Window
screen = pygame.display.set_mode((17 * initial_pixel_size, 16 * initial_pixel_size))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

pixel_size = initial_pixel_size
win_width = 17 * pixel_size
win_height = 16 * pixel_size
win = pygame.Surface((win_width, win_height))
win_position = win.get_rect(center=screen.get_rect().center)

# Margin bar
class Ma(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((17 * pixel_size, pixel_size))
        self.surf.fill((0, 0, 0))

# Snake segment
class Ta(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((pixel_size, pixel_size))
        self.surf.fill((0, 255, 0))

# Apple
class Ap(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((pixel_size, pixel_size))
        self.surf.fill((255, 0, 0))

# Assets
def rebuild_assets():
    global background, black_background, font, font_small, game_over, game_over_location, m1, t, a1

    background = pygame.Surface((win_width, win_height))
    for row in range(win_height // pixel_size):
        for col in range(win_width // pixel_size):
            color = (0, 0, 0) if (row + col) % 2 == 0 else (30, 30, 30)
            pygame.draw.rect(background, color, (col * pixel_size, row * pixel_size, pixel_size, pixel_size))

    black_background = pygame.Surface((win_width, win_height))
    black_background.fill((0, 0, 0))

    # Use Font(None) for pygbag compatibility
    font = pygame.font.Font(None, pixel_size + pixel_size // 5)
    font_small = pygame.font.Font(None, pixel_size - pixel_size // 5)

    game_over = font.render("GAME OVER", True, (255, 0, 0))
    game_over_location = game_over.get_rect(center=(win_width // 2, win_height // 2))

    m1 = Ma()
    t = Ta()
    a1 = Ap()

# Canvas setup
def set_canvas():
    global pixel_size, win_width, win_height, win, win_position
    pixel_size = initial_pixel_size
    win_width = pixel_size * 17
    win_height = pixel_size * 16
    win = pygame.Surface((win_width, win_height))
    win_position = win.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    rebuild_assets()

set_canvas()

# Snake setup
def snake_setup():
    global sprite_image, sprite_rect, speed, snake_length, tx, ty, ghost_tail_x, ghost_tail_y
    sprite_image = pygame.Surface((pixel_size, pixel_size))
    sprite_image.fill((0, 255, 0))
    sprite_rect = sprite_image.get_rect(center=(win_width // 2, win_height // 2))
    speed = 250
    snake_length = 3
    tx, ty = [8, 7, 6], [7, 7, 7]
    ghost_tail_x, ghost_tail_y = 6, 7

def apple():
    global a, x, b, y
    while True:
        a = random.randint(0, 16)
        b = random.randint(0, 14)
        if not any(tx[i] == a and ty[i] == b for i in range(len(tx))):
            x = a * pixel_size
            y = b * pixel_size
            break

def set_default_movement():
    global next_dx, next_dy, last_dx, last_dy, move_timer, MOVE_DELAY, moving, dx, dy
    dx, dy = 1, 0
    next_dx, next_dy = dx, dy
    last_dx, last_dy = dx, dy
    move_timer = 0
    MOVE_DELAY = speed
    moving = 1

def move():
    global sprite_rect, tx, ty, ghost_tail_x, ghost_tail_y
    sprite_rect.x += pixel_size * dx
    sprite_rect.y += pixel_size * dy
    hx, hy = sprite_rect.x // pixel_size, sprite_rect.y // pixel_size
    tx.insert(0, hx)
    ty.insert(0, hy)
    if len(tx) > snake_length:
        ghost_tail_x = tx[-1]
        tx.pop(snake_length)
    if len(ty) > snake_length:
        ghost_tail_y = ty[-1]
        ty.pop(snake_length)

def draw_snake():
    for i in range(snake_length):
        win.blit(t.surf, (tx[i] * pixel_size, ty[i] * pixel_size))

def draw_play_button(hovering):
    global play_button_hitbox, play_button_rect
    width = 9 * pixel_size
    height = 3 * pixel_size
    color_val = 225 if hovering else 255
    play_button_rect = pygame.Rect(4 * pixel_size, 10 * pixel_size, width, height)
    play_button_hitbox = pygame.Rect(play_button_rect.x + win_position.x,
                                     play_button_rect.y + win_position.y,
                                     width, height)
    # Draw button rectangle behind text
    pygame.draw.rect(win, (50, 50, 50) if hovering else (color_val, color_val, color_val),
                     play_button_rect, 0 if hovering else pixel_size // 10)
    pygame.draw.rect(win, (255, 255, 255), play_button_rect, pixel_size // 10)
    # Draw "Play" text on top
    play_button_text = font.render("Play", True, (color_val, color_val, color_val))
    text_pos = play_button_text.get_rect(center=(width // 2 + 4 * pixel_size,
                                                 height // 2 + 10 * pixel_size))
    win.blit(play_button_text, text_pos)

def draw_start_menu():
    start_menu_text = font.render("SNAKE", True, (0, 255, 0))
    text_pos = start_menu_text.get_rect(center=(win_width // 2, win_height // 2))
    win.blit(black_background, (0, 0))
    pygame.draw.rect(win, (0, 255, 0), (6 * pixel_size, 5 * pixel_size, 3 * pixel_size, pixel_size))
    pygame.draw.rect(win, (255, 0, 0), (10 * pixel_size, 5 * pixel_size, pixel_size, pixel_size))
    win.blit(start_menu_text, text_pos)

# ------------------------
# Async game loop for pygbag
# ------------------------
async def game():
    global score, MOVE_DELAY, dx, dy, move_timer, moving, next_dx, next_dy, last_dx, last_dy
    global snake_length, tx, ty, ghost_tail_x, ghost_tail_y, score_counter, score_pos

    start_timer = time.perf_counter()
    snake_setup()
    apple()
    set_default_movement()
    score = 0
    running = True

    while running:
        current_time = time.perf_counter() - start_timer
        dt = clock.tick(60)
        move_timer += dt
        await asyncio.sleep(0)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    next_dx, next_dy = -1, 0
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    next_dx, next_dy = 1, 0
                elif event.key in (pygame.K_UP, pygame.K_w):
                    next_dx, next_dy = 0, -1
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    next_dx, next_dy = 0, 1
                elif event.key in (pygame.K_p, pygame.K_ESCAPE):
                    moving = abs(moving - 1)

        # Movement
        if move_timer >= MOVE_DELAY and moving:
            if (next_dx, next_dy) != (-last_dx, -last_dy):
                dx, dy = next_dx, next_dy
            move()
            move_timer = 0
            last_dx, last_dy = dx, dy

        # Collision
        if tx[0] in (-1, 17) or ty[0] in (-1, 15):
            running = False
        elif any(tx[0] == tx[i] and ty[0] == ty[i] for i in range(4, snake_length)):
            running = False

        # Apple collision
        if tx[0] == a and ty[0] == b:
            snake_length += 1
            MOVE_DELAY = max(50, MOVE_DELAY - 0.5)
            tx.append(ghost_tail_x)
            ty.append(ghost_tail_y)
            apple()
            score += 1

        # Draw everything
        win.blit(background, (0, 0))
        win.blit(a1.surf, (x, y))
        draw_snake()
        win.blit(m1.surf, (0, 15 * pixel_size))
        timer = font_small.render(f"Time: {current_time:.0f}", True, (255, 255, 255))
        timer_pos = timer.get_rect(bottomright=(win_width - pixel_size, win_height))
        score_counter = font_small.render(f"Score: {score}", True, (255, 255, 255))
        win.blit(timer, timer_pos)
        win.blit(score_counter, (0, 15 * pixel_size))
        screen.blit(win, win_position)
        pygame.display.flip()

    # Game over screen
    if activate_game_over:
        elapsed_time = time.perf_counter() - start_timer
        game_over_loop = True
        while game_over_loop:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            hovering = (play_button_hitbox.left <= mouse_x <= play_button_hitbox.right and
                        play_button_hitbox.top <= mouse_y <= play_button_hitbox.bottom)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN and hovering:
                    await game()
                    return

            win.blit(black_background, (0, 0))
            win.blit(game_over, game_over_location)
            timer = font_small.render(f"Time: {elapsed_time:.0f}", True, (255, 255, 255))
            timer_pos = timer.get_rect(center=(win_width // 2, win_height // 2 - 3 * pixel_size))
            score_counter = font_small.render(f"Score: {score}", True, (255, 255, 255))
            score_pos = score_counter.get_rect(center=(win_width // 2, win_height // 2 - 1.5 * pixel_size))
            win.blit(timer, timer_pos)
            win.blit(score_counter, score_pos)
            draw_play_button(hovering)
            screen.blit(win, win_position)
            pygame.display.flip()
            await asyncio.sleep(0)

# ------------------------
# Main menu loop
# ------------------------
async def main():
    running = True
    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hovering = (play_button_hitbox.left <= mouse_x <= play_button_hitbox.right and
                    play_button_hitbox.top <= mouse_y <= play_button_hitbox.bottom)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and hovering:
                await game()
                running = False

        draw_start_menu()
        draw_play_button(hovering)
        screen.blit(win, win_position)
        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()

# Run
asyncio.run(main())