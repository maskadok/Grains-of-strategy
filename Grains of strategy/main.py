import pygame
from copy import deepcopy
from random import choice, randrange

W, H = 10, 20
BLOCK_SIZE = 35
GAME_AREA = W * BLOCK_SIZE, H * BLOCK_SIZE
WINDOW = 750, 750

pygame.init()
sc = pygame.display.set_mode(WINDOW)
game_sc = pygame.Surface(GAME_AREA)
clock = pygame.time.Clock()

grid_layout = [pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE) for x in range(W) for y in range(H)]

figures = [
    [(-1, 0), (-2, 0), (0, 0), (1, 0)],
    [(0, -1), (-1, -1), (-1, 0), (0, 0)],
    [(-1, 0), (-1, 1), (0, 0), (0, -1)],
    [(0, 0), (-1, 0), (0, 1), (-1, -1)],
    [(0, 0), (0, -1), (0, 1), (-1, -1)],
    [(0, 0), (0, -1), (0, 1), (1, -1)],
    [(0, 0), (0, -1), (0, 1), (-1, 0)]
]

figures = [[pygame.Rect(x + W // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in figures]
figure_rect = pygame.Rect(0, 0, BLOCK_SIZE - 2, BLOCK_SIZE - 2)
game_board = [[None for i in range(W)] for j in range(H)]

anim_count, anim_speed, anim_limit = 0, 60, 2000
background_image = pygame.image.load('img/bg.jpg').convert()
game_background = pygame.image.load('img/bg2.jpg').convert()
main_font = pygame.font.Font('font/font.ttf', 55)
font = pygame.font.Font('font/font.ttf', 45)
main_title = main_font.render('Grains', True, pygame.Color('white'))
title = main_font.render('of Strategy', True, pygame.Color('white'))
title_score = font.render('score:', True, pygame.Color('green'))

def get_color():
    return choice([(255, 0, 0), (0, 255, 0), (0, 0, 255)])

figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))
color, next_color = get_color(), get_color()

score, lines = 0, 0
scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}

def check_borders():
    if figure[i].x < 0 or figure[i].x > W - 1:
        return False
    elif figure[i].y > H - 1 or game_board[figure[i].y][figure[i].x]:
        return False
    return True

def fall_down():
    for y in range(H-2, -1, -1):
        for x in range(W):
            if game_board[y][x] and not game_board[y+1][x]:
                drop_distance = 1
                while y + drop_distance < H and not game_board[y + drop_distance][x]:
                    drop_distance += 1
                game_board[y + drop_distance - 1][x] = game_board[y][x]
                game_board[y][x] = 0

def is_line_uniform(row):
    first_color = game_board[row][0]
    if first_color is None:
        return False
    return all(block == first_color for block in game_board[row])

def dfs(x, y, target_color, visited):
    if x < 0 or x >= W or y < 0 or y >= H or game_board[y][x] != target_color or (x, y) in visited:
        return False
    visited.add((x, y))
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    for dx, dy in directions:
        dfs(x + dx, y + dy, target_color, visited)
    return True

def clear_connected_blocks():
    cleared = False
    for y in range(H):
        for x in range(W):
            if game_board[y][x] is not None:
                visited = set()
                dfs(x, y, game_board[y][x], visited)
                has_left = any(vx == 0 for vx, vy in visited)
                has_right = any(vx == W - 1 for vx, vy in visited)
                if has_left and has_right:
                    for vx, vy in visited:
                        game_board[vy][vx] = None
                    cleared = True
    return cleared


while True:
    dx, rotate = 0, False
    sc.blit(background_image, (0, 0))
    sc.blit(game_sc, (20, 20))
    game_sc.blit(game_background, (0, 0))
    for i in range(lines):
        pygame.time.wait(200)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_DOWN:
                anim_limit = 100
            elif event.key == pygame.K_UP:
                rotate = True
    figure_old = deepcopy(figure)
    for i in range(4):
        figure[i].x += dx
        if not check_borders():
            figure = deepcopy(figure_old)
            break
    anim_count += anim_speed
    if anim_count > anim_limit:
        anim_count = 0
        figure_old = deepcopy(figure)
        for i in range(4):
            figure[i].y += 1
            if not check_borders():
                for i in range(4):
                    game_board[figure_old[i].y][figure_old[i].x] = color
                figure, color = next_figure, next_color
                next_figure, next_color = deepcopy(choice(figures)), get_color()
                anim_limit = 2000
                break
    center = figure[0]
    figure_old = deepcopy(figure)
    if rotate:
        for i in range(4):
            x = figure[i].y - center.y
            y = figure[i].x - center.x
            figure[i].x = center.x - x
            figure[i].y = center.y + y
            if not check_borders():
                figure = deepcopy(figure_old)
                break

    line, lines = H - 1, 0
    for row in range(H - 1, -1, -1):
        if is_line_uniform(row):
            anim_speed += 3
            lines += 1
            for shift_row in range(row, 0, -1):
                game_board[shift_row] = game_board[shift_row - 1]
            game_board[0] = [None] * W
        else:
            game_board[line] = game_board[row]
            line -= 1
    score += scores[lines]
    if clear_connected_blocks():
        score += 100
    fall_down()
    [pygame.draw.rect(game_sc, (40, 40, 40), i_rect, 1) for i_rect in grid_layout]
    for i in range(4):
        figure_rect.x = figure[i].x * BLOCK_SIZE
        figure_rect.y = figure[i].y * BLOCK_SIZE
        pygame.draw.rect(game_sc, color, figure_rect)
    for y, raw in enumerate(game_board):
        for x, col in enumerate(raw):
            if col:
                figure_rect.x, figure_rect.y = x * BLOCK_SIZE, y * BLOCK_SIZE
                pygame.draw.rect(game_sc, col, figure_rect)
    for i in range(4):
        figure_rect.x = next_figure[i].x * BLOCK_SIZE + 290
        figure_rect.y = next_figure[i].y * BLOCK_SIZE + 485
        pygame.draw.rect(sc, next_color, figure_rect)
    sc.blit(main_title, (380, 10))
    sc.blit(title, (380, 80))
    sc.blit(title_score, (535, 580))
    sc.blit(font.render(str(score), True, pygame.Color('white')), (550, 640))
    for i in range(W):
        if game_board[0][i]:
            game_board = [[0 for i in range(W)] for i in range(H)]
            anim_count, anim_speed, anim_limit = 0, 60, 2000
            score = 0
            for i_rect in grid_layout:
                pygame.draw.rect(game_sc, get_color(), i_rect)
                sc.blit(game_sc, (20, 20))
                pygame.display.flip()
                clock.tick(200)
    pygame.display.flip()
    clock.tick(60)