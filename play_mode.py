# play_mode.py

from pico2d import *
import game_framework
import random

from Keroro import Keroro
from Dororo import Dororo
from Tamama import Tamama
from Giroro import Giroro
from Kururu import Kururu

from fighter_ai import FighterAI
import camera
from battle_ui import BattleUI   # ← UI 모듈

W, H = 1600, 900

background = None
player = None
enemy = None
ai = None
ui = None

selected_character = 0
CHARACTERS = ['Dororo', 'Tamama', 'Keroro', 'Giroro', 'Kururu']

# ────────────────────────────
# 전투 수치 설정
# ────────────────────────────
MAX_HP = 100
MAX_SP = 100

# 데미지
DAMAGE_TABLE = {
    'attack': 5,      # s 키 기본 공격
    'attack2': 5,     # d 키 공격(지정 없어서 5로 통일)
    'skill1': 20,     # 1번 스킬
    'skill2': 35,     # 2번 스킬
    'skill3': 50,     # 3번 스킬
}

# 스킬 사용 시 필요한 게이지
SP_COST = {
    'attack': 0,
    'attack2': 0,
    'skill1': 30,
    'skill2': 50,
    'skill3': 100,
}

# 일반 공격이 히트했을 때 게이지 증가량
SP_GAIN_ON_ATTACK_HIT = 10


def set_selected_index(index):
    global selected_character
    selected_character = index


# ────────────────────────────
# 캐릭터 생성
# ────────────────────────────
def create_fighter(name, is_left=True):
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
        print(f"[WARN] Unknown fighter name: {name}, use Keroro")
        c = Keroro()

    c.y = c.ground_y

    # 양쪽 끝에서 시작 (화면 안에는 들어오도록 약간 여유)
    MARGIN_X = 200
    if is_left:
        c.x = MARGIN_X
        c.face_dir = 1
    else:
        c.x = W - MARGIN_X
        c.face_dir = -1

    c.dir = 0

    # 스탯 기본값 세팅
    setup_stats(c)

    return c


def setup_stats(f):
    """캐릭터 HP/게이지/가드 플래그 초기화"""
    f.max_hp = MAX_HP
    f.hp = MAX_HP
    f.max_sp = MAX_SP
    if not hasattr(f, 'sp'):
        f.sp = 0
    else:
        f.sp = max(0, min(f.sp, MAX_SP))

    if not hasattr(f, 'is_guarding'):
        f.is_guarding = False

    # 한 번 공격 동작당 한 번만 맞도록
    f.has_hit = False


# ────────────────────────────
# 몸통 충돌 (둘이 겹쳐지지 않게만)
# ────────────────────────────
def resolve_body_collision():
    global player, enemy
    if not player or not enemy:
        return

    body_half = 35
    min_distance = body_half * 2

    dx = enemy.x - player.x
    if dx == 0:
        return

    distance = abs(dx)
    if distance < min_distance:
        if dx > 0:
            player.x = enemy.x - min_distance
        else:
            player.x = enemy.x + min_distance


# ────────────────────────────
# 스테이지 밖으로 못 나가게
# ────────────────────────────
def clamp_fighters():
    STAGE_LEFT = 0
    STAGE_RIGHT = W

    if player:
        player.x = max(STAGE_LEFT, min(STAGE_RIGHT, player.x))
    if enemy:
        enemy.x = max(STAGE_LEFT, min(STAGE_RIGHT, enemy.x))


# ────────────────────────────
# 공격 판정용 유틸
# ────────────────────────────
def get_attack_type(f):
    """현재 상태가 어떤 공격인지 문자열로 반환 (공격 아니면 None)."""
    s = f.state_machine.cur_state

    if hasattr(f, 'ATTACK') and s is f.ATTACK:
        return 'attack'
    if hasattr(f, 'ATTACK2') and s is f.ATTACK2:
        return 'attack2'
    if hasattr(f, 'SKILL') and s is f.SKILL:
        return 'skill1'
    if hasattr(f, 'SKILL2') and s is f.SKILL2:
        return 'skill2'
    if hasattr(f, 'SKILL3') and s is f.SKILL3:
        return 'skill3'
    return None


def get_body_aabb(f):
    """대략적인 몸통 히트박스 (중심 기준 직사각형)."""
    half_w = 30
    half_h = 45
    return (
        f.x - half_w,
        f.y - half_h,
        f.x + half_w,
        f.y + half_h
    )


