from pico2d import *
import game_framework
import title_mode  # 다음 화면으로 갈 모드

image = None
start_time = 0.0

def init():
    global image, start_time
    image = load_image('Keroro_logo.png')
    start_time = get_time()

def finish():
    global image
    del image

def update():

    if get_time() - start_time > 3.0:
        game_framework.change_mode(title_mode)

def draw():
    clear_canvas()
    image.draw(800, 450, 1600, 900)
    update_canvas()

def handle_events():
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                game_framework.quit()
            # 스페이스/엔터로 즉시 넘기기
            elif e.key in (SDLK_SPACE, SDLK_RETURN):
                game_framework.change_mode(title_mode)

def pause():
    pass

def resume():
    pass
