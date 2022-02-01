import sqlite3
import os
import sys
import pygame
from random import randrange, random

previous_y = 0
previous_x = 252
pl = pygame.sprite.Group()

jumping = True
jumping_menu = False

running_qwe = True
running_start = True
running_falling = True
running_scores = True

collide_brown = False
collide_with = None

platforms_y = []

br = 0
bl = 0
gr = 10

points = 0

con = sqlite3.connect("score.sqlite")
cur = con.cursor()

pygame.mixer.init()
sound1 = pygame.mixer.Sound('sounds/jump.wav')
sound2 = pygame.mixer.Sound('sounds/lomise.mp3')
sound3 = pygame.mixer.Sound('sounds/pada.mp3')
sound4 = pygame.mixer.Sound('sounds/monsterblizu.mp3')
sound5 = pygame.mixer.Sound('sounds/monster-crash.mp3')
sound6 = pygame.mixer.Sound('sounds/ooga-pucanje2.mp3')
sound7 = pygame.mixer.Sound('sounds/monsterpogodak.mp3')
pygame.display.set_icon(pygame.image.load("data/icon@2x.png"))


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


######################################################


class DoodleBodyMenu(pygame.sprite.Sprite):
    image_r = load_image("doodle_r_body.png", -1)
    image_jr = load_image("doodle_jr.png", -1)

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Doodle_body.image_r
        self.rect = self.image.get_rect()
        self.rect.x = 110
        self.rect.y = 300

    def update(self, green_platforms, b, l):  #
        global jumping_menu
        self.image = DoodleBodyMenu.image_r
        if jumping_menu:
            self.image = DoodleBodyMenu.image_jr
            self.rect.y = l.rect.y - 41
        if not jumping_menu:
            self.rect.y = l.rect.y - 41


class DoodleLegsMenu(pygame.sprite.Sprite):
    image_r = load_image("doodle_r_legs.png", -1)
    image_n = load_image("nothing.png", -1)

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Doodle_legs.image_r
        self.rect = self.image.get_rect()
        self.rect.x = 113
        self.rect.y = 341
        self.velocity = 0.2
        self.gravity = 0.08

    def update(self, green_platforms, b, l):  #
        global jumping_menu
        if pygame.sprite.spritecollideany(self, green_platforms):
            jumping_menu = True
            self.velocity = 3.4
            s = cur.execute("""SELECT * FROM Sounds""").fetchall()[0][0]
            if s == 1:
                sound1.play()
        if jumping_menu and self.velocity >= 0.15:
            self.velocity -= self.gravity
            self.image = DoodleLegsMenu.image_n
            self.velocity = round(self.velocity, 2)
            self.rect.y -= self.velocity
        if self.velocity < 0.15:
            self.velocity = 0.2
            jumping_menu = False
        if not jumping_menu:
            self.velocity += self.gravity
            self.velocity = round(self.velocity, 2)
            self.rect.y += self.velocity
            self.image = DoodleLegsMenu.image_r


class PlatformMenu(pygame.sprite.Sprite):
    image = load_image("platform.png", -1)

    def __init__(self, *group):
        super().__init__(*group)
        self.image = PlatformMenu.image
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 500

    def update(self):
        pass


class Hello(pygame.sprite.Sprite):
    image = load_image("doodle-jump2.png", -1)

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Hello.image
        self.rect = self.image.get_rect()
        self.rect.x = 30
        self.rect.y = 30


class PlayButton(pygame.sprite.Sprite):
    image = load_image("play.png")
    image2 = load_image("play-on.png")

    def __init__(self, *group):
        super().__init__(*group)
        self.image = PlayButton.image
        self.rect = self.image.get_rect()
        self.rect.x = 90
        self.rect.y = 200

    def update(self, *args):
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(args[0].pos):
            qwe()
        if args and args[0].type == pygame.MOUSEMOTION and \
                self.rect.collidepoint(args[0].pos):
            self.image = PlayButton.image2
        else:
            self.image = PlayButton.image


