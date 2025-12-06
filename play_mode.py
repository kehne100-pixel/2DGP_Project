from pico2d import *
import game_framework

from Keroro import Keroro
from Dororo import Dororo
from Tamama import Tamama
from Giroro import Giroro
from Kururu import Kururu

import camera  # ✅ 카메라 모듈

background = None
player = None
enemy = None       # 적 캐릭터 (없으면 None)
ai = None          # 인공지능 객체를 쓰고 있으면 여기 사용 (없으면 그냥 None)
selected_character = 0

# ✅ select_mode에서 전달받을 캐릭터 인덱스
def set_selected_index(index):
    global selected_character
    selected_character = index


# 캐릭터 이름 목록 (선택창 인덱스 순서)
CHARACTERS = ['Dororo', 'Tamama', 'Keroro', 'Giroro', 'Kururu']


def create_character(name, x, y):
    """
    캐릭터 이름 문자열로 객체 생성하는 헬퍼 함수
    """
    if name == 'Keroro':
        c = Keroro()
    elif name == 'Dororo':
        c = Dororo()
    elif name == 'Tamama':
        c = Tamama()
    elif name == 'Giroro':
        c = Giroro()
    elif name == 'Kururu':
        c = Kururu()
    else:
        print("⚠️ 잘못된 캐릭터 이름입니다:", name)
        return None

    c.x = x
    c.y = y
    return c


def init():
    global background, player, enemy, ai

    try:
        background = load_image('Keroro_background.png')
    except:
        print("⚠️ 'Keroro_background.png' 파일이 없습니다. 기본 회색 배경으로 대체합니다.")
        background = None

    # ✅ 배경이 있으면 월드 크기를 카메라에 세팅
    if background:
        camera.WORLD_W = background.w
        camera.WORLD_H = background.h
    else:
        camera.WORLD_W = 1600
        camera.WORLD_H = 900

    # ✅ 플레이어 캐릭터 생성 (선택한 인덱스 기준)
    name = CHARACTERS[selected_character]
    player_start_x = 500
    player_start_y = 90
    player = create_character(name, player_start_x, player_start_y)

    # ✅ 적 캐릭터는 일단 플레이어와 다른 캐릭터로 예시 생성 (원하면 바꿔도 됨)
    #    이미 너가 AI/적 생성 로직이 있다면 이 부분은 네 코드로 덮어써도 됨.
    enemy_name = 'Keroro' if name != 'Keroro' else 'Giroro'
    enemy_start_x = 1100
    enemy_start_y = 90
    enemy = create_character(enemy_name, enemy_start_x, enemy_start_y)

    # 인공지능 객체를 따로 쓰고 있다면 여기서 enemy와 player를 넘겨서 생성해주면 됨.
    # 예: ai = FighterAI(enemy, player)
    ai = None  # 이미 fighter_ai.py 를 쓰고 있다면 이 줄은 네 코드로 교체

    print(f"✅ 플레이어: {name},  적: {enemy_name} 로드 완료 — 전투 시작!")


def finish():
    global background, player, enemy, ai
    if background:
        del background
        background = None
    if player:
        del player
        player = None
    if enemy:
        del enemy
        enemy = None
    ai = None


def update():
    global player, enemy, ai

    if player:
        player.update()
    if enemy:
        enemy.update()
    if ai:
        ai.update()

    # ✅ 카메라 업데이트 (플레이어, 적 기준)
    camera.update(player, enemy)


def draw():
    clear_canvas()

    cw, ch = get_canvas_width(), get_canvas_height()

    # ✅ 배경 그리기 (스크롤 + 줌)
    if background:
        left, bottom, w, h = camera.get_window()

        # src 중심 좌표
        src_cx = int(left + w / 2.0)
        src_cy = int(bottom + h / 2.0)

        # 화면 중앙에, 캔버스 크기로 스케일해서 그리기
        background.clip_draw(
            src_cx, src_cy,
            int(w), int(h),
            cw // 2, ch // 2,
            cw, ch
        )
    else:
        set_clear_color(0.5, 0.5, 0.5, 1.0)
        clear_canvas()

    # ✅ 캐릭터 애니메이션 그리기 (각 캐릭터의 draw()에서 camera.world_to_screen 사용)
    if player:
        player.draw()
    if enemy:
        enemy.draw()

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
        # 적도 플레이어처럼 키로 조종하고 싶다면 여기에 enemy.handle_event(e) 추가 가능
        # 지금은 AI로 움직이는 가정이라 입력은 안 넘김.


def pause():
    pass


def resume():
    pass
