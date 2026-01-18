import pygame
import math
import random
from settings import *


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_pos, damage, speed, color=BLACK, piercing=False):
        super().__init__()
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (4, 4), 4)
        self.rect = self.image.get_rect(center=(x, y))
        angle = math.atan2(target_pos[1] - y, target_pos[0] - x)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.damage = damage
        self.piercing = piercing

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if abs(self.rect.x) > 5000 or abs(self.rect.y) > 5000: self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, target_pos):
        super().__init__()
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (20, 60, 20), (8, 8), 8)
        pygame.draw.circle(self.image, (0, 0, 0), (8, 8), 8, 2)
        self.rect = self.image.get_rect(center=(x, y))
        angle = math.atan2(target_pos[1] - y, target_pos[0] - x)
        dist = min(math.hypot(target_pos[0] - x, target_pos[1] - y), 300)
        self.target_x = x + math.cos(angle) * dist
        self.target_y = y + math.sin(angle) * dist
        self.speed = 8
        self.timer = 90
        self.exploded = False

    def update(self):
        dx, dy = self.target_x - self.rect.centerx, self.target_y - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 5:
            self.rect.x += (dx / dist) * self.speed
            self.rect.y += (dy / dist) * self.speed
        self.timer -= 1
        if self.timer <= 0: self.exploded = True


class Decoration(pygame.sprite.Sprite):
    def __init__(self, x, y, dtype):
        super().__init__()
        if dtype == "tree":
            self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(self.image, TREE_COLOR, (30, 30), 28)
            pygame.draw.circle(self.image, (0, 0, 0), (30, 30), 28, 2)
        elif dtype == "log":
            self.image = pygame.Surface((80, 30), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (100, 65, 30), [0, 5, 80, 20])
            pygame.draw.rect(self.image, (0, 0, 0), [0, 5, 80, 20], 2)
        elif dtype == "rock":
            self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, ROCK_COLOR, [0, 0, 40, 30])
        else:
            self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.line(self.image, GRASS_COLOR, (5, 10), (5, 0), 2)
        self.rect = self.image.get_rect(center=(x, y))


