import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen setup
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Animal Hero vs Human Enemies")

# Colors
BACKGROUND = (135, 206, 235)
GROUND_COLOR = (34, 139, 34)
RED = (220, 60, 60)
GREEN = (60, 180, 75)
BLUE = (65, 105, 225)
YELLOW = (255, 215, 0)
PURPLE = (180, 80, 220)
BROWN = (139, 69, 19)
BLACK = (30, 30, 30)
WHITE = (240, 240, 240)

# Fonts
font_large = pygame.font.SysFont("Arial", 48, bold=True)
font_medium = pygame.font.SysFont("Arial", 36)
font_small = pygame.font.SysFont("Arial", 24)

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
LEVEL_COMPLETE = 3

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.jump_power = -15
        self.gravity = 0.8
        self.is_jumping = False
        self.direction = 1  # 1 for right, -1 for left
        self.health = 100
        self.lives = 3
        self.score = 0
        self.shoot_cooldown = 0
        self.hurt_timer = 0

    def move(self, platforms):
        # Apply gravity
        self.vel_y += self.gravity
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Check platform collisions
        on_ground = False
        for platform in platforms:
            if self.check_collision(platform):
                # Bottom collision
                if self.vel_y > 0 and self.y + self.height > platform.y and self.y < platform.y:
                    self.y = platform.y - self.height
                    self.vel_y = 0
                    on_ground = True
                # Top collision
                elif self.vel_y < 0 and self.y < platform.y + platform.height and self.y + self.height > platform.y + platform.height:
                    self.y = platform.y + platform.height
                    self.vel_y = 0
                # Horizontal collisions
                if self.vel_x > 0 and self.x + self.width > platform.x and self.x < platform.x:
                    self.x = platform.x - self.width
                elif self.vel_x < 0 and self.x < platform.x + platform.width and self.x + self.width > platform.x + platform.width:
                    self.x = platform.x + platform.width
        
        # Boundary checks
        if self.x < 0:
            self.x = 0
        if self.x > 5000 - self.width:
            self.x = 5000 - self.width
        if self.y > HEIGHT:
            self.health = 0
        
        # Update jumping status
        if on_ground:
            self.is_jumping = False
        
        # Update cooldowns
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.hurt_timer > 0:
            self.hurt_timer -= 1

    def jump(self):
        if not self.is_jumping:
            self.vel_y = self.jump_power
            self.is_jumping = True

    def shoot(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 15
            return Projectile(self.x + self.width//2, self.y + self.height//2, 10 * self.direction, 0, "player")
        return None

    def check_collision(self, obj):
        return (self.x < obj.x + obj.width and
                self.x + self.width > obj.x and
                self.y < obj.y + obj.height and
                self.y + self.height > obj.y)

    def draw(self, screen, camera_x):
        # Draw player (animal hero - fox)
        draw_x = self.x - camera_x
        
        # Body
        pygame.draw.ellipse(screen, (255, 140, 0), (draw_x, self.y, self.width, self.height))
        
        # Head
        head_size = 30
        pygame.draw.circle(screen, (255, 140, 0), (draw_x + self.width//2 + (10 * self.direction), self.y - 10), head_size)
        
        # Ears
        pygame.draw.polygon(screen, (255, 100, 0), [
            (draw_x + self.width//2 - 10, self.y - 35),
            (draw_x + self.width//2 - 25, self.y - 50),
            (draw_x + self.width//2, self.y - 40)
        ])
        pygame.draw.polygon(screen, (255, 100, 0), [
            (draw_x + self.width//2 + 10, self.y - 35),
            (draw_x + self.width//2 + 25, self.y - 50),
            (draw_x + self.width//2, self.y - 40)
        ])
        
        # Eyes
        eye_offset = 5 * self.direction
        pygame.draw.circle(screen, BLACK, (draw_x + self.width//2 + eye_offset - 5, self.y - 15), 5)
        pygame.draw.circle(screen, BLACK, (draw_x + self.width//2 + eye_offset + 5, self.y - 15), 5)
        
        # Tail
        pygame.draw.ellipse(screen, (255, 100, 0), (draw_x - 15, self.y + 10, 30, 15))

class Projectile:
    def __init__(self, x, y, vel_x, vel_y, owner):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.radius = 6
        self.owner = owner  # "player" or "enemy"
        self.color = YELLOW if owner == "player" else RED

    def move(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.3  # Gravity effect

    def is_off_screen(self, camera_x):
        return (self.x < camera_x - 100 or 
                self.x > camera_x + WIDTH + 100 or
                self.y > HEIGHT + 100)

    def draw(self, screen, camera_x):
        pygame.draw.circle(screen, self.color, (self.x - camera_x, self.y), self.radius)
        pygame.draw.circle(screen, WHITE, (self.x - camera_x, self.y), self.radius - 2)

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.vel_x = 0
        self.vel_y = 0
        self.enemy_type = enemy_type  # "normal", "shooter", "boss"
        self.health = 50 if enemy_type == "normal" else 70 if enemy_type == "shooter" else 300
        self.max_health = self.health
        self.speed = random.choice([-1.5, -1, 1, 1.5])
        self.shoot_cooldown = random.randint(60, 120)
        self.direction = -1 if random.random() < 0.5 else 1
        self.move_timer = random.randint(30, 90)
        self.hurt_timer = 0

    def move(self, platforms, player_x):
        # Simple AI
        self.move_timer -= 1
        if self.move_timer <= 0:
            self.speed = random.choice([-1.5, -1, 1, 1.5])
            self.move_timer = random.randint(30, 90)
            self.direction = -1 if self.speed < 0 else 1
        
        # Move toward player if boss
        if self.enemy_type == "boss":
            if player_x < self.x:
                self.speed = -2
                self.direction = -1
            else:
                self.speed = 2
                self.direction = 1
        
        # Apply movement
        self.vel_x = self.speed
        self.vel_y += 0.8  # Gravity
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Platform collisions
        for platform in platforms:
            if self.check_collision(platform):
                # Bottom collision
                if self.vel_y > 0 and self.y + self.height > platform.y and self.y < platform.y:
                    self.y = platform.y - self.height
                    self.vel_y = 0
                # Top collision
                elif self.vel_y < 0 and self.y < platform.y + platform.height and self.y + self.height > platform.y + platform.height:
                    self.y = platform.y + platform.height
                    self.vel_y = 0
                # Horizontal collisions
                if self.vel_x > 0 and self.x + self.width > platform.x and self.x < platform.x:
                    self.x = platform.x - self.width
                    self.speed *= -1
                elif self.vel_x < 0 and self.x < platform.x + platform.width and self.x + self.width > platform.x + platform.width:
                    self.x = platform.x + platform.width
                    self.speed *= -1
        
        # Boundary checks
        if self.x < 0:
            self.x = 0
            self.speed *= -1
        if self.x > 5000 - self.width:
            self.x = 5000 - self.width
            self.speed *= -1
        
        # Update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.hurt_timer > 0:
            self.hurt_timer -= 1

    def shoot(self, player_x, player_y):
        if self.enemy_type in ["shooter", "boss"] and self.shoot_cooldown == 0:
            self.shoot_cooldown = 90 if self.enemy_type == "shooter" else 45
            
            # Calculate direction to player
            dx = player_x - self.x
            dy = player_y - self.y
            dist = max(1, math.sqrt(dx*dx + dy*dy))
            
            # Normalize and set velocity
            vel_x = 8 * dx / dist
            vel_y = 8 * dy / dist
            
            return Projectile(self.x + self.width//2, self.y + self.height//2, vel_x, vel_y, "enemy")
        return None

    def check_collision(self, obj):
        return (self.x < obj.x + obj.width and
                self.x + self.width > obj.x and
                self.y < obj.y + obj.height and
                self.y + self.height > obj.y)

    def draw(self, screen, camera_x):
        draw_x = self.x - camera_x
        
        # Draw based on enemy type
        if self.enemy_type == "normal":
            # Human soldier
            # Body
            pygame.draw.rect(screen, BLUE, (draw_x, self.y + 20, self.width, self.height - 20))
            # Head
            pygame.draw.circle(screen, (255, 220, 180), (draw_x + self.width//2, self.y + 10), 15)
            # Helmet
            pygame.draw.rect(screen, (100, 100, 120), (draw_x + 5, self.y, self.width - 10, 15))
            
        elif self.enemy_type == "shooter":
            # Human shooter
            # Body
            pygame.draw.rect(screen, RED, (draw_x, self.y + 20, self.width, self.height - 20))
            # Head
            pygame.draw.circle(screen, (255, 220, 180), (draw_x + self.width//2, self.y + 10), 15)
            # Helmet with visor
            pygame.draw.rect(screen, (60, 60, 80), (draw_x + 5, self.y, self.width - 10, 15))
            pygame.draw.rect(screen, (100, 200, 255, 100), (draw_x + 10, self.y + 3, self.width - 20, 8))
            
        else:  # boss
            # Big armored enemy
            # Body
            pygame.draw.rect(screen, PURPLE, (draw_x - 10, self.y + 20, self.width + 20, self.height - 20))
            # Head
            pygame.draw.circle(screen, (255, 220, 180), (draw_x + self.width//2, self.y + 5), 20)
            # Armor
            pygame.draw.rect(screen, (80, 80, 100), (draw_x - 15, self.y + 40, self.width + 30, 30))
            pygame.draw.rect(screen, (80, 80, 100), (draw_x - 5, self.y, self.width + 10, 25))
            
            # Health bar
            bar_width = 80
            pygame.draw.rect(screen, (100, 100, 100), (draw_x + self.width//2 - bar_width//2, self.y - 30, bar_width, 12))
            pygame.draw.rect(screen, RED, (draw_x + self.width//2 - bar_width//2, self.y - 30, bar_width * self.health / self.max_health, 12))
        
        # Health bar for normal enemies
        if self.enemy_type != "boss":
            bar_width = 40
            pygame.draw.rect(screen, (100, 100, 100), (draw_x + self.width//2 - bar_width//2, self.y - 20, bar_width, 8))
            pygame.draw.rect(screen, RED, (draw_x + self.width//2 - bar_width//2, self.y - 20, bar_width * self.health / self.max_health, 8))
        
        # Draw hurt effect
        if self.hurt_timer > 0:
            pygame.draw.rect(screen, (255, 150, 150), (draw_x, self.y, self.width, self.height), 3)

class Collectible:
    def __init__(self, x, y, collectible_type):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.collectible_type = collectible_type  # "health", "life", "coin"
        self.bounce = 0
        self.bounce_dir = 1

    def update(self):
        # Bouncing animation
        self.bounce += 0.1 * self.bounce_dir
        if self.bounce > 0.5:
            self.bounce_dir = -1
        elif self.bounce < -0.5:
            self.bounce_dir = 1

    def draw(self, screen, camera_x):
        draw_x = self.x - camera_x
        draw_y = self.y + self.bounce * 5
        
        if self.collectible_type == "health":
            # Health pack
            pygame.draw.rect(screen, RED, (draw_x, draw_y, self.width, self.height))
            pygame.draw.rect(screen, WHITE, (draw_x + 5, draw_y + 5, self.width - 10, self.height - 10))
            pygame.draw.circle(screen, RED, (draw_x + self.width//2, draw_y + self.height//2), 8)
            pygame.draw.rect(screen, RED, (draw_x + self.width//2 - 2, draw_y + 5, 4, self.height - 10))
            
        elif self.collectible_type == "life":
            # Extra life
            pygame.draw.circle(screen, GREEN, (draw_x + self.width//2, draw_y + self.height//2), self.width//2)
            pygame.draw.circle(screen, WHITE, (draw_x + self.width//2, draw_y + self.height//2), self.width//2 - 3)
            pygame.draw.polygon(screen, GREEN, [
                (draw_x + self.width//2, draw_y + 5),
                (draw_x + self.width//2 - 8, draw_y + self.height - 8),
                (draw_x + self.width//2 + 8, draw_y + self.height - 8)
            ])
            
        else:  # coin
            # Coin
            pygame.draw.circle(screen, YELLOW, (draw_x + self.width//2, draw_y + self.height//2), self.width//2)
            pygame.draw.circle(screen, (220, 190, 50), (draw_x + self.width//2, draw_y + self.height//2), self.width//2 - 3)
            pygame.draw.circle(screen, (240, 220, 100), (draw_x + self.width//2, draw_y + self.height//2), self.width//4)
            pygame.draw.rect(screen, YELLOW, (draw_x + self.width//2 - 2, draw_y + 5, 4, self.height - 10))

class Platform:
    def __init__(self, x, y, width, height, color=BROWN):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def draw(self, screen, camera_x):
        pygame.draw.rect(screen, self.color, (self.x - camera_x, self.y, self.width, self.height))
        # Platform top
        pygame.draw.rect(screen, (160, 110, 60), (self.x - camera_x, self.y, self.width, 5))

class Game:
    def __init__(self):
        self.state = MENU
        self.level = 1  # Initialize level FIRST
        self.reset()    # Then call reset
        self.camera_x = 0
        self.game_over_timer = 0
        self.level_complete_timer = 0
        
    def reset(self):
        self.player = Player(200, 300)
        self.projectiles = []
        self.enemies = []
        self.collectibles = []
        self.platforms = []
        self.create_level()
        
    def create_level(self):
        # Clear existing objects
        self.platforms = []
        self.enemies = []
        self.collectibles = []
        
        # Ground platform
        self.platforms.append(Platform(0, HEIGHT - 40, 5000, 40))
        
        # Level-specific platforms
        if self.level == 1:
            # Level 1 - Forest
            self.platforms.append(Platform(300, HEIGHT - 150, 200, 20))
            self.platforms.append(Platform(600, HEIGHT - 200, 200, 20))
            self.platforms.append(Platform(900, HEIGHT - 250, 200, 20))
            
            # Enemies
            self.enemies.append(Enemy(400, HEIGHT - 210, "normal"))
            self.enemies.append(Enemy(700, HEIGHT - 260, "normal"))
            self.enemies.append(Enemy(1000, HEIGHT - 310, "shooter"))
            
            # Collectibles
            self.collectibles.append(Collectible(350, HEIGHT - 190, "coin"))
            self.collectibles.append(Collectible(650, HEIGHT - 240, "health"))
            self.collectibles.append(Collectible(950, HEIGHT - 290, "coin"))
            
        elif self.level == 2:
            # Level 2 - Mountains
            self.platforms.append(Platform(300, HEIGHT - 180, 150, 20))
            self.platforms.append(Platform(500, HEIGHT - 250, 150, 20))
            self.platforms.append(Platform(700, HEIGHT - 320, 150, 20))
            self.platforms.append(Platform(900, HEIGHT - 250, 150, 20))
            self.platforms.append(Platform(1100, HEIGHT - 180, 150, 20))
            
            # Enemies
            self.enemies.append(Enemy(350, HEIGHT - 240, "shooter"))
            self.enemies.append(Enemy(550, HEIGHT - 310, "normal"))
            self.enemies.append(Enemy(750, HEIGHT - 380, "shooter"))
            self.enemies.append(Enemy(950, HEIGHT - 310, "normal"))
            
            # Collectibles
            self.collectibles.append(Collectible(330, HEIGHT - 220, "health"))
            self.collectibles.append(Collectible(550, HEIGHT - 290, "coin"))
            self.collectibles.append(Collectible(750, HEIGHT - 360, "life"))
            self.collectibles.append(Collectible(970, HEIGHT - 290, "coin"))
            
        else:  # Level 3 - Boss level
            self.platforms.append(Platform(300, HEIGHT - 200, 200, 20))
            self.platforms.append(Platform(600, HEIGHT - 300, 200, 20))
            self.platforms.append(Platform(900, HEIGHT - 200, 200, 20))
            self.platforms.append(Platform(1200, HEIGHT - 300, 200, 20))
            
            # Enemies
            self.enemies.append(Enemy(400, HEIGHT - 260, "shooter"))
            self.enemies.append(Enemy(700, HEIGHT - 360, "shooter"))
            self.enemies.append(Enemy(1000, HEIGHT - 260, "shooter"))
            self.enemies.append(Enemy(1500, HEIGHT - 360, "boss"))
            
            # Collectibles
            self.collectibles.append(Collectible(350, HEIGHT - 240, "health"))
            self.collectibles.append(Collectible(650, HEIGHT - 340, "health"))
            self.collectibles.append(Collectible(950, HEIGHT - 240, "life"))
            self.collectibles.append(Collectible(1250, HEIGHT - 340, "health"))
            
    def update_camera(self):
        # Camera follows player with smoothing
        target_x = self.player.x - WIDTH // 3
        self.camera_x += (target_x - self.camera_x) * 0.1
        
        # Keep camera within level bounds
        self.camera_x = max(0, min(self.camera_x, 5000 - WIDTH))
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        self.player.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.vel_x = -self.player.speed
            self.player.direction = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.vel_x = self.player.speed
            self.player.direction = 1
            
        # Jumping
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and not self.player.is_jumping:
            self.player.jump()
    
    def update(self):
        if self.state == PLAYING:
            # Update player
            self.player.move(self.platforms)
            
            # Update camera
            self.update_camera()
            
            # Update projectiles
            for proj in self.projectiles[:]:
                proj.move()
                if proj.is_off_screen(self.camera_x):
                    self.projectiles.remove(proj)
            
            # Update enemies
            for enemy in self.enemies:
                enemy.move(self.platforms, self.player.x)
                
                # Enemy shooting
                if random.random() < 0.02 and enemy.enemy_type in ["shooter", "boss"]:
                    new_proj = enemy.shoot(self.player.x, self.player.y)
                    if new_proj:
                        self.projectiles.append(new_proj)
            
            # Update collectibles
            for collectible in self.collectibles:
                collectible.update()
            
            # Check collisions
            self.check_collisions()
            
            # Check level completion
            if self.level == 3:
                # Boss level - check if boss is defeated
                boss_exists = any(e.enemy_type == "boss" for e in self.enemies)
                if not boss_exists:
                    self.state = LEVEL_COMPLETE
                    self.level_complete_timer = 180
            else:
                # Normal level - check if all enemies are defeated
                if len(self.enemies) == 0:
                    self.state = LEVEL_COMPLETE
                    self.level_complete_timer = 180
            
            # Check game over
            if self.player.health <= 0:
                self.player.lives -= 1
                if self.player.lives <= 0:
                    self.state = GAME_OVER
                    self.game_over_timer = 180
                else:
                    self.player.health = 100
                    self.player.x = 200
                    self.player.y = 300
        
        elif self.state == LEVEL_COMPLETE:
            self.level_complete_timer -= 1
            if self.level_complete_timer <= 0:
                self.level += 1
                if self.level > 3:
                    self.state = GAME_OVER
                    self.game_over_timer = 180
                else:
                    self.reset()
                    self.state = PLAYING
        
        elif self.state == GAME_OVER:
            self.game_over_timer -= 1
    
    def check_collisions(self):
        # Player with collectibles
        for collectible in self.collectibles[:]:
            if self.player.check_collision(collectible):
                if collectible.collectible_type == "health":
                    self.player.health = min(100, self.player.health + 30)
                elif collectible.collectible_type == "life":
                    self.player.lives += 1
                else:  # coin
                    self.player.score += 100
                self.collectibles.remove(collectible)
        
        # Player with enemies
        for enemy in self.enemies:
            if self.player.check_collision(enemy) and self.player.hurt_timer == 0:
                self.player.health -= 10
                self.player.hurt_timer = 30
        
        # Projectiles with enemies
        for proj in self.projectiles[:]:
            if proj.owner == "player":
                for enemy in self.enemies[:]:
                    dx = proj.x - (enemy.x + enemy.width//2)
                    dy = proj.y - (enemy.y + enemy.height//2)
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance < proj.radius + max(enemy.width, enemy.height)//2:
                        enemy.health -= 10
                        enemy.hurt_timer = 5
                        if proj in self.projectiles:
                            self.projectiles.remove(proj)
                        if enemy.health <= 0:
                            self.enemies.remove(enemy)
                            self.player.score += 50 if enemy.enemy_type != "boss" else 500
                        break
        
        # Projectiles with player
        for proj in self.projectiles[:]:
            if proj.owner == "enemy":
                dx = proj.x - (self.player.x + self.player.width//2)
                dy = proj.y - (self.player.y + self.player.height//2)
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < proj.radius + self.player.width//2 and self.player.hurt_timer == 0:
                    self.player.health -= 15
                    self.player.hurt_timer = 30
                    if proj in self.projectiles:
                        self.projectiles.remove(proj)
    
    def draw(self):
        # Draw background
        screen.fill(BACKGROUND)
        
        # Draw distant mountains (for parallax effect)
        for i in range(5):
            height = 150 + i*20
            pygame.draw.polygon(screen, (100, 120, 140), [
                (i*300 - self.camera_x*0.2, HEIGHT),
                (i*300 - self.camera_x*0.2, HEIGHT - height),
                ((i+1)*300 - self.camera_x*0.2, HEIGHT - height - 50),
                ((i+1)*300 - self.camera_x*0.2, HEIGHT)
            ])
        
        # Draw platforms
        for platform in self.platforms:
            platform.draw(screen, self.camera_x)
        
        # Draw collectibles
        for collectible in self.collectibles:
            collectible.draw(screen, self.camera_x)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(screen, self.camera_x)
        
        # Draw projectiles
        for proj in self.projectiles:
            proj.draw(screen, self.camera_x)
        
        # Draw player
        self.player.draw(screen, self.camera_x)
        
        # Draw HUD
        self.draw_hud()
        
        # Draw game state overlays
        if self.state == MENU:
            self.draw_menu()
        elif self.state == GAME_OVER:
            self.draw_game_over()
        elif self.state == LEVEL_COMPLETE:
            self.draw_level_complete()
    
    def draw_hud(self):
        # Health bar
        pygame.draw.rect(screen, (100, 100, 100), (20, 20, 204, 24))
        pygame.draw.rect(screen, RED, (22, 22, 200 * self.player.health / 100, 20))
        health_text = font_small.render(f"HEALTH: {self.player.health}", True, WHITE)
        screen.blit(health_text, (30, 22))
        
        # Lives
        lives_text = font_small.render(f"LIVES: {self.player.lives}", True, WHITE)
        screen.blit(lives_text, (250, 22))
        
        # Score
        score_text = font_small.render(f"SCORE: {self.player.score}", True, WHITE)
        screen.blit(score_text, (WIDTH - 200, 22))
        
        # Level
        level_text = font_small.render(f"LEVEL: {self.level}/3", True, WHITE)
        screen.blit(level_text, (WIDTH // 2 - 50, 22))
        
        # Controls hint
        if self.state == PLAYING:
            controls = font_small.render("ARROWS: Move | SPACE: Jump | F: Shoot", True, WHITE)
            screen.blit(controls, (WIDTH // 2 - 150, HEIGHT - 40))
    
    def draw_menu(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Title
        title = font_large.render("ANIMAL HERO", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
        
        # Subtitle
        subtitle = font_medium.render("vs Human Enemies", True, WHITE)
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//4 + 70))
        
        # Instructions
        start_text = font_medium.render("Press SPACE to Start", True, GREEN)
        screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2 + 50))
        
        controls = font_small.render("Controls: Arrow Keys to Move, SPACE to Jump, F to Shoot", True, WHITE)
        screen.blit(controls, (WIDTH//2 - controls.get_width()//2, HEIGHT//2 + 120))
        
        # Character preview
        pygame.draw.circle(screen, (255, 140, 0), (WIDTH//2 - 150, HEIGHT//2), 40)
        pygame.draw.circle(screen, BLUE, (WIDTH//2 + 150, HEIGHT//2), 40)
    
    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Game over text
        if self.level > 3:
            text = font_large.render("VICTORY!", True, GREEN)
        else:
            text = font_large.render("GAME OVER", True, RED)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//3))
        
        # Score
        score_text = font_medium.render(f"Final Score: {self.player.score}", True, YELLOW)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        
        # Restart prompt
        if self.game_over_timer < 90:
            restart_text = font_medium.render("Press R to Restart", True, GREEN)
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 80))
        
        # Level reached
        level_text = font_small.render(f"Level Reached: {min(self.level, 3)}/3", True, WHITE)
        screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//2 + 150))
    
    def draw_level_complete(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Level complete text
        text = font_large.render(f"LEVEL {self.level} COMPLETE!", True, GREEN)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//3))
        
        # Score
        score_text = font_medium.render(f"Score: {self.player.score}", True, YELLOW)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        
        # Next level prompt
        if self.level_complete_timer < 120:
            if self.level < 3:
                next_text = font_medium.render("Get ready for next level...", True, WHITE)
                screen.blit(next_text, (WIDTH//2 - next_text.get_width()//2, HEIGHT//2 + 80))
            else:
                next_text = font_medium.render("Get ready for the FINAL BATTLE!", True, RED)
                screen.blit(next_text, (WIDTH//2 - next_text.get_width()//2, HEIGHT//2 + 80))

# Create game instance
game = Game()

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game.state == MENU:
                    game.state = PLAYING
            
            if event.key == pygame.K_r:
                if game.state == GAME_OVER and game.game_over_timer < 90:
                    game.level = 1
                    game.reset()
                    game.state = PLAYING
            
            if event.key == pygame.K_f and game.state == PLAYING:
                new_proj = game.player.shoot()
                if new_proj:
                    game.projectiles.append(new_proj)
    
    # Update game state
    game.handle_input()
    game.update()
    
    # Draw everything
    game.draw()
    
    # Update display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

pygame.quit()
sys.exit()