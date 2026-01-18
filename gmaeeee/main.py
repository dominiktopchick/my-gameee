import pygame
import sys
import random
import math
from settings import *
from game import Player, Enemy, Bullet, Camera, Decoration, Item, Grenade


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Forest Survivor CS2 Style")
        pygame.mouse.set_visible(False)  # Приховуємо стандартний курсор
        self.clock = pygame.time.Clock()
        self.font_main = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 18)
        self.start_time = pygame.time.get_ticks()
        self.reset_game()

    def reset_game(self):
        self.state = "GAME"
        self.player = Player()
        self.enemies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.grenades_grp = pygame.sprite.Group()
        self.decorations = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.camera = Camera()
        self.max_enemies = 10
        for _ in range(400):
            x, y = random.randint(-4000, 4000), random.randint(-4000, 4000)
            self.decorations.add(Decoration(x, y, random.choice(["tree", "rock", "grass", "log"])))

    def draw_crosshair(self, pos):
        # Малюємо перехрестя (зелене)
        mx, my = pos
        length = 10
        gap = 4
        # Горизонтальні лінії
        pygame.draw.line(self.screen, CROSSHAIR_CLR, (mx - length - gap, my), (mx - gap, my), 2)
        pygame.draw.line(self.screen, CROSSHAIR_CLR, (mx + gap, my), (mx + length + gap, my), 2)
        # Вертикальні лінії
        pygame.draw.line(self.screen, CROSSHAIR_CLR, (mx, my - length - gap), (mx, my - gap), 2)
        pygame.draw.line(self.screen, CROSSHAIR_CLR, (mx, my + gap), (mx, my + length + gap), 2)
        # Крапка в центрі
        pygame.draw.circle(self.screen, CROSSHAIR_CLR, (mx, my), 2)

    def draw_hud(self):
        # Здоров'я
        pygame.draw.rect(self.screen, (30, 30, 30), [45, HEIGHT - 85, 210, 50])
        pygame.draw.rect(self.screen, HEALTH_CLR, [50, HEIGHT - 80, max(0, min(200, self.player.hp * 2)), 40])
        self.screen.blit(self.font_main.render(f"+ {int(self.player.hp)}", True, WHITE), (60, HEIGHT - 78))

        # Набої
        ammo_txt = f"{self.player.ammo}/{self.player.max_ammo}"
        self.screen.blit(self.font_main.render(ammo_txt, True, WHITE), (WIDTH - 160, HEIGHT - 80))
        self.screen.blit(self.font_small.render(f"GRENADES (G): {self.player.grenades}", True, AMMO_CLR),
                         (WIDTH - 180, HEIGHT - 105))

        # Статистика
        min_p = (pygame.time.get_ticks() - self.start_time) // 60000
        stats = f"Time: {min_p}m | Coins: {self.player.coins} | Medkits: {self.player.bandages}"
        self.screen.blit(self.font_small.render(stats, True, WHITE), (20, 20))

    def game_loop(self):
        now = pygame.time.get_ticks()
        self.max_enemies = 10 + ((now - self.start_time) // 60000) * 5
        mouse_p = pygame.mouse.get_pos()
        world_mouse = (mouse_p[0] - self.camera.x, mouse_p[1] - self.camera.y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.player.weapon_type != "AK-47":
                    bs = self.player.shoot(world_mouse)
                    if bs: [self.player_bullets.add(b) for b in bs]
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.state = "SHOP"; pygame.mouse.set_visible(True)
                if event.key == pygame.K_g and self.player.grenades > 0:
                    self.player.grenades -= 1
                    self.grenades_grp.add(Grenade(self.player.rect.centerx, self.player.rect.centery, world_mouse))
                if event.key == pygame.K_1 and self.player.bandages > 0:
                    self.player.hp = min(PLAYER_HP, self.player.hp + 30)
                    self.player.bandages -= 1

        if pygame.mouse.get_pressed()[0] and self.player.weapon_type == "AK-47":
            bs = self.player.shoot(world_mouse)
            if bs: [self.player_bullets.add(b) for b in bs]

        # Оновлення
        self.player.update(pygame.key.get_pressed())
        self.camera.update(self.player)
        self.enemies.update(self.player.rect, self.enemy_bullets)
        self.player_bullets.update()
        self.enemy_bullets.update()
        self.grenades_grp.update()

        # Вибухи гранат
        for gr in self.grenades_grp:
            if gr.exploded:
                for en in self.enemies:
                    if math.hypot(gr.rect.centerx - en.rect.centerx, gr.rect.centery - en.rect.centery) < 160:
                        en.hp -= 60
                        if en.hp <= 0: en.kill(); self.player.coins += 10
                gr.kill()

        if len(self.enemies) < self.max_enemies:
            self.enemies.add(
                Enemy(self.player.rect.x + random.choice([-900, 900]), self.player.rect.y + random.choice([-700, 700]),
                      random.choice(["basic", "basic", "orange"])))

        # Шкода
        if pygame.sprite.spritecollide(self.player, self.enemies, False): self.player.hp -= 0.3
        if pygame.sprite.spritecollide(self.player, self.enemy_bullets, True): self.player.hp -= 15

        # Стрільба гравця
        for b in self.player_bullets:
            hits = pygame.sprite.spritecollide(b, self.enemies, False)
            if hits:
                for en in hits:
                    en.hp -= b.damage
                    if en.hp <= 0:
                        en.kill();
                        self.player.coins += 10
                        if random.random() < 0.2: self.items.add(Item(en.rect.centerx, en.rect.centery, "medkit"))
                if not b.piercing: b.kill()

        for it in pygame.sprite.spritecollide(self.player, self.items, True): self.player.bandages += 1
        if self.player.hp <= 0: self.reset_game()

        # Малювання
        self.screen.fill(DARK_GREEN)
        for g in [self.decorations, self.items, self.enemies, self.enemy_bullets, self.player_bullets,
                  self.grenades_grp]:
            for s in g: self.screen.blit(s.image, self.camera.apply(s.rect))

        self.player.draw_weapon(self.screen, self.camera, mouse_p)
        self.screen.blit(self.player.image, self.camera.apply(self.player.rect))

        self.draw_hud()
        self.draw_crosshair(mouse_p)  # Малюємо приціл ПОВЕРХ усього
        pygame.display.flip()
        self.clock.tick(FPS)

    def shop_loop(self):
        self.screen.fill(BLACK)
        txt = ["--- ARSENAL SHOP ---", f"Your Coins: {self.player.coins}", "1. Bandage (+30 HP) - 20c",
               "2. Shotgun - 100c", "3. Sniper Rifle - 250c", "4. AK-47 - 150c", "5. Grenade - 30c",
               "ESC - Return to Battle"]
        for i, line in enumerate(txt):
            color = AMMO_CLR if "Coins" in line else WHITE
            self.screen.blit(self.font_main.render(line, True, color), (WIDTH // 2 - 150, 120 + i * 45))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "GAME"
                    pygame.mouse.set_visible(False)  # Знову ховаємо курсор при поверненні в гру
                if event.key == pygame.K_1 and self.player.coins >= 20: self.player.coins -= 20; self.player.bandages += 1
                if event.key == pygame.K_2 and self.player.coins >= 100: self.player.coins -= 100; self.player.weapon_type = "Shotgun"; self.player.max_ammo = 4; self.player.ammo = 4
                if event.key == pygame.K_3 and self.player.coins >= 250: self.player.coins -= 250; self.player.weapon_type = "Sniper"; self.player.max_ammo = 1; self.player.ammo = 1
                if event.key == pygame.K_4 and self.player.coins >= 150: self.player.coins -= 150; self.player.weapon_type = "AK-47"; self.player.max_ammo = 30; self.player.ammo = 30
                if event.key == pygame.K_5 and self.player.coins >= 30: self.player.coins -= 30; self.player.grenades += 1
        pygame.display.flip()

    def run(self):
        while True:
            if self.state == "GAME":
                self.game_loop()
            else:
                self.shop_loop()


if __name__ == "__main__":
    Game().run()