class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, itype):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        if itype == "medkit":
            self.image.fill(WHITE)
            pygame.draw.rect(self.image, HEALTH_CLR, [8, 2, 4, 16])
            pygame.draw.rect(self.image, HEALTH_CLR, [2, 8, 16, 4])
        self.rect = self.image.get_rect(center=(x, y))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, etype):
        super().__init__()
        self.type = etype
        self.image = pygame.Surface((35, 35), pygame.SRCALPHA)
        if etype == "basic":
            self.image.fill(ENEMY_BASIC); self.hp = 20; self.speed = 3
        elif etype == "orange":
            self.image.fill(ENEMY_ORANGE); self.hp = 40; self.speed = 2
        else:
            self.image.fill(ENEMY_SNIPER); self.hp = 25; self.speed = 0
        pygame.draw.rect(self.image, (0, 0, 0), [0, 0, 35, 35], 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.last_shot = 0

    def update(self, player_rect, enemy_bullets):
        dist = math.hypot(player_rect.centerx - self.rect.centerx, player_rect.centery - self.rect.centery)
        if self.type != "sniper" and dist < 1200:
            angle = math.atan2(player_rect.centery - self.rect.centery, player_rect.centerx - self.rect.centerx)
            self.rect.x += math.cos(angle) * self.speed
            self.rect.y += math.sin(angle) * self.speed
        now = pygame.time.get_ticks()
        if self.type == "orange" and dist < 500 and now - self.last_shot > 2000:
            enemy_bullets.add(Bullet(self.rect.centerx, self.rect.centery, player_rect.center, 5, 7, ENEMY_ORANGE))
            self.last_shot = now


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.image, PLAYER_CLR, (20, 20), 18)
        pygame.draw.circle(self.image, (0, 0, 0), (20, 20), 18, 2)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.hp = PLAYER_HP
        self.coins = START_COINS
        self.speed = 5
        self.bandages = 0
        self.grenades = 3
        self.weapon_type = "Pistol"
        self.ammo = 12
        self.max_ammo = 12
        self.reloading = False
        self.reload_start = 0
        self.last_shot_time = 0

    def draw_weapon(self, surface, camera, mouse_pos):
        p_x, p_y = self.rect.centerx + camera.x, self.rect.centery + camera.y
        angle = math.degrees(math.atan2(mouse_pos[1] - p_y, mouse_pos[0] - p_x))
        w_surf = pygame.Surface((80, 40), pygame.SRCALPHA)

        if self.weapon_type == "Pistol":
            pygame.draw.rect(w_surf, (50, 50, 50), [40, 12, 22, 10])
            pygame.draw.rect(w_surf, (30, 30, 30), [40, 18, 7, 12])
            pygame.draw.rect(w_surf, (10, 10, 10), [58, 10, 4, 3])
        elif self.weapon_type == "AK-47":
            pygame.draw.rect(w_surf, (100, 60, 30), [10, 16, 20, 10])
            pygame.draw.rect(w_surf, (30, 30, 30), [30, 15, 45, 8])
            pygame.draw.rect(w_surf, (20, 20, 20), [45, 22, 8, 14])
        elif self.weapon_type == "Shotgun":
            pygame.draw.rect(w_surf, (80, 50, 20), [15, 15, 12, 12])
            pygame.draw.rect(w_surf, (50, 50, 50), [27, 13, 35, 12])
        elif self.weapon_type == "Sniper":
            pygame.draw.rect(w_surf, (20, 40, 20), [5, 15, 22, 10])
            pygame.draw.rect(w_surf, (10, 10, 10), [27, 17, 50, 5])
            pygame.draw.rect(w_surf, (0, 0, 0), [35, 10, 15, 6])

        rotated = pygame.transform.rotate(w_surf, -angle)
        surface.blit(rotated, rotated.get_rect(center=(p_x, p_y)))

    def update(self, keys):
        if keys[pygame.K_a]: self.rect.x -= self.speed
        if keys[pygame.K_d]: self.rect.x += self.speed
        if keys[pygame.K_w]: self.rect.y -= self.speed
        if keys[pygame.K_s]: self.rect.y += self.speed
        if self.reloading and pygame.time.get_ticks() - self.reload_start > 1500:
            self.ammo = self.max_ammo;
            self.reloading = False

    def shoot(self, target):
        now = pygame.time.get_ticks()
        delays = {"Pistol": 350, "AK-47": 150, "Shotgun": 800, "Sniper": 1500}
        if now - self.last_shot_time < delays.get(self.weapon_type, 400): return None
        if self.ammo > 0 and not self.reloading:
            self.ammo -= 1;
            self.last_shot_time = now
            bullets = []
            if self.weapon_type == "Shotgun":
                angle = math.atan2(target[1] - self.rect.centery, target[0] - self.rect.centerx)
                for i in range(-3, 4):
                    a = angle + (i * 0.15)
                    bullets.append(Bullet(self.rect.centerx, self.rect.centery, (self.rect.centerx + math.cos(a) * 100,
                                                                                 self.rect.centery + math.sin(a) * 100),
                                          5, 12))
            elif self.weapon_type == "Sniper":
                bullets.append(Bullet(self.rect.centerx, self.rect.centery, target, 100, 35, (255, 215, 0), True))
            else:
                bullets.append(Bullet(self.rect.centerx, self.rect.centery, target, 10, 15))
            if self.ammo == 0: self.reloading = True; self.reload_start = now
            return bullets
        return None


class Camera:
    def __init__(self): self.x, self.y = 0, 0

    def apply(self, rect): return rect.move(self.x, self.y)

    def update(self, target):
        self.x = -target.rect.centerx + WIDTH // 2
        self.y = -target.rect.centery + HEIGHT // 2
