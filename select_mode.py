from pico2d import *
import game_framework
import play_mode  # ✅ play_mode로 전환하기 위해 import
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
    background = load_image('Keroro_select.png')

    # 캐릭터 이름, 위치, 크기
    characters.append(('Dororo', 400, 630, 380, 380))
    characters.append(('Tamama', 1200, 630, 370, 370))
    characters.append(('Keroro', 800, 480, 400, 400))
    characters.append(('Giroro', 1100, 260, 380, 380))
    characters.append(('Kururu', 400, 260, 380, 380))

    selected_index = 0
    previous_time = time.time()


def finish():
    global background, characters
    del background
    del characters


def update():
    global time_acc
    time_acc += get_frame_time() * 5


def draw():
    global selected_index
    clear_canvas()

    # 배경 꽉 채우기
    background.draw(800, 450, 1600, 900)

    # 캐릭터 영역 표시 (디버깅용 사각형)
    for i, (name, x, y, w, h) in enumerate(characters):
        scale = 1.0
        if i == selected_index:
            scale = 1.2 + 0.05 * sin(time_acc)
        sw, sh = w * scale, h * scale
        draw_rectangle(x - sw // 2, y - sh // 2, x + sw // 2, y + sh // 2)

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
                if selected_index > 0:
                    selected_index -= 1

            elif e.key == SDLK_RIGHT:
                if selected_index < len(characters) - 1:
                    selected_index += 1

            elif e.key in (SDLK_RETURN, SDLK_SPACE):
                # ✅ 선택 완료 → play_mode로 전환
                print(f"{characters[selected_index][0]} 선택됨! play_mode로 이동합니다.")
                game_framework.change_mode(play_mode)


def pause():
    pass


def resume():
    pass
