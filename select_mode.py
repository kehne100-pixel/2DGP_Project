from pico2d import *
import game_framework
import play_mode
import time
import math

# 🔹 프레임 시간 계산용
current_time = 0
previous_time = 0
frame_time = 0

def get_frame_time():
    global current_time, previous_time, frame_time
    current_time = time.time()
    frame_time = current_time - previous_time
    previous_time = current_time
    return frame_time


# 🔹 캐릭터 이미지 변수
dororo = None
tamama = None
kururu = None
keroro = None
giroro = None

selected_index = 0
time_acc = 0


def init():
    global dororo, tamama, kururu, keroro, giroro, previous_time
    dororo = load_image('Keroro_select(Dororo).png')
    tamama = load_image('Keroro_select(Tamama).png')
    kururu = load_image('Keroro_select(kururu).png')
    keroro = load_image('Keroro_select(Keroro).png')
    giroro = load_image('Keroro_select(giroro).png')

    previous_time = time.time()  # ✅ 시간 초기화


def finish():
    global dororo, tamama, kururu, keroro, giroro
    del dororo, tamama, kururu, keroro, giroro


def update():
    global time_acc
    time_acc += get_frame_time() * 5  # 깜빡임 속도


def draw():
    clear_canvas()

    # 🔹 캐릭터 위치 좌표
    positions = [
        (300, 400),   # Dororo
        (600, 400),   # Tamama
        (900, 400),   # Keroro
        (1200, 400),  # Giroro
        (1500, 400)   # Kururu
    ]

    # 🔹 이미지 리스트
    images = [dororo, tamama, keroro, giroro, kururu]

    # 🔹 캐릭터 출력
    for i, img in enumerate(images):
        x, y = positions[i]

        if i == selected_index:
            # 선택된 캐릭터: 확대 + 깜빡임 효과
            size_scale = 1.1 + 0.05 * math.sin(time_acc)
            img.draw(x, y, 300 * size_scale, 400 * size_scale)

            # ✅ 빛나는 테두리 (OpenGL 방식)
            glow_alpha = (math.sin(time_acc) + 1) / 2  # 0~1 반복
            r, g, b = 1.0, 1.0, 0.3  # 노란빛
            glColor4f(r, g, b, glow_alpha * 0.8)
            glLineWidth(5)
            glBegin(GL_LINE_LOOP)
            glVertex2f(x - 170, y - 230)
            glVertex2f(x + 170, y - 230)
            glVertex2f(x + 170, y + 230)
            glVertex2f(x - 170, y + 230)
            glEnd()
            glColor4f(1, 1, 1, 1)  # 색상 초기화
        else:
            img.draw(x, y, 280, 380)

    update_canvas()


def handle_events():
    global selected_index
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                import title_mode
                game_framework.change_mode(title_mode)
            elif event.key == SDLK_RIGHT:
                selected_index = (selected_index + 1) % 5
            elif event.key == SDLK_LEFT:
                selected_index = (selected_index - 1) % 5
            elif event.key == SDLK_RETURN or event.key == SDLK_SPACE:
                print(f"캐릭터 {selected_index} 선택됨!")
                game_framework.change_mode(play_mode)


def pause():
    pass


def resume():
    pass
