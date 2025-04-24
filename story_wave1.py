import pygame
import sys
import random
from story_wave2 import transition_to_wave2
from globals import punch_count

pygame.init()

def start_wave_1(screen):
    global punch_count

    pygame.mixer.music.load("music/fight_theme.mp3")
    pygame.mixer.music.play(-1)

    clock = pygame.time.Clock()
    font = pygame.font.Font("fonts/PressStart2P.ttf", 22)
    bg = pygame.transform.scale(pygame.image.load("assets/story_bg.jpg"), (800, 600))

    timer_font = pygame.font.Font("fonts/PressStart2P.ttf", 16)
    start_ticks = pygame.time.get_ticks()

    char_scales = {
        "nyborg": (82, 133),
        "archon_9": (140, 106)
    }

    foot_offsets = {
        "nyborg": 23,
        "archon_9": 17
    }

    def load_sprites(name, flip=False):
        path = f"characters/{name}/"
        scale = char_scales.get(name, (164, 266))
        sprites = {}
        for sprite_type in ["idle_1", "idle_2", "walk_1", "walk_2", "punch", "crouch"]:
            sprite = pygame.image.load(path + f"{name}_{sprite_type}.png").convert_alpha()
            sprite = pygame.transform.scale(sprite, scale)
            if flip:
                sprite = pygame.transform.flip(sprite, True, False)
            sprites[sprite_type] = sprite
        return sprites

    def get_hitbox(rect, char_name, state=None):
        if char_name == "archon_9":
            return pygame.Rect(rect.left + 35, rect.top + 25, rect.width - 70, rect.height - 40)
        elif char_name == "nyborg":
            if state == 'crouch':
                return pygame.Rect(rect.left + 20, rect.top + 50, rect.width - 40, rect.height - 80)
        return pygame.Rect(rect.left + 20, rect.top + 20, rect.width - 40, rect.height - 40)

    def get_punch_hitbox(rect, char_name, facing_right):
        if char_name == "archon_9":
            width = 16
            height = 24
            if facing_right:
                return pygame.Rect(rect.right - 10, rect.centery - height // 2, width, height)
            else:
                return pygame.Rect(rect.left - width + 10, rect.centery - height // 2, width, height)
        elif char_name == "nyborg":
            if facing_right:
                return pygame.Rect(rect.left + 120, rect.top + 100, 40, 30)
            else:
                return pygame.Rect(rect.left + 4, rect.top + 100, 40, 30)
        return None

    def apply_knockback(fighter, direction):
        offset = 20
        if direction == "left":
            fighter.rect.x -= offset
        elif direction == "right":
            fighter.rect.x += offset
        fighter.rect.x = max(0, min(fighter.rect.x, 800 - fighter.rect.width))

    class Fighter:
        def __init__(self, sprites, x, y, foot_offset, char_name, is_player=True):
            self.sprites = sprites
            self.rect = sprites["idle_1"].get_rect()
            self.rect.x = x
            self.rect.bottom = y + foot_offset
            self.state = "idle"
            self.frame = 1
            self.animation_timer = 0
            self.animation_delay = 12
            self.is_player = is_player
            self.health = 100
            self.punch_cooldown = 0
            self.is_punching = False
            self.facing_right = is_player
            self.speed = 5

            self.punch_damage = 5 if is_player else 6
            self.punch_range = 100
            self.ai_action_timer = 0
            self.ai_action_delay = 30
            self.ai_state = "idle"
            self.char_name = char_name
            self.blocked_movement = False
            self.dodge_penalty = 0
            self.crouch_timer = 0
            self.crouch_damage_interval = 45

            self.is_jumping = False
            self.jump_velocity = 0
            self.jump_strength = -18
            self.gravity = 1
            self.ground_y = y

            self.shield_active = False
            self.shield_energy = 100
            self.shield_drain_rate = 1.5
            self.shield_regen_rate = 0.5
            self.shield_cooldown = 0
            self.shield_cooldown_time = 30

            self.shield_broken = False
            self.shield_break_cooldown = 0
            self.is_performing_shield_break = False
            self.shield_break_duration = 60

            self.ai_aggression = 9
            self.ai_defense = 7

            self.recognize_crouch_timer = 0
            self.wait_after_enemy_crouch = 0
            self.enemy_crouch_recognized = False

            self.attack_combo_counter = 0
            self.combo_cooldown = 0

            self.hitbox = get_hitbox(self.rect, self.char_name, self.state)

            self.health_bar_bg = pygame.Surface((100, 10))
            self.health_bar_bg.fill((255, 0, 0))
            self.shield_bar_bg = pygame.Surface((100, 6))
            self.shield_bar_bg.fill((0, 0, 80))

        def update(self, opponent):
            self.animation_timer += 1
            if self.animation_timer >= self.animation_delay:
                self.animation_timer = 0
                if self.state in ["idle", "walk"]:
                    self.frame = 2 if self.frame == 1 else 1

            if self.state == "crouch":
                self.crouch_timer += 1
                if self.crouch_timer >= self.crouch_damage_interval:
                    self.crouch_timer = 0
                    self.health -= 1
                    if self.health < 0:
                        self.health = 0
            else:
                self.crouch_timer = 0

            if self.punch_cooldown > 0:
                self.punch_cooldown -= 1

            if self.state == "punch" and self.punch_cooldown <= 15:
                self.state = "idle"
                self.is_punching = False

            if self.shield_break_cooldown > 0:
                self.shield_break_cooldown -= 1
                if self.shield_break_cooldown == 0:
                    self.shield_broken = False

            if self.dodge_penalty > 0:
                self.dodge_penalty -= 1
                if self.dodge_penalty == 0 and self.state == "crouch":
                    self.state = "idle"

            if self.wait_after_enemy_crouch > 0:
                self.wait_after_enemy_crouch -= 1

            if self.combo_cooldown > 0:
                self.combo_cooldown -= 1
                if self.combo_cooldown == 0:
                    self.attack_combo_counter = 0

            if self.shield_cooldown > 0:
                self.shield_cooldown -= 1

            if self.shield_active and not self.shield_broken:
                self.shield_energy -= 1.5
                if self.shield_energy <= 0:
                    self.shield_energy = 0
                    self.shield_active = False
                    self.shield_cooldown = self.shield_cooldown_time
            else:
                if self.shield_cooldown == 0 and self.shield_energy < 100 and not self.shield_broken:
                    self.shield_energy += 0.5
                    if self.shield_energy > 100:
                        self.shield_energy = 100

            if self.is_jumping or self.rect.bottom < self.ground_y + foot_offsets[self.char_name]:
                self.jump_velocity += self.gravity
                self.rect.y += self.jump_velocity

                if self.rect.bottom >= self.ground_y + foot_offsets[self.char_name]:
                    self.rect.bottom = self.ground_y + foot_offsets[self.char_name]
                    self.is_jumping = False
                    self.jump_velocity = 0
                    if self.state not in ["punch", "crouch"] and not self.is_punching:
                        self.state = "idle"

            self.hitbox = get_hitbox(self.rect, self.char_name, self.state)

            if not self.is_player:
                self.update_ai(opponent)
                self.facing_right = opponent.rect.centerx > self.rect.centerx

            self.blocked_movement = False
            if self.hitbox.colliderect(opponent.hitbox):
                if abs(self.rect.bottom - opponent.rect.bottom) < 50 and abs(
                        self.rect.centery - opponent.rect.centery) < 60:
                    if self.hitbox.centerx < opponent.hitbox.centerx:
                        overlap = self.hitbox.right - opponent.hitbox.left
                        if overlap > 0:
                            self.rect.x -= min(overlap // 2, self.rect.left)
                    else:
                        overlap = opponent.hitbox.right - self.hitbox.left
                        if overlap > 0:
                            self.rect.x += min(overlap // 2, 800 - self.rect.right)
                    self.blocked_movement = True

        def update_ai(self, player):
            self.ai_action_timer += 1

            if player.state == "crouch":
                self.recognize_crouch_timer += 1
                if self.recognize_crouch_timer > 20:
                    self.enemy_crouch_recognized = True
                    self.wait_after_enemy_crouch = 30
            else:
                self.recognize_crouch_timer = 0
                self.enemy_crouch_recognized = False

            if (player.shield_active and not player.shield_broken and
                    random.random() < 0.05 and
                    abs(self.rect.centerx - player.rect.centerx) < 120):

                self.try_shield_break(player)

            if self.ai_action_timer >= self.ai_action_delay:
                self.ai_action_timer = 0
                distance = abs(self.rect.centerx - player.rect.centerx)

                if self.dodge_penalty > 0:
                    self.state = "idle"
                    return

                if player.state == "punch" and distance < 150:
                    if self.shield_energy > 30 and self.shield_cooldown == 0 and not self.shield_broken and random.random() < 0.7:
                        self.shield_active = True
                        return

                if (player.state == "punch" and abs(self.rect.centerx - player.rect.centerx) < 150 and
                        self.shield_energy > 10 and not self.shield_broken and self.shield_cooldown == 0 and not self.shield_active):
                    self.shield_active = True
                    return

                if self.shield_active and (
                        player.state != "punch" or abs(self.rect.centerx - player.rect.centerx) > 200):
                    self.shield_active = False
                    self.shield_cooldown = self.shield_cooldown_time

                if self.shield_active and (player.state != "punch" or distance > 180 or self.shield_energy < 20):
                    self.shield_active = False

                if player.state == "crouch" and self.enemy_crouch_recognized:
                    direction = 1 if self.rect.centerx > player.rect.centerx else -1
                    if distance < 150:
                        self.move(direction)
                    return

                if self.wait_after_enemy_crouch > 0 and distance < 200:
                    direction = 1 if self.rect.centerx > player.rect.centerx else -1
                    self.move(direction)
                    return

                if player.shield_active and distance < 160:
                    direction = 1 if self.rect.centerx > player.rect.centerx else -1
                    self.move(direction)
                    return

                if player.dodge_penalty > 0 and distance < 150 and self.punch_cooldown == 0 and random.random() < 0.85:
                    self.punch(player)
                    return

                if distance < 160 and self.punch_cooldown == 0 and not self.is_punching:
                    self.punch(player)
                    return

                if distance < 250 and player.state == "punch":
                    dodge_chance = 0.7
                    if random.random() < dodge_chance:
                        self.crouch()
                        self.ai_action_timer = -10
                    elif random.random() < 0.7:
                        self.jump()
                    return

                if distance < 120 and random.random() < 0.3:
                    self.crouch()
                    return

                if distance < 200 and random.random() < 0.15:
                    self.jump()
                    return

                self.ai_state = "walk"

            if self.dodge_penalty == 0 and not self.is_punching:
                if self.ai_state == "walk" and self.state not in ["punch",
                                                                  "crouch"] and not self.is_jumping and not self.is_punching and abs(
                        self.rect.centerx - player.rect.centerx) > 80:
                    direction = -1 if self.rect.centerx > player.rect.centerx else 1
                    self.move(direction)

        def try_shield_break(self, opponent):
            """Attempt to perform a shield break attack"""
            if self.punch_cooldown > 0 or self.is_performing_shield_break:
                return False

            self.is_performing_shield_break = True
            punch_hitbox = get_punch_hitbox(self.rect, self.char_name, self.facing_right)

            if punch_hitbox and punch_hitbox.colliderect(opponent.hitbox):
                if opponent.shield_active and not opponent.shield_broken:

                    opponent.shield_broken = True
                    opponent.shield_break_cooldown = opponent.shield_break_duration
                    opponent.shield_active = False

                    opponent.dodge_penalty = 30

                    return True

            self.is_performing_shield_break = False
            return False

        def toggle_shield(self):
            if self.shield_cooldown == 0 and self.shield_energy > 0 and not self.shield_broken:
                self.shield_active = not self.shield_active
            elif self.shield_active:
                self.shield_active = False

        def draw_top_health(self, screen):
            if self.char_name != "archon_9":
                return
            bar_width = 200
            bar_height = 20
            x = (screen.get_width() - bar_width) // 2
            y = 30
            pygame.draw.rect(screen, (80, 0, 0), (x, y, bar_width, bar_height))
            health_ratio = self.health / 100
            pygame.draw.rect(screen, (0, 255, 0), (x, y, int(bar_width * health_ratio), bar_height))

        def move(self, direction):
            if self.state == "crouch" or self.state == "punch" or self.dodge_penalty > 0:
                return

            if not self.blocked_movement:
                self.rect.x += direction * self.speed

            if self.rect.left < 0:
                self.rect.left = 0
            elif self.rect.right > 800:
                self.rect.right = 800

            if not self.is_jumping:
                self.state = "walk"

            if direction > 0:
                self.facing_right = True
            elif direction < 0:
                self.facing_right = False

        def jump(self):
            if not self.is_jumping and self.state != "crouch" and self.dodge_penalty == 0:
                self.is_jumping = True
                self.jump_velocity = self.jump_strength
                if self.state != "punch":
                    self.state = "idle"

        def punch(self, opponent):
            if self.punch_cooldown > 0 or self.state == "crouch" or self.dodge_penalty > 0:
                return

            self.state = "punch"
            self.is_punching = True
            self.punch_cooldown = 20 if self.is_player else 15

            punch_hitbox = get_punch_hitbox(self.rect, self.char_name, self.facing_right)

            if punch_hitbox and punch_hitbox.colliderect(opponent.hitbox):
                if opponent.shield_active and not opponent.shield_broken:
                    opponent.shield_energy -= 15
                    if opponent.shield_energy < 0:
                        opponent.shield_energy = 0
                        opponent.shield_active = False
                        opponent.shield_cooldown = opponent.shield_cooldown_time // 2
                else:
                    if opponent.state == "crouch":
                        if random.random() < 0.4:
                            self.dodge_penalty = 60
                            return
                        else:
                            opponent.take_damage(self.punch_damage // 2)
                    else:
                        opponent.take_damage(self.punch_damage)
                        if self.is_player:
                            global punch_count
                            punch_count += 1

                if not self.is_player and self.combo_cooldown == 0:
                    self.attack_combo_counter += 1
                    self.combo_cooldown = 45
                    if self.attack_combo_counter >= 1 and random.random() < 0.5:
                        self.punch_cooldown = 5

        def crouch(self):
            if not self.is_jumping and self.dodge_penalty == 0:
                self.state = "crouch"

        def stand(self):
            if self.state == "crouch" and self.dodge_penalty == 0:
                self.state = "idle"

        def take_damage(self, amount):
            """Take damage if shield is not active"""
            if not self.shield_active or self.shield_broken:
                self.health -= amount
                if self.health < 0:
                    self.health = 0

        def draw(self, screen):
            sprite_key = f"{self.state}_{self.frame}" if self.state in ["idle", "walk"] else self.state
            sprite = self.sprites.get(sprite_key, self.sprites["idle_1"])

            if not self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)

            screen.blit(sprite, self.rect)

            health_width = 100
            health_height = 10
            x_pos = self.rect.centerx - health_width // 2
            y_pos = self.rect.top - 20

            screen.blit(self.health_bar_bg, (x_pos, y_pos))

            bar_color = (255, 255, 0) if self.dodge_penalty > 0 else (0, 255, 0)
            health_bar = pygame.Surface((int(health_width * self.health / 100), health_height))
            health_bar.fill(bar_color)
            screen.blit(health_bar, (x_pos, y_pos))

            if self.shield_energy > 0 or self.shield_active:
                shield_width = 100
                shield_height = 6
                shield_x_pos = x_pos
                shield_y_pos = y_pos - shield_height - 2

                screen.blit(self.shield_bar_bg, (shield_x_pos, shield_y_pos))

                shield_color = (255, 0, 0) if self.shield_broken else (0, 100, 255) if self.shield_active else (
                0, 200, 255)
                shield_bar = pygame.Surface((int(shield_width * self.shield_energy / 100), shield_height))
                shield_bar.fill(shield_color)
                screen.blit(shield_bar, (shield_x_pos, shield_y_pos))

                if self.shield_active and not self.shield_broken:
                    shield_effect = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
                    shield_effect.fill((0, 100, 255, 40))
                    screen.blit(shield_effect, (self.rect.x - 5, self.rect.y - 5))
                elif self.shield_broken:

                    broken_effect = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
                    broken_effect.fill((255, 0, 0, 30))
                    screen.blit(broken_effect, (self.rect.x - 5, self.rect.y - 5))

            if self.dodge_penalty > 0:
                alpha = min(255, int(self.dodge_penalty * 2))
                penalty_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
                penalty_surf.fill((255, 255, 0, alpha))
                screen.blit(penalty_surf, (self.rect.centerx - 10, self.rect.top - 40))

            if self.shield_cooldown > 0:
                alpha = min(255, int(self.shield_cooldown * 3))
                cooldown_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
                cooldown_surf.fill((255, 0, 0, alpha))
                screen.blit(cooldown_surf, (self.rect.centerx - 10, self.rect.top - 60))

    nyborg_sprites = load_sprites("nyborg")
    archon_sprites = load_sprites("archon_9")

    ground_y = 500
    nyborg = Fighter(nyborg_sprites, 100, ground_y, foot_offsets["nyborg"], "nyborg", is_player=True)
    archon = Fighter(archon_sprites, 600, ground_y, foot_offsets["archon_9"], "archon_9", is_player=False)

    running = True
    game_over = False
    controls_rendered = pygame.font.SysFont("Arial", 16).render(
        "Controls: A/D - Move, W - Jump, S - Crouch, SPACE - Punch, E - Shield, SPACE+A+S - Shield Break", True,
        (255, 255, 255))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_s and nyborg.dodge_penalty == 0:
                    nyborg.stand()
                if event.key == pygame.K_w and nyborg.is_jumping and nyborg.jump_velocity < -3:
                    nyborg.jump_velocity = -3
                if event.key == pygame.K_e:
                    nyborg.shield_active = False

        keys = pygame.key.get_pressed()

        if not game_over:

            if keys[pygame.K_SPACE] and keys[pygame.K_a] and keys[pygame.K_s] and nyborg.dodge_penalty == 0:
                if nyborg.try_shield_break(archon):

                    nyborg.punch_cooldown = 45
            else:

                if keys[pygame.K_a] and nyborg.dodge_penalty == 0:
                    nyborg.move(-1)
                elif keys[pygame.K_d] and nyborg.dodge_penalty == 0:
                    nyborg.move(1)
                elif nyborg.state == "walk" and not nyborg.is_jumping:
                    nyborg.state = "idle"

                if keys[pygame.K_w] and nyborg.dodge_penalty == 0 and not nyborg.is_jumping:
                    nyborg.jump()

                if keys[pygame.K_s] and nyborg.dodge_penalty == 0 and not nyborg.is_jumping:
                    nyborg.crouch()

                if keys[pygame.K_SPACE] and nyborg.dodge_penalty == 0:
                    nyborg.punch(archon)

                if keys[
                    pygame.K_e] and nyborg.shield_cooldown == 0 and nyborg.shield_energy > 0 and not nyborg.shield_broken:
                    nyborg.shield_active = True
                elif not keys[pygame.K_e]:
                    nyborg.shield_active = False

            nyborg.update(archon)
            archon.update(nyborg)

            if nyborg.health <= 0 or archon.health <= 0:
                game_over = True

            elapsed_seconds = (pygame.time.get_ticks() - start_ticks) // 1000

        screen.blit(bg, (0, 0))
        timer_text = timer_font.render(f"Time: {elapsed_seconds}s", True, (255, 255, 255))
        punch_text = timer_font.render(f"Punches: {punch_count}", True, (255, 255, 255))
        screen.blit(timer_text, (10, 10))
        screen.blit(punch_text, (10, 40))

        nyborg.draw(screen)
        archon.draw(screen)
        archon.draw_top_health(screen)

        screen.blit(controls_rendered, (10, 10))

        if nyborg.shield_broken or archon.shield_broken:
            break_font = pygame.font.SysFont("Arial", 16)
            if nyborg.shield_broken:
                break_text = break_font.render("SHIELD BROKEN!", True, (255, 50, 50))
                screen.blit(break_text, (nyborg.rect.centerx - 60, nyborg.rect.top - 40))
            if archon.shield_broken:
                break_text = break_font.render("SHIELD BROKEN!", True, (255, 50, 50))
                screen.blit(break_text, (archon.rect.centerx - 60, archon.rect.top - 40))

        if game_over:
            game_over_font = pygame.font.SysFont("Arial", 48)
            if nyborg.health <= 0:
                text = game_over_font.render("GAME OVER - You Lose!", True, (255, 0, 0))
            else:
                text = game_over_font.render("VICTORY!", True, (0, 255, 0))

            text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(text, text_rect)

            restart_font = pygame.font.SysFont("Arial", 24)
            restart_text = restart_font.render("Press R to restart or N for next wave", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
            screen.blit(restart_text, restart_rect)

            if keys[pygame.K_r]:
                nyborg.health = 100
                archon.health = 100
                nyborg.rect.x = 100
                archon.rect.x = 600
                nyborg.dodge_penalty = 0
                archon.dodge_penalty = 0
                nyborg.shield_energy = 100
                archon.shield_energy = 100
                nyborg.shield_active = False
                archon.shield_active = False
                nyborg.shield_cooldown = 0
                archon.shield_cooldown = 0
                nyborg.shield_broken = False
                archon.shield_broken = False
                game_over = False
            elif keys[pygame.K_n]:
                pygame.mixer.music.stop()
                name_font = pygame.font.Font("fonts/PressStart2P.ttf", 22)
                dialogue_font = pygame.font.Font("fonts/PressStart2P.ttf", 18)
                from demon_cutscene import show_demon_cutscene
                show_demon_cutscene(screen, clock, dialogue_font, name_font)
                return

        pygame.display.flip()
        clock.tick(60)