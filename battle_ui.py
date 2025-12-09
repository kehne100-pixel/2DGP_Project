# battle_ui.py
from pico2d import *
import game_framework

# 화면 크기 (play_mode와 맞춤)
W, H = 1600, 900


class BattleUI:
    def __init__(self):
        # 60초 타이머
        self.time_limit = 60.0
        self.time_left = self.time_limit

        # 폰트 (2DGP 기본 폰트 사용 – 파일 이름은 상황에 맞게 바꿔도 됨)
        try:
            self.font = load_font('ENCR10B.TTF', 40)
        except:
            self.font = None
            print('⚠️ ENCR10B.TTF 를 찾지 못했습니다. 타이머 글자만 안 보일 수 있어요.')

        # HP/게이지 바 위치 & 크기
        self.bar_width = 320
        self.hp_height = 18
        self.sp_height = 10

        self.left_bar_x = 120
        self.right_bar_x = W - 120 - self.bar_width
        self.bar_y = H - 80      # HP 바의 아래 y
        self.gap_y = 4           # HP와 게이지 사이 간격

    # --------------------------
    # 타이머
    # --------------------------
    def reset_timer(self):
        self.time_left = self.time_limit

    def update(self):
        if self.time_left > 0:
            self.time_left -= game_framework.frame_time
            if self.time_left < 0:
                self.time_left = 0

    # --------------------------
    # 바 그리기 유틸
    # --------------------------
    def _draw_bar(self, x, y, w, h, ratio, left_to_right=True):
        """
        x, y : 왼쪽 아래 기준
        ratio : 0.0 ~ 1.0
        left_to_right=False 이면 오른쪽에서 왼쪽으로 줄어듦
        """
        ratio = max(0.0, min(1.0, ratio))

        # 바 테두리
        draw_rectangle(x, y, x + w, y + h)

        if ratio <= 0:
            return

        # 찬 부분
        if left_to_right:
            fx1 = x
            fx2 = x + w * ratio
        else:
            fx1 = x + w * (1.0 - ratio)
            fx2 = x + w

        # 채워진 것처럼 보이도록 가느다란 직사각형 여러 줄로 그림
        fy1 = y + 1
        fy2 = y + h - 1
        yy = fy1
        while yy < fy2:
            draw_rectangle(fx1, yy, fx2, yy + 1)
            yy += 2

    # --------------------------
    # 실제 그리기
    # --------------------------
    def draw(self, p1, p2):
        # p1, p2 가 None 이면 그리지 않음
        if p1 is None or p2 is None:
            return

        # -------- 타이머 --------
        if self.font:
            total_sec = int(self.time_left)
            mm = total_sec // 60
            ss = total_sec % 60
            time_str = f'{mm:02d}:{ss:02d}'

            # 가운데 위치
            self.font.draw(W // 2 - 50, H - 70, time_str, (255, 255, 0))

        # -------- HP / 게이지 값 읽기 --------
        # 각 캐릭터 클래스에 hp, max_hp, sp, max_sp 가 있다고 가정.
        # 없으면 기본값으로 100 사용.
        p1_hp = float(getattr(p1, 'hp', 100))
        p1_max_hp = float(getattr(p1, 'max_hp', 100))
        p1_sp = float(getattr(p1, 'sp', 0))
        p1_max_sp = float(getattr(p1, 'max_sp', 100))

        p2_hp = float(getattr(p2, 'hp', 100))
        p2_max_hp = float(getattr(p2, 'max_hp', 100))
        p2_sp = float(getattr(p2, 'sp', 0))
        p2_max_sp = float(getattr(p2, 'max_sp', 100))

        # 0 으로 나누기 방지
        if p1_max_hp <= 0: p1_max_hp = 1
        if p2_max_hp <= 0: p2_max_hp = 1
        if p1_max_sp <= 0: p1_max_sp = 1
        if p2_max_sp <= 0: p2_max_sp = 1

        p1_hp_ratio = p1_hp / p1_max_hp
        p2_hp_ratio = p2_hp / p2_max_hp
        p1_sp_ratio = p1_sp / p1_max_sp
        p2_sp_ratio = p2_sp / p2_max_sp

        # -------- 왼쪽(플레이어1) UI --------
        hp_y1 = self.bar_y
        sp_y1 = self.bar_y - self.hp_height - self.gap_y

        # HP 바 (왼→오)
        self._draw_bar(self.left_bar_x, hp_y1,
                       self.bar_width, self.hp_height,
                       p1_hp_ratio, left_to_right=True)
        # 필살 게이지 (왼→오)
        self._draw_bar(self.left_bar_x, sp_y1,
                       self.bar_width, self.sp_height,
                       p1_sp_ratio, left_to_right=True)

        # -------- 오른쪽(플레이어2) UI --------
        hp_y2 = hp_y1
        sp_y2 = sp_y1

        # HP 바 (오→왼)
        self._draw_bar(self.right_bar_x, hp_y2,
                       self.bar_width, self.hp_height,
                       p2_hp_ratio, left_to_right=False)
        # 필살 게이지 (오→왼)
        self._draw_bar(self.right_bar_x, sp_y2,
                       self.bar_width, self.sp_height,
                       p2_sp_ratio, left_to_right=False)
