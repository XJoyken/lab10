import pygame
import random
import json
from database import create_tables, get_or_create_user, save_game_state

pygame.init()
clock = pygame.time.Clock()
WIDTH, HEIGHT = 700, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))

DARK_GREEN = (0, 111, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

font = pygame.font.SysFont("Verdana", 20)
font_large = pygame.font.SysFont("Verdana", 50)
font_medium = pygame.font.SysFont("Verdana", 30)

def get_level_settings(level):
    if level == 1:
        return {'fps': 5, 'walls': []}
    elif level == 2:
        return {
            'fps': 7,
            'walls': [
                (0, 0, 10, HEIGHT), (WIDTH-10, 0, 10, HEIGHT),
                (0, 0, WIDTH, 10), (0, HEIGHT-10, WIDTH, 10)
            ]
        }
    else:
        return {
            'fps': 9,
            'walls': [
                (0, 0, 10, HEIGHT), (WIDTH-10, 0, 10, HEIGHT),
                (0, 0, WIDTH, 10), (0, HEIGHT-10, WIDTH, 10),
                (WIDTH//2-10, HEIGHT//4, 20, HEIGHT//2)
            ]
        }

def game_over(score, level):
    game_over_text = font_large.render("GAME OVER", True, BLACK)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
    end1_text = font_medium.render("Your score is: " + str(score), True, BLACK)
    end2_text = font_medium.render("Your level is: " + str(level), True, BLACK)
    screen.blit(end1_text, (WIDTH // 2 - end1_text.get_width() // 2, HEIGHT // 2 + game_over_text.get_height() // 2 + 20))
    screen.blit(end2_text,
                (WIDTH // 2 - end2_text.get_width() // 2, HEIGHT // 2 + game_over_text.get_height() // 2 + end1_text.get_height() + 40))
    pygame.display.update()
    pygame.time.delay(5000)
    
def win(screen):
    screen.fill((255, 255, 255))
    win_text = font_large.render("YOU WON!!!", True, BLACK)
    screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - win_text.get_height() // 2))
    pygame.display.update()
    pygame.time.delay(5000)
    pygame.quit()

def get_username():
    username = ""
    input_active = True
    while input_active:
        screen.fill(WHITE)
        prompt_text = font_medium.render("Enter your username:", True, BLACK)
        username_text = font_medium.render(username, True, BLACK)
        screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(username_text, (WIDTH // 2 - username_text.get_width() // 2, HEIGHT // 2 + 20))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif len(username) < 20 and event.unicode.isalnum():
                    username += event.unicode
    return username

create_tables()
username = get_username()
user_id, saved_data = get_or_create_user(username)

snake = [[20, 20], [30, 20], [40, 20]]
fruit = []
dir = "right"
new_dir = "right"
score = 0
level = 1

if saved_data:
    try:
        level, score, snake_length = saved_data
        print(f"Loaded level: {level}, score: {score}, snake length: {snake_length}")
        while len(snake) < snake_length:
            snake.insert(0, snake[0][:])
    except ValueError as e:
        print(f"Error unpacking saved_data: {saved_data}, starting with defaults. Error: {e}")
        level, score = 1, 0
else:
    level, score = 1, 0
    print("No saved data, starting with level 1, score 0")

FPS = get_level_settings(level)['fps']
head = snake[-1]
fruit_eaten = False
initial_moves = -(len(snake))
running = True
TIMER_START = 10
time_left = TIMER_START
last_tick = pygame.time.get_ticks()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                new_dir = "down"
            if event.key == pygame.K_UP:
                new_dir = "up"
            if event.key == pygame.K_RIGHT:
                new_dir = "right"
            if event.key == pygame.K_LEFT:
                new_dir = "left"
            if event.key == pygame.K_p:
                save_game_state(user_id, level, score, snake, fruit, dir)
                pause_text = font_large.render("PAUSED", True, BLACK)
                screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))
                pygame.display.update()
                while True:
                    for pause_event in pygame.event.get():
                        if pause_event.type == pygame.KEYDOWN and pause_event.key == pygame.K_p:
                            last_tick = pygame.time.get_ticks()
                            screen.fill(WHITE)
                            pygame.display.update()
                            break
                    else:
                        continue
                    break

    if new_dir == "right" and dir != "left":
        dir = "right"
    if new_dir == "left" and dir != "right":
        dir = "left"
    if new_dir == "up" and dir != "down":
        dir = "up"
    if new_dir == "down" and dir != "up":
        dir = "down"

    if time_left <= 0:
        fruit.clear()
        time_left = TIMER_START
        last_tick = pygame.time.get_ticks()

    if time_left > 0 and len(fruit) == 0:
        while len(fruit) == 0:
            fruit_x = random.randint(0, WIDTH // 10 - 10) * 10
            fruit_y = random.randint(0, HEIGHT // 10 - 10) * 10
            fruit.append(fruit_x)
            fruit.append(fruit_y)
            fruit_rect = pygame.Rect(fruit[0], fruit[1], 10, 10)
            check_collision = True
            for body in snake:
                body_rect = pygame.Rect(body[0], body[1], 10, 10)
                if fruit_rect.colliderect(body_rect):
                    check_collision = False
                    break
            walls = get_level_settings(level)['walls']
            for wall in walls:
                wall_rect = pygame.Rect(wall[0], wall[1], wall[2], wall[3])
                if fruit_rect.colliderect(wall_rect):
                    check_collision = False
                    break
            if check_collision:
                fruit_eaten = False
                break
            fruit.clear()

    screen.fill(WHITE)

    walls = get_level_settings(level)['walls']
    for wall in walls:
        pygame.draw.rect(screen, BLACK, wall)

    if not fruit_eaten and time_left >= 0 and len(fruit) > 0:
        pygame.draw.circle(screen, RED, (fruit[0] + 5, fruit[1] + 5), 5)

    end = snake[-1]
    for body in snake:
        if body[0] == end[0] and body[1] == end[1]:
            pygame.draw.rect(screen, DARK_GREEN, pygame.Rect(body[0], body[1], 10, 10))
        else:
            pygame.draw.rect(screen, GREEN, pygame.Rect(body[0], body[1], 10, 10))

    current_time = pygame.time.get_ticks()
    if current_time - last_tick >= 1000:
        time_left -= 1
        last_tick = current_time

    timer_text = font.render(f"Time: {time_left}", True, BLACK)
    screen.blit(timer_text, (10, 10))

    score_text = font.render("Score: " + str(score), True, BLACK)
    level_text = font.render("Level: " + str(level), True, BLACK)
    screen.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))
    screen.blit(level_text, (WIDTH - level_text.get_width() - 10, score_text.get_height() + 10))

    if dir == "down":
        head[1] += 10
    if dir == "up":
        head[1] -= 10
    if dir == "right":
        head[0] += 10
    if dir == "left":
        head[0] -= 10

    new_head = [head[0], head[1]]
    snake.append(new_head)
    snake.pop(0)
    new_head_rect = pygame.Rect(new_head[0], new_head[1], 10, 10)

    if len(fruit) > 0 and new_head_rect.colliderect(fruit_rect):
        fruit_eaten = True
        fruit.clear()
        time_left = TIMER_START
        last_tick = pygame.time.get_ticks()
        score += 1
        snake.insert(0, snake[0][:])
        if score % 50 == 0 and level != 3:
            level = min(level + 1, 3)
            FPS = get_level_settings(level)['fps']
            snake = [[20, 20], [30, 20], [40, 20]]
            initial_moves = -1
            score = 0
            head = snake[-1]
            dir = "right"
            new_dir = "right"
    if score > 0 and score % 50 == 0 and level == 3:
            win(screen)    
            

    head_check = snake[-1]
    if head_check[0] < 0 or head_check[0] >= WIDTH or head_check[1] < 0 or head_check[1] >= HEIGHT:
        running = False

    for wall in walls:
        wall_rect = pygame.Rect(wall[0], wall[1], wall[2], wall[3])
        if new_head_rect.colliderect(wall_rect):
            running = False
            break

    if initial_moves >= 2:
        for body in snake[:-1]:
            if body[0] == head_check[0] and body[1] == head_check[1]:
                running = False
    else:
        initial_moves += 1

    pygame.display.flip()
    clock.tick(FPS)

    if not running:
        save_game_state(user_id, level, score, snake, fruit, dir)
        game_over(score, level)

pygame.quit()