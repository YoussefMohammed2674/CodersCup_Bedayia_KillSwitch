import pygame
import sys
import sound
import music
import ctypes
from collectibles import CollectibleManager

user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)

class Menu:
    def __init__(self, screen):

        self.screen = screen
        gold_image = pygame.image.load("assets/gold_statue.png").convert_alpha()
        self.collectible_positions = {
            "main": (100, 100),
            "play": (700, 100),
            "options": (400, 500),
            "local_char_select": (700, 500)
        }
        self.collectible_manager = CollectibleManager(
            [gold_image] * 4,
            [self.collectible_positions[k] for k in ["main", "play", "options", "local_char_select"]],
            {
                "main": 0,
                "play": 1,
                "options": 2,
                "local_char_select": 3
            }
        )

        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "main"
        self.mouse_pressed = False
        self.selected_player_char = "nyborg"

        self.bg = pygame.image.load("assets/bg.jpg").convert_alpha()
        self.bg = pygame.transform.scale(self.bg, (800, 600))
        self.ground = pygame.image.load("assets/bg_ground.jpg").convert_alpha()
        self.ground = pygame.transform.scale(self.ground, (800, 600))

        self.show_unlock_message = False
        self.unlock_timer = 0
        self.unlock_duration = 2000

        self.character_folders = ["nyborg", "archon_9"]
        self.current_char_index = 0
        self.idle_frame = 0
        self.idle_timer = 0
        self.idle_delay = 500

        self.state_after_confirm = None
        self.show_confirm_prompt = False

        self.selecting_player = 1
        self.selected_chars = {1: None, 2: None}
        self.player_labels = {
            1: pygame.image.load("assets/player_1.png").convert_alpha(),
            2: pygame.image.load("assets/player_2.png").convert_alpha()
        }
        self.player_labels[1] = pygame.transform.scale(self.player_labels[1], (300, 100))
        self.player_labels[2] = pygame.transform.scale(self.player_labels[2], (300, 100))

        self.clicked_button: str | None = None

        def load_button(name):
            normal = pygame.image.load(f'assets/{name}.png').convert_alpha()
            hover = pygame.image.load(f'assets/{name}_hover.png').convert_alpha()
            down = pygame.image.load(f'assets/{name}_down.png').convert_alpha()
            size = (360, 157)
            return [
                pygame.transform.scale(normal, size),
                pygame.transform.scale(hover, size),
                pygame.transform.scale(down, size)
            ]

        self.buttons = {
            'play': load_button('play'),
            'options': load_button('options'),
            'exit': load_button('exit'),
            'story': load_button('story'),
            'local': load_button('local')
        }

        def load_map_button(name):
            normal = pygame.image.load(f'assets/{name}.png').convert_alpha()
            hover = pygame.image.load(f'assets/{name}_hover.png').convert_alpha()
            down = pygame.image.load(f'assets/{name}_down.png').convert_alpha()
            size = (360, 157)
            return [
                pygame.transform.scale(normal, size),
                pygame.transform.scale(hover, size),
                pygame.transform.scale(down, size)
            ]

        self.map_folders = ["ice", "abandoned"]
        self.current_map_index = 0
        self.map_vote = {1: None, 2: None}
        self.font = pygame.font.SysFont('Arial', 40)

        self.map_buttons = {}
        for map_name in self.map_folders:

            button = pygame.image.load(f"map/{map_name}/button.png").convert_alpha()
            button = pygame.transform.scale(button, (360, 157))
            self.map_buttons[map_name] = button

        self.map1_rect = pygame.Rect(220, 200, 360, 157)
        self.map2_rect = pygame.Rect(220, 400, 360, 157)

        self.play_rect = self.buttons['play'][0].get_rect(center=(400, 200))
        self.options_rect = self.buttons['options'][0].get_rect(center=(400, 330))
        self.exit_rect = self.buttons['exit'][0].get_rect(center=(400, 460))
        self.story_rect = self.buttons['story'][0].get_rect(center=(210, 300))
        self.local_rect = self.buttons['local'][0].get_rect(center=(590, 300))

        def load_toggle_button(name):
            normal = pygame.image.load(f'assets/{name}.png').convert_alpha()
            hover = pygame.image.load(f'assets/{name}_hover.png').convert_alpha()
            down = pygame.image.load(f'assets/{name}_down.png').convert_alpha()
            size = (360, 157)
            return [
                pygame.transform.scale(normal, size),
                pygame.transform.scale(hover, size),
                pygame.transform.scale(down, size)
            ]

        self.sound_buttons = {
            True: load_toggle_button("sound_on"),
            False: load_toggle_button("sound_off")
        }
        self.music_buttons = {
            True: load_toggle_button("music_on"),
            False: load_toggle_button("music_off")
        }

        self.sound_button_rect = self.sound_buttons[True][0].get_rect(center=(210, 300))
        self.music_button_rect = self.music_buttons[True][0].get_rect(center=(590, 300))

    def draw_main_menu(self):
        mouse_pos = pygame.mouse.get_pos()
        self.collectible_manager.draw(self.screen, self.state)
        for name, rect in [('play', self.play_rect), ('options', self.options_rect), ('exit', self.exit_rect)]:
            btn = self.buttons[name]
            if rect.collidepoint(mouse_pos):
                state = 2 if self.mouse_pressed else 1
            else:
                state = 0
            self.screen.blit(btn[state], rect)

    def draw_play_menu(self):
        mouse_pos = pygame.mouse.get_pos()
        self.collectible_manager.draw(self.screen, self.state)
        for name, rect in [('story', self.story_rect), ('local', self.local_rect)]:
            btn = self.buttons[name]
            if rect.collidepoint(mouse_pos):
                state = 2 if self.mouse_pressed else 1
            else:
                state = 0
            self.screen.blit(btn[state], rect)

    def draw_map_select(self):
        map_name = self.map_folders[self.current_map_index]

        try:
            background = pygame.image.load(f"map/{map_name}/map.jpg").convert()
        except:
            try:
                background = pygame.image.load(f"map/{map_name}/map.png").convert()
            except:
                background = pygame.Surface((800, 600))
                background.fill((30, 30, 30))
        background = pygame.transform.scale(background, (800, 600))
        self.screen.blit(background, (0, 0))

        button = pygame.image.load(f"map/{map_name}/button.png").convert_alpha()
        button = pygame.transform.scale(button, (360, 157))
        self.screen.blit(button, (220, 27))

        self.screen.blit(self.player_labels[self.selecting_player], (252, 172))

        p1_vote = self.map_vote.get(1)
        p2_vote = self.map_vote.get(2)

        p1_button_path = f"map/{p1_vote}/button.png" if p1_vote else "assets/none.png"
        p2_button_path = f"map/{p2_vote}/button.png" if p2_vote else "assets/none.png"

        p1_button = pygame.image.load(p1_button_path).convert_alpha()
        p2_button = pygame.image.load(p2_button_path).convert_alpha()

        p1_button = pygame.transform.scale(p1_button, (180, 78))
        p2_button = pygame.transform.scale(p2_button, (180, 78))

        self.screen.blit(p1_button, (50, 450))
        self.screen.blit(p2_button, (570, 450))

        p1_vote = self.map_vote.get(1)
        p2_vote = self.map_vote.get(2)

        p1_button_path = f"map/{p1_vote}/button.png" if p1_vote else "assets/none.png"
        p2_button_path = f"map/{p2_vote}/button.png" if p2_vote else "assets/none.png"

        p1_button = pygame.image.load(p1_button_path).convert_alpha()
        p2_button = pygame.image.load(p2_button_path).convert_alpha()

        p1_button = pygame.transform.scale(p1_button, (180, 78))
        p2_button = pygame.transform.scale(p2_button, (180, 78))

        self.screen.blit(p1_button, (50, 450))
        self.screen.blit(p2_button, (570, 450))

    def draw_confirm_prompt(self):
        confirm_image = pygame.image.load("assets/sure.png").convert_alpha()
        confirm_image = pygame.transform.scale(confirm_image, (360, 157))
        confirm_rect = confirm_image.get_rect(center=(400, 300))
        self.screen.blit(confirm_image, confirm_rect)

    def draw_options_menu(self):
        self.collectible_manager.draw(self.screen, self.state)
        mouse_pos = pygame.mouse.get_pos()

        sound_btn = self.sound_buttons[sound.sound_on]
        if self.sound_button_rect.collidepoint(mouse_pos):
            state = 2 if self.mouse_pressed else 1
        else:
            state = 0
        self.screen.blit(sound_btn[state], self.sound_button_rect)

        music_btn = self.music_buttons[music.music_on]
        if self.music_button_rect.collidepoint(mouse_pos):
            state = 2 if self.mouse_pressed else 1
        else:
            state = 0
        self.screen.blit(music_btn[state], self.music_button_rect)

    def draw_unlock_message(self):
        if self.show_unlock_message:

            if pygame.time.get_ticks() - self.unlock_timer > self.unlock_duration:
                self.show_unlock_message = False
            else:

                overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))
                self.screen.blit(overlay, (0, 0))

                font = pygame.font.SysFont('Arial', 50)
                text = font.render("DEMON ARCHON UNLOCKED!", True, (255, 0, 0))
                text_rect = text.get_rect(center=(400, 300))
                self.screen.blit(text, text_rect)

    def handle_main_click(self, mouse_pos):
        if self.play_rect.collidepoint(mouse_pos):
            if sound.sound_on:
                sound.click_sound.play()
            self.state = "play"
        elif self.options_rect.collidepoint(mouse_pos):
            if sound.sound_on:
                sound.click_sound.play()
            self.state = "options"
        elif self.exit_rect.collidepoint(mouse_pos):
            pygame.quit()
            sys.exit()

    def draw_local_char_select(self):
        self.collectible_manager.draw(self.screen, self.state)
        char_sizes = {
            "archon_9": (350, 262),
            "nyborg": (164, 266),
            "demon_archon": (382, 262),
        }

        char_positions = {
            "archon_9": (295, 240),
            "nyborg": (325, 248),
            "demon_archon": (295, 240)
        }

        char_name = self.character_folders[self.current_char_index]
        base_path = f"characters/{char_name}"
        button = pygame.image.load(f"{base_path}/button.png").convert_alpha()
        button = pygame.transform.scale(button, (360, 157))

        idle1 = pygame.image.load(f"{base_path}/{char_name}_idle_1.png").convert_alpha()
        idle2 = pygame.image.load(f"{base_path}/{char_name}_idle_2.png").convert_alpha()

        scale_size = char_sizes.get(char_name, (164, 266))
        idle1 = pygame.transform.scale(idle1, scale_size)
        idle2 = pygame.transform.scale(idle2, scale_size)

        current_time = pygame.time.get_ticks()
        if current_time - self.idle_timer > self.idle_delay:
            self.idle_timer = current_time
            self.idle_frame = 1 - self.idle_frame

        idle = idle1 if self.idle_frame == 0 else idle2

        self.screen.blit(button, (220, 27))
        position = char_positions.get(char_name, (325, 300))
        self.screen.blit(idle, position)
        self.screen.blit(self.player_labels[self.selecting_player], (252, 172))

        if char_name == "archon_9" and self.collectible_manager.all_collected():
            try:
                hint_font = pygame.font.SysFont('Arial', 24)
                hint_text = hint_font.render("Press W for Demon Form", True, (255, 0, 0))
                self.screen.blit(hint_text, (280, 500))
            except:

                pass

    def handle_play_click(self, mouse_pos):
        if self.story_rect.collidepoint(mouse_pos):
            if sound.sound_on:
                sound.click_sound.play()

            self.clicked_button = "story"
            return True
        elif self.local_rect.collidepoint(mouse_pos):
            if sound.sound_on:
                sound.click_sound.play()
            print("Local Mode")
            self.state = "local_char_select"
            return True
        return False

    def start_story_mode(self):
        fade = pygame.Surface((800, 600))
        fade.fill((0, 0, 0))

        for alpha in range(0, 300, 5):
            fade.set_alpha(alpha)
            self.screen.blit(self.bg, (0, 0))
            self.screen.blit(self.ground, (0, 0))
            self.draw_play_menu()
            self.screen.blit(fade, (0, 0))
            pygame.display.flip()
            pygame.time.delay(20)

        self.selected_player_char = "nyborg"
        from story_mode import start_story_mode
        start_story_mode(self.selected_player_char)

    def handle_options_menu_key(self, key):
        if key == pygame.K_ESCAPE:
            self.state = "main"
        elif key == pygame.K_m:
            if sound.sound_on:
                sound.click_sound.play()
            music.toggle_music()
        elif key == pygame.K_s:
            if sound.sound_on:
                sound.click_sound.play()
            sound.toggle_sound()

    def handle_options_click(self, mouse_pos):
        if self.sound_button_rect.collidepoint(mouse_pos):
            if sound.sound_on:
                sound.click_sound.play()
            sound.toggle_sound()
        elif self.music_button_rect.collidepoint(mouse_pos):
            if sound.sound_on:
                sound.click_sound.play()
            music.toggle_music()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if self.state == "options":
                        self.handle_options_menu_key(event.key)
                    elif self.state == "play":
                        if event.key == pygame.K_ESCAPE:
                            self.state = "main"
                    elif self.state == "local_char_select":
                        if event.key == pygame.K_a:
                            if sound.sound_on:
                                sound.click_sound.play()
                            print("A")
                            self.current_char_index = (self.current_char_index - 1) % len(self.character_folders)
                        elif event.key == pygame.K_d:
                            if sound.sound_on:
                                sound.click_sound.play()
                            print("D")
                            self.current_char_index = (self.current_char_index + 1) % len(self.character_folders)

                        elif self.state == "local_char_select":
                            if event.key == pygame.K_a:
                                if sound.sound_on:
                                    sound.click_sound.play()
                                print("A")
                                self.current_char_index = (self.current_char_index - 1) % len(self.character_folders)
                            elif event.key == pygame.K_d:
                                if sound.sound_on:
                                    sound.click_sound.play()
                                print("D")
                                self.current_char_index = (self.current_char_index + 1) % len(self.character_folders)
                            elif event.key == pygame.K_w:
                                if self.character_folders[self.current_char_index] == "archon_9":
                                    if self.collectible_manager.all_collected():
                                        if "demon_archon" not in self.character_folders:
                                            self.character_folders.append("demon_archon")
                                            if sound.sound_on:
                                                sound.click_sound.play()
                                            print("Unlocked demon_archon!")
                                        else:

                                            self.current_char_index = self.character_folders.index("demon_archon")
                            elif event.key == pygame.K_RETURN:
                                if sound.sound_on:
                                    sound.click_sound.play()
                                selected = self.character_folders[self.current_char_index]
                                self.selected_chars[self.selecting_player] = selected
                                print(f"Player {self.selecting_player} selected {selected}")

                                if self.selecting_player == 1:
                                    self.selecting_player = 2
                                    self.current_char_index = 0
                                else:
                                    print("Both players selected:", self.selected_chars)
                                    self.state = "map_select"
                                    self.selecting_player = 1
                                    self.clicked_button = None
                                    self.selecting_player = 1
                            elif event.key == pygame.K_ESCAPE:
                                if self.selecting_player == 1:
                                    self.state = "play"
                                else:
                                    self.selecting_player = 1
                                    self.selected_chars[2] = None
                            elif event.key == pygame.K_RETURN:
                                if sound.sound_on:
                                    sound.click_sound.play()
                                selected = self.character_folders[self.current_char_index]
                                self.selected_chars[self.selecting_player] = selected
                                print(f"Player {self.selecting_player} selected {selected}")

                                if self.selecting_player == 1:
                                    self.selecting_player = 2
                                    self.current_char_index = 0
                                else:
                                    print("Both players selected:", self.selected_chars)
                                    self.state = "map_select"
                                    self.selecting_player = 1
                                    self.clicked_button = None
                                    self.selecting_player = 1
                            elif event.key == pygame.K_ESCAPE:
                                if self.selecting_player == 1:
                                    self.state = "play"
                                else:
                                    self.selecting_player = 1
                                    self.selected_chars[2] = None
                        elif event.key == pygame.K_RETURN:
                            if sound.sound_on:
                                sound.click_sound.play()
                            selected = self.character_folders[self.current_char_index]
                            self.selected_chars[self.selecting_player] = selected
                            print(f"Player {self.selecting_player} selected {selected}")

                            if self.selecting_player == 1:
                                self.selecting_player = 2
                                self.current_char_index = 0
                            else:

                                print("Both players selected:", self.selected_chars)

                                self.state = "map_select"
                                self.selecting_player = 1
                                self.clicked_button = None
                                self.selecting_player = 1

                        elif event.key == pygame.K_ESCAPE:
                            if self.selecting_player == 1:
                                self.state = "play"
                            else:
                                self.selecting_player = 1
                                self.selected_chars[2] = None

                    elif self.state == "map_select":
                        if event.key == pygame.K_a:
                            self.current_map_index = (self.current_map_index - 1) % len(self.map_folders)
                        elif event.key == pygame.K_d:
                            self.current_map_index = (self.current_map_index + 1) % len(self.map_folders)
                        elif event.key == pygame.K_RETURN:
                            selected_map = self.map_folders[self.current_map_index]
                            self.map_vote[self.selecting_player] = selected_map

                            if self.selecting_player == 1:
                                self.selecting_player = 2
                            else:

                                import random
                                if self.map_vote[1] == self.map_vote[2]:
                                    self.chosen_map = self.map_vote[1]
                                else:
                                    self.chosen_map = random.choice([self.map_vote[1], self.map_vote[2]])

                                self.show_confirm_prompt = True
                                self.state_after_confirm = "start_match"
                                self.state = "confirm_map"

                        elif event.key == pygame.K_ESCAPE:
                            if self.selecting_player == 1:

                                self.state = "local_char_select"
                                self.selecting_player = 2
                                self.map_vote = {1: None, 2: None}
                            else:

                                self.selecting_player = 1
                                self.map_vote[2] = None

                    elif self.state == "confirm_map":
                        if event.key == pygame.K_RETURN:

                            import local
                            local.start_match(self.selected_chars[1], self.selected_chars[2], self.chosen_map, self.collectible_manager)

                            self.state = "main"
                            self.selecting_player = 1
                            self.selected_chars = {1: None, 2: None}
                            self.map_vote = {1: None, 2: None}
                            self.current_char_index = 0
                            self.current_map_index = 0
                            self.show_confirm_prompt = False
                        elif event.key == pygame.K_ESCAPE:

                            self.state = "map_select"
                            self.selecting_player = 2
                            self.show_confirm_prompt = False

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mouse_pressed = True
                    if self.state == "main":
                        if self.play_rect.collidepoint(event.pos):
                            self.clicked_button = "play"
                        elif self.options_rect.collidepoint(event.pos):
                            self.clicked_button = "options"
                        elif self.exit_rect.collidepoint(event.pos):
                            self.clicked_button = "exit"
                    elif self.state == "play":
                        if self.story_rect.collidepoint(event.pos):
                            self.clicked_button = "story"
                        elif self.local_rect.collidepoint(event.pos):
                            self.clicked_button = "local"
                    elif self.state == "options":
                        if self.sound_button_rect.collidepoint(event.pos):
                            self.clicked_button = "sound"
                        elif self.music_button_rect.collidepoint(event.pos):
                            self.clicked_button = "music"
                    elif self.state == "map_select":
                        if self.map1_rect.collidepoint(event.pos):
                            self.clicked_button = "map1"
                        elif self.map2_rect.collidepoint(event.pos):
                            self.clicked_button = "map2"
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.mouse_pressed = False
                    if self.clicked_button:
                        if self.state == "main":
                            if self.clicked_button == "play" and self.play_rect.collidepoint(event.pos):
                                if sound.sound_on:
                                    sound.click_sound.play()
                                self.state = "play"
                            elif self.clicked_button == "options" and self.options_rect.collidepoint(event.pos):
                                if sound.sound_on:
                                    sound.click_sound.play()
                                self.state = "options"
                            elif self.clicked_button == "exit" and self.exit_rect.collidepoint(event.pos):
                                pygame.quit()
                                sys.exit()
                        elif self.state == "play":
                            if self.clicked_button == "story" and self.story_rect.collidepoint(event.pos):
                                if sound.sound_on:
                                    sound.click_sound.play()
                                print("Story Mode")
                                self.start_story_mode()
                            elif self.clicked_button == "local" and self.local_rect.collidepoint(event.pos):
                                if sound.sound_on:
                                    sound.click_sound.play()
                                if sound.sound_on:
                                    sound.choose_sound.play()
                                self.state = "local_char_select"
                        elif self.state == "options":
                            if self.clicked_button == "sound" and self.sound_button_rect.collidepoint(event.pos):
                                if sound.sound_on:
                                    sound.click_sound.play()
                                sound.toggle_sound()
                            elif self.clicked_button == "music" and self.music_button_rect.collidepoint(event.pos):
                                if sound.sound_on:
                                    sound.click_sound.play()
                                music.toggle_music()

                        elif self.state == "map_select":

                            if self.clicked_button and hasattr(self, f"{self.clicked_button}_rect") and getattr(self,
                                                                                                                f"{self.clicked_button}_rect").collidepoint(
                                    event.pos):

                                map_index = int(self.clicked_button.replace("map", "")) - 1
                                if map_index < len(self.map_folders):
                                    selected_map = self.map_folders[map_index]
                                    self.map_vote[self.selecting_player] = selected_map

                                    if self.selecting_player == 1:
                                        self.selecting_player = 2
                                    else:

                                        import random
                                        if self.map_vote[1] == self.map_vote[2]:
                                            self.chosen_map = self.map_vote[1]
                                        else:
                                            self.chosen_map = random.choice([self.map_vote[1], self.map_vote[2]])

                                        print("Map selected:", self.chosen_map)
                                        self.show_confirm_prompt = True
                                        self.state_after_confirm = "start_match"
                                        self.state = "confirm_map"

                            self.clicked_button = None

                    self.clicked_button = None

            self.screen.fill((0, 0, 0))
            self.screen.blit(self.bg, (0, 0))
            self.screen.blit(self.ground, (0, 0))

            player_rect = pygame.Rect(pygame.mouse.get_pos(), (50, 50))

            self.collectible_manager.update(player_rect, self.state)

            if self.collectible_manager.all_collected():
                print("All collectibles collected!")

            if self.state == "main":
                self.draw_main_menu()
            elif self.state == "play":
                self.draw_play_menu()
            elif self.state == "options":
                self.draw_options_menu()
            elif self.state == "local_char_select":
                self.draw_local_char_select()
            elif self.state == "map_select":
                self.draw_map_select()
            elif self.state == "confirm_map":
                self.draw_map_select()
                self.draw_confirm_prompt()

            pygame.display.flip()
            self.clock.tick(60)