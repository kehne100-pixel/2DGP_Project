from pico2d import *
import game_framework
import play_mode

image = None
start_image = None
exit_image = None
controls_image = None


def init():
    global image,start_image,exit_image,controls_image

    image = load_image('Keroro_title.png')
    start_image = load_image('logo_start.png')
    exit_image = load_image('logo_exit.png')
    controls_image = load_image('logo_controls.png')

def finish():
    global image, start_image, exit_image, controls_image
    del image, start_image, exit_image, controls_image

def update():
    pass

def draw():
    clear_canvas()
    image.draw(800, 450, 1600, 900)
    start_image.draw(800, 450, 400, 150)  # Start (화면 중앙)
    controls_image.draw(800, 300, 400, 150)  # Controls (Start 아래)
    exit_image.draw(800, 150, 400, 150)
    update_canvas()
    pass

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            game_framework.change_mode(play_mode)
    pass

def pause():
    pass

def resume():
    pass