class Scores(pygame.sprite.Sprite):
    image = load_image("scores.png")
    image2 = load_image("scores-on.png")

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Scores.image
        self.rect = self.image.get_rect()
        self.rect.x = 130
        self.rect.y = 260

    def update(self, *args):
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(args[0].pos):
            score()
        if args and args[0].type == pygame.MOUSEMOTION and \
                self.rect.collidepoint(args[0].pos):
            self.image = Scores.image2
        else:
            self.image = Scores.image


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, g):
        super().__init__(g)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.start = self.rect.x
        self.end = self.rect.x + 100

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        global running_start
        if not running_start:
            if self.rect.x == self.start:
                self.x_changing = 5
            if self.rect.x == self.end:
                self.x_changing = -5
            self.rect.x += self.x_changing


class OffOn(pygame.sprite.Sprite):
    image = load_image("on.png", -1)
    image2 = load_image("off.png", -1)

    def __init__(self, *group):
        super().__init__(*group)
        s = cur.execute("""SELECT * FROM Sounds""").fetchall()[0][0]
        if s == 1:
            self.off_on = True
            self.image = OffOn.image
        elif s == 0:
            self.off_on = False
            self.image = OffOn.image2
        self.rect = self.image.get_rect()
        self.rect.x = 370
        self.rect.y = 510

    def update(self, *args):
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(args[0].pos):
            if self.off_on:
                cur.execute(f"""UPDATE Sounds SET Off_on = 0""")
                con.commit()
                self.image = OffOn.image2
            elif not self.off_on:
                cur.execute(f"""UPDATE Sounds SET Off_on = 1""")
                con.commit()
                self.image = OffOn.image
            self.off_on = not self.off_on


def start():
    global running_start
    pygame.init()
    pygame.display.set_caption('Doodle Jump')
    size = 505, 650
    screen = pygame.display.set_mode(size)
    background_image = pygame.image.load("data/background.jpg").convert()

    all_sprites = pygame.sprite.Group()
    pl = pygame.sprite.Group()
    green_platforms = pygame.sprite.Group()
    doodle_sprite = pygame.sprite.Group()

    anim_sprites = pygame.sprite.Group()
    anim_sprites_muha = pygame.sprite.Group()

    ufo = AnimatedSprite(load_image("ufo2.png"), 2, 1, 340, 20, anim_sprites)
    beetle = AnimatedSprite(load_image("muha@2x.png", -1), 5, 1, 300, 350, anim_sprites_muha)

    if 1:
        sprite = pygame.sprite.Sprite()
        sprite.image = load_image("beetle1.png", -1)
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = 200
        sprite.rect.y = 500
        all_sprites.add(sprite)

        sprite = pygame.sprite.Sprite()
        sprite.image = load_image("beetle2.png", -1)
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = 150
        sprite.rect.y = 100
        all_sprites.add(sprite)

        sprite = pygame.sprite.Sprite()
        sprite.image = load_image("beetle3.png", -1)
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = 250
        sprite.rect.y = 270
        all_sprites.add(sprite)

        sprite = pygame.sprite.Sprite()
        sprite.image = load_image("beetle4.png", -1)
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = 50
        sprite.rect.y = 200
        all_sprites.add(sprite)

        sprite = pygame.sprite.Sprite()
        sprite.image = load_image("beetle5.png", -1)
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = 440
        sprite.rect.y = 310
        all_sprites.add(sprite)

        sprite = pygame.sprite.Sprite()
        sprite.image = load_image("hole.png")
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = 370
        sprite.rect.y = 200
        all_sprites.add(sprite)

        sprite = pygame.sprite.Sprite()
        sprite.image = load_image("порванная_бумага.png")
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = 0
        sprite.rect.y = 560
        all_sprites.add(sprite)

    PlayButton(pl)
    Scores(pl)
    OffOn(pl)
    Hello(all_sprites)
    PlatformMenu(green_platforms)

    l = DoodleLegsMenu(doodle_sprite)
    b = DoodleBodyMenu(doodle_sprite)

    coords = []

    fps = 90
    count = 0
    count2 = 0
    clock = pygame.time.Clock()

    while running_start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                global running_qwe
                global running_scores
                global running_falling
                running_scores, running_falling, running_qwe, running_start = False, False, False, False
            if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONDOWN:
                pl.update(event)
                all_sprites.update(event)

        doodle_sprite.update(green_platforms, b, l)

        screen.fill((255, 255, 255))
        screen.blit(background_image, [0, 0])

        all_sprites.draw(screen)
        pl.draw(screen)
        green_platforms.draw(screen)
        doodle_sprite.draw(screen)

        coords.append(l.rect.y)

        f = pygame.font.Font('font.ttf', 20)
        t = f.render('sounds', True, (0, 0, 0))
        screen.blit(t, (350, 470))

        if count == 15:
            anim_sprites.update()
            count = 0
        if count2 == 4:
            anim_sprites_muha.update()
            count2 = 0
        anim_sprites_muha.draw(screen)
        anim_sprites.draw(screen)
        clock.tick(fps)
        count += 1
        count2 += 1
        pygame.display.flip()
    pygame.quit()


