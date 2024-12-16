import os
import pygame

main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_sound(file):
    """ Load a sound from the sounds directory. """
    file = os.path.join(main_dir, 'data', 'audio', file)
    try:
        sound = pygame.mixer.Sound(file)
    except pygame.error:
        raise SystemExit('Could not load sound "%s" %s' % (file, pygame.get_error()))
    return sound


small_explosion_sound = load_sound('small_explosion.wav')  # Pskott som träffar plåt

bullet_sound = load_sound('bullet.wav')  # pansarskott från S122

tank_destroyed_sound = load_sound('tank_destroyed.wav')  # jävla smäll

box_destroyed_sound = load_sound('box_destroyed.wav')  # kaplastavar

flag_captured_sound = load_sound('flag_captured.wav')  # Halo3 ljud

flag_dropped_sound = load_sound('flag_dropped.wav')  # Halo3 ljud

movement_sound = load_sound('movement.wav')  # bv410 som kör agresivt

idle_engine_sound = load_sound('idle_engine.wav')  # bv410 som kör lungt

win_sound = load_sound('win.wav')  # Meme ljud


def play_sound(sound, volume=0.2):
    """ Play a sound. """
    sound.set_volume(volume)
    sound.play()


def stop_sound(sound):
    """ Stop a sound. """
    sound.stop()
