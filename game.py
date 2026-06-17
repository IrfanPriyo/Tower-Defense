import pygame
from settings import *
from bfs import bfs, generate_obstacles
from enemy import Enemy
from tower import Tower
from ui import draw_grid, draw_header, draw_settings_popup


def run_game(screen, fonts, sounds, images, algo="bfs"):
    # Select pathfinding function based on user's algorithm choice
    if algo == "astar":
        from astar import astar
        pathfind = astar
    else:
        pathfind = bfs

    grid = [[0] * COLS for _ in range(ROWS)]
    grid = generate_obstacles(grid)

    towers = []
    enemies = []
    score = 0
    lives = 10
    wave = 1
    spawn_timer = 0
    spawn_interval = 120
    enemies_to_spawn = 5
    spawned = 0
    show_path = True
    game_over = False
    game_over_sound_played = False
    show_settings = False
    dragging_slider = False

    baby_alpha = 0
    baby_visible = False
    baby_fade_in = True

    path = pathfind(grid, START, END)
    btn_settings = pygame.Rect(5, 5, 70, 36)

    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(GRASS_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and not show_settings:
                    show_path = not show_path
                if event.key == pygame.K_r and game_over and not show_settings:
                    run_game(screen, fonts, sounds, images, algo)
                    return

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                if show_settings:
                    ui = draw_settings_popup(screen, master_volume, fonts)
                    handle_x = ui["slider_x"] + int(
                        ui["slider_w"] * master_volume)
                    handle_rect = pygame.Rect(
                        handle_x - 12, ui["slider_y"] - 12, 24, 24)
                    if handle_rect.collidepoint(mx, my):
                        dragging_slider = True
                    if ui["btn_restart"].collidepoint(mx, my):
                        run_game(screen, fonts, sounds, images, algo)
                        return
                    if ui["btn_quit"].collidepoint(mx, my):
                        pygame.quit()
                        exit()
                    if ui["btn_close"].collidepoint(mx, my):
                        show_settings = False
                else:
                    if btn_settings.collidepoint(mx, my):
                        show_settings = True
                        continue
                    if my < 80 or game_over:
                        continue
                    col = mx // TILE_SIZE
                    row = (my - 80) // TILE_SIZE
                    if not (0 <= row < ROWS and 0 <= col < COLS):
                        continue
                    if (row, col) == START or (row, col) == END:
                        continue
                    if grid[row][col] == 2:
                        continue
                    if event.button == 1:
                        if grid[row][col] == 0:
                            grid[row][col] = 1
                            test_path = pathfind(grid, START, END)
                            if test_path is None:
                                grid[row][col] = 0
                            else:
                                towers.append(Tower(row, col))
                                path = test_path
                                for enemy in enemies:
                                    if enemy.alive and not enemy.reached_end:
                                        enemy.recalculate_path(grid)
                    elif event.button == 3:
                        if grid[row][col] == 1:
                            grid[row][col] = 0
                            towers = [t for t in towers
                                     if not (t.row == row and t.col == col)]
                            path = pathfind(grid, START, END)
                            for enemy in enemies:
                                if enemy.alive and not enemy.reached_end:
                                    enemy.recalculate_path(grid)

            if event.type == pygame.MOUSEBUTTONUP:
                dragging_slider = False

            if event.type == pygame.MOUSEMOTION:
                if dragging_slider and show_settings:
                    mx, my = event.pos
                    ui = draw_settings_popup(screen, master_volume, fonts)
                    vol = (mx - ui["slider_x"]) / ui["slider_w"]
                    vol = max(0.0, min(1.0, vol))
                    from settings import set_volume
                    set_volume(sounds, vol)

        if not game_over and not show_settings:
            spawn_timer += 1
            if spawned < enemies_to_spawn and spawn_timer >= spawn_interval:
                spawn_timer = 0
                current_path = pathfind(grid, START, END)
                if current_path:
                    e = Enemy(current_path, wave, pathfind_fn=pathfind)
                    enemies.append(e)
                    spawned += 1

            alive = [e for e in enemies if e.alive and not e.reached_end]
            if spawned >= enemies_to_spawn and len(alive) == 0:
                wave += 1
                spawned = 0
                enemies_to_spawn += 2
                spawn_interval = max(60, spawn_interval - 10)
                enemies = []

            for tower in towers:
                tower.update(enemies, sounds)

            for enemy in enemies:
                enemy.update()
                if enemy.reached_end and enemy.alive:
                    enemy.alive = False
                    lives -= 1
                    score = max(0, score - 10)
                    sounds["lives_lost"].play()

            for enemy in enemies:
                if not enemy.alive and not enemy.dead_counted:
                    enemy.dead_counted = True
                    if not enemy.reached_end:
                        score += 10

            if lives <= 0:
                game_over = True
                baby_visible = True
                baby_alpha = 0
                baby_fade_in = True

        enemies_alive = len(
            [e for e in enemies if e.alive and not e.reached_end])

        draw_grid(screen, grid, path, show_path)
        for tower in towers:
            tower.draw(screen, fonts)
        for enemy in enemies:
            enemy.draw(screen)
        draw_header(screen, score, lives, wave,
                   enemies_alive, enemies_to_spawn, spawned, fonts, algo)

        # Settings button
        pygame.draw.rect(screen, (50, 50, 50), btn_settings, border_radius=6)
        pygame.draw.rect(screen, YELLOW, btn_settings, 2, border_radius=6)
        setting_text = fonts["small"].render("Setting", True, WHITE)
        screen.blit(setting_text,
                   (btn_settings.x + btn_settings.w // 2 - setting_text.get_width() // 2,
                    btn_settings.y + btn_settings.h // 2 - setting_text.get_height() // 2))

        if game_over:
            if not game_over_sound_played:
                sounds["game_over"].play()
                game_over_sound_played = True

            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            go_text = fonts["big"].render(
                "GAME OVER! Press R to restart", True, RED)
            score_final = fonts["normal"].render(
                f"Final Score: {score}", True, YELLOW)
            screen.blit(go_text,
                       (WIDTH // 2 - go_text.get_width() // 2,
                        HEIGHT // 2 + 60))
            screen.blit(score_final,
                       (WIDTH // 2 - score_final.get_width() // 2,
                        HEIGHT // 2 + 100))

            if baby_visible:
                if baby_fade_in:
                    baby_alpha = min(255, baby_alpha + 4)
                    if baby_alpha >= 255:
                        baby_fade_in = False
                else:
                    baby_alpha = max(0, baby_alpha - 4)

                baby_copy = images["burning_baby"].copy()
                baby_copy.set_alpha(baby_alpha)
                screen.blit(baby_copy,
                           (WIDTH // 2 - images["burning_baby"].get_width() // 2,
                            HEIGHT // 2 - images["burning_baby"].get_height() // 2 - 30))

        if show_settings:
            ui = draw_settings_popup(screen, master_volume, fonts)
            if dragging_slider:
                mx, my = pygame.mouse.get_pos()
                vol = (mx - ui["slider_x"]) / ui["slider_w"]
                vol = max(0.0, min(1.0, vol))
                from settings import set_volume
                set_volume(sounds, vol)

        pygame.display.flip()
        clock.tick(60)