#######################################################


class Platform(pygame.sprite.Sprite):
    image = load_image("platform.png", -1)

    def __init__(self, *group):
        super().__init__(*group)
        global previous_y, previous_x, pl, platforms_y
        self.image = Platform.image
        self.rect = self.image.get_rect()
        self.rect.x = randrange(previous_x - 200, previous_x + 200) % 420
        self.rect.y = randrange(previous_y + 57, previous_y + 63)
        while 25 >= self.rect.x or self.rect.x >= 420 or abs(self.rect.x - previous_x) <= 60 or \
                10 >= self.rect.y or self.rect.y >= 633:
            self.rect.x = randrange(previous_x - 200, previous_x + 200)
            self.rect.y = randrange(previous_y + 57, previous_y + 63)
        previous_y = self.rect.y
        previous_x = self.rect.x
        self.add(pl)
        for i in range(self.rect.y - 15, self.rect.y + 15):
            platforms_y.append(i)

    def update(self, green_platforms):
        pass


class AnimatedSpriteBrownPlatform(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, *group):
        super().__init__(*group)

        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]

        global previous_y, previous_x, pl, platforms_y
        self.rect.x = randrange(previous_x - 200, previous_x + 200) % 420
        self.rect.y = randrange(previous_y + 97, previous_y + 103)
        while pygame.sprite.spritecollideany(self, pl) or 25 >= self.rect.x or self.rect.x >= 420 or abs(
                self.rect.x - previous_x) <= 60 or \
                10 >= self.rect.y or self.rect.y >= 633:
            self.rect.x = randrange(previous_x - 200, previous_x + 200)
            self.rect.y = randrange(previous_y + 97, previous_y + 103)
        previous_y = self.rect.y
        previous_x = self.rect.x
        self.add(pl)

        for i in range(self.rect.y - 15, self.rect.y + 15):
            platforms_y.append(i)

        self.a = 1

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        global collide_brown
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if self.cur_frame == 4:
            collide_brown = False
            self.kill()


class BluePlatform(pygame.sprite.Sprite):
    image = load_image("blue_platform.png", -1)

    def __init__(self, *group):
        super().__init__(*group)
        global previous_y, previous_x, pl, platforms_y
        self.image = BluePlatform.image
        self.rect = self.image.get_rect()
        self.rect.x = randrange(100, 400)
        self.rect.y = randrange(50, 600)
        while self.rect.y in platforms_y:
            self.rect.y = randrange(100, 500)
        self.add(pl)
        for i in range(self.rect.y - 15, self.rect.y + 15):
            platforms_y.append(i)
        self.plus_min = 1

    def update(self, x):
        if self.rect.x <= 0:
            self.plus_min = 1
        elif self.rect.x >= 448:
            self.plus_min = -1
        a = x * self.plus_min
        self.rect.x += a


