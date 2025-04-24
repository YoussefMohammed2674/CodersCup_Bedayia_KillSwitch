music_on = True

def toggle_music():
    global music_on
    music_on = not music_on
    if music_on:
        print("Music ON")
        # pygame.mixer.music.play(-1)
    else:
        print("Music OFF")
        # pygame.mixer.music.stop()
