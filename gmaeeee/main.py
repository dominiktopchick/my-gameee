import pygame
import sys
import random
from settings import *
from game import Player, Enemy, Bullet, Camera, Decoration, Item


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Infinite Forest Shooter 2026")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 22)
        self.camera = Camera()
        self.reset_game()

    def reset_game(self):
        self.state = "GAME"
        self.player = Player()
        self.enemies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.decorations = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.spawn_timer = 0

        # Генерація початкового оточення навколо спавну
        for _ in range(100):
            x, y = random.randint(-2000, 2000), random.randint(-2000, 2000)
            dtype = random.choice(["tree", "rock", "grass"])
            self.decorations.add(Decoration(x, y, dtype))

    def game_loop(self):
        mouse_p = pygame.mouse.get_pos()
        world_mouse = (mouse_p[0] - self.camera.x, mouse_p[1] - self.camera.y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                b = self.player.shoot(world_mouse)
                if b: self.player_bullets.add(b)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.state = "SHOP"
                if event.key == pygame.K_1 and self.player.bandages > 0:
                    self.player.hp = min(100, self.player.hp + 30)
                    self.player.bandages -= 1

        self.player.update(pygame.key.get_pressed())
        self.camera.update(self.player)
        self.enemies.update(self.player.rect, self.enemy_bullets)
        self.player_bullets.update()
        self.enemy_bullets.update()

        # Динамічний спавн ворогів навколо гравця
        if pygame.time.get_ticks() - self.spawn_timer > 2000:
            off_x = random.choice([-700, 700])
            off_y = random.choice([-500, 500])
            self.enemies.add(Enemy(self.player.rect.x + off_x, self.player.rect.y + off_y,
                                   random.choice(["basic", "orange", "sniper"])))
            self.spawn_timer = pygame.time.get_ticks()

        # Колізії
        if pygame.sprite.spritecollide(self.player, self.enemy_bullets, True):
            self.player.hp -= 5

        hits = pygame.sprite.groupcollide(self.enemies, self.player_bullets, False, True)
        for en in hits:
            en.hp -= self.player.damage
            if en.hp <= 0:
                en.kill()
                self.player.coins += 10
                if random.random() < 0.2:
                    self.items.add(Item(en.rect.centerx, en.rect.centery, random.choice(["medkit", "speed"])))

        for it in pygame.sprite.spritecollide(self.player, self.items, True):
            if it.type == "medkit":
                self.player.bandages += 1
            else:
                self.player.speed += 0.5

        if self.player.hp <= 0: self.reset_game()

        # Малювання
        self.screen.fill(DARK_GREEN)
        # Малюємо все з урахуванням камери
        for group in [self.decorations, self.items, self.enemies, self.enemy_bullets, self.player_bullets]:
            for sprite in group:
                self.screen.blit(sprite.image, self.camera.apply(sprite.rect))

        self.screen.blit(self.player.image, self.camera.apply(self.player.rect))

        ui = f"HP: {int(self.player.hp)} | Coins: {self.player.coins} | Bandages: {self.player.bandages} | Ammo: {self.player.ammo}"
        self.screen.blit(self.font.render(ui, True, WHITE), (10, 10))
        pygame.display.flip()
        self.clock.tick(FPS)

    def shop_loop(self):
        self.screen.fill(BLACK)
        txt = ["--- МАГАЗИН ---", f"Монети: {self.player.coins}",
               "1. Купити бінт (20c)", "2. Дробовик (100c)", "3. Снайперка (200c)", "4. AK-47 (150c)", "ESC - Вихід"]
        for i, line in enumerate(txt):
            self.screen.blit(self.font.render(line, True, WHITE), (WIDTH // 2 - 100, 150 + i * 40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.state = "GAME"
                if event.key == pygame.K_1 and self.player.coins >= 20:
                    self.player.coins -= 20;
                    self.player.bandages += 1
                if event.key == pygame.K_2 and self.player.coins >= 100:
                    self.player.coins -= 100;
                    self.player.weapon_type = "Shotgun"
                    self.player.max_ammo = 3;
                    self.player.damage = 20;
                    self.player.reload_delay = 1000
                if event.key == pygame.K_3 and self.player.coins >= 200:
                    self.player.coins -= 200;
                    self.player.weapon_type = "Sniper"
                    self.player.max_ammo = 1;
                    self.player.damage = 100;
                    self.player.reload_delay = 4000
                if event.key == pygame.K_4 and self.player.coins >= 150:
                    self.player.coins -= 150;
                    self.player.weapon_type = "AK-47"
                    self.player.max_ammo = 30;
                    self.player.damage = 8;
                    self.player.reload_delay = 1500

        pygame.display.flip()

    def run(self):
        while True:
            if self.state == "GAME":
                self.game_loop()
            else:
                self.shop_loop()


if __name__ == "__main__":
    Game().run()
