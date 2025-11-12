from pico2d import *
import game_framework
import play_mode
from math import sin
import time

background = None
characters = []
selected_index = 0
time_acc = 0.0
previous_time = 0.0


def get_frame_time():
    global previous_time
    current_time = time.time()
    frame_time = current_time - previous_time
    previous_time = current_time
    return frame_time


def init():
    global background, characters, selected_index, previous_time
    try:
        background = load_image('Keroro_select.png')
    except:
        print("⚠️ 'Keroro_select.png' 파일이 없습니다. 기본 회색 배경으로 대체합니다.")
        background = None

    characters.extend([
        ('Dororo', 400, 630, 380, 380),
        ('Tamama', 1200, 630, 370, 370),
        ('Keroro', 800, 480, 400, 400),
        ('Giroro', 1100, 260, 380, 380),
        ('Kururu', 400, 260, 380, 380),
    ])
    selected_index = 0
    previous_time = time.time()


def finish():
    global background, characters
    del characters
    background = None


def update():
    global time_acc
    time_acc += get_frame_time() * 5


def draw():
    clear_canvas()
    if background:
        background.draw(800, 450, 1600, 900)
    else:
        set_clear_color(0.4, 0.4, 0.4, 1.0)
        clear_canvas()

    for i, (name, x, y, w, h) in enumerate(characters):
        scale = 1.2 if i == selected_index else 1.0
        sw, sh = w * scale, h * scale
        draw_rectangle(x - sw//2, y - sh//2, x + sw//2, y + sh//2)
    update_canvas()


def handle_events():
    global selected_index
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                game_framework.quit()
            elif e.key == SDLK_LEFT:
                selected_index = (selected_index - 1) % len(characters)
            elif e.key == SDLK_RIGHT:
                selected_index = (selected_index + 1) % len(characters)
            elif e.key in (SDLK_RETURN, SDLK_SPACE):
                print(f"✅ {characters[selected_index][0]} 선택됨! → play_mode 진입")
                play_mode.set_selected_index(selected_index)  # ✅ 인덱스 전달
                game_framework.change_mode(play_mode)


def pause(): pass
def resume(): pass
