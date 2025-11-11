import game_framework
from pico2d import *

def init():
    global image
    global running
    global logo_start_time

    image = load_image('Keroro_logo.png')
    running = True
    logo_start_time = get_time()

def finish():
    global load_image
    del image

def update():
    global logo_start_time
    if get_time() - logo_start_time >= 2.0:
        logo_start_time = get_time()
        game_framework.change_mode(title_mode)

