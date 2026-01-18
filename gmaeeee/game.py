import pygame
import math
import random
from settings import *


def load_image(name, size):
    try:
        img = pygame.image.load(name).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        return None


class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, itype):
        super().__init__()
        self.type = itype
        img = load_image(IMG_MEDKIT, (30, 30))
        self.image = img if img else pygame.Surface((25, 25), pygame.SRCALPHA)
        if not img:
            pygame.draw.rect(self.image, (255, 255, 255), [0, 0, 25, 25], border_radius=5)
            pygame.draw.rect(self.image, (220, 0, 0), [10, 4, 5, 17])
            pygame.draw.rect(self.image, (220, 0, 0), [4, 10, 17, 5])
        self.rect = self.image.get_rect(center=(x, y))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_pos, damage, speed, color=BLACK, piercing=False):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (5, 5), 4)
        if piercing:
            pygame.draw.circle(self.image, (255, 255, 255), (5, 5), 2)
        self.rect = self.image.get_rect(center=(x, y))
        angle = math.atan2(target_pos[1] - y, target_pos[0] - x)
        self.dx, self.dy = math.cos(angle) * speed, math.sin(angle) * speed
        self.damage, self.piercing = damage, piercing

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if abs(self.rect.x) > 5000 or abs(self.rect.y) > 5000: self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, target_pos):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (30, 60, 30), (10, 10), 9)
        pygame.draw.circle(self.image, (0, 0, 0), (10, 10), 9, 2)
        pygame.draw.rect(self.image, (60, 60, 60), [8, 0, 4, 5])  # Запал
        pygame.draw.circle(self.image, (150, 150, 150), (6, 3), 3, 1)  # Чека
        self.rect = self.image.get_rect(center=(x, y))
        angle = math.atan2(target_pos[1] - y, target_pos[0] - x)
        dist = min(math.hypot(target_pos[0] - x, target_pos[1] - y), 350)
        self.target_x, self.target_y = x + math.cos(angle) * dist, y + math.sin(angle) * dist
        self.speed, self.timer, self.exploded = 9, 100, False

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
            self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (15, 30, 15), (50, 50), 45)  # Тінь
            pygame.draw.circle(self.image, TREE_COLOR, (50, 50), 40)
            pygame.draw.circle(self.image, (0, 0, 0), (50, 50), 40, 2)
        elif dtype == "log":
            self.image = pygame.Surface((90, 40), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (80, 50, 20), [5, 10, 80, 25], border_radius=5)
            pygame.draw.rect(self.image, (100, 70, 40), [10, 15, 70, 15], border_radius=3)
        elif dtype == "rock":
            self.image = pygame.Surface((60, 50), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (50, 50, 50), [0, 0, 60, 50])
            pygame.draw.ellipse(self.image, ROCK_COLOR, [5, 5, 50, 40])
        else:
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.line(self.image, GRASS_COLOR, (10, 20), (5, 5), 2)
            pygame.draw.line(self.image, (60, 160, 60), (10, 20), (15, 8), 2)
        self.rect = self.image.get_rect(center=(x, y))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, etype, wave_m=1.0):
        super().__init__()
        self.type = etype
        size = (46, 46)
        path = IMG_ENEMY_BASIC if etype == "basic" else (IMG_ENEMY_ORANGE if etype == "orange" else IMG_ENEMY_SNIPER)
        img = load_image(path, size)

        self.hp = (25 if etype == "basic" else 45 if etype == "orange" else 35) * wave_m
        self.speed = 3.2 if etype == "basic" else 2.3 if etype == "orange" else 0
        self.color = ENEMY_BASIC if etype == "basic" else ENEMY_ORANGE if etype == "orange" else (50, 50, 200)

        self.image = img if img else pygame.Surface(size, pygame.SRCALPHA)
        if not img:
            pygame.draw.rect(self.image, self.color, [4, 4, 38, 38], border_radius=10)
            pygame.draw.rect(self.image, BLACK, [4, 4, 38, 38], 2, border_radius=10)
        self.rect = self.image.get_rect(center=(x, y))
        self.last_shot = 0

    def update(self, player_rect, enemy_bullets):
        dist = math.hypot(player_rect.centerx - self.rect.centerx, player_rect.centery - self.rect.centery)
        if self.type != "sniper" and dist < 1600:
            angle = math.atan2(player_rect.centery - self.rect.centery, player_rect.centerx - self.rect.centerx)
            self.rect.x += math.cos(angle) * self.speed
            self.rect.y += math.sin(angle) * self.speed

        now = pygame.time.get_ticks()
        if self.type == "orange" and dist < 600 and now - self.last_shot > 1900:
            enemy_bullets.add(Bullet(self.rect.centerx, self.rect.centery, player_rect.center, 10, 8, ENEMY_ORANGE))
            self.last_shot = now


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        img = load_image(IMG_PLAYER, (54, 54))
        self.base_image = img if img else pygame.Surface((54, 54), pygame.SRCALPHA)
        if not img:
            pygame.draw.circle(self.base_image, PLAYER_CLR, (27, 27), 24)
            pygame.draw.circle(self.base_image, (0, 0, 0), (27, 27), 24, 2)
            pygame.draw.rect(self.base_image, (40, 40, 40), [42, 22, 14, 10], border_radius=2)

        self.image = self.base_image
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.hp, self.coins, self.speed = PLAYER_HP, START_COINS, 5.5
        self.bandages, self.grenades = 1, 2
        self.weapon_type, self.ammo, self.max_ammo = "Pistol", 12, 12
        self.reloading, self.reload_start, self.last_shot_time = False, 0, 0

    def update(self, keys, mouse_pos, camera):
        mx, my = 0, 0
        if keys[pygame.K_a]: mx -= self.speed
        if keys[pygame.K_d]: mx += self.speed
        if keys[pygame.K_w]: my -= self.speed
        if keys[pygame.K_s]: my += self.speed
        if mx != 0 and my != 0: mx, my = mx * 0.707, my * 0.707
        self.rect.x += mx
        self.rect.y += my

        p_scr_x, p_scr_y = self.rect.centerx + camera.x, self.rect.centery + camera.y
        angle = math.degrees(math.atan2(-(mouse_pos[1] - p_scr_y), mouse_pos[0] - p_scr_x))
        self.image = pygame.transform.rotate(self.base_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        if self.reloading and pygame.time.get_ticks() - self.reload_start > 1400:
            self.ammo = self.max_ammo;
            self.reloading = False

    def draw_weapon(self, surface, camera, mouse_pos):
        p_x, p_y = self.rect.centerx + camera.x, self.rect.centery + camera.y
        angle = math.degrees(math.atan2(mouse_pos[1] - p_y, mouse_pos[0] - p_x))
        w_surf = pygame.Surface((120, 60), pygame.SRCALPHA)

        if self.weapon_type == "Pistol":
            pygame.draw.rect(w_surf, (45, 45, 45), [50, 22, 30, 14], border_radius=2)
            pygame.draw.rect(w_surf, (20, 20, 20), [54, 30, 10, 15], border_radius=2)
        elif self.weapon_type == "AK-47":
            pygame.draw.rect(w_surf, (120, 70, 40), [10, 22, 35, 16], border_radius=3)
            pygame.draw.rect(w_surf, (40, 40, 40), [45, 20, 60, 14])
            pygame.draw.rect(w_surf, (15, 15, 15), [75, 32, 14, 24], border_radius=5)
            pygame.draw.rect(w_surf, (25, 25, 25), [105, 25, 12, 5])
        elif self.weapon_type == "Shotgun":
            pygame.draw.rect(w_surf, (100, 60, 30), [15, 22, 35, 18], border_radius=2)
            pygame.draw.rect(w_surf, (60, 60, 60), [50, 20, 55, 18])
            pygame.draw.rect(w_surf, (40, 40, 40), [60, 36, 30, 8], border_radius=4)
        elif self.weapon_type == "Sniper":
            pygame.draw.rect(w_surf, (40, 60, 40), [5, 24, 45, 14], border_radius=2)
            pygame.draw.rect(w_surf, (25, 25, 25), [50, 27, 65, 8])
            pygame.draw.rect(w_surf, (10, 10, 10), [60, 14, 30, 12], border_radius=3)
            pygame.draw.circle(w_surf, (0, 200, 255), (85, 20), 4)

        rotated_w = pygame.transform.rotate(w_surf, -angle)
        surface.blit(rotated_w, rotated_w.get_rect(center=(p_x, p_y)))

    def shoot(self, target):
        now = pygame.time.get_ticks()
        delays = {"Pistol": 380, "AK-47": 130, "Shotgun": 850, "Sniper": 1750}
        if now - self.last_shot_time < delays.get(self.weapon_type, 400): return None
        if self.ammo > 0 and not self.reloading:
            self.ammo -= 1;
            self.last_shot_time = now
            bullets = []
            if self.weapon_type == "Shotgun":
                angle = math.atan2(target[1] - self.rect.centery, target[0] - self.rect.centerx)
                for a in [angle - 0.18, angle, angle + 0.18]:
                    bullets.append(Bullet(self.rect.centerx, self.rect.centery, (self.rect.centerx + math.cos(a) * 100,
                                                                                 self.rect.centery + math.sin(a) * 100),
                                          10, 15))
            elif self.weapon_type == "Sniper":
                bullets.append(Bullet(self.rect.centerx, self.rect.centery, target, 160, 45, (255, 240, 0), True))
            else:
                bullets.append(
                    Bullet(self.rect.centerx, self.rect.centery, target, 19 if self.weapon_type == "AK-47" else 24, 19))
            if self.ammo == 0: self.reloading, self.reload_start = True, now
            return bullets
        return None


class Camera:
    def __init__(self): self.x, self.y = 0, 0

    def apply(self, rect): return rect.move(self.x, self.y)

    def update(self, target):
        self.x += (-target.rect.centerx + WIDTH // 2 - self.x) * 0.1
        self.y += (-target.rect.centery + HEIGHT // 2 - self.y) * 0.1
