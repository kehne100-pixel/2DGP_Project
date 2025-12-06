# play_mode.py
from pico2d import *
import game_framework
import random

from Keroro import Keroro
from Dororo import Dororo
from Tamama import Tamama
from Giroro import Giroro
from Kururu import Kururu

from fighter_ai import FighterAI     # AI 컨트롤러
import camera                        # 카메라 모듈 (camera.py)


background = None
player = None
enemy = None
ai = None

selected_character = 0   # select_mode에서 넘어오는 인덱스 보관


# 캐릭터 이름 목록 (선택창 인덱스와 동일하게)
CHARACTERS = ['Dororo', 'Tamama', 'Keroro', 'Giroro', 'Kururu']


def set_selected_index(index: int):
    """select_mode에서 선택한 캐릭터 인덱스를 전달받는 함수"""
    global selected_character
    selected_character = index


def create_character(name: str):
    """문자열 이름으로 캐릭터 인스턴스를 생성하는 헬퍼 함수"""
    if name == 'Dororo':
        return Dororo()
    elif name == 'Tamama':
        return Tamama()
    elif name == 'Keroro':
        return Keroro()
    elif name == 'Giroro':
        return Giroro()
    elif name == 'Kururu':
        return Kururu()
    else:
        print(f"⚠️ 알 수 없는 캐릭터 이름: {name}")
        return Dororo()  # 안전용 기본값


def init():
    global background, player, enemy, ai

    # ---------------------------
    # 배경 이미지 로드
    # ---------------------------
    try:
        background = load_image('Keroro_background.png')
        print("✅ Keroro_background.png 로드 완료")
    except:
        try:
            background = load_image('background.png')
            print("✅ Keroro_background.png 가 없어 background.png 로드")
        except:
            print("⚠️ 배경 이미지가 없습니다. 단색 배경으로 대체합니다.")
            background = None

    # ---------------------------
    # 플레이어 캐릭터 생성
    # ---------------------------
    player_name = CHARACTERS[selected_character]
    player = create_character(player_name)
    # 시작 위치 & 방향
    player.x = 500
    player.y = 90
    player.face_dir = 1  # 오른쪽을 보게
    if hasattr(player, 'dir'):
        player.dir = 0

    # ---------------------------
    # 적 캐릭터 랜덤 선택 & 생성
    # ---------------------------
    remain = [c for c in CHARACTERS if c != player_name]
    enemy_name = random.choice(remain)
    enemy = create_character(enemy_name)
    enemy.x = 1100
    enemy.y = 90
    enemy.face_dir = -1  # 왼쪽을 보게
    if hasattr(enemy, 'dir'):
        enemy.dir = 0

    print(f"✅ 플레이어 캐릭터: {player_name}")
    print(f"✅ 적 캐릭터: {enemy_name}")

    # ---------------------------
    # 적 AI 생성 (적이 움직이고 공격하도록)
    # ---------------------------
    ai = FighterAI(enemy, player)
    print("✅ FighterAI 초기화 완료")


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


def resolve_body_collision():
    """
    캐릭터끼리 몸이 겹치지 않게 해주는 함수.
    - 서로 통과하지는 않게 하고
    - 플레이어가 적을 '밀어내지' 않게, 플레이어 쪽만 위치를 제한(clamp)한다.
    """
    global player, enemy
    if not player or not enemy:
        return

    # 서로 너무 가까운 최소 거리 (캐릭터 크기에 맞게 조절 가능)
    MIN_GAP = 70  # 픽셀 단위

    # player가 왼쪽, enemy가 오른쪽
    if player.x < enemy.x:
        # 두 캐릭터 사이 거리
        dist = enemy.x - player.x
        if dist < MIN_GAP:
            # 플레이어가 더 못 가도록 막는다 (적은 그대로)
            player.x = enemy.x - MIN_GAP
    else:
        # player가 오른쪽, enemy가 왼쪽
        dist = player.x - enemy.x
        if dist < MIN_GAP:
            # 플레이어를 반대쪽으로 clamp
            player.x = enemy.x + MIN_GAP

    # 월드 경계 안에 두기
    player.x = max(50, min(1550, player.x))
    enemy.x = max(50, min(1550, enemy.x))


def update():
    global player, enemy, ai

    if player:
        player.update()
    if enemy:
        enemy.update()
    if ai:
        ai.update()  # 적 행동(이동, 공격, 가드 등) 수행

    # 몸통 충돌 처리 (통과 금지 + 적 밀리지 않게)
    if player and enemy:
        resolve_body_collision()

        # 카메라 위치/줌 업데이트 (두 캐릭터 위치 기준)
        camera.update(player, enemy)


def draw():
    clear_canvas()

    # ---------------------------
    # 배경 그리기 (카메라/줌 없이 고정)
    # ---------------------------
    if background:
        # 네가 원래 쓰던 해상도 기준
        background.draw(800, 450, 1600, 900)
    else:
        # 배경 이미지 없으면 단색
        set_clear_color(0.3, 0.3, 0.3, 1.0)
        clear_canvas()

    # ---------------------------
    # 캐릭터 그리기
    # 각 캐릭터 파일(Dororo, Keroro, ...)에서
    # camera.world_to_screen() + camera.get_zoom()를 사용해서
    # 위치/크기를 그리도록 이미 수정해 둔 상태라고 가정.
    # ---------------------------
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

        # 플레이어 조작 이벤트만 넘겨줌 (적은 AI가 조작)
        if player:
            player.handle_event(e)


def pause():
    pass


def resume():
    pass
ㅁ