class Doodle_body(pygame.sprite.Sprite):
    image_l = load_image("doodle_l_body.png", -1)
    image_r = load_image("doodle_r_body.png", -1)
    image_jl = load_image("doodle_jl.png", -1)
    image_jr = load_image("doodle_jr.png", -1)
    image_shot = load_image("shot.png", -1)

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Doodle_body.image_r
        self.rect = self.image.get_rect()
        self.rect.x = 252
        self.rect.y = 600
        self.count2 = 0

    def update(self, x, l_r, green_platforms, br, bl, b, l, monsters):
        global jumping, COORD, shot
        if l_r:
            self.image = Doodle_body.image_l
        else:
            self.image = Doodle_body.image_r
        if jumping:
            if l_r:
                self.image = Doodle_body.image_jl
            else:
                self.image = Doodle_body.image_jr
            self.rect.y = l.rect.y - 41
        if not jumping:
            self.rect.y = l.rect.y - 41
        if shot:
            self.count2 += 1
            self.image = Doodle_body.image_shot
            if self.count2 > 30:
                shot = False
                self.count2 = 0

        self.rect.x = (self.rect.x + x) % 505
        COORD = self.rect.x, self.rect.y


class Doodle_legs(pygame.sprite.Sprite):
    image_r = load_image("doodle_r_legs.png", -1)
    image_l = load_image("doodle_l_legs.png", -1)
    image_n = load_image("nothing.png", -1)

    def __init__(self, *group):
        global jumping, points, jumping_start, shot
        super().__init__(*group)
        self.image = Doodle_legs.image_r
        self.rect = self.image.get_rect()
        self.rect.x = 255
        self.rect.y = 641
        jumping_start = 641
        self.velocity = 4.6
        self.gravity = 0.1
        self.score = points
        jumping = True

    def update(self, x, l_r, green_platforms, brown_platforms, blue_platforms, b, l, monsters):  #
        global points
        global jumping, jumping_start
        global collide_brown
        global collide_with
        global platforms_y, br, bl

        global previous_y, previous_x

        if self.rect.y > 650 or pygame.sprite.spritecollideany(self, monsters):
            sound4.stop()
            br = 0
            bl = 0
            s = cur.execute("""SELECT * FROM Sounds""").fetchall()[0][0]
            if s == 1 and pygame.sprite.spritecollideany(self, monsters):
                sound7.play()
            else:
                sound3.play()
            previous_y = 0
            previous_x = 252
            falling()
            b.kill()
            self.kill()
        if self.rect.y < 50:
            b.kill()
            self.kill()
            previous_y = 0
            previous_x = 252
            qwe()

        platforms_y = []

        if pygame.sprite.spritecollideany(self, brown_platforms) and not jumping:  #
            collide_brown = True
            collide_with = pygame.sprite.spritecollideany(self, brown_platforms)
            collide_with.a -= 1
            if collide_with.a == 0:
                s = cur.execute("""SELECT * FROM Sounds""").fetchall()[0][0]
                if s == 1:
                    sound2.play()
        if (pygame.sprite.spritecollideany(self, green_platforms) or pygame.sprite.spritecollideany(self,
                                                                                                    blue_platforms)) and not jumping:
            self.velocity = 3.4
            s = cur.execute("""SELECT * FROM Sounds""").fetchall()[0][0]
            if s == 1:
                sound1.play()
            self.score += jumping_start - self.rect.y
            jumping_start = self.rect.y
            jumping = True

        self.rect.x = (self.rect.x + x) % 505
        points = self.score

        if jumping and self.velocity >= 0.15:
            self.velocity -= self.gravity
            self.image = DoodleLegsMenu.image_n
            self.velocity = round(self.velocity, 2)
            self.rect.y -= self.velocity
        if self.velocity < 0.15:
            self.velocity = 0.2
            jumping = False
        if not jumping:
            self.velocity += self.gravity
            self.velocity = round(self.velocity, 2)
            self.rect.y += self.velocity
            if l_r:
                self.image = Doodle_legs.image_l
            else:
                self.image = Doodle_legs.image_r
        if shot:
            self.image = Doodle_legs.image_n


