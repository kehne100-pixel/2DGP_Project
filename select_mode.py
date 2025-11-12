from pico2d import *
import game_framework
import play_mode
import math
import time

# ======= 프레임 타이밍 함수 =======
current_time, previous_time, frame_time = 0, 0, 0
def get_frame_time():
    global current_time, previous_time, frame_time
    current_time = time.time()
    frame_time = current_time - previous_time
    previous_time = current_time
    return frame_time


# ======= 전역 변수 =======
background = None
characters = []          # 캐릭터 이미지들
selected_index = 0
time_acc = 0.0


# ======= 초기화 =======
def init():
    global background, characters, previous_time

    # 배경 이미지 로드
    background = load_image('Keroro_select.png')

    # 캐릭터 이미지 로드 (순서 중요!)
    characters.append(load_image('Keroro_select(Dororo).png'))
    characters.append(load_image('Keroro_select(Tamama).png'))
    characters.append(load_image('Keroro_select(Keroro).png'))
    characters.append(load_image('Keroro_select(Giroro).png'))
    characters.append(load_image('Keroro_select(kururu).png'))

    previous_time = time.time()


# ======= 리소스 해제 =======
def finish():
    global background, characters
    del background
    for c in characters:
        del c
    characters.clear()


# ======= 업데이트 (애니메이션) =======
def update():
    global time_acc
    time_acc += get_frame_time() * 5


# ======= 화면 그리기 =======
def draw():
    clear_canvas()
    background.draw(512, 384)  # (1024x768 기준 중앙)

    positions = [
        (200, 350),  # Dororo
        (400, 350),  # Tamama
        (600, 350),  # Keroro
        (800, 350),  # Giroro
        (1000, 350)  # Kururu
    ]

    for i, img in enumerate(characters):
        x, y = positions[i]

        if i == selected_index:
            # 선택된 캐릭터: 확대 + 깜빡임 효과
            size_scale = 1.1 + 0.05 * math.sin(time_acc)
            alpha = 0.7 + 0.3 * abs(math.sin(time_acc))
            img.opacify(alpha)
            img.draw(x, y, 250 * size_scale, 250 * size_scale)
        else:
            # 일반 캐릭터: 기본 크기
            img.opacify(1.0)
            img.draw(x, y, 200, 200)

    update_canvas()


# ======= 입력 처리 =======
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
                selected_index = (selected_index + 1) % len(characters)
            elif event.key == SDLK_LEFT:
                selected_index = (selected_index - 1) % len(characters)
            elif event.key == SDLK_RETURN or event.key == SDLK_SPACE:
                print(f"캐릭터 선택 완료: {['Dororo', 'Tamama', 'Keroro', 'Giroro', 'Kururu'][selected_index]}")
                game_framework.change_mode(play_mode)


# ======= 상태 전환 =======
def pause(): pass
def resume(): pass
