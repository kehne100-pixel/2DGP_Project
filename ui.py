# ui.py
from pico2d import *

# -----------------------
# 화면 크기 (play_mode와 맞추기)
# -----------------------
W, H = 1600, 900

# -----------------------
# 이미지 / 폰트 전역 변수
# -----------------------
hp_frame_img_p1 = None
hp_frame_img_p2 = None
sp_frame_img_p1 = None
sp_frame_img_p2 = None
timer_frame_img = None

# HP / SP 채워지는 바(단색 이미지 1장씩)
hp_fill_img = None
sp_fill_img = None

ui_font = None   # 타이머 / 숫자용


def init():
    global hp_frame_img_p1, hp_frame_img_p2
    global sp_frame_img_p1, sp_frame_img_p2
    global timer_frame_img
    global hp_fill_img, sp_fill_img
    global ui_font

    # ------------- 여기서부터 네가 가진 일러스트 파일 이름으로 바꿔주면 됨 -------------

    # 예시) 왼쪽 HP 프레임, 오른쪽 HP 프레임
    try:
        hp_frame_img_p1 = load_image('ui_hp_frame_p1.png')   # 왼쪽 HP UI 일러스트
        hp_frame_img_p2 = load_image('ui_hp_frame_p2.png')   # 오른쪽 HP UI 일러스트
    except:
        hp_frame_img_p1 = None
        hp_frame_img_p2 = None
        print('[UI] HP 프레임 이미지를 찾지 못했습니다.')

    # 예시) 왼쪽 SP(필살게이지) 프레임, 오른쪽 SP 프레임
    try:
        sp_frame_img_p1 = load_image('ui_sp_frame_p1.png')
        sp_frame_img_p2 = load_image('ui_sp_frame_p2.png')
    except:
        sp_frame_img_p1 = None
        sp_frame_img_p2 = None
        print('[UI] SP 프레임 이미지를 찾지 못했습니다.')

    # 예시) 타이머 배경 일러스트
    try:
        timer_frame_img = load_image('ui_timer_frame.png')
    except:
        timer_frame_img = None
        print('[UI] 타이머 프레임 이미지를 찾지 못했습니다.')

    # HP / SP 채워지는 바 (가로로 긴 단색 이미지 한 장씩)
    # 없으면 나중에 포토샵으로 200x20짜리 빨간색/파란색 바 하나씩 만들어도 됨.
    try:
        hp_fill_img = load_image('ui_hp_fill.png')   # 빨간/노란 HP 바 일러스트
    except:
        hp_fill_img = None
        print('[UI] hp_fill_img 없어서 기본 사각형으로 대체합니다.')

    try:
        sp_fill_img = load_image('ui_sp_fill.png')   # 파란/초록 게이지 바 일러스트
    except:
        sp_fill_img = None
        print('[UI] sp_fill_img 없어서 기본 사각형으로 대체합니다.')

    # 폰트 (프로젝트에 있는 TTF 파일 사용)
    try:
        ui_font = load_font('ENCR10B.TTF', 40)  # 없으면 폰트 파일 이름 맞춰서 변경
    except:
        ui_font = None
        print('[UI] 폰트를 찾지 못했습니다.')


def finish():
    # 굳이 del 안 해도 되지만, 깔끔하게 마무리용
    global hp_frame_img_p1, hp_frame_img_p2
    global sp_frame_img_p1, sp_frame_img_p2
    global timer_frame_img
    global hp_fill_img, sp_fill_img
    global ui_font

    hp_frame_img_p1 = None
    hp_frame_img_p2 = None
    sp_frame_img_p1 = None
    sp_frame_img_p2 = None
    timer_frame_img = None
    hp_fill_img = None
    sp_fill_img = None
    ui_font = None


# -----------------------
# 내부 유틸 (채워진 바 그리기)
# -----------------------
def _draw_bar_fill(img, x_left, y_center, width, height, ratio, flip=False, color=(255, 0, 0)):
    ratio = max(0.0, min(1.0, ratio))
    dst_w = int(width * ratio)
    if dst_w <= 0:
        return

    if img:
        iw, ih = img.w, img.h

        # ✅ 소스에서 자를 폭은 "이미지 폭 기준"
        src_w = int(iw * ratio)
        if src_w <= 0:
            return

        if not flip:
            # 왼쪽 -> 오른쪽
            img.clip_draw(
                0, 0,
                src_w, ih,
                x_left + dst_w / 2, y_center,
                dst_w, height
            )
        else:
            # 오른쪽 -> 왼쪽
            sx = iw - src_w
            img.clip_draw(
                sx, 0,
                src_w, ih,
                x_left + (width - dst_w / 2), y_center,
                dst_w, height
            )
    else:
        r, g, b = color
        draw_rectangle(x_left, y_center - height / 2,
                       x_left + dst_w, y_center + height / 2)



