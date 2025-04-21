"""

  __  __       _          _____                      _
 |  \/  |     (_)        / ____|                    | |
 | \  / | __ _ _ _ __   | |  __  __ _ _ __ ___   ___| | ___   ___  _ __
 | |\/| |/ _` | | '_ \  | | |_ |/ _` | '_ ` _ \ / _ \ |/ _ \ / _ \| '_ \
 | |  | | (_| | | | | | | |__| | (_| | | | | | |  __/ | (_) | (_) | |_) |
 |_|  |_|\__,_|_|_| |_|  \_____|\__,_|_| |_| |_|\___|_|\___/ \___/| .__/
                                                                  | |
                                                                  |_|

"""

# Main libraries
import json, pygame, math, os, time, random
from sys import exit
from pytmx.util_pygame import load_pygame

# Get all information from other files
from images import *
from classes import *
from variables import *


# Screen information
screen_x = 1920
screen_y = 1080
os.environ['SDL_AUDIODRIVER'] = 'dsp'
pygame.init()
window = pygame.display.set_mode((screen_x, screen_y))
clock = pygame.time.Clock()


def can_shoot():
    global shoot_last_attack_time
    current_time = pygame.time.get_ticks()
    if current_time - shoot_last_attack_time >= shoot_attack_cooldown_time:
        shoot_last_attack_time = current_time
        return True
    return False

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 10
        self.direction = direction

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right < 0 or self.rect.left > screen_x:
            self.kill()
        for enemy_fly in enemy_fly_sprites:
            if self.mask.overlap(enemy_fly.mask, (self.rect.x - enemy_fly.rect.x, self.rect.y - enemy_fly.rect.y)):
                enemy_fly.kill()
                money_small = Money_small(enemy_fly.rect.centerx, enemy_fly.rect.centery, money_small_scaled)
                money_small_sprites.add(money_small)
                all_sprites.add(money_small)
                break

        for enemy_ground in enemy_ground_sprites:
            if self.mask.overlap(enemy_ground.mask,
                                 (self.rect.x - enemy_ground.rect.x, self.rect.y - enemy_ground.rect.y)):
                enemy_ground.kill()
                money_big = Money_big(enemy_ground.rect.centerx + random.randint(0, 100), enemy_ground.rect.centery,
                                      money_big_scaled)
                money_big_sprites.add(money_big)
                all_sprites.add(money_big)
                for i in range(2):
                    money_small = Money_small(enemy_ground.rect.centerx + random.randint(0, 100),
                                              enemy_ground.rect.centery, money_small_scaled)
                    money_small_sprites.add(money_small)
                    all_sprites.add(money_small)
                break

# Sprite data
all_sprites = pygame.sprite.Group()
enemy_fly_sprites = pygame.sprite.Group()
enemy_ground_sprites = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()
projectile_sprites = pygame.sprite.Group()
money_small_sprites = pygame.sprite.Group()
money_big_sprites = pygame.sprite.Group()
tile_sprites = pygame.sprite.Group()
spike_sprites = pygame.sprite.Group()


idle_owl = [owl_spritesheet.parse_sprite('Owl1.png'),owl_spritesheet.parse_sprite('Owl2.png'),owl_spritesheet.parse_sprite('Owl3.png'),owl_spritesheet.parse_sprite('Owl4.png')]

# Getting positions from files
with open(spike_json, 'r') as json_file:
    spike_data = json.load(json_file)
    level_data = next((lvl for lvl in spike_data if lvl["level"] == levelnum), None)
    if level_data and "spike" in level_data:
        for spike_data in level_data["spike"]:
            if "x" in spike_data and "y" in spike_data:
                spike = Spike(spike_data["x"], spike_data["y"], spikes_scaled)
                spike_sprites.add(spike)
                all_sprites.add(spike)
with open(path_points_json, 'r') as json_file:
    path_points_data = json.load(json_file)
with open(enemy_fly_json, 'r') as json_file:
    enemy_fly_data = json.load(json_file)
    for enemy_data in enemy_fly_data:
        enemy_paths = []
        for path_entry in path_points_data:
            if path_entry["enemy_id"] == enemy_data["id"]:
                enemy_paths = [(p["x"], p["y"], p["x2"], p["y2"]) for p in path_entry["paths"]]

        enemy_fly = Enemy_fly(enemy_data["x"], enemy_data["y"], 2, images=idle_owl, path=enemy_paths)
        enemy_fly_sprites.add(enemy_fly)
        all_sprites.add(enemy_fly)
