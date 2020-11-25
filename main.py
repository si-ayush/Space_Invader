import pygame
import os
import time
import random
from Ship import Ship
from Ship import Laser
from Ship import collide

from pygame import mixer

pygame.font.init()
pygame.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

RED_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
BLUE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
GREEN_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))

# player ship
YELLOW_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))

# Asteroid
ASTEROID_IMG = pygame.image.load(os.path.join("assets", "asteroid.png"))

YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
BULLET_SOUND = mixer.Sound(os.path.join("assets", "laser.wav"))

COLLISION_SOUND = mixer.Sound(os.path.join("assets", "explosion.wav"))

# Background
BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))
mixer.music.load(os.path.join("assets", "background.wav"))
mixer.music.play(-1)


class Asteroid:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.asteroid_img = ASTEROID_IMG
        self.mask = pygame.mask.from_surface(self.asteroid_img)

    def move_asteroid(self, velocity):
        self.y += velocity

    def draw(self, window):
        window.blit(self.asteroid_img, (self.x, self.y))


class Player(Ship):

    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, velocity, objs):
        self.cool_down()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        COLLISION_SOUND.play()
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):

        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):

        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (
            self.x, self.y + self.ship_img.get_height() + 10,
            self.ship_img.get_width() * ((self.health) / self.max_health),
            10))


class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SHIP, RED_LASER),
        "blue": (BLUE_SHIP, BLUE_LASER),
        "green": (GREEN_SHIP, GREEN_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def moveTopBottom(self, velocity):
        self.y += velocity

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def main():
    run = True
    FPS = 60
    level = 0
    lives = 3
    lost = False
    lost_count = 0

    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_velocity = 1
    player_velocity = 5
    laser_velocity = 5
    player = Player(300, 630)
    asteroids = []
    clock = pygame.time.Clock()

    def redraw_window():
        WIN.blit(BACKGROUND, (0, 0))

        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        for asteroid in asteroids:
            asteroid.draw(WIN)

        if lost:
            lost_label = lost_font.render("YOU LOST !!", 1, (255, 255, 255))
            WIN.blit(lost_label, ((WIDTH - lost_label.get_width()) / 2, 350))
        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            laser_velocity += 1
            player_velocity += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                              random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

            for i in range(3):
                asteroid = Asteroid(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100))
                asteroids.append(asteroid)
        #if random.randrange(0,  60) == 1:
        #Asteroid(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100))
        #asteroid.move_asteroid(7)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed();
        if keys[pygame.K_a] and player.x - player_velocity > 0:
            player.x -= player_velocity
        if keys[pygame.K_d] and player.x + player_velocity + player.get_width() < WIDTH:
            player.x += player_velocity
        if keys[pygame.K_w] and player.y - player_velocity > 0:
            player.y -= player_velocity
        if keys[pygame.K_s] and player.y + player_velocity + player.get_height() + 15 < HEIGHT:
            player.y += player_velocity
        if keys[pygame.K_SPACE]:
            BULLET_SOUND.play()
            player.shoot()

        for asteroid in asteroids[:]:
            asteroid.move_asteroid(enemy_velocity)

            if collide(asteroid,player):
                COLLISION_SOUND.play()
                lives -= 1
                asteroids.remove(asteroid)

        for enemy in enemies[:]:
            enemy.moveTopBottom(enemy_velocity)
            enemy.move_lasers(laser_velocity, player)
            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                COLLISION_SOUND.play()
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_velocity, enemies)


def main_menu():
    run = True
    title_font = pygame.font.SysFont("comicsans", 75)
    while run:
        WIN.blit(BACKGROUND, (0, 0))
        title_label = title_font.render("Press the mouse to begin . . . ", 1, (0, 0, 255))
        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()


main_menu()