monsters = pygame.sprite.Group()


class Bullet(pygame.sprite.Sprite):
    image = load_image("пуля.png")

    def __init__(self, pos, *group):
        global COORD
        super().__init__(*group)
        self.image = Bullet.image
        self.rect = self.image.get_rect()
        self.rect.x = COORD[0] + 15
        self.rect.y = COORD[1]
        if abs(pos - self.rect.x) < 50:
            self.x_changing = 0
        elif pos > self.rect.x:
            self.x_changing = 5
        else:
            self.x_changing = -5

    def update(self):
        global monsters
        if pygame.sprite.spritecollideany(self, monsters):
            coll = pygame.sprite.spritecollideany(self, monsters)
            coll.kill()
            s = cur.execute("""SELECT * FROM Sounds""").fetchall()[0][0]
            if s == 1:
                sound5.play()
            sound4.stop()
        self.rect.x += self.x_changing
        self.rect.y -= 5


def qwe():
    global points
    global running_qwe
    global previous_y
    global previous_x
    global pl, br, bl, gr
    global shot

    for i in pl:
        i.kill()

    for i in monsters:
        i.kill()

    beetle = None
    if points >= 1000:
        if randrange(0, 2) == 0:
            if randrange(0, 2) == 0:
                beetle = AnimatedSprite(load_image("муха.png", -1), 5, 1, randrange(50, 350), randrange(50, 450),
                                        monsters)
            else:
                beetle = AnimatedSprite(load_image("monster3.png", -1), 4, 1, randrange(50, 350), randrange(50, 450),
                                        monsters)
    if beetle:
        s = cur.execute("""SELECT * FROM Sounds""").fetchall()[0][0]
        if s == 1:
            sound4.set_volume(1)
            sound4.play()
    pygame.init()
    pygame.display.set_caption('Doodle Jump')
    size = width, height = 505, 650
    screen = pygame.display.set_mode(size)
    background_image = pygame.image.load("data/background.jpg").convert()

    if points > 0 and br < 5:
        br += 1  #
        bl += 1  #
    gr = 10  #

    all_sprites = pygame.sprite.Group()
    Doodle_sprite = pygame.sprite.Group()
    green_platforms = pygame.sprite.Group()
    brown_platforms = pygame.sprite.Group()
    blue_platforms = pygame.sprite.Group()
    bullet_sprite = pygame.sprite.Group()

    doodle_legs = Doodle_legs(Doodle_sprite)
    b = Doodle_body(Doodle_sprite)
    for i in range(gr):  #
        Platform(green_platforms)

    previous_y = 0
    previous_x = 252

    for i in range(br):  #
        AnimatedSpriteBrownPlatform(load_image("brown_platform_anim.png", -1), 5, 1, brown_platforms)

    for i in range(bl):  #
        BluePlatform(blue_platforms)  #

    all_sprites.draw(screen)

    left_right = False
    x_pos = 0  #
    v = 120
    if points > 1500 and v <= 250:
        v += 5 * int(str(points)[0])
    fps = 90
    moving = False
    shot = False
    count2 = 0
    count_brown = 0
    clock = pygame.time.Clock()
    x_changing = 0

    while running_qwe:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                global running_start
                global running_scores
                global running_falling
                running_scores, running_falling, running_qwe, running_start = False, False, False, False
            if event.type == pygame.KEYUP and (event.key in [1073741903, 100] or event.key in [1073741904, 97]):
                moving = False
            if event.type == pygame.KEYDOWN and (event.key in [1073741903, 100] or event.key in [1073741904, 97]):
                moving = True
                if event.key in [1073741903, 100]:
                    x_changing = 5
                    left_right = False
                else:
                    left_right = True
                    x_changing = -5
            if event.type == pygame.MOUSEBUTTONDOWN:
                shot = True
                Bullet(event.pos[0], bullet_sprite)
                Doodle_body.image = load_image('shot.png', -1)
                s = cur.execute("""SELECT * FROM Sounds""").fetchall()[0][0]
                if s == 1:
                    sound6.play()
        if not moving:
            x_changing = 0
        Doodle_sprite.update(x_changing, left_right, green_platforms, brown_platforms, blue_platforms, b, doodle_legs,
                             monsters)
        bullet_sprite.update()
        screen.fill((255, 255, 255))
        screen.blit(background_image, [0, 0])

        all_sprites.draw(screen)
        green_platforms.draw(screen)

        if collide_brown:
            if count_brown == 3:
                collide_with.update()
                count_brown = 0
            count_brown += 1
        brown_platforms.draw(screen)

        x_pos = v // fps  #
        blue_platforms.update(x_pos)  #
        blue_platforms.draw(screen)  #

        if count2 == 4:
            monsters.update()
            count2 = 0
        monsters.draw(screen)
        count2 += 1

        Doodle_sprite.draw(screen)
        bullet_sprite.draw(screen)



        s = pygame.Surface((640, 40), pygame.SRCALPHA)
        s.fill((166, 202, 240, 240))
        screen.blit(s, (0, 0))
        f = pygame.font.Font('font.ttf', 24)
        t = f.render(f'{points}', True, (0, 0, 0))
        screen.blit(t, (20, 0))

        pygame.draw.line(screen, (0, 0, 0), (0, 40), (640, 40), 2)
        clock.tick(fps)
        pygame.display.flip()


