def start_match(player1_char, player2_char, map_name, collectible_manager=None):
    import pygame
    import sys
    import time
    import os

    p1_shield_active = False
    p1_shield_energy = 100
    p1_shield_broken = False
    p1_shield_cooldown = 0

    p2_shield_active = False
    p2_shield_energy = 100
    p2_shield_broken = False
    p2_shield_cooldown = 0

    def get_hitbox(rect, char_name):
        # Fix hitboxes for all characters
        if char_name == "archon_9":
            return pygame.Rect(rect.left + 58, rect.top + 32, 58, 65)
        elif char_name == "demon_archon":
            return pygame.Rect(rect.left + 58, rect.top + 32, 58, 65)
        elif char_name == "nyborg":
            return pygame.Rect(rect.left + 41, rect.top + 35, 41, 98)
        return rect

    def get_punch_hitbox(rect, char_name, facing_right):
        # Fix punch hitboxes for all characters
        if char_name == "archon_9":
            if facing_right:
                return pygame.Rect(rect.left + 58 + 58, rect.top + 45, 20, 20)
            else:
                return pygame.Rect(rect.left + 58 - 20, rect.top + 45, 20, 20)
        elif char_name == "demon_archon":
            if facing_right:
                return pygame.Rect(rect.left + 58 + 58, rect.top + 45, 20, 20)
            else:
                return pygame.Rect(rect.left + 58 - 20, rect.top + 45, 20, 20)
        elif char_name == "nyborg":
            if facing_right:
                return pygame.Rect(rect.left + 41 + 41, rect.top + 65, 20, 20)
            else:
                return pygame.Rect(rect.left + 41 - 20, rect.top + 65, 20, 20)
        return get_hitbox(rect, char_name)

    def knockback(rect, direction):
        new_rect = rect.move(30 if direction == "right" else -30, 0)
        if new_rect.left < 0:
            new_rect.left = 0
        elif new_rect.right > 800:
            new_rect.right = 800
        return new_rect

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Local Match")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 36)
    small_font = pygame.font.SysFont("Arial", 20)


    def draw_text_center(text, y):
        render = font.render(text, True, (255, 255, 255))
        rect = render.get_rect(center=(400, y))
        screen.blit(render, rect)

    def draw_text_above_player(text, rect, color=(255, 0, 0)):
        render = small_font.render(text, True, color)
        text_rect = render.get_rect(centerx=rect.centerx, bottom=rect.top - 5)
        screen.blit(render, text_rect)

    def show_announcer(text, duration=2):
        start = time.time()
        while time.time() - start < duration:
            screen.blit(background, (0, 0))
            draw_text_center(text, 250)
            pygame.display.flip()
            clock.tick(60)

    def draw_health_bar(x, y, health, max_width=300):
        bar_width = int((health / 100) * max_width)
        red_value = 255 - int(2.55 * health)
        green_value = int(2.55 * health)
        color = (red_value, green_value, 0)
        pygame.draw.rect(screen, color, (x, y, bar_width, 30))
        pygame.draw.rect(screen, (255, 255, 255), (x, y, max_width, 30), 2)
        # Removed percentage text

    wins = {1: 0, 2: 0}

    while wins[1] < 2 and wins[2] < 2:
        jpg_path = f"map/{map_name}/map.jpg"
        png_path = f"map/{map_name}/map.png"
        if os.path.exists(jpg_path):
            background = pygame.image.load(jpg_path).convert()
        elif os.path.exists(png_path):
            background = pygame.image.load(png_path).convert()
        else:
            background = pygame.Surface((800, 600))
            background.fill((30, 30, 30))
        background = pygame.transform.scale(background, (800, 600))

        ground_y = 500
        gravity = 1
        jump_force = -15
        feet_offsets = {"nyborg": -13, "archon_9": 0}

        # Reduce character scales by half
        char_scales = {
            "archon_9": (140, 106),  # Was (280, 213)
            "nyborg": (82, 133),  # Was (164, 266)
            "demon_archon": (191, 131)  # Was (382, 262)
        }

        def load_character_sprites(char_name, flip=False):
            base_path = f"characters/{char_name}/"
            scale = char_scales.get(char_name, (82, 133))  # Default to nyborg size if not found
            sprites = {
                "idle_1": pygame.image.load(base_path + f"{char_name}_idle_1.png").convert_alpha(),
                "idle_2": pygame.image.load(base_path + f"{char_name}_idle_2.png").convert_alpha(),
                "walk_1": pygame.image.load(base_path + f"{char_name}_walk_1.png").convert_alpha(),
                "walk_2": pygame.image.load(base_path + f"{char_name}_walk_2.png").convert_alpha(),
                "punch": pygame.image.load(base_path + f"{char_name}_punch.png").convert_alpha(),
                "shield": pygame.image.load(base_path + f"{char_name}_shield.png").convert_alpha(),
                "crouch": pygame.image.load(base_path + f"{char_name}_crouch.png").convert_alpha(),
            }
            for key in sprites:
                sprites[key] = pygame.transform.scale(sprites[key], scale)
                if flip:
                    sprites[key] = pygame.transform.flip(sprites[key], True, False)
            return sprites

        p1_sprites = load_character_sprites(player1_char)
        p2_sprites = load_character_sprites(player2_char, flip=True)

        p1_rect = p1_sprites["idle_1"].get_rect(midleft=(100, ground_y))
        p2_rect = p2_sprites["idle_1"].get_rect(midright=(700, ground_y))
        p1_rect.bottom = p2_rect.bottom = ground_y

        p1_health = p2_health = 100
        p1_action = p2_action = "idle"
        p1_frame = p2_frame = 0
        p1_punching = p2_punching = False
        p1_punch_cooldown = p2_punch_cooldown = 0
        p1_vel_y = p2_vel_y = 0
        frame_timer = 0
        frame_delay = 300

        # Reset shield states at the start of each round
        p1_shield_active = False
        p1_shield_energy = 100
        p1_shield_broken = False
        p1_shield_cooldown = 0

        p2_shield_active = False
        p2_shield_energy = 100
        p2_shield_broken = False
        p2_shield_cooldown = 0

        pygame.mixer.music.load("music/fight_theme.mp3")
        pygame.mixer.music.play(-1)
        show_announcer("FIGHT!")
        start_ticks = pygame.time.get_ticks()
        running = True

        # Track combo keys for shield break
        p1_combo_keys = {"a": False, "d": False, "s": False, "space": False}
        p2_combo_keys = {"left": False, "right": False, "down": False, "rshift": False}
        p1_combo_timer = 0
        p2_combo_timer = 0

        while running:
            elapsed = (pygame.time.get_ticks() - start_ticks) // 1000
            time_left = max(0, 60 - elapsed)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    # Shield toggle for Player 1
                    if event.key == pygame.K_e:
                        if not p1_shield_broken and p1_shield_cooldown == 0 and p1_shield_energy > 0:
                            p1_shield_active = not p1_shield_active

                    # Shield toggle for Player 2
                    if event.key == pygame.K_RCTRL:
                        if not p2_shield_broken and p2_shield_cooldown == 0 and p2_shield_energy > 0:
                            p2_shield_active = not p2_shield_active

                    # Player 1 punch
                    if event.key == pygame.K_f and not p1_punching:
                        p1_action = "punch"
                        p1_punching = True
                        p1_punch_cooldown = pygame.time.get_ticks()
                        punch_box = get_punch_hitbox(p1_rect, player1_char, True)
                        if punch_box.colliderect(get_hitbox(p2_rect, player2_char)):
                            if not p2_shield_active or p2_shield_broken:
                                p2_health = max(0, p2_health - 10)
                                p2_rect = knockback(p2_rect, "right")

                    # Player 2 punch
                    if event.key == pygame.K_RSHIFT and not p2_punching:
                        p2_action = "punch"
                        p2_punching = True
                        p2_punch_cooldown = pygame.time.get_ticks()
                        punch_box = get_punch_hitbox(p2_rect, player2_char, False)
                        if punch_box.colliderect(get_hitbox(p1_rect, player1_char)):
                            if not p1_shield_active or p1_shield_broken:
                                p1_health = max(0, p1_health - 10)
                                p1_rect = knockback(p1_rect, "left")

                    # Jumping
                    if event.key == pygame.K_w and p1_rect.bottom >= ground_y and not p1_shield_broken:
                        p1_vel_y = jump_force
                    if event.key == pygame.K_UP and p2_rect.bottom >= ground_y and not p2_shield_broken:
                        p2_vel_y = jump_force

                elif event.type == pygame.KEYUP:
                    # Track key releases for combo detection
                    if event.key == pygame.K_a:
                        p1_combo_keys["a"] = False
                    elif event.key == pygame.K_d:
                        p1_combo_keys["d"] = False
                    elif event.key == pygame.K_s:
                        p1_combo_keys["s"] = False
                    elif event.key == pygame.K_SPACE:
                        p1_combo_keys["space"] = False

                    if event.key == pygame.K_LEFT:
                        p2_combo_keys["left"] = False
                    elif event.key == pygame.K_RIGHT:
                        p2_combo_keys["right"] = False
                    elif event.key == pygame.K_DOWN:
                        p2_combo_keys["down"] = False
                    elif event.key == pygame.K_RSHIFT:
                        p2_combo_keys["rshift"] = False

            # Handle shield energy and cooldown
            if p1_shield_active and not p1_shield_broken:
                p1_shield_energy -= 1.5
                if p1_shield_energy <= 0:
                    p1_shield_energy = 0
                    p1_shield_active = False
                    p1_shield_broken = True
                    p1_shield_cooldown = 60  # 1 second at 60 FPS
            elif p1_shield_broken:
                if p1_shield_cooldown > 0:
                    p1_shield_cooldown -= 1
                else:
                    p1_shield_broken = False
                    p1_shield_energy = 30  # Give some energy back after cooldown
            elif not p1_shield_active and p1_shield_energy < 100:
                p1_shield_energy += 0.5  # Regenerate when not using shield

            if p2_shield_active and not p2_shield_broken:
                p2_shield_energy -= 1.5
                if p2_shield_energy <= 0:
                    p2_shield_energy = 0
                    p2_shield_active = False
                    p2_shield_broken = True
                    p2_shield_cooldown = 60  # 1 second at 60 FPS
            elif p2_shield_broken:
                if p2_shield_cooldown > 0:
                    p2_shield_cooldown -= 1
                else:
                    p2_shield_broken = False
                    p2_shield_energy = 30  # Give some energy back after cooldown
            elif not p2_shield_active and p2_shield_energy < 100:
                p2_shield_energy += 0.5  # Regenerate when not using shield

            keys = pygame.key.get_pressed()

            # Update combo key tracking
            p1_combo_keys["a"] = keys[pygame.K_a]
            p1_combo_keys["d"] = keys[pygame.K_d]
            p1_combo_keys["s"] = keys[pygame.K_s]
            p1_combo_keys["space"] = keys[pygame.K_SPACE]

            p2_combo_keys["left"] = keys[pygame.K_LEFT]
            p2_combo_keys["right"] = keys[pygame.K_RIGHT]
            p2_combo_keys["down"] = keys[pygame.K_DOWN]
            p2_combo_keys["rshift"] = keys[pygame.K_RSHIFT]

            # Shield Break Combo for Player 1
            if p1_combo_keys["a"] and p1_combo_keys["d"] and p1_combo_keys["s"] and p1_combo_keys["space"]:
                if p1_combo_timer == 0:  # Newly activated combo
                    p1_combo_timer = pygame.time.get_ticks()
                elif pygame.time.get_ticks() - p1_combo_timer > 300:  # Held for 300ms
                    if get_hitbox(p1_rect, player1_char).colliderect(get_hitbox(p2_rect, player2_char)):
                        if not p2_shield_broken:
                            p2_shield_broken = True
                            p2_shield_cooldown = 60  # stunned
                            p2_shield_active = False
                            p2_shield_energy = 0
                            p2_health = max(0, p2_health - 10)
                            p1_combo_timer = 0  # Reset timer after successful combo
            else:
                p1_combo_timer = 0

            # Shield Break Combo for Player 2
            if p2_combo_keys["left"] and p2_combo_keys["right"] and p2_combo_keys["down"] and p2_combo_keys["rshift"]:
                if p2_combo_timer == 0:  # Newly activated combo
                    p2_combo_timer = pygame.time.get_ticks()
                elif pygame.time.get_ticks() - p2_combo_timer > 300:  # Held for 300ms
                    if get_hitbox(p2_rect, player2_char).colliderect(get_hitbox(p1_rect, player1_char)):
                        if not p1_shield_broken:
                            p1_shield_broken = True
                            p1_shield_cooldown = 60
                            p1_shield_active = False
                            p1_shield_energy = 0
                            p1_health = max(0, p1_health - 10)
                            p2_combo_timer = 0  # Reset timer after successful combo
            else:
                p2_combo_timer = 0

            # Set player actions
            if not p1_punching:
                p1_action = "crouch" if keys[pygame.K_s] else "walk" if keys[pygame.K_a] or keys[pygame.K_d] else "idle"
                if p1_shield_active:
                    p1_action = "shield"

            if not p2_punching:
                p2_action = "crouch" if keys[pygame.K_DOWN] else "walk" if keys[pygame.K_LEFT] or keys[
                    pygame.K_RIGHT] else "idle"
                if p2_shield_active:
                    p2_action = "shield"

            # End punch animations
            if p1_punching and pygame.time.get_ticks() - p1_punch_cooldown > 400:
                p1_punching = False
            if p2_punching and pygame.time.get_ticks() - p2_punch_cooldown > 400:
                p2_punching = False

            # Movement - Players can't move when shield is broken
            if not p1_shield_broken:
                if not p1_shield_active:
                    p1_speed = -5 if keys[pygame.K_a] else 5 if keys[pygame.K_d] else 0
                else:
                    p1_speed = 0  # Can't move while shield is active
            else:
                p1_speed = 0  # Can't move when shield is broken

            if not p2_shield_broken:
                if not p2_shield_active:
                    p2_speed = -5 if keys[pygame.K_LEFT] else 5 if keys[pygame.K_RIGHT] else 0
                else:
                    p2_speed = 0  # Can't move while shield is active
            else:
                p2_speed = 0  # Can't move when shield is broken

            new_p1 = p1_rect.move(p1_speed, 0)
            new_p2 = p2_rect.move(p2_speed, 0)

            if not get_hitbox(new_p1, player1_char).colliderect(
                    get_hitbox(p2_rect, player2_char)) and 0 <= new_p1.left <= 800 - new_p1.width:
                p1_rect = new_p1
            if not get_hitbox(new_p2, player2_char).colliderect(
                    get_hitbox(p1_rect, player1_char)) and 0 <= new_p2.left <= 800 - new_p2.width:
                p2_rect = new_p2

            # Apply gravity
            p1_vel_y += gravity
            p2_vel_y += gravity
            p1_rect.y += p1_vel_y
            p2_rect.y += p2_vel_y
            if p1_rect.bottom > ground_y:
                p1_rect.bottom = ground_y
                p1_vel_y = 0
            if p2_rect.bottom > ground_y:
                p2_rect.bottom = ground_y
                p2_vel_y = 0

            # Animation frame update
            if pygame.time.get_ticks() - frame_timer > frame_delay:
                frame_timer = pygame.time.get_ticks()
                p1_frame = (p1_frame + 1) % 2
                p2_frame = (p2_frame + 1) % 2

            # Drawing
            screen.blit(background, (0, 0))

            # Draw Player 1
            current_p1_sprite = p1_sprites["punch"] if p1_action == "punch" else \
                p1_sprites["shield"] if p1_action == "shield" else \
                    p1_sprites["crouch"] if p1_action == "crouch" else \
                        p1_sprites[f"walk_{p1_frame + 1}"] if p1_action == "walk" else \
                            p1_sprites[f"idle_{p1_frame + 1}"]
            screen.blit(current_p1_sprite, p1_rect)

            # Draw Player 2
            current_p2_sprite = p2_sprites["punch"] if p2_action == "punch" else \
                p2_sprites["shield"] if p2_action == "shield" else \
                    p2_sprites["crouch"] if p2_action == "crouch" else \
                        p2_sprites[f"walk_{p2_frame + 1}"] if p2_action == "walk" else \
                            p2_sprites[f"idle_{p2_frame + 1}"]
            screen.blit(current_p2_sprite, p2_rect)

            # Draw UI elements
            draw_health_bar(50, 40, p1_health)
            draw_health_bar(450, 40, p2_health)
            draw_text_center(f"Time Left: {time_left}s", 85)

            # Draw shield bars
            shield_bar_color_p1 = (0, 0, 255) if not p1_shield_broken else (100, 100, 100)
            shield_bar_color_p2 = (0, 0, 255) if not p2_shield_broken else (100, 100, 100)

            pygame.draw.rect(screen, shield_bar_color_p1, (50, 80, p1_shield_energy * 3, 10))
            pygame.draw.rect(screen, (255, 255, 255), (50, 80, 300, 10), 1)
            pygame.draw.rect(screen, shield_bar_color_p2, (450, 80, p2_shield_energy * 3, 10))
            pygame.draw.rect(screen, (255, 255, 255), (450, 80, 300, 10), 1)

            # Visual feedback for broken shields
            if p1_shield_broken:
                pygame.draw.rect(screen, (255, 0, 0),
                                 (p1_rect.x - 5, p1_rect.y - 5, p1_rect.width + 10, p1_rect.height + 10), 2)
                draw_text_above_player("SHIELD BROKEN", p1_rect)
            if p2_shield_broken:
                pygame.draw.rect(screen, (255, 0, 0),
                                 (p2_rect.x - 5, p2_rect.y - 5, p2_rect.width + 10, p2_rect.height + 10), 2)
                draw_text_above_player("SHIELD BROKEN", p2_rect)

            # Visual feedback for active shields
            if p1_shield_active:
                pygame.draw.rect(screen, (0, 0, 255),
                                 (p1_rect.x - 5, p1_rect.y - 5, p1_rect.width + 10, p1_rect.height + 10), 2)
            if p2_shield_active:
                pygame.draw.rect(screen, (0, 0, 255),
                                 (p2_rect.x - 5, p2_rect.y - 5, p2_rect.width + 10, p2_rect.height + 10), 2)

            # Draw cooldown indicator for broken shields
            if p1_shield_broken:
                cooldown_text = f"Cooldown: {p1_shield_cooldown // 6}"
                draw_text_above_player(cooldown_text, p1_rect.move(0, -20), (255, 255, 0))
            if p2_shield_broken:
                cooldown_text = f"Cooldown: {p2_shield_cooldown // 6}"
                draw_text_above_player(cooldown_text, p2_rect.move(0, -20), (255, 255, 0))

            pygame.display.flip()
            clock.tick(60)

            if time_left <= 0 or p1_health <= 0 or p2_health <= 0:
                running = False

        if p1_health > p2_health:
            wins[1] += 1
            show_announcer("PLAYER 1 WINS!", 3)
        elif p2_health > p1_health:
            wins[2] += 1
            show_announcer("PLAYER 2 WINS!", 3)
        else:
            show_announcer("DRAW!", 3)

    final_winner = "PLAYER 1" if wins[1] == 2 else "PLAYER 2"
    show_announcer(f"{final_winner} WINS THE MATCH!", 4)
    pygame.mixer.music.stop()