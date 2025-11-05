from pico2d import *

open_canvas(800, 600)

character = load_image('Keroro_Sheet.png')


running = True
x, y = 400, 300
frame = 0
dir_x, dir_y = 0, 0
look_dir = 0

def handle_events():
    global running, dir_x, dir_y, look_dir, dir_x, dir_y, frame, last_dir
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_RIGHT:
                dir_x += 1
                last_dir = 1
            elif event.key == SDLK_LEFT:
                dir_x -= 1
                last_dir = -1
            elif event.key == SDLK_UP:
                dir_y += 1

            elif event.key == SDLK_DOWN:
                dir_y -= 1
            elif event.key == SDLK_ESCAPE:
                running = False
        elif event.type == SDL_KEYUP:
            if event.key == SDLK_RIGHT:
                dir_x -= 1
            elif event.key == SDLK_LEFT:
                dir_x += 1
            elif event.key == SDLK_UP:
                dir_y -= 1
            elif event.key == SDLK_DOWN:
                dir_y += 1








while running:
    clear_canvas()