#########################################################


class GoMenu(pygame.sprite.Sprite):
    image = load_image("menu.png")
    image1 = load_image('menu-on.png')

    def __init__(self, *group):
        super().__init__(*group)
        self.image = GoMenu.image
        self.rect = self.image.get_rect()
        self.rect.x = 140
        self.rect.y = 400
        self.a = 0

    def update(self, *args):
        global points
        if args and args[0].type == pygame.MOUSEMOTION and \
                self.rect.collidepoint(args[0].pos):
            self.image = GoMenu.image1
        else:
            self.image = GoMenu.image
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(args[0].pos):
            text = cur.execute("""SELECT * FROM Name""").fetchall()[0][0]
            cur.execute(f"""UPDATE Scores SET Name = '{text}' WHERE Score = {points}""")
            con.commit()
            points = 0
            start()


class Restart(pygame.sprite.Sprite):
    image = load_image("play.png")
    image2 = load_image('play-on.png')

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Restart.image
        self.rect = self.image.get_rect()
        self.rect.x = 260
        self.rect.y = 360
        self.a = 0

    def update(self, *args):
        global points
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(args[0].pos):
            text = cur.execute("""SELECT * FROM Name""").fetchall()[0][0]
            cur.execute(f"""UPDATE Scores SET Name = '{text}' WHERE Score = {points}""")
            con.commit()
            points = 0
            qwe()
        elif args and args[0].type == pygame.MOUSEMOTION and \
                self.rect.collidepoint(args[0].pos):
            self.image = Restart.image2
        else:
            self.image = Restart.image


