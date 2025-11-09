from pico2d import *
from Keroro import keroro
import play_mode as start_mode
import game_framework

open_canvas()
game_framework.run(start_mode)
close_canvas()



# Game object class here


def handle_events():
    global running

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            keroro.handle_event(event)


def reset_world():
    global world
    global keroro

    world = []




    world.append(keroro)



def update_world():
    for o in world:
        o.update()
    pass


def render_world():
    clear_canvas()
    for o in world:
        o.draw()
    update_canvas()


running = True



open_canvas()
reset_world()
# game loop
while running:
    handle_events()
    update_world()
    render_world()
    delay(0.1)
# finalization code
close_canvas()
