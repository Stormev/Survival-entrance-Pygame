import pygame
from pygame.locals import *
import sqlite3
from random import randint
import sys
import os

# background size
# width 1024
# height 512
# background_3 <- background_1 ->  background_2

FPS = 15
pygame.init()
WIDTH, HEIGHT = size = 1024, 512
screen = pygame.display.set_mode(size=(WIDTH, HEIGHT))
clock = pygame.time.Clock()


database = sqlite3.connect('data/scores.db')
cursor = database.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS main
                (id INTEGER PRIMARY KEY AUTOINCREMENT,  
                scores INTEGER,
                time_life INTEGER,
                is_win INTEGER)
            """)


def out():  # Выход
    database.close()
    pygame.quit()
    sys.exit()


def load_image(name):  # Загрузка картинки
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"'{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


Locations = [load_image('images/background_3.png'), load_image('images/background_1.png'),
             load_image('images/background_2.png')]


def start_screen(): # Стартовый экран
    intro_text = ["Управление:", 'A - Движение налево', 'D - Движение направо']
    fon = 'images/start_screen_controll.png'
    fon = pygame.transform.scale(load_image(fon), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 120, 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('Black'))
        intro_rect = string_rendered.get_rect()
        text_coord = text_coord[0], text_coord[1] + 10
        intro_rect.top = text_coord[1]
        intro_rect.x = text_coord[0]
        text_coord = text_coord[0], text_coord[1] + intro_rect.height
        screen.blit(string_rendered, intro_rect)

    tip = font.render('Нажмите TAB чтобы начать игру', 1, pygame.Color('Black'))
    tip_rect = tip.get_rect()
    tip_rect.x = text_coord[0]
    tip_rect.y = 430
    screen.blit(tip, tip_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                out()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    return
        pygame.display.flip()
        clock.tick(FPS)


start_screen()
item_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()

SCORE = 0
TIME_LIFE = 0


class Player(pygame.sprite.Sprite): # Персонаж
    def __init__(self, pos_x):
        super().__init__(player_group)
        self.pos_y = HEIGHT - 155
        self.speed = 8

        self.hungry = 100
        self.temp = 36

        self.Rframes = []
        self.Lframes = []

        self.cut_sheet(load_image('images/pygame_character.png'), 3, 3)
        self.frames_static = self.Rframes[0:3]
        self.Lframes = self.Rframes[6:]
        self.Rframes = self.Rframes[3:6]
        self.cur_frame = 0
        self.image = self.frames_static[0]
        self.rect = self.rect.move(pos_x, self.pos_y)

    def move(self, side):  # True = right, False = Left ДВИЖЕНИЕ
        if side:
            self.rect = self.rect.move(self.speed, 0)

            self.cur_frame = (self.cur_frame + 1) % len(self.Rframes)
            self.image = self.Rframes[self.cur_frame]
        else:
            self.rect = self.rect.move(-self.speed, 0)

            self.cur_frame = (self.cur_frame + 1) % len(self.Lframes)
            self.image = self.Lframes[self.cur_frame]

    def static(self):
        self.image = self.frames_static[0]

    def cut_sheet(self, sheet, columns, rows):  # Нарезка
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.Rframes.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))


items = [[load_image('images/item_bytilka.png'), -5, -1], [load_image('images/item_chocolate.png'), 8, 3],
         [load_image('images/item_doshik.png'), 4, 2], [load_image('images/item_honey.png'), 12, 4]]


class Item(pygame.sprite.Sprite):
    def __init__(self, pos_x=randint(60, WIDTH - 60)):
        super().__init__(item_group)
        self.pos_y = HEIGHT - 70
        data = items[randint(0, len(items) - 1)]
        self.image = data[0]
        self.cost = data[1]
        self.score = data[2]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(pos_x, self.pos_y)


player = Player(-100)


def load_location(cur_id):
    if 0 <= cur_id < len(Locations):
        background = Locations[cur_id]
        screen.blit(background, (0, 0))


LOCATION_NOW = len(Locations) // 2


def next_locations(cur_player, turn):  # True = right False = left ЗАГРУЗКА ЛОКАЦИИ
    global LOCATION_NOW
    if turn and len(Locations) > LOCATION_NOW + 1:
        LOCATION_NOW += 1
        cur_player.rect.x = 100
    elif LOCATION_NOW - 1 >= 0 and not turn:
        LOCATION_NOW -= 1
        cur_player.rect.x = WIDTH - 150
    elif turn:
        cur_player.rect.x -= 20
    else:
        cur_player.rect.x += 20


def end_game(status):  # False = lose  True = wib GAME END
    screen.fill((50, 50, 70))
    fon = 'images/start_screen_controll.png'
    fon = pygame.transform.scale(load_image(fon), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    cursor.execute(f'''INSERT INTO main(scores, time_life, is_win) VALUES({SCORE}, {TIME_LIFE}, {status})''')
    database.commit()

    font = pygame.font.Font(None, 30)

    info = [f'Игра окончена! Ваш персонаж: {"Выжил" if status else "Невыжил"}', f'Ваши очки: {SCORE}',
            f'Вы прожили : {TIME_LIFE} секунд', f'Ваши Результаты были успешно сохранены!',
            f'Чтобы начать новую игру нажмите TAB',]

    text_coord = 120, 50
    for i, line in enumerate(info):
        if i == len(info) - 2:
            text_coord = text_coord[0], text_coord[1] + 185
        string_rendered = font.render(line, 1, pygame.Color('Black'))
        intro_rect = string_rendered.get_rect()
        text_coord = text_coord[0], text_coord[1] + 20
        intro_rect.top = text_coord[1]
        intro_rect.x = text_coord[0]
        text_coord = text_coord[0], text_coord[1] + intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                out()
            elif events.type == pygame.KEYDOWN:
                if events.key == pygame.K_TAB:
                    start_game()
        pygame.display.flip()
        clock.tick(FPS)


def start_game():
    global TIME_LIFE
    global player_group
    global item_group

    player_group = pygame.sprite.Group()
    item_group = pygame.sprite.Group()
    player = Player(WIDTH // 2.5)

    to_second_count = 0

    def collide_items():
        global SCORE
        for item in item_group:
            if player.rect.collidepoint(item.rect.center):
                player.hungry += item.cost
                SCORE += item.score
                item.kill()

    item = Item(300)
    # main cycle
    while True:
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                out()
            if keys[K_d]:
                player.move(True)
            elif keys[K_a]:
                player.move(False)
        plr_pos = player.rect.x
        if plr_pos < 50:
            next_locations(player, False)
        elif plr_pos > WIDTH - 50:
            next_locations(player, True)

        if to_second_count >= FPS:  # Счётчик 1-й секунды
            to_second_count = 0
            player.hungry -= 1
            TIME_LIFE += 1

            if randint(0, 4) == 4:
                player.temp -= 1

            print('--------------------------')
            print('Hungry:', player.hungry)
            print('Temperature:', player.temp)
        else:
            to_second_count += 1

        if player.hungry < 0:
            end_game(False)
            break
        elif player.temp <= 25:
            end_game(False)
            break

        screen.fill((50, 50, 70))
        load_location(LOCATION_NOW)

        collide_items()
        player_group.update()
        player_group.draw(screen)
        item_group.update()
        item_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


start_game()

