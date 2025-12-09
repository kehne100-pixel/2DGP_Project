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

# -------------------------------------------------
# 기본 화면 크기
# -------------------------------------------------
W, H = 1600, 900

# -------------------------------------------------
# 전역 객체들
# -------------------------------------------------
background = None
player = None
enemy = None
ai = None

selected_character = 0
CHARACTERS = ['Dororo', 'Tamama', 'Keroro', 'Giroro', 'Kururu']

# -------------------------------------------------
# UI 관련 전역 (체력/게이지/타이머)
# -------------------------------------------------
ui_hp_frame = None   # 검은 프레임
ui_hp_fill = None    # 빨간 HP 바
ui_sp_fill = None    # 파란 SP 바
ui_timer_bg = None   # 타이머 박스

digit_images = {}    # '0'~'9', ':' 이미지

ROUND_TIME = 60.0       # 60초
round_start_time = 0.0  # 시작 시각(초)

# ====== UI 위치/크기 조절용 상수 (여기만 바꾸면 됨) ======
UI_SCALE = 0.3          # HP/필살 프레임 전체 스케일
UI_TOP_MARGIN = 140     # 화면 위에서 얼마만큼 내려올지 (숫자 커질수록 아래로)

LEFT_HP_X = 260         # 왼쪽 HP 프레임 중심 X
RIGHT_HP_X = W - 260    # 오른쪽 HP 프레임 중심 X

TIMER_SCALE = 0.35      # 타이머 프레임 스케일
TIMER_Y = H - 120       # 타이머 중심 Y

TIMER_DIGIT_W = 34      # 타이머 숫자 폭
TIMER_DIGIT_H = 52      # 타이머 숫자 높이
TIMER_DIGIT_GAP = 4     # 숫자 사이 간격


def set_selected_index(index):
    global selected_character
    selected_character = index


# -------------------------------------------------
# 캐릭터 생성
# -------------------------------------------------
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

    # 양 끝에서 시작
    MARGIN_X = 200
    if is_left:
        c.x = MARGIN_X
        c.face_dir = 1
    else:
        c.x = W - MARGIN_X
        c.face_dir = -1

    c.dir = 0
    return c


# -------------------------------------------------
# 몸통 충돌 (서로 살짝 밀치기)
# -------------------------------------------------
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
        overlap = min_distance - distance
        push = overlap / 2.0
        if dx > 0:
            player.x -= push
            enemy.x += push
        else:
            player.x += push
            enemy.x -= push


# -------------------------------------------------
# 스테이지 한계 (월드 기준)
# -------------------------------------------------
def clamp_fighters():
    STAGE_LEFT = 60
    STAGE_RIGHT = W - 60

    if player:
        player.x = max(STAGE_LEFT, min(STAGE_RIGHT, player.x))
    if enemy:
        enemy.x = max(STAGE_LEFT, min(STAGE_RIGHT, enemy.x))


# -------------------------------------------------
# AABB 충돌 / 전투 판정
# -------------------------------------------------
def aabb_intersect(box1, box2):
    l1, b1, r1, t1 = box1
    l2, b2, r2, t2 = box2
    if r1 < l2:
        return False
    if r2 < l1:
        return False
    if t1 < b2:
        return False
    if t2 < b1:
        return False
    return True


def handle_combat(attacker, defender):
    """
    - attacker.get_attack_hitbox() 가 None 이 아니고
      defender.get_hurtbox() 와 겹치면
      defender.take_hit(damage, attacker.face_dir) 호출
    """
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
    if not aabb_intersect(hitbox, hurtbox):
        return

    # 공격 1번에 한 번만 맞도록 (캐릭터 쪽 flag)
    if hasattr(attacker, 'attack_hit_done') and attacker.attack_hit_done:
        return

    # --- 데미지/게이지 값 ---
    DAMAGE_ATTACK = 5
    DAMAGE_SKILL1 = 20
    DAMAGE_SKILL2 = 35
    DAMAGE_SKILL3 = 50

    SP_GAIN_ON_HIT = 10

    damage = DAMAGE_ATTACK

    cur_state = getattr(attacker.state_machine, 'cur_state', None)

    if cur_state is getattr(attacker, 'SKILL', None):
        damage = DAMAGE_SKILL1
    elif cur_state is getattr(attacker, 'SKILL2', None):
        damage = DAMAGE_SKILL2
    elif cur_state is getattr(attacker, 'SKILL3', None):
        damage = DAMAGE_SKILL3

    defender.take_hit(damage, attacker.face_dir)

    # 공격자 필살 게이지 증가
    if hasattr(attacker, 'sp') and hasattr(attacker, 'max_sp'):
        attacker.sp += SP_GAIN_ON_HIT
        if attacker.sp > attacker.max_sp:
            attacker.sp = attacker.max_sp

    if hasattr(attacker, 'attack_hit_done'):
        attacker.attack_hit_done = True


