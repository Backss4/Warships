import pygame
from game.constants import FieldStatus

X_CONST = 'ABCDEFGHIJK'

class Board:
    def __init__(self, x, y, field_width, field_height, surface, msg=None):
        self.board_border = pygame.Rect((x + field_width, y + field_height), (field_width * 10 + 2, field_height * 10 + 2))
        self.font = pygame.font.SysFont(None, 48)
        self.surface = surface
        self.fields_borders = []
        self.fields = []
        self.field_status = [[FieldStatus.EMPTY for i in range(10)] for i in range(10)]
        self.x_coords = []
        self.y_coords = []
        self.boom_image = pygame.transform.scale(pygame.image.load('boom.png'), (field_width, field_height))
        self.splash_image = pygame.transform.scale(pygame.image.load('splash.png'), (field_width, field_height))
        self.ship_image = self.font.render('o', True, (255, 255, 255))
        #self.font.set_bold(True)
        self.text = None
        self.text_pos = None
        if msg is not None:
            self.text = self.font.render(msg, True, (255, 255, 255))
            self.text_pos = (x + (12 * field_width) / 2 - self.text.get_width() / 2, y + 20 + 11 * field_height)
        for i in range(10):
            self.fields_borders.append([])
            self.fields.append([])
            for j in range(10):
                self.fields_borders[i].append(pygame.Rect((x + 1 + (i + 1) * field_width, y + 1 + (j + 1) * field_height),
                                                         (field_width, field_height)))
                self.fields[i].append(self.fields_borders[i][j].inflate(-2, -2).clamp(self.fields_borders[i][j]))
        for i in range(10):
            letter = self.font.render(X_CONST[i], True, (255, 255, 255))
            coords = (x + 1 + (i + 1) * field_width + field_width / 2 - letter.get_width() / 2,
                      y + 1 + field_height - letter.get_height())
            self.x_coords.append((letter, coords))
            letter = self.font.render(str(i + 1), True, (255, 255, 255))
            coords = (x + field_width / 2 - letter.get_width() / 2,
                        y + 1 + (i + 1) * field_height + field_height - letter.get_height())
            print(letter.get_height())
            self.y_coords.append((letter, coords))

    def set_field_status(self, x, y, status):
        self.field_status[x][y] = status

    def draw(self):
        pygame.draw.rect(self.surface, (0, 0, 0), self.board_border, width=1)
        for i in range(10):
            self.surface.blit(self.x_coords[i][0], self.x_coords[i][1])
            self.surface.blit(self.y_coords[i][0], self.y_coords[i][1])
            for j in range(10):
                pygame.draw.rect(self.surface, (0, 0, 0), self.fields_borders[i][j], width=1)
                if self.field_status[i][j] == FieldStatus.EMPTY:
                    pygame.draw.rect(self.surface, (22, 158, 211), self.fields[i][j])
                elif self.field_status[i][j] == FieldStatus.SHIP:
                    pygame.draw.rect(self.surface, (0, 0, 0), self.fields[i][j])
                    new_rect = self.ship_image.get_rect().clamp(self.fields[i][j]).move((self.fields[i][j].w - self.ship_image.get_width()) / 2,
                                                                                        (self.fields[i][j].w - self.ship_image.get_height()) / 2)
                    self.surface.blit(self.ship_image, new_rect)
                elif self.field_status[i][j] == FieldStatus.DESTROYED:
                    pygame.draw.rect(self.surface, (240, 128, 128), self.fields[i][j])
                    self.surface.blit(self.boom_image, self.fields[i][j])
                elif self.field_status[i][j] == FieldStatus.MISSED:
                    pygame.draw.rect(self.surface, (176, 224, 230), self.fields[i][j])
                    self.surface.blit(self.splash_image, self.fields[i][j])
        if self.text is not None:
            self.surface.blit(self.text, self.text_pos)
