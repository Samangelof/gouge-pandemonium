import math
import arcade
from player_conf import (
    PlayerCharacter, 
    EnemyCharacter,
    ZombieCharacter)


SPRITE_SCALING_PLAYER = .3
SPRITE_SCALING_LASER = 0.8
SPRITE_SCALING_ENEMY_MAIN = .3
SPRITE_SCALING_BULLET = .5

SPRITE_SCALING_BLOOD = .8


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Gouge pandemonium"

# СКОРОСТЬ ДВИЖЕНИЯ
MOVEMENT_SPEED = 3

# СКОРОСТЬ ПОВОРОТА
ANGLE_SPEED = 4

BOX_SIZE = .4

#СКОРОСТЬ ПУЛИ
BULLET_SPEED = 10

DEAD = False



class GougeGame(arcade.Window):
    """ GAME CLASS """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self._correct = True
        self.score = 0
        self.score_text = None

        self.mouse_pos = 0, 0
        
        # Переменные, в которых будут храниться списки спрайтов
        self.bullet_player_list = None
        self.bullet_enemy_list = None

        self.enemy_list = None
        self.zombie_list = None

        self.wall_list = None
        self.player_list = None

        self.player_sprite = None
        self.physics_engine = None

        self.frame_count = 0

        arcade.set_background_color(arcade.color.AMAZON)

    



    def setup(self):
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.bullet_player_list = arcade.SpriteList()
        self.bullet_enemy_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.death_list = arcade.SpriteList()
        self.zombie_list = arcade.SpriteList()



        # ПОЛОЖЕНИЕ ИГРОКА
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = SCREEN_HEIGHT / 2
        self.player_list.append(self.player_sprite)
        self.score = 0

        # ОБЪЕКТ СМЕРТИ
        self.death = arcade.Sprite('image/blood.png', SPRITE_SCALING_BLOOD)

        # ПОЛОЖЕНИЕ ВРАГА
        self.enemy_sprite = EnemyCharacter('image/roll20.png', SPRITE_SCALING_ENEMY_MAIN)
        self.enemy_sprite.center_x = 50
        self.enemy_sprite.center_y = 70
        self.enemy_list.append(self.enemy_sprite)


        # ПОЛОЖЕНИЕ ДОМА
        self.house_sprite = arcade.Sprite('image/house.png', scale=.4)
        self.house_sprite.center_x = 820
        self.house_sprite.center_y = 400
        self.wall_list.append(self.house_sprite)


        # ПОЛОЖЕНИЕ ЗОМБИ
        self.zombie_sprite = None
        for y in range(273, 550, 64):
            self.zombie_sprite = ZombieCharacter("image/zombie.png", scale=0.3)
            self.zombie_sprite.center_x = 50
            self.zombie_sprite.center_y = y
            self.zombie_list.append(self.zombie_sprite)


        # -- SETUP WALLS
        # CREATE ROW BOXES
        for x in range(173, 650, 64):
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png",
                                BOX_SIZE)
            wall.center_x = x
            wall.center_y = 200
            self.wall_list.append(wall)

        # CREATE COLUMN BOXES
        for y in range(273, 500, 64):
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png",
                                 BOX_SIZE)
            wall.center_x = 465
            wall.center_y = y
            self.wall_list.append(wall)

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite,
                                                         self.wall_list)



    def on_draw(self):
        """ ОТРИСОВКА """
        self.clear()
        self.bullet_player_list.draw()
        self.bullet_enemy_list.draw()
        self.player_list.draw()
        self.wall_list.draw()
        self.enemy_list.draw()
        self.zombie_list.draw()

        self.death_list.draw()


        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)


    def aim_player(self, delta_time):
        mouse_angle = arcade.get_angle_degrees(
            self.player_sprite.center_y, self.player_sprite.center_x,
            self.mouse_pos[1], self.mouse_pos[0]
        )
        mouse_angle += 90
        if self.correct:
            angle_change = mouse_angle - self.player_sprite.angle
            self.player_sprite.rotate_around_point(self.player_sprite.position, angle_change)
        else:
            self.player_sprite.angle = mouse_angle
    


    def on_update(self, delta_time: float):
        self.player_list.update()
        self.player_list.update_animation()
        self.physics_engine.update()
        self.bullet_player_list.update()
        self.bullet_enemy_list.update()
        self.zombie_list.update()

        
        # Наводка прицела с помощью мыши
        self.aim_player(delta_time)
        
        # ПРОТИВНИК СТРЕЛЯЕТ В ИГРОКА
        self.frame_count += 1

        # Зомби преследуют игрока
        for zomb in self.zombie_list:
            zomb.follow_zombie(self.player_sprite)


        # Loop through each enemy that we have
        for enemy in self.enemy_list:

            # First, calculate the angle to the player. We could do this
            # only when the bullet fires, but in this case we will rotate
            # the enemy to face the player each frame, so we'll do this
            # each frame.

            # Position the start at the enemy's current location
            start_x = enemy.center_x
            start_y = enemy.center_y

            # Get the destination location for the bullet
            dest_x = self.player_sprite.center_x
            dest_y = self.player_sprite.center_y

            # Do math to calculate how to get the bullet to the destination.
            # Calculation the angle in radians between the start points
            # and end points. This is the angle the bullet will travel.
            x_diff = dest_x - start_x
            y_diff = dest_y - start_y
            angle = math.atan2(y_diff, x_diff)

            # Set the enemy to face the player.
            enemy.angle = math.degrees(angle) - 90

            # Shoot every 60 frames change of shooting each frame
            if self.frame_count % 60 == 0:
                bullet_enemy = arcade.Sprite(":resources:images/space_shooter/laserRed01.png")
                bullet_enemy.center_x = start_x
                bullet_enemy.center_y = start_y

                # Angle the bullet sprite
                bullet_enemy.angle = math.degrees(angle)

                # Taking into account the angle, calculate our change_x
                # and change_y. Velocity is how fast the bullet travels.
                bullet_enemy.change_x = math.cos(angle) * BULLET_SPEED
                bullet_enemy.change_y = math.sin(angle) * BULLET_SPEED

                self.bullet_enemy_list.append(bullet_enemy)


        for bullet in self.bullet_player_list:
            # Проверем пулю попала ли она в барьер
            hit_wall = arcade.check_for_collision_with_list(bullet, self.wall_list)
            # Проверем пулю попали ли она во врага
            hit_player = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            # Проверем пулю попали ли она в зомби
            hit_zombi = arcade.check_for_collision_with_list(bullet, self.zombie_list)
            
            # Если пуля вылетает за пределы экрана, убераем ее
            if bullet.bottom > self.width or bullet.top < 0 or bullet.right < 0 or bullet.left > self.width:
                bullet.remove_from_sprite_lists()
            # Если пуля попала в барьер, убераем ее
            elif len(hit_wall) > 0:
                bullet.remove_from_sprite_lists()

            # За каждого попадаемого врага прибавляем к счету и убираем врага
            for enemy in hit_player:
                enemy.remove_from_sprite_lists()
                self.death.center_y = self.enemy_sprite.center_y
                self.death.center_x = self.enemy_sprite.center_x
                self.death_list.append(self.death)
                self.score += 1

            #ДОБАВЛЯЕМ ЗОМБИ ПОСЛЕ УБИЙСТВА ((ГЛАВНОГО ПРОТИВНИКА))
            # for enemy in hit_zombi:
            #     self.death.center_y = self.zombie_sprite.center_y
            #     self.death.center_x = self.zombie_sprite.center_x
            #     self.death_list.append(self.death)
            #     self.score += 1

        """ УБИЙСТВО ИГРОКА (СОЮЗНИКОВ)"""
        for bullet in self.bullet_enemy_list:
            hit_wall = arcade.check_for_collision_with_list(bullet, self.wall_list)
            hit_enemy = arcade.check_for_collision_with_list(bullet, self.player_list)

            if bullet.bottom > self.width or bullet.top < 0 or bullet.right < 0 or bullet.left > self.width:
                bullet.remove_from_sprite_lists()
            elif len(hit_wall) > 0:
                bullet.remove_from_sprite_lists()

            # БАГ, ПРИ СМЕРТИ ИГРОКА ОН ИСЧЕЗАЕТ, ДВИГАТЬСЯ И СТРЕЛЯТЬ ВСЕ ЕЩЕ ВОЗМОЖНО
            for enemy in hit_enemy:
                enemy.remove_from_sprite_lists()
                # Удалить игрока убитым врагом
                hit_enemy.remove(self.player_sprite)
                # Закрываем игру, когда в игрока убили
                arcade.exit()

                self.death.center_y = self.player_sprite.center_y
                self.death.center_x = self.player_sprite.center_x
                self.death_list.append(self.death)

                #? Сделать отдельный спрайт смерти для игрока
                    # self.death.center_y = self.player_sprite.center_y
                    # self.death.center_x = self.player_sprite.center_x
                    # self.death_list.append(self.death)

                # Всли враг попал в игрока, завершить игру 
                #* СДЕЛАТЬ ЧЕРЕЗ ХП, ЕСЛИ ХП МеньшеРавно НУЛЯ ТО ГГ
                    # time.sleep(.5)
                    # arcade.exit()


    # СОЗДАТЬ ФУНКЦИЮ РАЗМЕЩЕНИЯ ВРАГОВ

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
            self.mouse_pos = x, y
            # print(f"Mouse pos: {x}, {y}")

    @property
    def correct(self):
            return self._correct
        



