#  FIX: When press esc to exit the game mid game, the game will not reset and dublicate the gameobjects
"""
Main ile for the game.
"""
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import time
import math

#  ----- Initialisation ----- #

#  Initialise the display
pygame.init()
pygame.display.set_mode()

#  Initialise the clock
clock = pygame.time.Clock()

#  Initialise the physics engine
space = pymunk.Space()
space.gravity = (0.0, 0.0)
space.damping = 0.1  # Adds friction to the ground for all objects

#  State vaiables
hotspot_multiplayer = False
all_ai = False
coop = False

#  Import from the ctf framework
#  The framework needs to be imported after initialisation of pygame
import ai
import images
import gameobjects
import maps
import sounds
import ctf

#  Constants
FRAMERATE = 50


#  Variables
#  Define the current level
current_map = maps.map0
win_condition = 2  # 1 = most score, 2 = time limit, 3 = rounds fired, 4 = freeplay

#  List of all game objects
game_objects_list = []
tanks_list = []
bullets_list = []
ai_list = []
explosion_list = []
flag = None
screen = None
background = None
ticks = 0

#  ----- Map Generator -----#


def generate_map():
    """
    Generates the map and all game objects
    """
    #  Resize the screen to the size of the current level
    global screen
    screen = pygame.display.set_mode(current_map.rect().size)
    #  Generate the background
    global background
    background = pygame.Surface(screen.get_size())
    spawn_border(space)
    spawn_floor()
    spawn_boxes()
    spawn_tanks()
    spawn_flag()


def spawn_border(space):
    """
    Spawns a border around the map
    """
    static_body = space.static_body
    thickness = 0
    static_lines = [
        pymunk.Segment(space.static_body, (0, 0), (current_map.width, 0), thickness),  # Top border
        pymunk.Segment(space.static_body, (0, 0), (0, current_map.height), thickness),  # Left border
        pymunk.Segment(space.static_body, (0, current_map.height), (current_map.width, current_map.height), thickness),  # Bottom border
        pymunk.Segment(space.static_body, (current_map.width, 0), (current_map.width, current_map.height), thickness)  # Right border
    ]
    for line in static_lines:
        line.elasticity = 1
        line.friction = 0.5
        line.collision_type = 4
        space.add(line)


def spawn_floor():
    """
    Spawns the floor
    """
    #  Copy the grass tile all over the level area
    for width in range(0, current_map.width):
        for height in range(0, current_map.height):
            # The call to the function "blit" will copy the image
            # contained in "images.grass" into the "background"
            # image at the coordinates given as the second argument
            background.blit(images.grass, (width * images.TILE_SIZE, height * images.TILE_SIZE))


def spawn_boxes():
    """
    Spawns boxes
    """
    #  Create the boxes
    for width in range(0, current_map.width):
        for height in range(0, current_map.height):
            # Get the type of boxes
            box_type = current_map.boxAt(width, height)
            # If the box type is not 0 (aka grass tile), create a box
            if (box_type != 0):
                # Create a "Box" using the box_type, aswell as the x,y coordinates,
                # and the pymunk space
                box = gameobjects.get_box_with_type(width, height, box_type, space)
                game_objects_list.append(box)


