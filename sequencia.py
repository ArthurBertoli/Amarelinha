import pygame
import random
from settings import path_assets, resource_path, getModo
from os.path import join

class Sequencia():
    def __init__(self, x: int, y: int, bpm: int, offset: float = 0.0):
        self.next = -1
        self.pontos = [[0,0], # Copas   / NO (Total, Acertos)
                       [0,0], # Paus    / SO
                       [0,0], # Ouros   / SL
                       [0,0]] # Espadas / NL
        self.sortear()

        # Tamanho fixo do "bloco" que representa a nota (sem imagem de seta)
        self.rect = pygame.Rect(0, 0, 80, 80)
        self.rect.center = (x, y)

        self.fonte = pygame.font.SysFont("aakar", 40)

        # Calculate velocity based on BPM (pixels per second)
        self.speed = bpm * 1.125
        self.defaultSpeed = self.speed

        self.bpm = bpm
        self.offset = offset
        offset_seconds = (60.0 / float(self.bpm)) * 4.0 * self.offset
        self.offset_remaining = max(0.0, float(offset_seconds))
        self.started = False

    def sortear(self):
        ''' Sortea direções aleatórias'''
        modo = getModo()
        if modo == 'esquerdo':
            self.next = random.choice([1,2])
        elif modo == 'direito':
            self.next = random.choice([3,4])
        else:
            atual = self.next
            while self.next == atual:
                self.next = random.randint(1,4)

    def update(self, dt: float):
        if not self.started:
            self.offset_remaining -= dt
            if self.offset_remaining <= 0:
                self.started = True
            else:
                return
        self.rect.y += int(self.speed * dt)

    def reset(self):
        self.rect.y = -200
        self.sortear()

    def errou(self):
        self.pontos[self.next-1][0] += 1
        self.reset()

    def acertou(self):
        self.pontos[self.next-1][0] += 1
        self.pontos[self.next-1][1] += 1
        self.reset()

    def render(self, surface: pygame.surface.Surface):
        # Bloco simples no lugar da seta
        pygame.draw.rect(surface, (255, 255, 255), self.rect, border_radius=8)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, width=3, border_radius=8)

        texto = self.fonte.render(str(self.next), True, (0, 0, 0))
        texto_rect = texto.get_rect(center=self.rect.center)
        surface.blit(texto, texto_rect)

    def changeSpeed(self, factor: int, step=0.2):
        self.speed = self.defaultSpeed + self.defaultSpeed * factor * step

    def hardreset(self):
        self.reset()
        self.pontos = [[0,0],
                       [0,0],
                       [0,0],
                       [0,0]]
        self.changeSpeed(0)

    def getPercentage(self, idx: int) -> int:
        return round(self.pontos[idx][1] / self.pontos[idx][0] * 100) if self.pontos[idx][0] != 0 else 100