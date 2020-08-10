import pygame
import os
from PIL import Image
import time
import random
pygame.font.init()
pygame.init()


WIDTH, HEIGHT = 750,750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")


ufo_1_img = Image.open("C:\\Users\\Admin\\Desktop\\Deck\\ufo1.png")
ufo_2_img = Image.open("C:\\Users\\Admin\\Desktop\\Deck\\ufo2.png")
ufo_3_img = Image.open("C:\\Users\\Admin\\Desktop\\Deck\\ufo3.png")
Ufo_1 = pygame.image.fromstring(ufo_1_img.tobytes(), ufo_1_img.size, ufo_1_img.mode)
Ufo_2 = pygame.image.fromstring(ufo_2_img.tobytes(), ufo_2_img.size, ufo_2_img.mode)
Ufo_3 = pygame.image.fromstring(ufo_3_img.tobytes(), ufo_3_img.size, ufo_3_img.mode)

player_img = Image.open("C:\\Users\\Admin\\Desktop\\Deck\\spaceship.png").resize((100,90))
Player_Ship = pygame.image.fromstring(player_img.tobytes(), player_img.size, player_img.mode)

RED_LASER = pygame.image.load("C:\\Users\\Admin\\Desktop\\Deck\\pixel_laser_red.png")
GREEN_LASER = pygame.image.load("C:\\Users\\Admin\\Desktop\\Deck\\pixel_laser_green.png")
BLUE_LASER = pygame.image.load("C:\\Users\\Admin\\Desktop\\Deck\\pixel_laser_blue.png")
YELLOW_LASER = pygame.image.load("C:\\Users\\Admin\\Desktop\\Deck\\pixel_laser_yellow.png")

BG = pygame.transform.scale(pygame.image.load("C:\\Users\\Admin\\Desktop\\Deck\\b.png"), (WIDTH, HEIGHT))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self,obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30
    
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                #if obj.health == 0:
                  # lives -= 1
                self.lasers.remove(laser)

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = Player_Ship
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height()+10,  self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height()+10,  self.ship_img.get_width() * (self.health / self.max_health), 10))

class Enemy(Ship):
    COLOR_MAP = {
                    "red" : (Ufo_1, RED_LASER),
                    "green": (Ufo_3, GREEN_LASER),
                    "blue": (Ufo_2, BLUE_LASER)
                  }
    
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
    

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


class Button:
    def __init__(self, color, x, y, width, height):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, window, text, fontsize, outline = None):
        if outline:
            pygame.draw.rect(window, outline, (self.x-2, self.y-2, self.width+4, self.height+4), 0)

        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height), 0)

        font = pygame.font.SysFont('comicsans', fontsize)
        text_label = font.render(text, 1, (250,250,250))
        window.blit(text_label, (self.x + (int(self.width/2) - int(text_label.get_width()/2)), self.y + (int(self.height/2) - int(text_label.get_height()/2))))

    def isOver(self, pos):
        if pos[0] > self.x and pos[0] < self.x+ self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
        return False



def main():
    run = True
    end = 0
    FPS = 60
    level = 0
    lives = 3
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 70)
    enemies = []
    No_of_enemies = 5
    enemy_vel = 1
    player_vel = 5
    laser_vel = 7
    player = Player(300,630)
    lost = False
    lost_count = 0
    Main_menu_button = Button((0, 153, 153), 10, 10, 200, 40)

    def redraw_window():
        WIN.blit(BG, (0,0))

        # Draw Text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        WIN.blit(lives_label, (WIDTH - lives_label.get_width() - 10, 50))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        Main_menu_button.draw(WIN, "Back to Main Menu", 25)

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!", 1,  (255,255,255))
            WIN.blit(lost_label, (int(WIDTH/2) - int(lost_label.get_width()/2), 350))

        pygame.display.update()

    while run:
        redraw_window()

        if lives <= 0: #or player.health == 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 2:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            No_of_enemies += 5
            for i in range(No_of_enemies):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if Main_menu_button.isOver(pos):
                    return "menu"



            if event.type == pygame.MOUSEMOTION:
                if Main_menu_button.isOver(pos):
                    Main_menu_button.color = (0, 102, 102)
                else:
                    Main_menu_button.color = (0, 153, 153)


        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x  + player_vel + player.get_width() <WIDTH:
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height()  + 15 < HEIGHT:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            if player.health == 0:
                lives -= 1
                player.health = player.max_health

            if random.randrange(0, 1*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 20
                if player.health <= 0:
                    lives -= 1
                    player.health = player.max_health
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)