def falling():
    global running_falling
    global points
    pygame.init()
    pygame.display.set_caption('Doodle Jump')
    size = 505, 650
    screen = pygame.display.set_mode(size)
    background_image = pygame.image.load("data/background.jpg").convert()

    name = cur.execute("""SELECT * FROM name""").fetchall()[0][0]
    a = randrange(10, 3000)
    cur.execute(f"""INSERT INTO scores(name, score) VALUES('{name}', {points})""")
    con.commit()

    font = pygame.font.Font(None, 32)
    input_box = pygame.Rect(230, 285, 140, 32)
    color_inactive = pygame.Color(210, 150, 54)
    color_active = pygame.Color(182, 125, 110)
    color = color_inactive
    active = False
    all_sprites = pygame.sprite.Group()
    pl = pygame.sprite.Group()
    text = cur.execute("""SELECT * FROM name""").fetchall()[0][0]
    if 1:
        sprite = pygame.sprite.Sprite()
        sprite.image = load_image("game_over.png", -1)
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = 30
        sprite.rect.y = 50
        all_sprites.add(sprite)

        sprite = pygame.sprite.Sprite()
        sprite.image = load_image("your_score.png", -1)
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = 130
        sprite.rect.y = 210
        all_sprites.add(sprite)

        sprite = pygame.sprite.Sprite()
        sprite.image = load_image("your_high_score.png", -1)
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = 70
        sprite.rect.y = 240
        all_sprites.add(sprite)

        sprite = pygame.sprite.Sprite()
        sprite.image = load_image("your_name.png", -1)
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = 70
        sprite.rect.y = 290
        all_sprites.add(sprite)

        sprite = pygame.sprite.Sprite()
        sprite.image = load_image("tap_to_change.png", -1)
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = 340
        sprite.rect.y = 320
        all_sprites.add(sprite)

        sprite = pygame.sprite.Sprite()
        sprite.image = load_image("порванная_бумага.png")
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = 0
        sprite.rect.y = 530
        all_sprites.add(sprite)

        r = Restart(pl)
        m = GoMenu(pl)
    r.a = a
    m.a = a
    fps = 70
    clock = pygame.time.Clock()

    while running_falling:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                global running_start
                global running_qwe
                global running_scores
                running_scores, running_falling, running_qwe, running_start = False, False, False, False
            if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONDOWN:
                pl.update(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    cur.execute(f"""UPDATE Name SET name = '{text}'""")
                    con.commit()
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        active = False
                        cur.execute(f"""UPDATE Name SET name = '{text}'""")
                        con.commit()
                        color = color_active if active else color_inactive
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        if len(text) < 12:
                            if event.unicode not in ['й', 'Й', 'ц', 'Ц', 'у', 'У', 'к', 'К', 'е', 'Е', 'н', 'Н', 'г',
                                                     'Г',
                                                     'Ш', 'ш', 'щ', 'Щ', 'з', 'З', 'Х', 'х',
                                                     'Ъ', 'ъ', 'ё', 'Ё', 'ф', 'Ф', 'ы', 'Ы', 'в', 'В', 'а', 'А', 'п',
                                                     'П',
                                                     'р', 'Р', 'о', 'О', 'л', 'Л', 'д', 'Д',
                                                     'ж', 'Ж', 'э', 'Э', 'я', 'Я', 'ч', 'Ч', 'с', 'С', 'м', 'М', 'и',
                                                     'И',
                                                     'т', 'Т', 'ь', 'Ь', 'Б', 'б', 'ю', 'Ю']:
                                text += event.unicode
        screen.fill((255, 255, 255))
        screen.blit(background_image, [0, 0])

        all_sprites.draw(screen)
        pl.draw(screen)

        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)

        result = cur.execute("""SELECT * FROM scores""").fetchall()
        result = sorted(result, key=lambda x: x[1])
        result.reverse()
        f = pygame.font.Font('font.ttf', 24)
        t = f.render(f'{result[0][1]}', True, (0, 0, 0))
        screen.blit(t, (300, 240))

        f = pygame.font.Font('font.ttf', 24)
        t = f.render(f'{points}', True, (0, 0, 0))
        screen.blit(t, (300, 200))

        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()


#########################################################

class GoMenuScores(pygame.sprite.Sprite):
    image = load_image("menu.png")
    image1 = load_image('menu-on.png')

    def init(self, *group):
        super().__init__(*group)
        self.image = GoMenu.image
        self.rect = self.image.get_rect()
        self.rect.x = 140
        self.rect.y = 400
        self.a = 0

    def update(self, *args):
        if args and args[0].type == pygame.MOUSEMOTION and \
                self.rect.collidepoint(args[0].pos):
            self.image = GoMenu.image1
        else:
            self.image = GoMenu.image
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(args[0].pos):
            start()


