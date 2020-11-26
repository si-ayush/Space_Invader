import pygame
import os
import random
from Ship import Ship
from Ship import Laser
from Ship import collide
from pygame import mixer

pygame.font.init()
pygame.init()

# Main Window Size
WIDTH, HEIGHT = 1000, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders" )

RED_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
BLUE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
GREEN_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))

# Player Ship
YELLOW_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))

# Asteroid
ASTEROID_IMG = pygame.image.load(os.path.join("assets", "asteroid.png"))
METEROID = pygame.image.load(os.path.join("assets", "asteroid.png"))
GEM = pygame.image.load(os.path.join("assets","energy.png"))

# Energy
ENERGY_IMG = pygame.image.load(os.path.join("assets", "energy.png"))

YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

BULLET_SOUND = mixer.Sound(os.path.join("assets", "laser.wav"))
LOSS_SOUND =   mixer.Sound(os.path.join("assets", "loss.wav"))
COLLISION_SOUND = mixer.Sound(os.path.join("assets", "explosion.wav"))

SPACE_INVADER_IMG = pygame.image.load(os.path.join("assets", "space_title.png"))
ENEMY_TITLE = pygame.image.load(os.path.join("assets", "enemy_title.png"))

# Background
BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))
mixer.music.load(os.path.join("assets", "background.wav"))
mixer.music.play(-1)

LEVEL_UP = "Level Up !!"
class Creature:
    def __init__(self,x, y):
        self.x = x
        self.y = y
        self.img = None
        self.mask = None

    def moveTopBottom(self, vel):
        self.y += vel

    def draw(self, window):
        window.blit(self.img,(self.x,self.y))

    def get_height(self):
        return self.img.get_height()

    def checkCollision(self, objs):
        for obj in objs[:]:
            if collide(self, obj):
                objs.remove(obj)

class Meteroid(Creature):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.img = METEROID
        self.vel = 3
        self.mask = pygame.mask.from_surface(self.img)
class Gem(Creature):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.img = GEM
        self.mask = pygame.mask.from_surface(self.img)
        self.vel = 3

class Player(Ship):

    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.score = 0

    def move_lasers(self, velocity, objs1, objs2):
        self.cool_down()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs1:
                    if laser.collision(obj):
                        COLLISION_SOUND.play()
                        objs1.remove(obj)
                        self.score += obj.enemy_points
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                for obj in objs2:
                    if laser.collision(obj):
                        COLLISION_SOUND.play()
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
        "red": (RED_SHIP, RED_LASER, 5),
        "green": (GREEN_SHIP, GREEN_LASER, 10),
        "blue": (BLUE_SHIP, BLUE_LASER, 15)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img,self.enemy_points = self.COLOR_MAP[color]
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
    score = 0
    lost = False
    lost_count = 0

    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 50)
    score_font = pygame.font.SysFont("comicsans", 50)
    level_up_font = pygame.font.SysFont("comicsans", 70)

    enemies = []
    wave_length = 5
    enemy_velocity = 1
    player_velocity = 5
    laser_velocity = 5
    gem_count = -1
    player = Player(300, 630)
    meteroids = []
    gems = []
    clock = pygame.time.Clock()
    pause = False
    hold_count = 0

    level_up_label = level_up_font.render(f"LEVEL UP", 1, (255, 255, 255))
    level_up_label2 = level_up_font.render(f"LEVEL UP", 1, (0, 0, 0))

    def redraw_window():
        WIN.blit(BACKGROUND, (0, 0))

        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        score_label = score_font.render(f"Score: {player.score}", 1, (255, 255, 255))


        if get_high_score() > player.score:
            high_score_label = score_font.render(f"High Score: {get_high_score()}", 1, (255, 255, 255))
        else:
            high_score_label = score_font.render(f"High Score: {player.score}", 1, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(score_label, (10, 50))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(high_score_label, (WIDTH - high_score_label.get_width() - 10, 50))


        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        for meteroid in meteroids:
            meteroid.draw(WIN)

        for gem in gems:
            gem.draw(WIN)

        if lost:
           # LOSS_SOUND.play()
            lost_label = lost_font.render("YOU LOST !!", 1, (255, 255, 255))
            WIN.blit(lost_label, ((WIDTH - lost_label.get_width()) / 2, 350))
            high = get_high_score()
            if player.score > high:
                save_high_score(player.score)


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


            if hold_count < FPS*1 and level > 0 :
                hold_count += 1
                WIN.blit(level_up_label, ((WIDTH - level_up_label.get_width())/2, 350))
                pygame.display.update()

                continue

            level += 1
            hold_count = 0
            gem_count += 1
            laser_velocity += 1
            player_velocity += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                              random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

            for j in range(gem_count):
                meteroid = Meteroid(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100))
                meteroids.append(meteroid)

            for k in range(gem_count):
                gem = Gem(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100))
                gems.append(gem)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
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

        for meteroid in meteroids[:]:
            meteroid.moveTopBottom(enemy_velocity + 1)
            if collide(meteroid, player):
                COLLISION_SOUND.play()
                lives -= 1
                meteroids.remove(meteroid)
            elif meteroid.y + meteroid.get_height() > HEIGHT:
                meteroids.remove(meteroid)

        for gem in gems[:]:
            gem.moveTopBottom(enemy_velocity + 1)
            if collide(gem, player):
                lives += 1
                player.health = 100
                COLLISION_SOUND.play()
                gems.remove(gem)
            elif gem.y + gem.get_height() > HEIGHT:
                gems.remove(gem)

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

        player.move_lasers(-laser_velocity, enemies, meteroids)


def main_menu():
    global TOP_HEIGHT
    run = True
    title_font = pygame.font.SysFont("comicsans", 75)
    while run:
        WIN.blit(BACKGROUND, (0, 0))

        WIN.blit(SPACE_INVADER_IMG, ((WIDTH - 240)/2, 25))
        WIN.blit(ENEMY_TITLE, ((WIDTH - 220) / 2, 225))
        title_label = title_font.render("Press the mouse to begin . . . ", 1, (180, 180, 255))
        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 550))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()


def save_high_score(score):
    try:
        high_score_file = open("high_score.txt", "w")
        high_score_file.write(str(score))
        high_score_file.close()
    except IOError:
        print("Unable to save")


def get_high_score():
    high_score = 0
    try:
        high_score_file = open("high_score.txt", "r")
        high_score = int(high_score_file.read())
        high_score_file.close()
    except IOError:
        print("No High Score")
    except ValueError:
        print("High Score Value error ")
    return high_score


main_menu()