def aabb_overlap(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    if ax2 < bx1 or bx2 < ax1:
        return False
    if ay2 < by1 or by2 < ay1:
        return False
    return True


def handle_attack_collisions():
    """양쪽 공격 판정 실행."""
    if not player or not enemy:
        return

    handle_one_side_attack(player, enemy)
    handle_one_side_attack(enemy, player)


def handle_one_side_attack(attacker, defender):
    """attacker가 공격 중일 때 defender에게 맞는지 판정."""
    attack_type = get_attack_type(attacker)

    # 공격 상태가 아니면 플래그만 리셋
    if attack_type is None:
        attacker.has_hit = False
        return

    # 이미 이번 공격 동작에서 한 번 맞췄으면 더 이상 판정 X
    if getattr(attacker, 'has_hit', False):
        return

    # 히트박스 체크
    if not aabb_overlap(get_body_aabb(attacker), get_body_aabb(defender)):
        return

    # 상대가 가드 중이면 데미지도, 넉백도 없음
    if getattr(defender, 'is_guarding', False):
        attacker.has_hit = True  # 같은 공격에서 계속 튕기는 거 방지
        return

    # 필요한 게이지 확인 (스킬만)
    need_sp = SP_COST.get(attack_type, 0)
    cur_sp = getattr(attacker, 'sp', 0)

    if need_sp > 0 and cur_sp < need_sp:
        # 게이지 부족 → 스킬은 나가지만 데미지/게이지 변화 없음
        attacker.has_hit = True
        return

    # 실제 데미지 계산
    damage = DAMAGE_TABLE.get(attack_type, 0)

    defender.hp = max(0, getattr(defender, 'hp', MAX_HP) - damage)

    # 필살 게이지 증감
    if attack_type in ('attack', 'attack2'):
        # 일반 공격 히트 시 +10
        attacker.sp = min(attacker.max_sp,
                          getattr(attacker, 'sp', 0) + SP_GAIN_ON_ATTACK_HIT)
    else:
        # 스킬은 사용에 따른 게이지 소모
        if need_sp > 0:
            attacker.sp = max(0, cur_sp - need_sp)

    # 넉백 (가드가 아닐 때만)
    KNOCKBACK = 15 if attack_type in ('attack', 'attack2') else 25
    if attacker.x < defender.x:
        defender.x += KNOCKBACK
    else:
        defender.x -= KNOCKBACK

    attacker.has_hit = True


# ────────────────────────────
# 초기화
# ────────────────────────────
def init():
    global background, player, enemy, ai, ui

    try:
        background = load_image('Keroro_background.png')
        print("✅ Keroro_background.png 로드 완료")
    except:
        print("⚠️ Keroro_background.png 를 찾지 못했습니다.")
        background = None

    player_name = CHARACTERS[selected_character]
    player = create_fighter(player_name, is_left=True)
    print(f"✅ Player1 : {player_name}")

    enemy_candidates = [n for n in CHARACTERS if n != player_name]
    enemy_name = random.choice(enemy_candidates)
    enemy = create_fighter(enemy_name, is_left=False)
    print(f"✅ Enemy (AI) : {enemy_name}")

    ai = FighterAI(enemy, player)

    camera.init()
    print("✅ Camera init 완료")

    ui = BattleUI()
    print("✅ BattleUI 생성 완료")


def finish():
    global background, player, enemy, ai, ui
    background = None
    player = None
    enemy = None
    ai = None
    ui = None


# ────────────────────────────
# 매 프레임 업데이트
# ────────────────────────────
def update():
    global player, enemy, ai, background, ui

    if player:
        player.update()
    if enemy:
        enemy.update()
    if ai:
        ai.update()

    clamp_fighters()
    resolve_body_collision()

    # 공격 판정
    handle_attack_collisions()

    camera.update(player, enemy, background)

    if ui:
        ui.update()


# ────────────────────────────
# 그리기
# ────────────────────────────
def draw():
    clear_canvas()

    zoom = camera.get_zoom()
    cx, cy = camera.get_center()

    if background:
        src_w = int(W / zoom)
        src_h = int(H / zoom)

        bx = int(cx - src_w / 2)
        by = int(cy - src_h / 2)

        if bx < 0:
            bx = 0
        if by < 0:
            by = 0
        if bx + src_w > background.w:
            bx = background.w - src_w
        if by + src_h > background.h:
            by = background.h - src_h

        src_center_x = bx + src_w // 2
        src_center_y = by + src_h // 2

        background.clip_draw(
            src_center_x, src_center_y,
            src_w, src_h,
            W // 2, H // 2,
            W, H
        )
    else:
        set_clear_color(0.5, 0.5, 0.5, 1.0)
        clear_canvas()

    if player:
        player.draw()
    if enemy:
        enemy.draw()

    if ui:
        ui.draw(player, enemy)

    update_canvas()


# ────────────────────────────
# 입력 처리
# ────────────────────────────
def handle_events():
    global player
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
            game_framework.quit()

        if player:
            player.handle_event(e)


def pause():
    pass


def resume():
    pass
