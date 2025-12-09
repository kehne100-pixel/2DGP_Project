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
import ui  # HP/게이지/타이머 UI

W, H = 1600, 900

background = None
player = None
enemy = None
ai = None

selected_character = 0
CHARACTERS = ['Dororo', 'Tamama', 'Keroro', 'Giroro', 'Kururu']

round_time = 60.0     # 60초 라운드 타이머


def set_selected_index(index: int):
    """select_mode에서 호출해서 1P 캐릭터 선택"""
    global selected_character
    selected_character = index


# ----------------- 캐릭터 생성 -----------------
def create_fighter(name: str, is_left: bool = True):
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

    # 바닥 y는 각 캐릭터 클래스의 ground_y 사용
    c.y = getattr(c, 'ground_y', 90)

    # 양 끝에서 출발 (화면 안쪽으로만)
    MARGIN_X = 200
    if is_left:
        c.x = MARGIN_X
        c.face_dir = 1
    else:
        c.x = W - MARGIN_X
        c.face_dir = -1

    c.dir = 0
    return c


# ------------- 몸통 충돌 (서로 통과 X, 적은 안 밀리고 플레이어만 밀리게) -------------
def resolve_body_collision():
    global player, enemy
    if not player or not enemy:
        return

    # 대략적인 반경
    body_half = 35
    min_distance = body_half * 2  # 70

    dx = enemy.x - player.x
    if dx == 0:
        return

    distance = abs(dx)
    if distance < min_distance:
        # 적은 고정, 플레이어만 적에게 겹치지 않게 이동
        if dx > 0:
            # enemy가 오른쪽에 있음 -> player를 왼쪽으로
            player.x = enemy.x - min_distance
        else:
            # enemy가 왼쪽에 있음 -> player를 오른쪽으로
            player.x = enemy.x + min_distance


# ------------- 스테이지 밖으로 못 나가게 클램프 -------------
def clamp_fighters():
    STAGE_LEFT = 60
    STAGE_RIGHT = W - 60

    if player:
        player.x = max(STAGE_LEFT, min(STAGE_RIGHT, player.x))
    if enemy:
        enemy.x = max(STAGE_LEFT, min(STAGE_RIGHT, enemy.x))


# ------------- 사각형 충돌 체크 -------------
def rects_overlap(a, b):
    """
    a, b : (left, bottom, right, top)
    """
    left1, bottom1, right1, top1 = a
    left2, bottom2, right2, top2 = b

    if right1 < left2:
        return False
    if right2 < left1:
        return False
    if top1 < bottom2:
        return False
    if top2 < bottom1:
        return False
    return True


# ------------- 공격 판정 처리 -------------
def handle_attack(attacker, defender):
    """
    attacker.get_attack_hitbox(), defender.get_hurtbox(), defender.take_hit() 이 있다고 가정
    Tamama, Dororo, Keroro, Giroro, Kururu 모두 동일한 구조여야 함
    """
    # 공격 박스 함수가 없으면 패스
    if not hasattr(attacker, 'get_attack_hitbox'):
        return
    if not hasattr(defender, 'get_hurtbox'):
        return
    if not hasattr(defender, 'take_hit'):
        return

    hitbox = attacker.get_attack_hitbox()
    if hitbox is None:
        return

    hurtbox = defender.get_hurtbox()
    if hurtbox is None:
        return

    if not rects_overlap(hitbox, hurtbox):
        return

    # 일단 충돌 발생 -> 한 번만 맞게 처리
    # (각 캐릭터 클래스에서 is_attacking, attack_hit_done 플래그를 쓰고 있음)
    if hasattr(attacker, 'attack_hit_done'):
        if attacker.attack_hit_done:
            return
        attacker.attack_hit_done = True

    # 데미지 & SP 증가 (기본값: 일반 공격 5데미지, SP +10)
    # 스킬별 데미지까지 분리하려면 캐릭터 쪽에 current_attack_type 등을 추가하면 됨.
    damage = 5

    # 공격 방향 (defender에게서 보면 +1이면 오른쪽으로 넉백, -1이면 왼쪽으로 넉백)
    if attacker.x < defender.x:
        hit_from_dir = 1
    else:
        hit_from_dir = -1

    defender.take_hit(damage, hit_from_dir)

    # 공격 성공 시 SP 10 증가
    if hasattr(attacker, 'sp') and hasattr(attacker, 'max_sp'):
        attacker.sp += 10
        if attacker.sp > attacker.max_sp:
            attacker.sp = attacker.max_sp


# ------------- 초기화 -------------
def init():
    global background, player, enemy, ai, round_time

    try:
        background = load_image('Keroro_background.png')
        print("✅ Keroro_background.png 로드 완료")
    except:
        background = None
        print("⚠️ Keroro_background.png 를 찾지 못했습니다. 단색 배경 사용")

    # 1P 플레이어
    player_name = CHARACTERS[selected_character]
    player = create_fighter(player_name, is_left=True)
    print(f"✅ Player1 : {player_name}")

    # 2P 적 (플레이어와 다른 캐릭터 중 랜덤)
    enemy_candidates = [name for name in CHARACTERS if name != player_name]
    enemy_name = random.choice(enemy_candidates)
    enemy = create_fighter(enemy_name, is_left=False)
    print(f"✅ Enemy (AI) : {enemy_name}")

    # 적 AI (enemy가 움직이고 player를 목표로)
    ai = FighterAI(enemy, player)

    # 라운드 타이머
    round_time = 60.0

    # UI 초기화
    ui.init()
    print("✅ UI init 완료")


def finish():
    global background, player, enemy, ai
    background = None
    player = None
    enemy = None
    ai = None
    ui.finish()


# ------------- 매 프레임 업데이트 -------------
def update():
    global player, enemy, ai, background, round_time

    if player:
        player.update()
    if enemy:
        enemy.update()
    if ai:
        ai.update()

    # 스테이지 경계
    clamp_fighters()

    # 몸통 충돌 (서로 통과 X)
    resolve_body_collision()

    # 공격 판정 (양쪽 다 공격할 수 있으므로 둘 다 체크)
    if player and enemy:
        handle_attack(player, enemy)
        handle_attack(enemy, player)

    # 라운드 타이머 감소
    round_time -= game_framework.frame_time
    if round_time < 0:
        round_time = 0
        # TODO: 시간 끝났을 때 승패 처리 넣고 싶으면 여기서 처리


# ------------- 그리기 -------------
def draw():
    clear_canvas()

    # 배경
    if background:
        background.draw(W // 2, H // 2, W, H)
    else:
        set_clear_color(0.3, 0.3, 0.3, 1.0)
        clear_canvas()

    # 캐릭터
    if player:
        player.draw()
    if enemy:
        enemy.draw()

    # HP / SP / Timer UI
    if player and enemy:
        ui.draw(player, enemy, round_time)

    update_canvas()


# ------------- 입력 처리 -------------
def handle_events():
    global player
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
            game_framework.quit()

        # 플레이어 입력만 처리 (적은 AI)
        if player:
            player.handle_event(e)


def pause():
    pass


def resume():
    pass