# -------------------------------------------------
# 타이머 보조 함수
# -------------------------------------------------
def get_remaining_time():
    """0~ROUND_TIME 초 사이 정수 반환"""
    global round_start_time
    elapsed = get_time() - round_start_time
    remain = ROUND_TIME - elapsed
    if remain < 0:
        remain = 0
    return int(remain)


# -------------------------------------------------
# 초기화
# -------------------------------------------------
def init():
    global background, player, enemy, ai
    global ui_hp_frame, ui_hp_fill, ui_sp_fill, ui_timer_bg
    global digit_images, round_start_time

    # 배경
    try:
        background = load_image('Keroro_background.png')
        print("✅ Keroro_background.png 로드 완료")
    except:
        print("⚠️ Keroro_background.png 를 찾지 못했습니다.")
        background = None

    # 캐릭터 생성
    player_name = CHARACTERS[selected_character]
    player = create_fighter(player_name, is_left=True)
    print(f"✅ Player1 : {player_name}")

    enemy_candidates = [n for n in CHARACTERS if n != player_name]
    enemy_name = random.choice(enemy_candidates)
    enemy = create_fighter(enemy_name, is_left=False)
    print(f"✅ Enemy (AI) : {enemy_name}")

    # AI
    ai = FighterAI(enemy, player)

    # 카메라
    camera.init()
    print("✅ Camera init 완료")

    # ----- UI 이미지 로드 -----
    try:
        ui_hp_frame = load_image('ui_hp_frame.png')
    except:
        ui_hp_frame = None
        print("⚠️ ui_hp_frame.png 로드 실패")

    try:
        ui_hp_fill = load_image('ui_hp_fill.png')
    except:
        ui_hp_fill = None
        print("⚠️ ui_hp_fill.png 로드 실패")

    try:
        ui_sp_fill = load_image('ui_sp_fill.png')
    except:
        ui_sp_fill = None
        print("⚠️ ui_sp_fill.png 로드 실패")

    try:
        ui_timer_bg = load_image('ui_timer.png')
    except:
        ui_timer_bg = None
        print("⚠️ ui_timer.png 로드 실패")

    # 숫자 이미지(0~9, :)
    digit_images = {}
    for ch in '0123456789':
        # timer0.png ~ timer9.png
        fname = f'timer{ch}.png'
        try:
            digit_images[ch] = load_image(fname)
        except:
            digit_images[ch] = None
            print(f"⚠️ {fname} 로드 실패")

    # 콜론 이미지 (timer_colon.png 를 만들어뒀다면 사용)
    try:
        digit_images[':'] = load_image('timer_colon.png')
    except:
        digit_images[':'] = None
        print("⚠️ timer_colon.png 로드 실패 (없으면 그냥 건너뜀)")

    # 라운드 타이머 시작 시각
    round_start_time = get_time()


def finish():
    global background, player, enemy, ai
    global ui_hp_frame, ui_hp_fill, ui_sp_fill, ui_timer_bg, digit_images
    background = None
    player = None
    enemy = None
    ai = None
    ui_hp_frame = None
    ui_hp_fill = None
    ui_sp_fill = None
    ui_timer_bg = None
    digit_images = {}


# -------------------------------------------------
# 매 프레임 업데이트
# -------------------------------------------------
def update():
    global player, enemy, ai, background

    if player:
        player.update()
    if enemy:
        enemy.update()
    if ai:
        ai.update()

    clamp_fighters()
    resolve_body_collision()

    if player and enemy:
        handle_combat(player, enemy)
        handle_combat(enemy, player)

    camera.update(player, enemy, background)


