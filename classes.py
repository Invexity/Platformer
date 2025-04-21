import json, pygame, math, os, time
from pytmx.util_pygame import load_pygame

screen_x = 1920
screen_y = 1080

class Player(pygame.sprite.Sprite):
    def __init__(self, window, image, x, y, speed, velocity, jump_amount, wall_jump_amount, gravity, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.original_image = image
        self.window = window
        self.x = x
        self.start_x = x
        self.y = y
        self.start_y = y
        self.speed = speed
        self.vel_x = 0
        self.vel_y = velocity
        self.gravity = gravity
        self.direction = 1
        self.facing_right = True
        self.can_jump = False
        self.can_wall_jump = False
        self.health = health
        self.wall_jump_amount = wall_jump_amount
        self.jump_amount = jump_amount
        self.OGjump_amount = jump_amount
        self.max_health = health
        self.health_time = 0
        self.take_damage_cooldown = 60
        self.money = 0
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, window):
        window.blit(self.image, self.rect)

    def update(self, collision_group, enemy_group, money_small_group, money_big_group, spikes_group):
        self.health_time += 1

        # Apply gravity
        self.vel_y += self.gravity

        # Move horizontally
        self.rect.x += self.vel_x
        collided_platforms = pygame.sprite.spritecollide(self, collision_group, False)
        for platform in collided_platforms:
            if self.vel_x > 0:  # moving right
                self.rect.right = platform.rect.left
                self.vel_x = 0
                self.can_wall_jump = True
            elif self.vel_x < 0:  # moving left
                self.rect.left = platform.rect.right
                self.vel_x = 0
                self.can_wall_jump = True

        # Move vertically
        self.rect.y += self.vel_y
        collided_platforms = pygame.sprite.spritecollide(self, collision_group, False)
        for platform in collided_platforms:
            if self.vel_y > 0:  # falling
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                self.can_jump = True
                self.jump_amount = self.OGjump_amount
                self.wall_jump_amount = 1
                self.can_wall_jump = False
            elif self.vel_y < 0:  # jumping up
                self.rect.top = platform.rect.bottom
                self.vel_y = 0

        # Friction
        self.vel_x *= 0.8

        # Enemy collision
        collided_enemies = pygame.sprite.spritecollide(self, enemy_group, False)
        for enemy in collided_enemies:
            self.take_damage(25)

        # Money collision
        collided_money = pygame.sprite.spritecollide(self, money_small_group, True)
        for money in collided_money:
            self.money_add(10)

        collided_money = pygame.sprite.spritecollide(self, money_big_group, True)
        for money in collided_money:
            self.money_add(50)

        # Spike collision
        collided_spikes = pygame.sprite.spritecollide(self, spikes_group, False)
        for spikes in collided_spikes:
            self.take_damage(100)

    def move(self, direction, collision_group):
        # Move left (-1) or right (1)
        self.vel_x = direction * self.speed

        if direction == 1 and not self.facing_right:
            self.image = self.original_image
            self.facing_right = True
        elif direction == -1 and self.facing_right:
            self.image = pygame.transform.flip(self.original_image, True, False)
            self.facing_right = False

    def is_touching_wall(self, collision_group):
        self.rect.x -= 1
        collide_left = pygame.sprite.spritecollideany(self, collision_group)
        self.rect.x += 1

        self.rect.x += 1
        collide_right = pygame.sprite.spritecollideany(self, collision_group)
        self.rect.x -= 1

        return collide_left or collide_right

    def jump(self, collision_group):
        touching_wall = self.is_touching_wall(collision_group)

        if self.can_jump and self.jump_amount > 0:
            # Normal ground jump
            self.vel_y = -9
            self.jump_amount -= 1
            if self.jump_amount == 0:
                self.can_jump = False

        elif touching_wall:
            if self.wall_jump_amount > 0 and self.can_wall_jump == True:
                # Wall jump
                self.vel_y = -9  # same strong jump upward

                # Push away from wall
                self.rect.x -= 5 if self.facing_right else -5
                self.vel_x = -6 if self.facing_right else 6

                self.can_jump = False  # block normal jumps
                self.jump_amount = 0
                self.wall_jump_amount -= 1

            elif self.wall_jump_amount <= 0:
                self.can_wall_jump = False

    def take_damage(self, amount):
        if self.health_time >= self.take_damage_cooldown:
            self.health -= amount
            if self.health <= 0:
                self.die()
            self.health_time = 0

    def die(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.health = self.max_health

    def draw_health_bar(self, screen, camera):
        if self.health_time <= 120:
            bar_width = 50
            bar_height = 10
            x_pos = self.rect.x - camera.offset.x
            y_pos = self.rect.y - 25 - camera.offset.y

            health_percentage = self.health / self.max_health
            health_bar_width = bar_width * health_percentage

            pygame.draw.rect(screen, (0, 0, 0), (x_pos - 5, y_pos - 5, bar_width + 10, bar_height + 10))
            pygame.draw.rect(screen, (255, 0, 0), (x_pos, y_pos, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (x_pos, y_pos, health_bar_width, bar_height))

    def money_add(self, amount):
        self.money += amount

    def get_money_value(self):
        return self.money


class Enemy_fly(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, images, path):
        super().__init__()
        self.images = images
        self.current_sprite = 0
        self.image = self.images[self.current_sprite]
        self.original_image = self.image
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = speed
        self.path = path
        self.current_path = 0

        self.state = "idle"

    def set_state(self, new_state):
        self.state = new_state
        self.current_sprite = 0

    def update(self, anim_speed):
        if self.state == "idle":
            self.current_sprite += anim_speed
            if int(self.current_sprite) >= len(self.images):
                self.current_sprite = 0

            self.image = self.images[int(self.current_sprite)]

        # elif self.state == "attack":
        #     # Handle attack animation
        # elif self.state == "run":
        #     # Handle run animation


    def follow_player(self, playerclass, enemy_fly_speed, maxdistance):
        dx = playerclass.rect.x - self.rect.x
        dy = playerclass.rect.y - self.rect.y

        distanceplayer = math.sqrt(dx ** 2 + dy ** 2)
        if distanceplayer == 0:
            return
        if distanceplayer <= maxdistance:
            dx = playerclass.rect.x - self.rect.x
            dy = playerclass.rect.y - self.rect.y
            dx /= distanceplayer
            dy /= distanceplayer

            self.rect.x += dx * enemy_fly_speed
            self.rect.y += dy * enemy_fly_speed

            if dx >= 0:
                self.image = self.original_image
            else:
                self.image = pygame.transform.flip(self.original_image, True, False)
        if distanceplayer >= maxdistance:
            if len(self.path) == 0:
                return

            targetx1 = self.path[0][0]
            targety1 = self.path[0][1]
            targetx2 = self.path[0][2]
            targety2 = self.path[0][3]
            dx = targetx1 - self.rect.x
            dy = targety1 - self.rect.y
            distancepath = math.sqrt(dx ** 2 + dy ** 2)

            if self.current_path == 0:
                self.image = pygame.transform.flip(self.original_image, True, False)
                dx2 = targetx1 - self.rect.x
                dy2 = targety1 - self.rect.y

                distancepath = math.sqrt(dx2 ** 2 + dy2 ** 2)

                if distancepath != 0:
                    dx2 /= distancepath
                    dy2 /= distancepath

                self.rect.x += dx2 * enemy_fly_speed
                self.rect.y += dy2 * enemy_fly_speed

                if distancepath <= 5:
                    self.rect.x = targetx1
                    self.rect.y = targety1
                    self.current_path = 1

            elif self.current_path == 1:
                self.image = self.original_image
                dx2 = targetx2 - self.rect.x
                dy2 = targety2 - self.rect.y

                distancepath = math.sqrt(dx2 ** 2 + dy2 ** 2)

                if distancepath != 0:
                    dx2 /= distancepath
                    dy2 /= distancepath

                self.rect.x += dx2 * enemy_fly_speed
                self.rect.y += dy2 * enemy_fly_speed

                if distancepath <= 5:
                    self.rect.x = targetx2
                    self.rect.y = targety2
                    self.current_path = 0

class Enemy_ground(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.original_image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

        self.velocity_y = 0
        self.gravity = 0.5
        self.direction = -1  # 1 = right, -1 = left
        self.speed = 2

    def walk(self, collision_group):
        # -------- GRAVITY first --------
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # Check vertical collisions only
        collided_platforms = pygame.sprite.spritecollide(self, collision_group, False)
        for platform in collided_platforms:
            if self.velocity_y > 0:  # Falling down
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
            elif self.velocity_y < 0:  # Jumping up
                self.rect.top = platform.rect.bottom
                self.velocity_y = 0

        # -------- HORIZONTAL movement --------
        self.rect.x += self.direction * self.speed

        collided_platforms = pygame.sprite.spritecollide(self, collision_group, False)
        for platform in collided_platforms:
            if self.direction > 0:  # Moving right
                self.rect.right = platform.rect.left
                self.direction = -1
                self.image = pygame.transform.flip(self.original_image, True, False)  # Flip sprite
            elif self.direction < 0:  # Moving left
                self.rect.left = platform.rect.right
                self.direction = 1
                self.image = self.original_image  # Flip back

    def update(self, collision_group):
        self.walk(collision_group)


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.mask = pygame.mask.from_surface(self.image)

class Money_small(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.velocity_y = 0
        self.gravity = 1.5
        self.is_on_ground  = False

    def update(self, collision_group):
        self.velocity_y -= self.gravity
        self.rect.y -= self.velocity_y
        collided_platforms = pygame.sprite.spritecollide(self, collision_group, False)
        if collided_platforms:
            highest_platform = min(collided_platforms, key=lambda platform: platform.rect.top)
            self.rect.bottom = highest_platform.rect.top
            self.velocity_y = 0

class Money_big(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.velocity_y = 0
        self.gravity = 1.5
        self.is_on_ground = False

    def update(self, collision_group):
        self.velocity_y -= self.gravity
        self.rect.y -= self.velocity_y
        collided_platforms = pygame.sprite.spritecollide(self, collision_group, False)
        if collided_platforms:
            highest_platform = min(collided_platforms, key=lambda platform: platform.rect.top)
            self.rect.bottom = highest_platform.rect.top
            self.velocity_y = 0

class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))

class Checkpoint(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))

class Camera:
    def __init__(self, width, height):
        self.offset = pygame.Vector2(0, 0)
        self.width = width
        self.height = height
        self.level_width = 3000  # total width of your map/level

    def follow(self, target):
        # First, center the player
        self.offset.x = target.rect.centerx - screen_x // 2

        # Clamp the offset so it doesn't go outside the level
        self.offset.x = max(0, min(self.offset.x, self.level_width - screen_x))

    def apply(self, entity):
        return entity.rect.move(-self.offset.x, 0)

class Button():
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False

		pos = pygame.mouse.get_pos()

		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				action = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False


		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action