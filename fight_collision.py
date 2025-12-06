# fight_collision.py
from pico2d import draw_rectangle

DEBUG_COLLISION = True  # 디버그용 박스 보고 싶지 않으면 False 로


def aabb_collide(bb1, bb2):
    if bb1 is None or bb2 is None:
        return False

    left_a, bottom_a, right_a, top_a = bb1
    left_b, bottom_b, right_b, top_b = bb2

    if left_a > right_b:  return False
    if right_a < left_b:  return False
    if top_a < bottom_b:  return False
    if bottom_a > top_b:  return False
    return True


def draw_bb(bb):
    if bb is None:
        return
    left, bottom, right, top = bb
    draw_rectangle(left, bottom, right, top)


def handle_fight_collision(player, enemy):


    # 1) 플레이어의 공격이 적 몸에 맞았는지
    p_hit_bb = player.get_attack_bb()   # 공격 판정 박스
    e_body_bb = enemy.get_body_bb()    # 적 몸통 박스