with open(enemy_ground_json, 'r') as json_file:
    enemy_ground_data = json.load(json_file)
    for enemy_ground_data in enemy_ground_data:
        enemy_ground = Enemy_ground(enemy_ground_data["x"], enemy_ground_data["y"], enemy_ground_scaled)
        enemy_ground_sprites.add(enemy_ground)
        all_sprites.add(enemy_ground)

for layer in tmx_data.visible_layers:
    if hasattr(layer, 'data'):
        for x, y, surf in layer.tiles():
            pos = (x * 24, y * 24)
            Tile(pos=pos, surf=surf, groups=tile_sprites)

enemy_sprites.add(enemy_fly_sprites)
enemy_sprites.add(enemy_ground_sprites)

#PreInstalization
playerclass = Player(window, player_scaled, 80, 1000, 5, 1, 1, 1, .5, 100)
camera = Camera(2000, 2000)


# Gameloop
run = True
while run:
    clock.tick(60)

    # Player inputs
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and can_jump > 0:
                playerclass.jump(tile_sprites)
    if keys[pygame.K_a]:
        playerclass.move(-1, tile_sprites)
    if keys[pygame.K_d]:
        playerclass.move(1, tile_sprites)

    if keys[pygame.K_e]:
        if can_shoot():
            projectile = Projectile(playerclass.rect.centerx, playerclass.rect.centery, 1 if playerclass.direction == 1 else -1,projectile_scaled)
            all_sprites.add(projectile)
            projectile_sprites.add(projectile)

    # Enemy Behavior
    for enemy_fly in enemy_fly_sprites:
        enemy_fly.follow_player(playerclass, 2, 300)
    for enemy1 in enemy_fly_sprites:
        for enemy2 in enemy_fly_sprites:
            if enemy1 != enemy2:
                offset = (
                enemy2.rect.x - enemy1.rect.x, enemy2.rect.y - enemy1.rect.y)
                if enemy1.mask.overlap(enemy2.mask, offset):

                    if enemy1.rect.centerx < enemy2.rect.centerx:
                        enemy1.rect.x -= enemy_fly_speed
                        enemy2.rect.x += enemy_fly_speed
                    else:
                        enemy1.rect.x += enemy_fly_speed
                        enemy2.rect.x -= enemy_fly_speed

    # Ground enemy Behavior
    for enemy_ground in enemy_ground_sprites:
        enemy_ground.walk(tile_sprites)
    for enemy_ground in enemy_ground_sprites:
        if enemy_ground_speed == 2:
            enemy_ground.image = enemy_ground_scaled
        else:
            enemy_ground.image = enemy_ground_flipped

    # Projectile updates
    projectile_sprites.update()


    #Money
    font = pygame.font.SysFont('Comic Sans MS', 40)
    money1 = playerclass.get_money_value()
    money_text = str(money1)
    text_surface = font.render(money_text, False, (0, 0, 0))
    text_pos = 60, 0
    money_symbol_pos = (10, 10)

    for money_small in money_small_sprites:
        money_small.update(tile_sprites)
    for money_big in money_big_sprites:
        money_big.update(tile_sprites)

    # Color window
    window.fill((255, 255, 255))

    # Update player first
    playerclass.update(tile_sprites, enemy_sprites, money_small_sprites, money_big_sprites, spike_sprites)

    enemy_fly_sprites.update(.2)

    # Camera follows player
    camera.follow(playerclass)

    # Draw tiles with camera
    for sprite in tile_sprites:
        window.blit(sprite.image, camera.apply(sprite))

    # Draw enemies or other sprites
    for sprite in all_sprites:
        window.blit(sprite.image, camera.apply(sprite))

    # Draw player

    window.blit(playerclass.image, camera.apply(playerclass))

    # Draw player health bar
    playerclass.draw_health_bar(window, camera)

    # Draw UI (text, money symbol — no camera offset needed)
    window.blit(text_surface, text_pos)
    window.blit(money_symbol_scaled, money_symbol_pos)

    # Update display
    pygame.display.flip()

pygame.quit()