def instructions():
    Main_menu_button = Button((0, 153, 153), 10, 10, 200, 40)
    instr_font = pygame.font.SysFont("comicsans", 50)
    instruction_font = pygame.font.SysFont("comicsans", 30)
    run = True

    while run:
        WIN.blit(BG, (0,0))
        instr_label = instr_font.render("Instructions", 1, (255, 255, 255))
        WIN.blit(instr_label, (int(WIDTH / 2) - int(instr_label.get_width() / 2), 120))
        instructions1 = instruction_font.render("1. Kill enemy battleships by shooting lasers with Spacebar", 1, (255, 255, 255))
        WIN.blit(instructions1, (75, 200))
        instructions2 = instruction_font.render("2. Navigate using arrow keys", 1, (255, 255, 255))
        WIN.blit(instructions2, (75, 240))
        instructions3 = instruction_font.render("3. Player looses a life every time an enemy ship reaches bottom", 1, (255, 255, 255))
        WIN.blit(instructions3, (75, 280))
        instructions4 = instruction_font.render("or player health becomes zero", 1, (255, 255, 255))
        WIN.blit(instructions4, (100, 300))
        Main_menu_button.draw(WIN, "Back to Main Menu", 25)

        pygame.display.update()

        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()

            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if Main_menu_button.isOver(pos):
                    return "menu"

            if event.type == pygame.MOUSEMOTION:
                if Main_menu_button.isOver(pos):
                    Main_menu_button.color = (0, 102, 102)
                else:
                    Main_menu_button.color = (0, 153, 153)



def main_menu():
    MainMenu = True
    while MainMenu:
        welcome_font = pygame.font.SysFont("comicsans", 70)
        Begin_Game_button = Button((0, 153, 153), (int(WIDTH / 2) - 125), int(HEIGHT / 2) - 35, 250, 70)
        Instructions_button = Button((0, 153, 153), (int(WIDTH / 2) - 125), int(HEIGHT / 2) + 55, 250, 70)
        run = True
        while run:
            WIN.blit(BG, (0,0))
            welcome = welcome_font.render("Welcome to Space Shooter!", 1, (255, 255, 255))
            WIN.blit(welcome, (int(WIDTH / 2) - int(welcome.get_width() / 2), 195))
            Begin_Game_button.draw(WIN, "Begin Game", 40)
            Instructions_button.draw(WIN, "Instructions", 40)
            pygame.display.update()


            for event in pygame.event.get():
                pos = pygame.mouse.get_pos()

                if event.type == pygame.QUIT:
                    run = False
                    MainMenu = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if Begin_Game_button.isOver(pos):
                        a = main()
                        if a == "quit":
                            run = False
                            MainMenu = False
                        else:
                            run = False

                    if Instructions_button.isOver(pos):
                        a = instructions()
                        if a == "quit":
                            run = False
                            MainMenu = False
                        else:
                            run = False


                if event.type == pygame.MOUSEMOTION:
                    if Begin_Game_button.isOver(pos):
                        Begin_Game_button.color = (0, 102, 102)
                    else:
                        Begin_Game_button.color = (0, 153, 153)

                    if Instructions_button.isOver(pos):
                        Instructions_button.color = (0, 102, 102)
                    else:
                        Instructions_button.color = (0, 153, 153)

    pygame.quit()

if __name__ == "__main__":
    main_menu()
