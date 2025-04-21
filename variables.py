import json, pygame, math, os, time
from images import *
from classes import *
from pytmx.util_pygame import load_pygame
from spritesheet import Spritesheet

player_x, player_y = player_rect.centerx, player_rect.centery
player_vel = 5
jump_amount = 2
can_jump = jump_amount
gravity = 0.5
jump_strength = -12
velocity_y = 0
ground_y = screen_y - 75
player_face = 1
enemy_ground_face = 1
enemy_fly_speed = 2
enemy_ground_speed = 2
levelnum = 1
shoot_attack_cooldown_time = 1000
shoot_last_attack_time = 0
enemy_ground_json = 'enemy_ground.json'
walls_json = 'walls.json'
enemy_fly_json = 'enemy_fly.json'
path_points_json = 'path_points.json'
spike_json = 'spike.json'
tmx_data = load_pygame('Tilesets/OakWoods.tmx')
owl_spritesheet = Spritesheet('OwlFly-Sheet.png')

