import pygame
import math
import random
from settings import *


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_pos, damage, speed, color=BLACK):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        angle = math.atan2(target_pos[1] - y, target_pos[0] - x)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.damage = damage

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        # Кулі зникають через 2000 пікселів від гравця для економії пам'яті
        if abs(self.rect.x) > 5000 or abs(self.rect.y) > 5000:
            self.kill()


class Decoration(pygame.sprite.Sprite):
    def __init__(self, x, y, dtype):
        super().__init__()
        if dtype == "tree":
            self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(self.image, TREE_COLOR, (30, 30), 30)
        elif dtype == "rock":
            self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, ROCK_COLOR, [0, 0, 40, 30])
        else:  # grass
            self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.line(self.image, GRASS_COLOR, (5, 10), (5, 0), 2)
        self.rect = self.image.get_rect(center=(x, y))


class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, itype):
        super().__init__()
        self.type = itype
        self.image = pygame.Surface((20, 20))
        if itype == "medkit":
            self.image.fill(WHITE)
            pygame.draw.rect(self.image, MEDKIT_CLR, [8, 2, 4, 16])
            pygame.draw.rect(self.image, MEDKIT_CLR, [2, 8, 16, 4])
        else:  # speed
            self.image.fill((0, 255, 255))
        self.rect = self.image.get_rect(center=(x, y))


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(PLAYER_CLR)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.hp = PLAYER_HP
        self.speed = 5
        self.coins = 0
        self.bandages = 0
        self.weapon_type = "Pistol"
        self.ammo = 5
        self.max_ammo = 5
        self.damage = 5
        self.bullet_speed = 10
        self.reload_delay = 3000
        self.reloading = False
        self.reload_start = 0

    def update(self, keys):
        if keys[pygame.K_a]: self.rect.x -= self.speed
        if keys[pygame.K_d]: self.rect.x += self.speed
        if keys[pygame.K_w]: self.rect.y -= self.speed
        if keys[pygame.K_s]: self.rect.y += self.speed

        if self.reloading:
            if pygame.time.get_ticks() - self.reload_start > self.reload_delay:
                self.ammo = self.max_ammo
                self.reloading = False

    def shoot(self, mouse_world_pos):
        if self.ammo > 0 and not self.reloading:
            self.ammo -= 1
            if self.ammo == 0:
                self.reloading = True
                self.reload_start = pygame.time.get_ticks()
            return Bullet(self.rect.centerx, self.rect.centery, mouse_world_pos, self.damage, self.bullet_speed)
        return None


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, etype):
        super().__init__()
        self.type = etype
        self.image = pygame.Surface((35, 35))
        self.last_shot = 0
        if etype == "basic":
            self.image.fill(ENEMY_BASIC);
            self.hp = 10;
            self.speed = 3
        elif etype == "orange":
            self.image.fill(ENEMY_ORANGE);
            self.hp = 20;
            self.speed = 2
        else:
            self.image.fill(ENEMY_SNIPER);
            self.hp = 15;
            self.speed = 0
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, player_rect, enemy_bullets):
        dist = math.hypot(player_rect.centerx - self.rect.centerx, player_rect.centery - self.rect.centery)
        if self.type != "sniper" and dist < 1000:
            if self.rect.x < player_rect.x: self.rect.x += self.speed
            if self.rect.x > player_rect.x: self.rect.x -= self.speed
            if self.rect.y < player_rect.y: self.rect.y += self.speed
            if self.rect.y > player_rect.y: self.rect.y -= self.speed

        now = pygame.time.get_ticks()
        if self.type == "orange" and dist < 500 and now - self.last_shot > 2000:
            enemy_bullets.add(Bullet(self.rect.centerx, self.rect.centery, player_rect.center, 5, 7, ENEMY_ORANGE))
            self.last_shot = now
        elif self.type == "sniper" and dist < 800 and now - self.last_shot > 3500:
            enemy_bullets.add(Bullet(self.rect.centerx, self.rect.centery, player_rect.center, 10, 15, ENEMY_SNIPER))
            self.last_shot = now


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0

    def apply(self, rect):
        return rect.move(self.x, self.y)

    def update(self, target):
        self.x = -target.rect.centerx + WIDTH // 2
        self.y = -target.rect.centery + HEIGHT // 2