# --
# ..
    def on_mouse_press(self, x, y, button, modifiers):
        """ Called whenever the mouse button is clicked """

        # Создать пулю
        bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", SPRITE_SCALING_BULLET)

        # Расположить пулю в текущем местоположении игрока
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y
        bullet.center_x = start_x
        bullet.center_y = start_y

        # Получить от мыши место назначения для пули
        dest_x = x
        dest_y = y

        # Посчитать, как доставить пулю до места назначения
        # Расчет угла в радианах между начальными точками
        # и конечные точки. Это угол, под которым полетит пуля
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        # Наклонить спрайт пули так, чтобы не было похоже, что она летит боком
        bullet.angle = math.degrees(angle)
        # print(f"Bullet angle: {bullet.angle:.2f}")

        # С учетом угла рассчитать изменение Х и изменить У 
        bullet.change_x = math.cos(angle) * BULLET_SPEED
        bullet.change_y = math.sin(angle) * BULLET_SPEED

        # Добавляем пулю в соответствующий список
        self.bullet_player_list.append(bullet)


    def on_key_press(self, key, modifiers):
        """
        Called whenever a key is pressed.
        """
        if key == arcade.key.UP:
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """
        Called when the user releases a key.
        """
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

def main():
    """ Main function """
    window = GougeGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()