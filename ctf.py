import pygame
import sys
from pygame.locals import *
import rungame
import maps
import gameobjects
import images

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Capture The Flag")


# Fonts and Colors
TITLE_FONT = pygame.font.SysFont("Times New Roman", 74)
BUTTON_FONT = pygame.font.SysFont("Times New Roman", 50)
selected_font3 = pygame.font.SysFont("Times New Roman", 30)
WHITE = (255, 255, 255)
BLUE = (0, 102, 204)
LIGHT_BLUE = (173, 216, 230)
scores = [0, 0, 0, 0, 0, 0]
coop_scores = [0, 0, 0]


def draw_text(text, font, color, surface, x, y):
    """
    Draws text with given attributes
    """
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))  # rectangle object
    surface.blit(text_obj, text_rect)


def button(text, back_collor, text_collor, y, x=None, font=BUTTON_FONT, width=250, height=50):
    """
    Creates a button with given attributes
    """
    x = SCREEN_WIDTH // 2 - width // 2 if not x else x
    button = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, back_collor, button)
    draw_text(text, font, text_collor, screen, button.centerx, button.centery)
    return button


def display_map(map, start_x, start_y, width, height):
    """
    Displays .json map as image at given position and given attributes
    """
    for x in range(0, map.width):
        for y in range(0, map.height):
            screen.blit(pygame.transform.scale(images.grass, (width // map.width, height // map.height)), (start_x + x * width // map.width, start_y + y * height // map.height))
            box_type = map.boxAt(x, y)
            box_img = None
            if box_type == 1:
                box_img = images.rockbox
            elif box_type == 2:
                box_img = images.woodbox
            elif box_type == 3:
                box_img = images.metalbox
            if box_img:
                screen.blit(pygame.transform.scale(box_img, (width // map.width, height // map.height)), (start_x + x * width // map.width, start_y + y * height // map.height))


def main_menu():
    """
    Creates the main menu window
    """
    global screen  # Use global screen reference

    # Initialize display only if needed
    if not pygame.get_init():
        pygame.init()

    # Set up display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Capture The Flag")

    while True:
        screen.fill(BLUE)

        # Title
        draw_text("CAPTURE THE FLAG", TITLE_FONT, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)

        # Button dimensions
        button_width, button_height = 250, 50

        scoreboard_button = button("Scoreboard", WHITE, BLUE, SCREEN_HEIGHT // 2 - 265)
        play_button = button("PLAY", WHITE, BLUE, SCREEN_HEIGHT // 2 - 100)
        setings_button = button("SETTINGS", WHITE, BLUE, SCREEN_HEIGHT // 2)
        exit_button = button("EXIT", WHITE, BLUE, SCREEN_HEIGHT // 2 + 100)

        # Event Handling
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    # Don't quit display, just start game
                    rungame.main_loop()
                    # After game ends, ensure display is active
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                    pygame.display.flip()
                elif setings_button.collidepoint(event.pos):
                    show_settings()
                elif scoreboard_button.collidepoint(event.pos):
                    scoreboard()
                elif exit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
        pygame.display.flip()


def show_settings():
    """
    Creates settings window
    """
    while True:
        screen.fill(WHITE)

        playermode_button = button("Player Mode", WHITE, BLUE, SCREEN_HEIGHT // 2 - 200)
        wincondition_button = button("Win Condition", WHITE, BLUE, SCREEN_HEIGHT // 2 - 130)
        ai_button = button("Select AI", WHITE, BLUE, SCREEN_HEIGHT // 2 - 60)
        map_button = button("Select Map", WHITE, BLUE, SCREEN_HEIGHT // 2 + 10)
        back_button = button("Back", WHITE, BLUE, SCREEN_HEIGHT // 2 + 80)

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse click
                if back_button.collidepoint(event.pos):
                    return
                elif ai_button.collidepoint(event.pos):
                    show_settings_AI()
                elif map_button.collidepoint(event.pos):
                    show_settings_Map()
                elif wincondition_button.collidepoint(event.pos):
                    show_settings_WINCONDITION()
                elif playermode_button.collidepoint(event.pos):
                    show_settings_Playermode()
        pygame.display.flip()


def show_settings_AI():
    """
    Creates AI settings window
    """
    while True:
        screen.fill(WHITE)

        easy = button("Easy", WHITE, BLUE, SCREEN_HEIGHT // 2 - 60)
        hard = button("Hard", WHITE, BLUE, SCREEN_HEIGHT // 2 + 10)
        back_button = button("Back", WHITE, BLUE, SCREEN_HEIGHT // 2 + 80)

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse click
                if back_button.collidepoint(event.pos):
                    return
                elif easy.collidepoint(event.pos):
                    gameobjects.hard_ai = False
                    print("easy")
                    return
                elif hard.collidepoint(event.pos):
                    gameobjects.hard_ai = True
                    print("hard")
                    return
        pygame.display.flip()


def show_settings_Map():
    """
    Creates map settings window
    """
    while True:
        screen.fill(WHITE)

        draw_text("MAP SELECTION", TITLE_FONT, BLUE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 - 100)

        display_map(maps.map2, 80, 150, 144 / 9 * 10, 145 / 9 * 5)
        small_button = button("Small", WHITE, BLUE, SCREEN_HEIGHT // 2 - 50, 40)

        display_map(maps.map0, 330, 150, 144, 144)
        medium_button = button("Medium", WHITE, BLUE, SCREEN_HEIGHT // 2, 280)

        display_map(maps.map1, 530, 150, 144 / 9 * 15, 144 / 9 * 11)
        large_button = button("Large", WHITE, BLUE, SCREEN_HEIGHT // 2 + 30, 510)

        display_map(maps.custom_map, 80, 340, 144, 144)
        custommap_button = button("Custom map", WHITE, BLUE, SCREEN_HEIGHT // 2 + 190, 40)

        back_button = button("Back", WHITE, BLUE, SCREEN_HEIGHT // 2 + 190, 500)

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse click
                if back_button.collidepoint(event.pos):
                    return
                elif medium_button.collidepoint(event.pos):
                    rungame.current_map = maps.map0
                    print("Map0")
                    return
                elif large_button.collidepoint(event.pos):
                    rungame.current_map = maps.map1
                    print("Map1")
                    return
                elif small_button.collidepoint(event.pos):
                    rungame.current_map = maps.map2
                    print("MAP2")
                    return
                elif custommap_button.collidepoint(event.pos):
                    rungame.current_map = maps.custom_map
                    print("Custom Map")
        pygame.display.flip()


def show_settings_WINCONDITION():
    """
    Creates winconditions window
    """
    while True:
        screen.fill(WHITE)

        # Button dimensions
        button_x = SCREEN_WIDTH // 2 - 250 // 2

        best_of_5 = button("Best of 5", WHITE, BLUE, SCREEN_HEIGHT // 2 - 60, button_x - SCREEN_WIDTH // 4)
        time_limit = button("Time limit", WHITE, BLUE, SCREEN_HEIGHT // 2 - 60, button_x + SCREEN_WIDTH // 4)
        rounds_fired = button("Rounds fired", WHITE, BLUE, SCREEN_HEIGHT // 2 + 10, button_x - SCREEN_WIDTH // 4)
        freeplay = button("Freeplay", WHITE, BLUE, SCREEN_HEIGHT // 2 + 10, button_x + SCREEN_WIDTH // 4)
        back_button = button("Back", WHITE, BLUE, SCREEN_HEIGHT // 2 + 80)

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse click
                if back_button.collidepoint(event.pos):
                    return
                elif best_of_5.collidepoint(event.pos):
                    rungame.win_condition = "best_of_5"
                    return
                elif time_limit.collidepoint(event.pos):
                    rungame.win_condition = "time_limit"
                    return
                elif rounds_fired.collidepoint(event.pos):
                    rungame.win_condition = "rounds_fired"
                    return
                elif freeplay.collidepoint(event.pos):
                    rungame.win_condition = "freeplay"
                    return
        pygame.display.flip()


def show_settings_Playermode():
    """
    Creates playermode settings window
    """
    while True:
        screen.fill(WHITE)

        singleplayer_button = button("Single Player", WHITE, BLUE, SCREEN_HEIGHT // 2 - 200)
        hotseat_button = button("Hotseat Two Player", WHITE, BLUE, SCREEN_HEIGHT // 2 - 130)
        coop_button = button("Co-Op", WHITE, BLUE, SCREEN_HEIGHT // 2 - 60)
        notcoop_button = button("Not Co-Op", WHITE, BLUE, SCREEN_HEIGHT // 2 + 10)
        back_button = button("Back", WHITE, BLUE, SCREEN_HEIGHT // 2 + 80)

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse click
                if back_button.collidepoint(event.pos):
                    return
                elif singleplayer_button.collidepoint(event.pos):
                    rungame.hotspot_multiplayer = False
                    print("Single Player")
                elif hotseat_button.collidepoint(event.pos):
                    rungame.hotspot_multiplayer = True
                    rungame.all_ai = False
                    print("Hotseat Two Player")
                elif coop_button.collidepoint(event.pos):
                    rungame.coop = True
                    print("Co-Op")
                elif notcoop_button.collidepoint(event.pos):
                    rungame.coop = False
                    print("Not Co-Op")
        pygame.display.flip()


def scoreboard():
    """
    Creates scoreboard window
    """
    while True:
        screen.fill(WHITE)

        back_button = button("Back", WHITE, BLUE, SCREEN_HEIGHT // 2 + 80)

        # Scoreboard
        draw_text("SCOREBOARD", TITLE_FONT, BLUE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 - 100)
        if rungame.coop:
            for score in range(len(coop_scores)):
                draw_text("Team " + str(score + 1) + " has won " + str(coop_scores[score]) + " times", selected_font3, BLUE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 - 50 + 50 * score)
        else:
            for score in range(6):
                draw_text("Player " + str(score + 1) + " has won " + str(scores[score]) + " times", selected_font3, BLUE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 - 50 + 50 * score)

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse click
                if back_button.collidepoint(event.pos):
                    return
        pygame.display.flip()


if __name__ == '__main__':
    main_menu()
