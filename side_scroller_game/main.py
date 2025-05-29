import pygame
import random
import sys
import os

# Initialize pygame
pygame.init()

# Set up paths
BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Side Scroller Game")

# Colors and Constants
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
FPS = 60

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# Load background
background_img = pygame.image.load(os.path.join(ASSETS_DIR, "background.png"))

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join(ASSETS_DIR, "player.png"))
        self.rect = self.image.get_rect()
        self.rect.center = (100, HEIGHT - 100)
        self.speed = 5
        self.jump_power = 15
        self.vel_y = 0
        self.on_ground = True
        self.health = 100
        self.lives = 3
        self.score = 0

    def update(self, keys):
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_RIGHT]:
            dx = self.speed
        self.rect.x += dx

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -self.jump_power
            self.on_ground = False

        self.vel_y += 1  # gravity
        self.rect.y += self.vel_y

        if self.rect.bottom > HEIGHT - 50:
            self.rect.bottom = HEIGHT - 50
            self.on_ground = True

    def shoot(self):
        bullet = Projectile(self.rect.centerx + 20, self.rect.centery)
        projectiles.add(bullet)

    def draw_health_bar(self):
        pygame.draw.rect(screen, RED, (20, 20, 100, 10))
        pygame.draw.rect(screen, GREEN, (20, 20, self.health, 10))

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(os.path.join(ASSETS_DIR, "projectile.png"))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > WIDTH:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, health=30):
        super().__init__()
        self.image = pygame.image.load(os.path.join(ASSETS_DIR, "enemy.png"))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.health = health

    def update(self):
        self.rect.x -= 2
        if self.health <= 0:
            player.score += 10
            self.kill()

class BossEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, health=200)
        self.image = pygame.Surface((100, 100))
        self.image.fill((139, 0, 0))

    def draw_health_bar(self):
        bar_width = 200
        bar_height = 20
        x = WIDTH // 2 - bar_width // 2
        y = 50
        pygame.draw.rect(screen, RED, (x, y, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (x, y, bar_width * (self.health / 200), bar_height))

class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, kind="health"):
        super().__init__()
        path = "collectible_health.png" if kind == "health" else "collectible_life.png"
        self.image = pygame.image.load(os.path.join(ASSETS_DIR, path))
        self.kind = kind
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def apply(self, player):
        if self.kind == "health":
            player.health = min(100, player.health + 30)
        elif self.kind == "life":
            player.lives += 1
        player.score += 5
        self.kill()

# Level Management
def spawn_enemies(level):
    if level == 3:
        boss = BossEnemy(WIDTH + 200, HEIGHT - 150)
        enemies.add(boss)
    else:
        for _ in range(level * 3):
            enemy = Enemy(random.randint(WIDTH + 100, WIDTH + 800), HEIGHT - 70)
            enemies.add(enemy)

def spawn_collectibles(level):
    for _ in range(level):
        collectible = Collectible(random.randint(WIDTH + 100, WIDTH + 800), HEIGHT - 80, "health")
        collectibles.add(collectible)

# Screen
def game_over_screen():
    screen.fill((0, 0, 0))
    text = font.render("Game Over - Press R to Restart", True, WHITE)
    screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                main()

def intro_screen():
    screen.fill((0, 0, 0))
    title = font.render("Welcome to the Side Scroller Game!", True, WHITE)
    instructions = font.render("Press ENTER to Start", True, WHITE)
    screen.blit(title, (WIDTH // 2 - 200, HEIGHT // 2 - 40))
    screen.blit(instructions, (WIDTH // 2 - 100, HEIGHT // 2 + 10))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False

# Main Game Function
def main():
    global player, projectiles, enemies, collectibles

    player = Player()
    projectiles = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    collectibles = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player)

    level = 1
    spawn_enemies(level)
    spawn_collectibles(level)

    running = True
    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                player.shoot()

        player.update(keys)
        projectiles.update()
        enemies.update()

        # Collision: bullets vs enemies
        for bullet in projectiles:
            hit = pygame.sprite.spritecollide(bullet, enemies, False)
            for e in hit:
                e.health -= 10
                bullet.kill()

        # Collision: player vs enemy
        for enemy in enemies:
            if player.rect.colliderect(enemy.rect):
                player.health -= 1
                if player.health <= 0:
                    player.lives -= 1
                    player.health = 100
                    if player.lives <= 0:
                        game_over_screen()

        for c in pygame.sprite.spritecollide(player, collectibles, False):
            c.apply(player)

        if not enemies:
            if level >= 3:
                game_over_screen()
            else:
                level += 1
                spawn_enemies(level)
                spawn_collectibles(level)

        screen.blit(background_img, (0, 0))
        all_sprites.draw(screen)
        projectiles.draw(screen)
        enemies.draw(screen)
        collectibles.draw(screen)
        player.draw_health_bar()
        screen.blit(font.render(f"Score: {player.score}", True, WHITE), (20, 40))
        screen.blit(font.render(f"Lives: {player.lives}", True, WHITE), (20, 60))
        screen.blit(font.render(f"Level: {level}", True, WHITE), (20, 80))

        for enemy in enemies:
            if isinstance(enemy, BossEnemy):
                enemy.draw_health_bar()

        pygame.display.flip()

    pygame.quit()

# Run Game
if __name__ == "__main__":
    intro_screen()
    main()
