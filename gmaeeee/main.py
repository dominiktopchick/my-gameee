import pygame, sys, random, math
from settings import *
from game import Player, Enemy, Bullet, Camera, Decoration, Item, Grenade


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Forest Survivor: CS2 Edition")
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock()
        self.fonts = {
            "title": pygame.font.SysFont("Impact", 72),
            "main": pygame.font.SysFont("Arial", 32, bold=True),
            "hud": pygame.font.SysFont("Consolas", 24, bold=True)
        }
        self.reset_game()

    def reset_game(self):
        self.state = "GAME"
        self.player = Player()
        self.groups = {
            "dec": pygame.sprite.Group(), "enemies": pygame.sprite.Group(),
            "p_bullets": pygame.sprite.Group(), "e_bullets": pygame.sprite.Group(),
            "grenades": pygame.sprite.Group(), "items": pygame.sprite.Group()
        }
        self.camera = Camera()
        self.wave, self.killed, self.to_kill, self.total_k = 1, 0, 10, 0
        for _ in range(300):
            x, y = random.randint(-4000, 4000), random.randint(-4000, 4000)
            self.groups["dec"].add(Decoration(x, y, random.choice(["tree", "rock", "grass", "log"])))

    def draw_crosshair(self, pos):
        mx, my = pos
        color = (0, 255, 0)
        pygame.draw.line(self.screen, color, (mx - 15, my), (mx - 5, my), 2)
        pygame.draw.line(self.screen, color, (mx + 5, my), (mx + 15, my), 2)
        pygame.draw.line(self.screen, color, (mx, my - 15), (mx, my - 5), 2)
        pygame.draw.line(self.screen, color, (mx, my + 5), (mx, my + 15), 2)
        pygame.draw.circle(self.screen, color, (mx, my), 2)

    def draw_hud(self):
        # Здоров'я
        pygame.draw.rect(self.screen, (20, 20, 20), [30, HEIGHT - 70, 220, 40], border_radius=5)
        pygame.draw.rect(self.screen, HEALTH_CLR, [35, HEIGHT - 65, max(0, self.player.hp * 2.1), 30], border_radius=3)
        self.screen.blit(self.fonts["main"].render(f"+ {int(self.player.hp)}", True, WHITE), (40, HEIGHT - 110))
        # Набої
        ammo_c = AMMO_CLR if not self.player.reloading else (255, 0, 0)
        self.screen.blit(self.fonts["main"].render(f"{self.player.ammo}/{self.player.max_ammo}", True, ammo_c),
                         (WIDTH - 160, HEIGHT - 70))
        # Статистика
        info = f"WAVE {self.wave} | {self.killed}/{self.to_kill} KILLS | COINS: {self.player.coins}"
        self.screen.blit(self.fonts["hud"].render(info, True, WHITE), (WIDTH // 2 - 250, 20))

    def game_loop(self):
        mouse_p = pygame.mouse.get_pos()
        world_mouse = (mouse_p[0] - self.camera.x, mouse_p[1] - self.camera.y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.player.weapon_type != "AK-47":
                    bs = self.player.shoot(world_mouse)
                    if bs: [self.groups["p_bullets"].add(b) for b in bs]
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.state = "SHOP"; pygame.mouse.set_visible(True)
                if event.key == pygame.K_g and self.player.grenades > 0:
                    self.player.grenades -= 1
                    self.groups["grenades"].add(
                        Grenade(self.player.rect.centerx, self.player.rect.centery, world_mouse))
                if event.key == pygame.K_1 and self.player.bandages > 0:
                    self.player.hp = min(PLAYER_HP, self.player.hp + 45);
                    self.player.bandages -= 1

        if pygame.mouse.get_pressed()[0] and self.player.weapon_type == "AK-47":
            bs = self.player.shoot(world_mouse)
            if bs: [self.groups["p_bullets"].add(b) for b in bs]

        # Update
        self.player.update(pygame.key.get_pressed(), mouse_p, self.camera)
        self.camera.update(self.player)
        self.groups["enemies"].update(self.player.rect, self.groups["e_bullets"])
        for g in ["p_bullets", "e_bullets", "grenades"]: self.groups[g].update()

        # Вибухи гранат
        for gr in self.groups["grenades"]:
            if gr.exploded:
                for en in self.groups["enemies"]:
                    if math.hypot(gr.rect.centerx - en.rect.centerx, gr.rect.centery - en.rect.centery) < 200:
                        en.hp -= 120
                        if en.hp <= 0: en.kill(); self.killed += 1; self.total_k += 1; self.player.coins += 15
                gr.kill()

        # Хвилі та спавн
        if self.killed >= self.to_kill:
            self.wave += 1;
            self.to_kill += 5;
            self.killed = 0;
            self.player.coins += 100
        if len(self.groups["enemies"]) < (10 + self.wave):
            x, y = self.player.rect.x + random.choice([-1200, 1200]), self.player.rect.y + random.randint(-900, 900)
            self.groups["enemies"].add(
                Enemy(x, y, random.choices(["basic", "orange"], [75, 25])[0], 1.0 + (self.wave - 1) * 0.2))

        # Колізії
        if pygame.sprite.spritecollide(self.player, self.groups["enemies"], False): self.player.hp -= 0.8
        if pygame.sprite.spritecollide(self.player, self.groups["e_bullets"], True): self.player.hp -= 20
        if self.player.hp <= 0: self.state = "GAMEOVER"; pygame.mouse.set_visible(True)

        for b in self.groups["p_bullets"]:
            hits = pygame.sprite.spritecollide(b, self.groups["enemies"], False)
            for en in hits:
                en.hp -= b.damage
                if en.hp <= 0:
                    en.kill();
                    self.killed += 1;
                    self.total_k += 1;
                    self.player.coins += 15
                    if random.random() < 0.25: self.groups["items"].add(
                        Item(en.rect.centerx, en.rect.centery, "medkit"))
            if hits and not b.piercing: b.kill()

        for it in pygame.sprite.spritecollide(self.player, self.groups["items"], True): self.player.bandages += 1

        # Draw
        self.screen.fill(DARK_GREEN)
        for g in ["dec", "items", "enemies", "e_bullets", "p_bullets", "grenades"]:
            for s in self.groups[g]: self.screen.blit(s.image, self.camera.apply(s.rect))

        self.player.draw_weapon(self.screen, self.camera, mouse_p)
        self.screen.blit(self.player.image, self.camera.apply(self.player.rect))
        self.draw_hud()
        self.draw_crosshair(mouse_p)

        pygame.display.flip()
        self.clock.tick(FPS)

    def shop_loop(self):
        self.screen.fill((15, 25, 15))  # Темно-зелений фон магазину

        # Заголовок
        title = self.fonts["title"].render("BLACK MARKET", True, (200, 255, 200))
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        coins_txt = self.fonts["main"].render(f"YOUR COINS: {self.player.coins}", True, (255, 215, 0))
        self.screen.blit(coins_txt, (WIDTH // 2 - coins_txt.get_width() // 2, 130))

        # Список товарів (назва, ціна, клавіша, колір)
        items = [
            ("1. MEDKIT", 35, "K_1", (255, 100, 100)),
            ("2. SHOTGUN", 160, "K_2", (150, 150, 150)),
            ("3. AK-47", 280, "K_3", (200, 150, 50)),
            ("4. SNIPER", 450, "K_4", (100, 200, 255)),
            ("5. GRENADE", 60, "K_5", (100, 150, 100))
        ]

        # Малювання карток товарів
        for i, (name, price, key, color) in enumerate(items):
            rect_x = WIDTH // 2 - 250
            rect_y = 200 + i * 75

            # Фон картки (міняє колір, якщо вистачає грошей)
            bg_color = (40, 50, 40) if self.player.coins >= price else (30, 30, 30)
            border_color = color if self.player.coins >= price else (60, 60, 60)

            pygame.draw.rect(self.screen, bg_color, [rect_x, rect_y, 500, 65], border_radius=10)
            pygame.draw.rect(self.screen, border_color, [rect_x, rect_y, 500, 65], 2, border_radius=10)

            # Текст назви
            name_surf = self.fonts["main"].render(name, True, WHITE)
            self.screen.blit(name_surf, (rect_x + 20, rect_y + 15))

            # Текст ціни
            price_txt = f"{price} Coins"
            price_surf = self.fonts["main"].render(price_txt, True, (255, 215, 0))
            self.screen.blit(price_surf, (rect_x + 350, rect_y + 15))

        # Підказка для виходу
        exit_txt = self.fonts["hud"].render("Press ESC to Back to Forest", True, (150, 150, 150))
        self.screen.blit(exit_txt, (WIDTH // 2 - exit_txt.get_width() // 2, HEIGHT - 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "GAME"
                    pygame.mouse.set_visible(False)

                # Логіка покупок
                if event.key == pygame.K_1 and self.player.coins >= 35:
                    self.player.coins -= 35;
                    self.player.bandages += 1
                if event.key == pygame.K_2 and self.player.coins >= 160:
                    self.player.coins -= 160
                    self.player.weapon_type, self.player.max_ammo, self.player.ammo = "Shotgun", 6, 6
                if event.key == pygame.K_3 and self.player.coins >= 280:
                    self.player.coins -= 280
                    self.player.weapon_type, self.player.max_ammo, self.player.ammo = "AK-47", 30, 30
                if event.key == pygame.K_4 and self.player.coins >= 450:
                    self.player.coins -= 450
                    self.player.weapon_type, self.player.max_ammo, self.player.ammo = "Sniper", 5, 5
                if event.key == pygame.K_5 and self.player.coins >= 60:
                    self.player.coins -= 60;
                    self.player.grenades += 1

        pygame.display.flip()

    def game_over_loop(self):
        self.screen.fill((50, 0, 0))
        t = self.fonts["title"].render("GAME OVER", True, WHITE)
        s = self.fonts["main"].render(f"Wave: {self.wave} | Kills: {self.total_k}", True, WHITE)
        r = self.fonts["main"].render("Press 'R' to RESTART", True, (255, 200, 0))
        self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 200))
        self.screen.blit(s, (WIDTH // 2 - s.get_width() // 2, 300))
        self.screen.blit(r, (WIDTH // 2 - r.get_width() // 2, 420))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r: self.reset_game(); pygame.mouse.set_visible(
                False)
        pygame.display.flip()

    def run(self):
        while True:
            if self.state == "GAME":
                self.game_loop()
            elif self.state == "SHOP":
                self.shop_loop()
            else:
                self.game_over_loop()


if __name__ == "__main__":
    Game().run()
