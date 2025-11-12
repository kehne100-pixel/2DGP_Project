from pico2d import *
import game_framework
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

    # 각 캐릭터 (이 좌표는 스크린샷을 기준으로 수정된 값)
    # name, x, y, w, h
    characters.append(('Dororo', 400, 630, 380, 380))   # 왼쪽 위
    characters.append(('Tamama', 1200, 630, 370, 370))  # 오른쪽 위
    characters.append(('Keroro', 800, 480, 400, 400))   # 중앙
    characters.append(('Giroro', 1100, 260, 380, 380))  # 오른쪽 아래
    characters.append(('Kururu', 400, 260, 380, 380))   # 왼쪽 아래

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

    # 전체 배경 꽉 채우기
    background.draw(800, 450, 1600, 900)

    # 캐릭터별 위치/크기
    for i, (name, x, y, w, h) in enumerate(characters):
        scale = 1.0
        if i == selected_index:
            scale = 1.2 + 0.05 * sin(time_acc)
        sw, sh = w * scale, h * scale

        # 선택 캐릭터 확대 효과
        draw_rectangle(x - sw//2, y - sh//2, x + sw//2, y + sh//2)
        # 🔹 이 부분에 나중에 glow 효과나 캐릭터 강조 이미지 추가 가능

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
            elif e.key == SDLK_RETURN:
                print(f"{characters[selected_index][0]} 선택됨!")


def pause():
    pass


def resume():
    pass
