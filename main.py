# main.py
from pico2d import *
from Keroro import Boy

def handle_events(boy):
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            return False
        if e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
            return False
        boy.handle_event(e)
    return True

def main():
    open_canvas(800, 600)
    boy = Boy()
    running = True
    while running:
        running = handle_events(boy)
        clear_canvas()
        boy.update()
        boy.draw()
        update_canvas()
        delay(0.01)
    close_canvas()

if __name__ == '__main__':
    main()
