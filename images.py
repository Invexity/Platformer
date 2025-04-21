import json, pygame, math, os, time

screen_x = 1920
screen_y = 1080

enemy_fly_image = pygame.image.load("enemy_fly.png").convert_alpha()
enemy_fly_scaled = pygame.transform.scale(enemy_fly_image, (75,75))
enemy_fly_rect = enemy_fly_scaled.get_rect(center=(100, screen_y-50))
enemy_fly_flipped = pygame.transform.flip(enemy_fly_scaled, True, False)
enemy_fly_mask = pygame.mask.from_surface(enemy_fly_scaled)

enemy_ground_image = pygame.image.load("enemy_ground.png").convert_alpha()
enemy_ground_scaled = pygame.transform.scale(enemy_ground_image, (50,50))
enemy_ground_rect = enemy_ground_scaled.get_rect(center=(100, screen_y-50))
enemy_ground_flipped = pygame.transform.flip(enemy_ground_scaled, True, False)
enemy_ground_mask = pygame.mask.from_surface(enemy_ground_scaled)

player_image = pygame.image.load("player.png").convert_alpha()
player_scaled = pygame.transform.scale(player_image, (50, 50))
player_rect = player_scaled.get_rect(center=(100, screen_y-50))
player_fliped = pygame.transform.flip(player_scaled, True, False)
player_mask = pygame.mask.from_surface(player_scaled)
player_centerx = player_scaled.get_rect().centerx
player_centery = player_scaled.get_rect().centery

wall_image = pygame.image.load("wall.png").convert_alpha()
wall_scaled = pygame.transform.scale(wall_image, (50, 50))
wall_mask = pygame.mask.from_surface(wall_scaled)

projectile_image = pygame.image.load("projectile.png").convert_alpha()
projectile_scaled = pygame.transform.scale(projectile_image, (50, 50))
projectile_rect = projectile_scaled.get_rect(center=(100, screen_y-50))
projectile_flipped = pygame.transform.flip(projectile_scaled, True, False)
projectile_mask = pygame.mask.from_surface(projectile_scaled)

money_symbol_image = pygame.image.load("money_symbol.png").convert_alpha()
money_symbol_scaled = pygame.transform.scale(money_symbol_image, (40,40))

money_small_image = pygame.image.load("money.png").convert_alpha()
money_small_scaled = pygame.transform.scale(money_small_image, (30,30))
money_small_rect = projectile_scaled.get_rect(center=(100, screen_y-50))
money_small_mask = pygame.mask.from_surface(money_small_scaled)

money_big_image = pygame.image.load("money.png").convert_alpha()
money_big_scaled = pygame.transform.scale(money_big_image, (40,40))
money_big_rect = projectile_scaled.get_rect(center=(100, screen_y-50))
money_big_mask = pygame.mask.from_surface(money_big_scaled)

spikes_image = pygame.image.load("spikes.png").convert_alpha()
spikes_scaled = pygame.transform.scale(spikes_image, (40,40))
spikes_rect = projectile_scaled.get_rect(center=(100, screen_y-50))