import pygame


class Board:
    def __init__(self, x, y, field_width, field_height, surface):
        self.board_border = pygame.Rect((x, y), (field_width * 10 + 2, field_height * 10 + 2))
        self.surface = surface
        self.fields_borders = []
        self.fields = []
        for i in range(10):
            self.fields_borders.append([])
            self.fields.append([])
            for j in range(10):
                self.fields_borders[i].append(pygame.Rect((x + 1 + i * field_width, y + 1 + j * field_height),
                                                         (field_width, field_height)))
                self.fields[i].append(self.fields_borders[i][j].inflate(-2, -2).clamp(self.fields_borders[i][j]))

    def draw(self):
        pygame.draw.rect(self.surface, (0, 0, 0), self.board_border, width=1)
        for i in range(10):
            for j in range(10):
                pygame.draw.rect(self.surface, (0, 0, 0), self.fields_borders[i][j], width=1)
                pygame.draw.rect(self.surface, (22, 158, 211, 128), self.fields[i][j])