def spawn_tanks():
    """
    Spanws tanks and assignes teams and AI
    """
    #  Create the tanks
    #  Loop over the starting poistion
    TEAMS = ["Team one", "Team two", "Team three"]
    if all_ai:
        ai_contoll = [True, True, True, True, True, True]
    elif hotspot_multiplayer:
        ai_contoll = [False, False, True, True, True, True]
    else:  # singleplayer
        ai_contoll = [False, True, True, True, True, True]
    for tank_index in range(0, len(current_map.start_positions)):
        # Get the starting position of the tank "i"
        pos = current_map.start_positions[tank_index]
        # Create the tank, images.tanks contains the image representing the tank
        tank = gameobjects.Tank(pos[0], pos[1], pos[2], images.tanks[tank_index], space)
        # Add the tank to the list of tanks
        tanks_list.append(tank)
        #  Add bases
        base = gameobjects.GameVisibleObject(pos[0], pos[1], images.bases[tank_index])
        game_objects_list.append(base)
        #  Add ai to tanks
        my_ai = ai.Ai(tank, game_objects_list, tanks_list, bullets_list, space, current_map, FRAMERATE, coop, ai_contoll[tank_index])
        ai_list.append(my_ai)
        if coop:
            tanks_list[tank_index].team = TEAMS[tank_index // 2]


def spawn_flag():
    """
    Spawns the flag
    """
    # Create the flag
    global flag
    flag = gameobjects.Flag(current_map.flag_position[0], current_map.flag_position[1])
    game_objects_list.append(flag)

# ----- Collision Logic -----#


def Collision_bullets_tanks(arbiter, space, data):
    """
    Collision handler for bullets with tanks
    """
    sounds.play_sound(sounds.small_explosion_sound, 0.7)
    tank, bullet = arbiter.shapes[0].parent, arbiter.shapes[1].parent
    remove_bullet(bullet)
    if tank.spawn_protection is False:
        if tank.hp > 1:
            tank.hp -= 1
        else:
            reset_tank(tank)
        return False
    return False


def Collision_bullets_boxes(arbiter, space, data):
    """
    Collision handler for bullets with boxes
    """
    sounds.play_sound(sounds.small_explosion_sound, 0.7)
    box, bullet = arbiter.shapes[0].parent, arbiter.shapes[1].parent
    remove_bullet(bullet)
    if box.destructable:
        remove_box(box)
    return False  # This changes if boxes moves after hit


def Collision_bullets_walls(arbiter, space, data):
    """
    Collision handler for bullets with wall
    """
    sounds.play_sound(sounds.small_explosion_sound, 0.7)
    bullet = arbiter.shapes[0].parent
    remove_bullet(bullet)
    return True


def reset_tank(tank):
    """
    Reset the tank to its starting position and rotation
    """
    sounds.play_sound(sounds.tank_destroyed_sound)
    if tank.flag:
        drop_flag(tank)
    tank.body.position = tank.start_position
    tank.body.angle = tank.start_orientation
    tank.hp = 5
    tank.stoped = True
    tank.spawn_protection = True
    tank.spawn_protection_timer = 0


def drop_flag(tank):
    """
    Drop the flag from the tank
    """
    sounds.play_sound(sounds.flag_dropped_sound)
    flag.is_on_tank = False
    tank.flag = None


def remove_bullet(bullet):
    """
    Remove the bullet from the game
    """
    if bullet in bullets_list:
        explosion_list.append(gameobjects.Explosion(bullet.shape.body.position.x, bullet.shape.body.position.y))
        space.remove(bullet.shape, bullet.shape.body)
        bullets_list.remove(bullet)


def remove_box(box):
    """
    Remove the box from the game
    """
    if box in game_objects_list:
        sounds.play_sound(sounds.box_destroyed_sound)
        space.remove(box.shape, box.shape.body)
        game_objects_list.remove(box)


# add collision_handeler box and bullet
collision_handeler = space.add_collision_handler(1, 2)
collision_handeler.pre_solve = Collision_bullets_boxes

# add collision_handeler tank and bullet
collision_handeler = space.add_collision_handler(3, 2)
collision_handeler.pre_solve = Collision_bullets_tanks

# add collision_handeler bullet and border
collision_handeler = space.add_collision_handler(2, 4)
collision_handeler.pre_solve = Collision_bullets_walls


def update_scores(winner_index):
    """
    Update the scores and return to the ctf
    """
    #  Update scores and string representations
    if coop:
        ctf.coop_scores[math.ceil(winner_index / 2)] += 1
    else:
        ctf.scores[winner_index] += 1

#  ----- Main Loop -----#


def main_loop():
    """
    Main loop of the game
    """
    global screen, background

    #  Clear any existing pygame display
    pygame.display.quit()
    pygame.display.init()

    #  Initialize game display with correct dimensions
    map_width = current_map.width * images.TILE_SIZE
    map_height = current_map.height * images.TILE_SIZE
    screen = pygame.display.set_mode((map_width, map_height))
    background = pygame.Surface((map_width, map_height))

    generate_map()
    sounds.play_sound(sounds.idle_engine_sound, 1)
    #  Control whether the game run
    running = True
    skip_update = 0

    while running:
        #  Handle the events
        for event in pygame.event.get():
            #  Check if we receive a QUIT event (for instance, if the user press the
            #  close button of the wiendow) or if the user press the escape key.
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                sounds.stop_sound(sounds.idle_engine_sound)
                running = False

            if (event.type == KEYDOWN):
                if event.key == K_UP:
                    tanks_list[0].accelerate()
                elif (event.key == K_DOWN):
                    tanks_list[0].decelerate()
                elif (event.key == K_LEFT):
                    tanks_list[0].turn_left()
                elif (event.key == K_RIGHT):
                    tanks_list[0].turn_right()
                elif (event.key == K_RSHIFT):
                    tanks_list[0].shoot(bullets_list, space, FRAMERATE)

            if (event.type == KEYUP):
                if event.key == K_UP:
                    tanks_list[0].stop_moving()
                elif (event.key == K_DOWN):
                    tanks_list[0].stop_moving()
                elif (event.key == K_LEFT):
                    tanks_list[0].stop_turning()
                elif (event.key == K_RIGHT):
                    tanks_list[0].stop_turning()

            if hotspot_multiplayer is True:
                if (event.type == KEYDOWN):
                    if event.key == K_w:
                        tanks_list[1].accelerate()
                    elif (event.key == K_s):
                        tanks_list[1].decelerate()
                    elif (event.key == K_a):
                        tanks_list[1].turn_left()
                    elif (event.key == K_d):
                        tanks_list[1].turn_right()
                    elif (event.key == K_SPACE):
                        tanks_list[1].shoot(bullets_list, space, FRAMERATE)

                if (event.type == KEYUP):
                    if event.key == K_w:
                        tanks_list[1].stop_moving()
                    elif (event.key == K_s):
                        tanks_list[1].stop_moving()
                    elif (event.key == K_a):
                        tanks_list[1].stop_turning()
                    elif (event.key == K_d):
                        tanks_list[1].stop_turning()

        #  Update physics
        if skip_update == 0:
            #  Loop over all the game objects and update their speed in function of their acceleration.
            for tank_index in range(0, len(tanks_list)):
                if tanks_list[tank_index].has_won():
                    sounds.play_sound(sounds.win_sound, 1)
                    sounds.stop_sound(sounds.idle_engine_sound)
                    update_scores(tank_index)
                    running = False
            if wincondition(win_condition):
                running = False

            for obj in game_objects_list:
                obj.update()
            for tank in tanks_list:
                tank.update(FRAMERATE)
            for bullet in bullets_list:
                bullet.update()
            for ai in ai_list:
                ai.decide()
            for explosion in explosion_list:
                if explosion.update():
                    explosion_list.remove(explosion)
            global ticks
            ticks += 1

            skip_update = 2
        else:
            skip_update -= 1

        #    Check collisions and update the objects position
        space.step(1 / FRAMERATE)

        #    Update object that depends on an other object position (for instance a flag)
        for obj in game_objects_list:
            obj.post_update()
        for tank in tanks_list:
            tank.try_grab_flag(flag)
            tank.post_update()

        #  Uppdate bakground
        screen.blit(background, (0, 0))

        #  Update the display of the game objects on the screen
        for obj in game_objects_list:
            obj.update_screen(screen)

        for tank in tanks_list:
            if tank.spawn_protection:
                tank.sprite.set_alpha(128)
            else:
                tank.sprite.set_alpha(255)
            tank.update_screen(screen)

        for bullet in bullets_list:
            bullet.update_screen(screen)

        for explosion in explosion_list:
            explosion.update_screen(screen)

        flag.update_screen(screen)

        #    Redisplay the entire screen (see double buffer technique)
        pygame.display.flip()

        #    Control the game framerate
        clock.tick(FRAMERATE)
    if wincondition(win_condition):
        reset_game_state()
    resetgame()
    ctf.main_menu()


def display_win_screen(message):
    """
    Displays win screen
    """
    #  Create a win screen surface
    win_surface = pygame.Surface(screen.get_size())
    win_surface.fill((0, 0, 0))

    #  Display win message

    font = pygame.font.Font(None, 25)
    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2))
    win_surface.blit(text, text_rect)

    #  Display win screen
    screen.blit(win_surface, (0, 0))
    pygame.display.flip()
    pygame.time.wait(3000)  # Show win screen for 3 seconds
    reset_game_state()