# -------------------------------------------------
# UI 그리기 (HP/SP)
# -------------------------------------------------
def draw_hp_sp_bar(fighter, side):
    global ui_hp_frame, ui_hp_fill, ui_sp_fill

    if fighter is None:
        return

    max_hp = getattr(fighter, 'max_hp', 100)
    hp     = getattr(fighter, 'hp', max_hp)
    max_sp = getattr(fighter, 'max_sp', 100)
    sp     = getattr(fighter, 'sp', 0)

    # 0.0 ~ 1.0 비율
    hp_ratio = 0.0 if max_hp <= 0 else max(0.0, min(1.0, hp / max_hp))
    sp_ratio = 0.0 if max_sp <= 0 else max(0.0, min(1.0, sp / max_sp))

    # ==========================
    # 위치 / 크기 설정 부분
    # ==========================
    frame_y  = H - 120   # 너무 위에 붙어 있으면 잘려보이니 살짝 더 내려줌
    frame_w  = 420       # HP 프레임 전체 가로
    frame_h  = 60        # HP 프레임 전체 세로 (회색 둥근 바 높이 느낌)

    # HP / SP 바의 최대 너비와 높이
    bar_w_max = 340      # 실제 HP/SP가 차는 최대 길이
    hp_h      = 26       # HP 붉은 바 두께
    sp_h      = 18       # SP 파란 바 두께

    # 프레임 중심을 기준으로 위/아래에 배치
    hp_y = frame_y + 6   # 프레임 중앙보다 살짝 위쪽
    sp_y = frame_y - 10  # 프레임 중앙보다 살짝 아래쪽

    if side == 'left':
        frame_x = 260          # 왼쪽 HP UI 중심 x (필요하면 숫자 조금씩 조정)

        # --- 프레임(검정/회색 바) ---
        if ui_hp_frame:
            ui_hp_frame.clip_draw(
                ui_hp_frame.w // 2, ui_hp_frame.h // 2,
                ui_hp_frame.w, ui_hp_frame.h,
                frame_x, frame_y,
                frame_w, frame_h
            )

        # --- HP 붉은 바 (처음엔 가득 / 깎이면 양 끝이 남고 검정이 보임) ---
        if ui_hp_fill and hp_ratio > 0.0:
            w  = int(bar_w_max * hp_ratio)
            cx = frame_x - bar_w_max / 2 + w / 2
            ui_hp_fill.clip_draw(
                ui_hp_fill.w // 2, ui_hp_fill.h // 2,
                ui_hp_fill.w, ui_hp_fill.h,
                int(cx), hp_y,
                w, hp_h
            )

        # --- SP 파란 바 (처음엔 0 → 공격 성공할수록 채워짐) ---
        if ui_sp_fill and sp_ratio > 0.0:
            w  = int(bar_w_max * sp_ratio)
            cx = frame_x - bar_w_max / 2 + w / 2
            ui_sp_fill.clip_draw(
                ui_sp_fill.w // 2, ui_sp_fill.h // 2,
                ui_sp_fill.w, ui_sp_fill.h,
                int(cx), sp_y,
                w, sp_h
            )

    else:  # right side (적 HP)
        frame_x = W - 260       # 오른쪽 HP UI 중심 x

        # --- 프레임 (좌우 반전) ---
        if ui_hp_frame:
            ui_hp_frame.clip_composite_draw(
                ui_hp_frame.w // 2, ui_hp_frame.h // 2,
                ui_hp_frame.w, ui_hp_frame.h,
                0, 'h',
                frame_x, frame_y,
                frame_w, frame_h
            )

        # --- HP 붉은 바 (오른쪽에서 왼쪽으로 줄어들도록 반전) ---
        if ui_hp_fill and hp_ratio > 0.0:
            w  = int(bar_w_max * hp_ratio)
            cx = frame_x + bar_w_max / 2 - w / 2
            ui_hp_fill.clip_composite_draw(
                ui_hp_fill.w // 2, ui_hp_fill.h // 2,
                ui_hp_fill.w, ui_hp_fill.h,
                0, 'h',
                int(cx), hp_y,
                w, hp_h
            )

        # --- SP 파란 바 ---
        if ui_sp_fill and sp_ratio > 0.0:
            w  = int(bar_w_max * sp_ratio)
            cx = frame_x + bar_w_max / 2 - w / 2
            ui_sp_fill.clip_composite_draw(
                ui_sp_fill.w // 2, ui_sp_fill.h // 2,
                ui_sp_fill.w, ui_sp_fill.h,
                0, 'h',
                int(cx), sp_y,
                w, sp_h
            )




def draw_timer_ui():
    global ui_timer_bg, digit_images

    if not ui_timer_bg:
        return

    cx = W // 2 + 15
    cy = TIMER_Y

    # ---- 타이머 프레임 크기 ----
    src_w, src_h = ui_timer_bg.w, ui_timer_bg.h
    dest_w = int(src_w * TIMER_SCALE)
    dest_h = int(src_h * TIMER_SCALE)

    # 타이머 배경
    ui_timer_bg.draw(cx, cy, dest_w, dest_h)

    # 남은 시간 -> "MM:SS" 문자열
    remain = get_remaining_time()
    mm = remain // 60
    ss = remain % 60
    text = f"{mm:02}:{ss:02}"   # 예: "01:40"

    digit_w = TIMER_DIGIT_W
    digit_h = TIMER_DIGIT_H
    gap = TIMER_DIGIT_GAP

    total_width = len(text) * (digit_w + gap) - gap
    start_x = cx - total_width / 2
    base_y = cy - 8   # 박스 안의 y 위치

    for ch in text:
        img = digit_images.get(ch, None)
        if img:
            img.draw(int(start_x + digit_w / 2), base_y, digit_w, digit_h)
        start_x += (digit_w + gap)


# -------------------------------------------------
# 그리기
# -------------------------------------------------
def draw():
    clear_canvas()

    zoom = camera.get_zoom()
    cx, cy = camera.get_center()

    # ----- 배경 (카메라/줌 반영) -----
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

    # ----- 캐릭터 -----
    if player:
        player.draw()
    if enemy:
        enemy.draw()

    # ----- UI (HP/SP + 타이머) -----
    draw_hp_sp_bar(player, 'left')
    draw_hp_sp_bar(enemy, 'right')
    draw_timer_ui()

    update_canvas()


# -------------------------------------------------
# 입력 처리
# -------------------------------------------------
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
