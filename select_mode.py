from pico2d import *
import game_framework
import select_mode

background = None


def init():
    global background

    background = load_image('background_title.png')


def finish():
    global background
    del background


def update():
    pass


def draw():
    clear_canvas()
    background.draw(W / 2, H / 2)
    update_canvas()
    pass


def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.key == SDLK_RETURN or event.key == SDLK_SPACE:  # Enter 또는 Space 키
            game_framework.change_mode(select_mode)


def pause():
    pass


def resume():
    pass
