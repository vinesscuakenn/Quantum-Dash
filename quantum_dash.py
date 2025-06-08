import pygame
import random
import math
import asyncio
import platform
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quantum Dash")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
RED = (255, 0, 0)
PURPLE = (128, 0, 128)

# Game settings
PLAYER_SIZE = 20
ENEMY_SIZE = 25
CORE_SIZE = 15
PLAYER_SPEED = 5
ENEMY_SPEED = 2
TELEPORT_DISTANCE = 100
TELEPORT_COOLDOWN = 500  # milliseconds
FPS = 60

class Player:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.last_teleport = 0

    def move(self, keys: pygame.key.ScancodeWrapper):
        if keys[pygame.K_LEFT] and self.x > PLAYER_SIZE:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.x < WIDTH - PLAYER_SIZE:
            self.x += PLAYER_SPEED
        if keys[pygame.K_UP] and self.y > PLAYER_SIZE:
            self.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN] and self.y < HEIGHT - PLAYER_SIZE:
            self.y += PLAYER_SPEED

    def teleport(self, mouse_pos: Tuple[int, int], current_time: int) -> bool:
        if current_time - self.last_teleport < TELEPORT_COOLDOWN:
            return False
        distance = math.hypot(mouse_pos[0] - self.x, mouse_pos[1] - self.y)
        if distance <= TELEPORT_DISTANCE:
            self.x, self.y = mouse_pos
            self.last_teleport = current_time
            return True
        return False

    def draw(self):
        pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), PLAYER_SIZE // 2)

class Enemy:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.angle = random.uniform(0, 2 * math.pi)

    def move_towards(self, target_x: int, target_y: int):
        angle = math.atan2(target_y - self.y, target_x - self.x)
        self.x += math.cos(angle) * ENEMY_SPEED
        self.y += math.sin(angle) * ENEMY_SPEED

    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), ENEMY_SIZE // 2)

class Core:
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)

    def draw(self):
        pygame.draw.circle(screen, PURPLE, (int(self.x), int(self.y)), CORE_SIZE // 2)

class Game:
    def __init__(self):
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        self.enemies: List[Enemy] = []
        self.cores: List[Core] = []
        self.score = 0
        self.font = pygame.font.SysFont("arial", 24)
        self.clock = pygame.time.Clock()
        self.enemy_spawn_rate = 0.03
        self.core_spawn_rate = 0.02

    def spawn_entities(self):
        if random.random() < self.enemy_spawn_rate:
            self.enemies.append(Enemy())
        if random.random() < self.core_spawn_rate and len(self.cores) < 3:
            self.cores.append(Core())

    def check_collisions(self) -> bool:
        player_rect = pygame.Rect(self.player.x - PLAYER_SIZE // 2, self.player.y - PLAYER_SIZE // 2, PLAYER_SIZE, PLAYER_SIZE)
        for core in self.cores[:]:
            core_rect = pygame.Rect(core.x - CORE_SIZE // 2, core.y - CORE_SIZE // 2, CORE_SIZE, CORE_SIZE)
            if player_rect.colliderect(core_rect):
                self.cores.remove(core)
                self.score += 10
        for enemy in self.enemies:
            enemy_rect = pygame.Rect(enemy.x - ENEMY_SIZE // 2, enemy.y - ENEMY_SIZE // 2, ENEMY_SIZE, ENEMY_SIZE)
            if player_rect.colliderect(enemy_rect):
                return False
        return True

    def draw(self):
        screen.fill(BLACK)
        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()
        for core in self.cores:
            core.draw()
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        cooldown = (TELEPORT_COOLDOWN - (pygame.time.get_ticks() - self.player.last_teleport)) / 1000
        if cooldown > 0:
            cooldown_text = self.font.render(f"Teleport: {cooldown:.1f}s", True, WHITE)
            screen.blit(cooldown_text, (10, 40))

async def main():
    game = Game()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                game.player.teleport(event.pos, pygame.time.get_ticks())

        keys = pygame.key.get_pressed()
        game.player.move(keys)
        game.spawn_entities()
        for enemy in game.enemies:
            enemy.move_towards(game.player.x, game.player.y)
        if not game.check_collisions():
            running = False
        game.draw()
        pygame.display.flip()
        game.clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

    pygame.quit()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
