from pico2d import *
import game_framework

# 각 캐릭터 모듈 불러오기
from Keroro import Keroro
from Dororo import Dororo
from Tamama import Tamama
from Giroro import Giroro
from Kururu import Kururu

background = None
player = None
selected_character = 0


# ✅ select_mode에서 전달받을 캐릭터 인덱스
def set_selected_index(index):
    global selected_character
    selected_character = index


# 캐릭터 이름 목록 (선택창 인덱스 순서)
CHARACTERS = ['Dororo', 'Tamama', 'Keroro', 'Giroro', 'Kururu']


def init():
    global background, player

    try:
        background = load_image('Keroro_background.png')
    except:
        print("⚠️ 'Keroro_background.png' 파일이 없습니다. 기본 회색 배경으로 대체합니다.")
        background = None

    # ✅ 선택된 캐릭터 인덱스에 맞는 객체 생성
    name = CHARACTERS[selected_character]
    if name == 'Keroro':
        player = Keroro()
    elif name == 'Dororo':
        player = Dororo()
    elif name == 'Tamama':
        player = Tamama()
    elif name == 'Giroro':
        player = Giroro()
    elif name == 'Kururu':
        player = Kururu()
    else:
        print("⚠️ 잘못된 캐릭터 인덱스입니다.")
        player = None

    print(f"✅ {name} 로드 완료 — 전투 시작!")


def finish():
    global background, player
    if background:
        del background
    if player:
        del player


def update():
    if player:
        player.update()


def draw():
    clear_canvas()

    # 배경 그리기
    if background:
        background.draw(800, 450, 1600, 900)
    else:
        set_clear_color(0.5, 0.5, 0.5, 1.0)
        clear_canvas()

    # 캐릭터 애니메이션 그리기
    if player:
        player.draw()
    else:
        draw_rectangle(750, 100, 850, 200)

    update_canvas()


def handle_events():
    global player
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                game_framework.quit()
        # 캐릭터가 존재하면 이벤트 전달
        if player:
            player.handle_event(e)


def pause(): pass
def resume(): pass
