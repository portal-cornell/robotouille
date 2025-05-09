import pygame

class Button():
    def __init__(self, x, y, image, scale, text, text_x, text_y):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.text = text
        self.text_x = text_x
        self.text_y = text_y

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))
        surface.blit(self.text, (self.text_x, self.text_y))