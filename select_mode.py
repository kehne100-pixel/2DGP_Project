from pico2d import *
import game_framework

# 이미지들
background = None
characters = []
selected_index = 0
time_acc = 0.0

def init():
    global background, characters, selected_index
    open_canvas(1600, 900)
    background = load_image('Keroro_select.png')

    # 캐릭터 이름 순서대로
    characters.append(('Dororo', 400, 650, 300, 300))
    characters.append(('Tamama', 1200, 650, 300, 300))
    characters.append(('Keroro', 800, 500, 300, 300))
    characters.append(('Giroro', 1100, 250, 300, 300))
    characters.append(('Kururu', 400, 250, 300, 300))

    selected_index = 0


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

    # 각 캐릭터 위치 지정
    for i, (name, x, y, w, h) in enumerate(characters):
        scale = 1.0
        if i == selected_index:
            scale = 1.2 + 0.05 * sin(time_acc)
        draw_rectangle(x - w//2, y - h//2, x + w//2, y + h//2)
        # 확대 효과 표현용 더미 사각형 (위치 확인용)
        # 실제로는 캐릭터 영역 효과 (Glow 등)에 맞게 수정 가능
        # draw_rectangle을 제거하고 draw 효과를 여기에 추가 가능

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
