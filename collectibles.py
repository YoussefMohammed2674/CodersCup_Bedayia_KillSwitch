import pygame

gold_statue = pygame.image.load('assets/gold_statue.png')

class Collectible:
    def __init__(self, pos, image):
        self.rect = image.get_rect(topleft=pos)
        self.image = image
        self.found = False

    def draw(self, screen):
        if not self.found:
            screen.blit(self.image, self.rect)

    def check_collision(self, player_rect):
        if not self.found and self.rect.colliderect(player_rect):
            self.found = True
            return True
        return False

class CollectibleManager:
    def __init__(self, collectible_images, collectible_positions, state_mappings):
        self.collectibles = [Collectible(pos, img) for pos, img in zip(collectible_positions, collectible_images)]
        self.state_mappings = state_mappings
        self.collected_count = 0

    def update(self, player_rect, current_state):
        for i, collectible in enumerate(self.collectibles):
            if self.state_mappings and current_state in self.state_mappings:
                index = self.state_mappings[current_state]
                if i == index:
                    collectible.check_collision(player_rect)

    def all_collected(self):
        return all(c.found for c in self.collectibles)

    def draw(self, screen, current_state):
        if self.state_mappings and current_state in self.state_mappings:
            index = self.state_mappings[current_state]
            self.collectibles[index].draw(screen)