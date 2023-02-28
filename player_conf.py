# создать классы на разных врагов разная скорость и урон 
# Пример: 
    # Zombie1 speed 5 scratch 10
    # Zombie2 speed 12 scratch 18
    # Footman1 speed 14 rifle 24
    # Sniper1  speed 8 sniper rifle 48
# Создавать циклом слабых, более сильных - делать отдельные спрайты


import arcade
import random
import math
import os


# Отследить, куда смотрит игрок влево или вправо
RIGHT_FACING = 0
LEFT_FACING = 1

# Скорость движения зомби
ZOMBIE_SPEED = .2

# Скорость запуска анимации
UPDATES_PER_FRAME = 3

# Размер игрока, врага, зомби
SPRITE_SCALING_PLAYER = .3
SPRITE_SCALING_ENEMY = .3
SPRITE_SCALING_ZOMBIE = .3



def load_texture_pair(filename):
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]



# --
# ..
class PlayerCharacter(arcade.Sprite):
    def __init__(self):
        super().__init__()

        
        self.speed = 0

        self.character_face_direction = RIGHT_FACING
        self.cur_texture = 0
        self.scale = SPRITE_SCALING_PLAYER
        self.points = [[-22, -64], [22, -64], [22, 28], [-22, 28]]

        main_path = "image/Top_Down_Survivor/rifle/move/"
        self.idle_texture_pair = load_texture_pair(f"{main_path}survivor-move_rifle_0.png")

        self.walk_textures = []
        for i in range(20):
            texture = load_texture_pair(f"{main_path}survivor-move_rifle_{i}.png")
            self.walk_textures.append(texture)


    def update(self):
        angle_rad = math.radians(self.angle)
        self.angle += self.change_angle
        self.center_x += -self.speed * math.sin(angle_rad)
        self.center_y += self.speed * math.cos(angle_rad)


    def rotate_around_point(self, point: arcade.Point, degrees: float):
        self.angle += degrees
        self.position = arcade.rotate_point(
            self.center_x, self.center_y,
            point[0], point[1], degrees)
        
        
    def update_animation(self, delta_time: float = 1 / 60):
        # Проверить куда нужно повернуть лицо, налево или направо
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING



        # Анимация бездействия
        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return
        
        # Анимация ходьбы
        self.cur_texture += 1
        if self.cur_texture > 19 * UPDATES_PER_FRAME:
            self.cur_texture = 0
        frame = self.cur_texture // UPDATES_PER_FRAME
        direction = self.character_face_direction
        self.texture = self.walk_textures[frame][direction]




class EnemyCharacter(arcade.Sprite):
    def __init__(self, image, scale):
        super().__init__(image, scale)



class ZombieCharacter(arcade.Sprite):
    def follow_zombie(self, player_sprite):
        """
            Эта функция будет перемещать текущий спрайт в любую сторону
            другой спрайт указывается в качестве параметра
        """

        self.center_x += self.change_x
        self.center_y += self.change_y

        # Рандом 1 из 100, что мы изменим свое старое направление и
        # затем повторно нацелимся на игрока
        if random.randrange(100) == 0:
            start_x = self.center_x
            start_y = self.center_y

            # Получить место назначения для пути
            dest_x = player_sprite.center_x
            dest_y = player_sprite.center_y

            # Считаем, как доставить зомби до места назначения
            # Расчет угла в радианах между начальными точками и конечной точки
            # это угол, под которым пойдет зомби
            x_diff = dest_x - start_x
            y_diff = dest_y - start_y
            angle = math.atan2(y_diff, x_diff)

            # С учетом угла рассчитайте изменение оси Х и изменение оси У 

            self.change_x = math.cos(angle) * ZOMBIE_SPEED
            self.change_y = math.sin(angle) * ZOMBIE_SPEED