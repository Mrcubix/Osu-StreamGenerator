import pygame
import math

class circles(pygame.sprite.Sprite): # Initalise a new circle with set position and size (defined by cs)

    def __init__(self, x, y, cs: int, draw=True, surface=None):
        self.x = x
        self.y = y
        if draw:
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.image.load("./assets/circle.png").convert_alpha()
            self.size = (int(round(2.25*(109-(9*cs)))),int(round(2.25*(109-(9*cs)))))
            self.image = pygame.transform.scale(self.image, self.size)
            self.Draw(surface)

    def transparency(self, surface: pygame.Surface):
        temp_surface = pygame.Surface(self.size, pygame.SRCALPHA)
        self.circle = pygame.draw.circle(temp_surface, (255, 255, 255, 100), (self.size[0]//2, self.size[1]//2), int(self.size[0]/2)-5)
        topleft = self.x - self.size[0] // 2, self.y - self.size[1] // 2
        surface.blit(temp_surface, topleft)

    def Draw(self, surface: pygame.Surface):
        self.transparency(surface)
        surface.blit(self.image,(self.x-((self.size[0])/2),self.y-((self.size[1])/2)))
        pygame.display.update()

    def Remove(self):
        del self

    def isClicked(self):
        mouse_pos = pygame.mouse.get_pos()
        if math.hypot(mouse_pos[0] - self.x, mouse_pos[1] - self.y) < self.size[0]//2:
            return True
        return False