def reset_game_state():
    """
    Reset all game state variables and return to ctf
    """
    global space, game_objects_list, tanks_list, bullets_list, ai_list, flag, screen, background, ticks

    print("Resetting game state...")  # Debug

    ctf.scores = [0] * 6
    ctf.coop_scores = [0] * 3
    total_rounds_fired = 0
    ticks = 0

    #  Reset display
    map_width = current_map.width * images.TILE_SIZE
    map_height = current_map.height * images.TILE_SIZE
    screen = pygame.display.set_mode((map_width, map_height))
    background = pygame.Surface((map_width, map_height))

    resetgame()

    print("Reset complete")  # Debug

    ctf.main_menu()


def resetgame():
    """
    Resets the game
    """
    global space, game_objects_list, tanks_list, bullets_list, ai_list, flag, screen, background

    #  Clear game state and physics
    game_objects_list.clear()
    tanks_list.clear()
    bullets_list.clear()
    ai_list.clear()
    flag = None

    for shape in space.shapes[:]:
        space.remove(shape)
    for body in space.bodies[:]:
        space.remove(body)

    #  Force ctf display update
    screen = pygame.display.set_mode((ctf.SCREEN_WIDTH, ctf.SCREEN_HEIGHT))
    pygame.display.flip()


def wincondition(condition):
    """
    Checks if win condition is reached and updates scoreborad and resets the game
    """

    if coop:
        scores = ctf.coop_scores
        who = "Team"
    else:
        scores = ctf.scores
        who = "Player"

    if condition == "best_of_5":   # Best of five
        tot_score = 0
        for score in scores:
            tot_score += score
        if tot_score >= 5:
            #  Find highest score and who has it
            max_score = max(scores)
            winners = [index + 1 for index, score in enumerate(scores) if score == max_score]
            #  Determine winner text
            if len(winners) == 1:
                winner = f'{who}, {winners[0]}'
                display_win_screen(f"{winner} wins best of five!")
            else:
                winner = 'Tie between ' + who + ', '.join(str(w) for w in winners)
                display_win_screen(f"{winner}")
            return True

    elif condition == "time_limit":   # Time limit
        if ticks >= 2500:
            print('Time limit reached')
            #  Find highest score and who has it
            max_score = max(scores)
            winners = [index + 1 for index, score in enumerate(scores) if score == max_score]
            #  Determine winner text
            if len(winners) == 1:
                winner = f'{who}, {winners[0]}'
                display_win_screen(f"{winner} wins by time limit!")
            else:
                winner = 'Tie between ' + who + ', '.join(str(w) for w in winners)
                display_win_screen(f"{winner}")
            return True

    elif condition == "rounds_fired":   # Rounds fired
        if gameobjects.total_rounds_fired >= 250:
            print('Round limit reached')
            #  Find highest score and who has it
            max_score = max(scores)
            winners = [index + 1 for index, score in enumerate(scores) if score == max_score]
            # Determine winner text
            if len(winners) == 1:
                winner = f'{winners[0]}'
                display_win_screen(f"{winner} wins, game ended by rounds fired!")
            else:
                winner = 'Tie between ' + ', '.join(str(w) for w in winners)
                display_win_screen(f"{winner}, game ended by rounds fired!")
            return True

    elif condition == "freeplay":   # Freeplay
        pass
    return False


if __name__ == "__main__":
    main_loop()
