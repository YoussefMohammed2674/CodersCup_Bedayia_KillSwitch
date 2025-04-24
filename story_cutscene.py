import pygame
import sys

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    lines.append(current_line.strip())
    return lines

def render_typewriter(screen, bg, box_ui, portrait, name_text, line, font, name_font, clock):

    text_area_width = 560
    text_start_x = 115
    text_start_y = 400
    line_spacing = 30

    wrapped = wrap_text(line, font, text_area_width)

    screen.blit(bg, (0, 0))
    screen.blit(portrait, (140, 160))
    screen.blit(box_ui, (0, 0))
    name_surf = name_font.render(name_text, True, 'black')
    name_rect = name_surf.get_rect(topleft=(170, 320))
    screen.blit(name_surf, name_rect)

    skip = False
    for i, text_line in enumerate(wrapped):
        typed = ""
        for char in text_line:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    skip = True

            if skip:
                break

            typed += char
            screen.blit(bg, (0, 0))
            screen.blit(portrait, (140, 160))
            screen.blit(box_ui, (0, 0))
            screen.blit(name_surf, name_rect)

            for j in range(i):
                prev_surf = font.render(wrapped[j], True, 'black')
                prev_rect = prev_surf.get_rect(topleft=(text_start_x, text_start_y + (j * line_spacing)))
                screen.blit(prev_surf, prev_rect)

            line_surf = font.render(typed, True, 'black')
            line_rect = line_surf.get_rect(topleft=(text_start_x, text_start_y + (i * line_spacing)))
            screen.blit(line_surf, line_rect)

            pygame.display.flip()
            clock.tick(60)
            pygame.time.delay(20)

        if skip:
            break

    screen.blit(bg, (0, 0))
    screen.blit(portrait, (140, 160))
    screen.blit(box_ui, (0, 0))
    screen.blit(name_surf, name_rect)

    for j, text_line in enumerate(wrapped):
        text_surf = font.render(text_line, True, 'black')
        text_rect = text_surf.get_rect(topleft=(text_start_x, text_start_y + (j * line_spacing)))
        screen.blit(text_surf, text_rect)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
                waiting = False
        clock.tick(60)

def show_cutscene(screen, clock, font, name_font):
    dialogues = [
        ("archon_9", "So... you've made it this far."),
        ("nyborg", "I'm not here for your approval. I'm here to end this."),
        ("archon_9", "End this? You think you're the hero in this tale?"),
        ("nyborg", "You're the last obstacle standing between me and peace."),
        ("archon_9", "Then come. Let's see if you're worthy of the final chapter.")
    ]

    display_names = {
        "archon_9": "Archon",
        "nyborg": "Kryos"
    }

    bg = pygame.transform.scale(pygame.image.load("assets/story_bg.jpg"), (800, 600))
    box_ui = pygame.image.load("assets/cutscene.png").convert_alpha()
    portraits = {
        "archon_9": pygame.transform.scale(pygame.image.load("characters/archon_9/portrait.png").convert_alpha(), (280, 213)),
        "nyborg": pygame.transform.scale(pygame.image.load("characters/nyborg/portrait.png").convert_alpha(), (164, 266))
    }

    for speaker, line in dialogues:
        render_typewriter(
            screen,
            bg,
            box_ui,
            portraits[speaker],
            display_names.get(speaker, speaker),
            line,
            font,
            name_font,
            clock
        )

    from story_wave1 import start_wave_1
    start_wave_1(screen)