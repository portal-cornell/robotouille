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
        self.clicked = False
        self.visible = False

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))
        surface.blit(self.text, (self.text_x, self.text_y))
        self.visible = True

    def is_clicked(self):
        action = False
        self.clicked = False # for reset
        x,y = pygame.mouse.get_pos()
        x = x - 520 # offset
        _, _, width, height = self.rect
        x_lower, y_lower = self.rect.topleft
        x_upper, y_upper = (x_lower + width, y_lower + height)
        if (x >= x_lower and x <= x_upper) and (y >= y_lower and y <= y_upper):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False and self.visible == True:
                self.clicked = True
                action = True

        return action

    def set_visibility(self, toggle_value):
        self.visible = toggle_value

    def has_clicked(self):
        if self.clicked:
            return True
        return False