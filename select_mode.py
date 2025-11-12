from pico2d import *
import game_framework
import play_mode
import time, math, os

background = None
characters = []
menu_index = 0
time_acc = 0.0
previous_time = 0.0

def get_frame_time():
    global previous_time
    current = time.time()
    frame = current - previous_time
    previous_time = current
    return frame


def init():
    global background, characters, previous_time
    print("[DEBUG] 현재 경로:", os.getcwd())

    # 전체 해상도에 맞게 표시할 배경
    background = load_image('Keroro_select.png')

    # 캐릭터 이미지들 로드
    file_names = [
        'Keroro_select(Dororo).png',
        'Keroro_select(Tamama).png',
        'Keroro_select(keroro).png',
        'Keroro_select(giroro).png',
        'Keroro_select(kururu).png'
    ]

    for f in file_names:
        try:
            characters.append(load_image(f))
            print(f"✅ {f} 불러오기 성공")
        except:
            print(f"❌ {f} 파일을 찾을 수 없습니다.")
            raise

    previous_time = time.time()


def finish():
    global background, characters
    del background
    for c in characters:
        del c
    characters.clear()


def update():
    global time_acc
    time_acc += get_frame_time() * 5


def draw():
    clear_canvas()

    # ✅ 배경을 해상도(1600x900)에 맞게 꽉 채우기
    background.draw_to_origin(0, 0, 1600, 900)

    # ✅ 캐릭터별 실제 배경 위치 맞춤 좌표
    positions = [
        (370, 650, 380, 380),   # Dororo
        (1220, 650, 370, 370),  # Tamama
        (780, 470, 420, 420),   # Keroro (중앙)
        (1220, 300, 420, 420),  # Giroro
        (370, 250, 400, 400)    # Kururu
    ]

    for i, (x, y, w, h) in enumerate(positions):
        img = characters[i]
        if i == menu_index:
            size_scale = 1.1 + 0.05 * math.sin(time_acc)
            alpha = 0.7 + 0.3 * abs(math.sin(time_acc))
            img.opacify(alpha)
            img.draw(x, y, w * size_scale, h * size_scale)
        else:
            img.opacify(1.0)
            img.draw(x, y, w, h)

    update_canvas()


def handle_events():
    global menu_index
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                import title_mode
                game_framework.change_mode(title_mode)
            elif e.key == SDLK_RIGHT:
                menu_index = (menu_index + 1) % len(characters)
            elif e.key == SDLK_LEFT:
                menu_index = (menu_index - 1) % len(characters)
            elif e.key == SDLK_RETURN or e.key == SDLK_SPACE:
                selected = ["Dororo", "Tamama", "Keroro", "Giroro", "Kururu"][menu_index]
                print(f"✅ {selected} 선택됨!")
                game_framework.change_mode(play_mode)


def pause(): pass
def resume(): pass
