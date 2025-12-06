# play_mode.py

from pico2d import *
import game_framework

from Keroro import Keroro
from Dororo import Dororo
from Tamama import Tamama
from Giroro import Giroro
from Kururu import Kururu
from fighter_ai import FighterAI   # ✅ 적 인공지능

background = None
player = None
enemy = None
enemy_ai = None

# 선택된 플레이어 캐릭터 인덱스 (select_mode에서 설정)
selected_character = 0

# 선택창 인덱스 기준 캐릭터 이름
CHARACTERS = ['Dororo', 'Tamama', 'Keroro', 'Giroro', 'Kururu']

# 스테이지 벽 위치(캐릭터 x 범위와 맞춰줌)
STAGE_LEFT  = 50
STAGE_RIGHT = 1550


def set_selected_index(index):
    """select_mode에서 호출해서 플레이어 캐릭터 인덱스 설정"""
    global selected_character
    selected_character = index


def create_character_by_name(name, x, y, face_dir=1):
    """문자열 이름으로 캐릭터 객체 생성 + 위치/방향 설정"""
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
        c = Dororo()

    c.x = x
    c.y = y
    c.face_dir = face_dir
    return c


# ============================================
#  ⚔ 몸통 충돌 처리 (서로 통과 못하게 하기)
# ============================================

def get_body_box(fighter):
    """
    각 캐릭터의 '몸통' 박스 (충돌 박스) 대략 지정
    캐릭터마다 스프라이트 크기는 조금씩 다르지만,
    다 비슷한 크기로 그려지고 있으니까 공통 크기로 씀.
    """
    half_w = 40   # 좌우 반폭
    half_h = 60   # 상하 반높이

    left   = fighter.x - half_w
    right  = fighter.x + half_w
    bottom = fighter.y - half_h
    top    = fighter.y + half_h
    return left, bottom, right, top


def resolve_body_collision(f1, f2):
    """
    두 캐릭터 몸통끼리 겹치면,
    '움직이던 쪽만' 밀어내서, 가만히 있던 캐릭터가 뒤로 밀리지 않게 한다.
    f1, f2 : player, enemy (순서 상관 X, 하지만 우리는 player, enemy 순서로 호출 중)
    """
    if f1 is None or f2 is None:
        return

    l1, b1, r1, t1 = get_body_box(f1)
    l2, b2, r2, t2 = get_body_box(f2)

    # AABB 겹침 확인
    if r1 < l2 or r2 < l1:
        return  # 가로로 안 겹침
    if t1 < b2 or t2 < b1:
        return  # 세로로 안 겹침

    # 가로 방향으로 겹친 정도
    overlap_x = min(r1, r2) - max(l1, l2)
    if overlap_x <= 0:
        return

    # 각 캐릭터의 이동 방향(dir) 확인
    d1 = getattr(f1, 'dir', 0)
    d2 = getattr(f2, 'dir', 0)

    # 1) f1만 움직이고, f2는 가만히 있을 때 → f1만 되돌린다.
    if d1 != 0 and d2 == 0:
        if d1 > 0:      # 오른쪽으로 파고들었으면
            f1.x -= overlap_x  # 왼쪽으로 되돌리기
        else:           # 왼쪽으로 파고들었으면
            f1.x += overlap_x  # 오른쪽으로 되돌리기

    # 2) f2만 움직이고, f1은 가만히 있을 때 → f2만 되돌린다.
    elif d2 != 0 and d1 == 0:
        if d2 > 0:
            f2.x -= overlap_x
        else:
            f2.x += overlap_x

    # 3) 둘 다 움직이거나, 둘 다 안 움직일 때 → 둘 다 반씩 밀어내기(이전 방식)
    else:
        push = overlap_x / 2.0
        if f1.x < f2.x:
            f1.x -= push
            f2.x += push
        else:
            f1.x += push
            f2.x -= push

    # 스테이지 범위 안으로 다시 클램프
    f1.x = max(STAGE_LEFT, min(STAGE_RIGHT, f1.x))
    f2.x = max(STAGE_LEFT, min(STAGE_RIGHT, f2.x))



# ============================================
#  init / finish
# ============================================

def init():
    global background, player, enemy, enemy_ai

    # 배경 이미지 로드
    try:
        background = load_image('Keroro_background.png')
    except:
        print("⚠️ 'Keroro_background.png' 파일이 없습니다. 기본 회색 배경으로 대체합니다.")
        background = None

    # ✅ 플레이어 캐릭터 생성
    player_name = CHARACTERS[selected_character]
    player_start_x = 400
    player_start_y = 90
    player_face_dir = 1  # 오른쪽

    player_char = create_character_by_name(player_name,
                                           x=player_start_x,
                                           y=player_start_y,
                                           face_dir=player_face_dir)
    globals()['player'] = player_char

    # ✅ 적 캐릭터는 랜덤 (플레이어와 다른 캐릭터 중에서)
    import random
    enemy_candidates = [n for n in CHARACTERS if n != player_name]
    enemy_name = random.choice(enemy_candidates)

    enemy_start_x = 1200
    enemy_start_y = 90
    enemy_face_dir = -1  # 왼쪽

    enemy_char = create_character_by_name(enemy_name,
                                          x=enemy_start_x,
                                          y=enemy_start_y,
                                          face_dir=enemy_face_dir)
    globals()['enemy'] = enemy_char

    # ✅ 적 인공지능: enemy가 player를 기준으로 움직임
    globals()['enemy_ai'] = FighterAI(enemy_char, player_char)

    print(f"✅ Player: {player_name}, Enemy: {enemy_name} 로드 완료 — 전투 시작!")


def finish():
    """게임 모드 종료 시 정리"""
    global background, player, enemy, enemy_ai
    background = None
    player = None
    enemy = None
    enemy_ai = None


# ============================================
#  update / draw / 입력 처리
# ============================================

def update():
    """게임 한 프레임 업데이트"""
    global player, enemy, enemy_ai

    # 🟢 플레이어: 키 입력 기반 상태 업데이트
    if player:
        player.update()

    # 🔴 적: AI가 먼저 행동 결정 → 그다음 상태 업데이트
    if enemy:
        if enemy_ai:
            enemy_ai.update()
        enemy.update()

    # ✅ 몸통 충돌 처리: 서로 통과 못하게
    if player and enemy:
        resolve_body_collision(player, enemy)

    # (공격 히트판정은 나중에 별도 resolve_attack_collision에서 추가 예정)


def draw():
    """화면 그리기"""
    clear_canvas()

    # 배경
    if background:
        background.draw(800, 450, 1600, 900)
    else:
        set_clear_color(0.5, 0.5, 0.5, 1.0)
        clear_canvas()

    # 캐릭터 그리기
    if player:
        player.draw()
    if enemy:
        enemy.draw()

    update_canvas()


def handle_events():
    """입력 처리: 플레이어에게만 키 입력 전달, 적은 AI가 알아서"""
    global player
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()

        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                game_framework.quit()

        # ✅ 키보드 입력은 플레이어에게만 전달
        if player:
            player.handle_event(e)


def pause():
    pass


def resume():
    pass