def score():
    global running_scores
    pygame.init()
    pygame.display.set_caption('Doodle Jump')
    size = 505, 650
    screen = pygame.display.set_mode(size)
    background_image = pygame.image.load("data/background.jpg").convert()

    all_sprites = pygame.sprite.Group()
    pl = pygame.sprite.Group()
    green_platforms = pygame.sprite.Group()
    doodle_sprite = pygame.sprite.Group()

    if 1:
        sprite = pygame.sprite.Sprite()
        sprite.image = load_image("beetle1.png", -1)
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = 65
        sprite.rect.y = 30
        all_sprites.add(sprite)

        sprite = pygame.sprite.Sprite()
        sprite.image = load_image("beetle5.png", -1)
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = 30
        sprite.rect.y = 400
        all_sprites.add(sprite)

        sprite = pygame.sprite.Sprite()
        sprite.image = load_image("beetle3.png", -1)
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = 370
        sprite.rect.y = 50
        all_sprites.add(sprite)

        sprite = pygame.sprite.Sprite()
        sprite.image = load_image("beetle4.png", -1)
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = 50
        sprite.rect.y = 120
        all_sprites.add(sprite)

        sprite = pygame.sprite.Sprite()
        sprite.image = load_image("scores_stats.png", -1)
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = 100
        sprite.rect.y = 90
        all_sprites.add(sprite)

        sprite = pygame.sprite.Sprite()
        sprite.image = load_image("порванная_бумага.png")
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = 0
        sprite.rect.y = 560
        all_sprites.add(sprite)

    a = GoMenu(pl)
    a.rect.y = 500
    a.rect.x = 300
    Hello(all_sprites)
    PlatformMenu(green_platforms)

    l = DoodleLegsMenu(doodle_sprite)
    b = DoodleBodyMenu(doodle_sprite)

    all_sprites.draw(screen)

    fps = 90
    clock = pygame.time.Clock()

    while running_scores:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                global running_start
                global running_qwe
                global running_falling
                running_scores, running_falling, running_qwe, running_start = False, False, False, False
            if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONDOWN:
                pl.update(event)
                all_sprites.update(event)

        doodle_sprite.update(green_platforms, b, l)

        screen.fill((255, 255, 255))
        screen.blit(background_image, [0, 0])

        all_sprites.draw(screen)
        pl.draw(screen)
        green_platforms.draw(screen)
        doodle_sprite.draw(screen)

        result = cur.execute("""SELECT * FROM scores""").fetchall()
        result = sorted(result, key=lambda x: x[1])
        result.reverse()
        flag = False
        pygame.draw.rect(screen, (pygame.Color(0, 0, 0)), (200, 170, 320, 312), 2)
        for i in range(5):
            if i % 2 == 0:
                pygame.draw.rect(screen, (pygame.Color(244, 220, 187)), (202, 172 + i * 60, 310, 68))
                y = 172 + i * 60
            else:
                pygame.draw.rect(screen, (pygame.Color(250, 239, 224)), (202, 172 + i * 60, 310, 60))
                y = 172 + i * 60
            if len(result) >= 5:
                font = pygame.font.Font('font.ttf', 16)
                text = font.render(f" {i + 1}. " + f'{result[i][0]}', True, (0, 0, 0))
                screen.blit(text, (210, y + 15))

                font = pygame.font.Font('font.ttf', 16)
                text = font.render(f'{result[i][1]}', True, (0, 0, 0))
                screen.blit(text, (400, y + 15))
            else:
                flag = True
        y = 0
        if flag:
            for i in range(len(result)):
                y = 172 + i * 60
                font = pygame.font.Font('font.ttf', 16)
                text = font.render(f" {i + 1}. " + f'{result[i][0]}', True, (0, 0, 0))
                screen.blit(text, (210, y + 15))

                font = pygame.font.Font('font.ttf', 16)
                text = font.render(f'{result[i][1]}', True, (0, 0, 0))
                screen.blit(text, (400, y + 15))

            flag = False
            y = 0

        doodle_sprite.draw(screen)
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    start()