# -----------------------
# 실제 UI 그리기
# -----------------------
def draw(player, enemy, time_left):
    """
    player / enemy : 캐릭터 객체 (hp, max_hp, sp, max_sp가 있다고 가정)
    time_left      : 남은 시간 (초)
    """

    # --------- 위치/크기 설정 (여기서 마음에 들 때까지 조정) ---------
    # HP 바 위치/크기
    hp_bar_width  = 400
    hp_bar_height = 24

    # P1 HP : 왼쪽 위 (x 기준)
    p1_hp_x = 200
    p1_hp_y = H - 60

    # P2 HP : 오른쪽 위
    p2_hp_x = W - 200 - hp_bar_width  # 오른쪽에서 hp_bar_width만큼 왼쪽
    p2_hp_y = H - 60

    # SP(필살게이지) 위치 (HP아래)
    sp_bar_width  = 300
    sp_bar_height = 18

    p1_sp_x = 200
    p1_sp_y = H - 90

    p2_sp_x = W - 200 - sp_bar_width
    p2_sp_y = H - 90

    # 타이머 위치
    timer_x = W // 2
    timer_y = H - 55

    # --------- 프레임(일러스트) 먼저 깔기 ---------
    # HP 프레임
    if hp_frame_img_p1:
        hp_frame_img_p1.draw(p1_hp_x + hp_bar_width / 2, p1_hp_y, hp_bar_width, 60)
    if hp_frame_img_p2:
        hp_frame_img_p2.draw(p2_hp_x + hp_bar_width / 2, p2_hp_y, hp_bar_width, 60)

    # SP 프레임
    if sp_frame_img_p1:
        sp_frame_img_p1.draw(p1_sp_x + sp_bar_width / 2, p1_sp_y, sp_bar_width, 40)
    if sp_frame_img_p2:
        sp_frame_img_p2.draw(p2_sp_x + sp_bar_width / 2, p2_sp_y, sp_bar_width, 40)

    # 타이머 프레임
    if timer_frame_img:
        timer_frame_img.draw(timer_x, timer_y, 160, 60)

    # --------- HP / SP 값 비율 계산 ---------
    # 방어 코드: hp, max_hp가 없는 캐릭터여도 터지지 않게
    if hasattr(player, 'hp') and hasattr(player, 'max_hp') and player.max_hp > 0:
        p1_hp_ratio = player.hp / player.max_hp
    else:
        p1_hp_ratio = 1.0

    if hasattr(enemy, 'hp') and hasattr(enemy, 'max_hp') and enemy.max_hp > 0:
        p2_hp_ratio = enemy.hp / enemy.max_hp
    else:
        p2_hp_ratio = 1.0

    if hasattr(player, 'sp') and hasattr(player, 'max_sp') and player.max_sp > 0:
        p1_sp_ratio = player.sp / player.max_sp
    else:
        p1_sp_ratio = 0.0

    if hasattr(enemy, 'sp') and hasattr(enemy, 'max_sp') and enemy.max_sp > 0:
        p2_sp_ratio = enemy.sp / enemy.max_sp
    else:
        p2_sp_ratio = 0.0

    # --------- HP 채우기 (왼쪽→오른쪽 / 오른쪽→왼쪽) ---------
    _draw_bar_fill(hp_fill_img, p1_hp_x, p1_hp_y, hp_bar_width, hp_bar_height,
                   p1_hp_ratio, flip=False, color=(255, 0, 0))

    _draw_bar_fill(hp_fill_img, p2_hp_x, p2_hp_y, hp_bar_width, hp_bar_height,
                   p2_hp_ratio, flip=True, color=(255, 0, 0))

    # --------- SP(필살게이지) 채우기 ---------
    _draw_bar_fill(sp_fill_img, p1_sp_x, p1_sp_y, sp_bar_width, sp_bar_height,
                   p1_sp_ratio, flip=False, color=(0, 0, 255))

    _draw_bar_fill(sp_fill_img, p2_sp_x, p2_sp_y, sp_bar_width, sp_bar_height,
                   p2_sp_ratio, flip=True, color=(0, 0, 255))

    # --------- 타이머 숫자 표시 ---------
    if ui_font:
        sec = int(time_left)
        if sec < 0:
            sec = 0
        # 가운데 약간 위/아래로 위치 조정하고 싶으면 y값 조절
        text = f'{sec:02d}'
        # 글자는 프레임보다 살짝 위에 올리거나 중앙에 오게 조정 가능
        ui_font.draw(timer_x - 20, timer_y - 15, text, (255, 255, 255))
