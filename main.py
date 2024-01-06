import pygame
import sys
import os

# background size
# width 1024
# height 512
# background_3 <- background_1 ->  background_2

FPS = 50
pygame.init()
WIDTH, HEIGHT = size = 1024, 512
screen = pygame.display.set_mode(size=(WIDTH, HEIGHT))
clock = pygame.time.Clock()


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)

    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


Locations = [load_image('images/background_1.png'), load_image('images/background_2.png'),
             load_image('images/background_3.png')]


def start_screen():
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
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    return
        pygame.display.flip()
        clock.tick(FPS)


start_screen()
player_group = pygame.sprite.Group()
background_group = pygame.sprite.Group()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x):
        super().__init__(player_group)
        self.frames = []
        self.cut_sheet(load_image('images/pygame_character.png'), 2, 2)
        self.frames_static = self.frames[0:2]
        self.cur_frame = 0
        self.image = self.frames_static[0]
        self.rect = self.rect.move(pos_x, HEIGHT - 170)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        pass
        #self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        #self.image = self.frames[self.cur_frame]


def load_location(cur_id):
    if 0 < cur_id < len(background_group):
        background = Locations[cur_id]
        screen.blit(background, (0, 0))


LOCATION_NOW = 0
player = Player(WIDTH // 2.5)

# main cycle
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()

    screen.fill((50, 50, 70))
    load_location(LOCATION_NOW)
    player_group.update()
    player_group.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)