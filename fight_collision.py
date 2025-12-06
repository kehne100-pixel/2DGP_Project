# fight_collision.py
from pico2d import draw_rectangle


DEBUG_COLLISION = True


def aabb_collide(bb1, bb2):

    if bb1 is None or bb2 is None:
        return False

    l1, b1, r1, t1 = bb1
    l2, b2, r2, t2 = bb2

    if l1 > r2: return False
    if r1 < l2: return False
    if t1 < b2: return False
    if b1 > t2: return False
    return True


def draw_bb(bb):

    if bb is None:
        return
    l, b, r, t = bb
    draw_rectangle(l, b, r, t)


def resolve_body_block(a, b):

    bb_a = a.get_body_bb()
    bb_b = b.get_body_bb()
    if not aabb_collide(bb_a, bb_b):
        return

    # 이번 프레임에 얼마나 움직였는지
    da = abs(a.x - getattr(a, 'prev_x', a.x))
    db = abs(b.x - getattr(b, 'prev_x', b.x))

    # 더 많이 움직인 쪽을 이전 위치로 되돌려서 '막힌 느낌'을 줌
    if da >= db:
        a.x = getattr(a, 'prev_x', a.x)
    else:
        b.x = getattr(b, 'prev_x', b.x)


def handle_fight_collision(player, enemy):

    # 1) 플레이어의 공격 히트박스 vs 적 몸통
    p_atk_bb = player.get_attack_bb()
    e_body_bb = enemy.get_body_bb()
    if aabb_collide(p_atk_bb, e_body_bb):
        dmg = player.get_attack_damage()
        if dmg > 0:
            enemy.take_damage(dmg)

    # 2) 적의 공격 히트박스 vs 플레이어 몸통
    e_atk_bb = enemy.get_attack_bb()
    p_body_bb = player.get_body_bb()
    if aabb_collide(e_atk_bb, p_body_bb):
        dmg = enemy.get_attack_damage()
        if dmg > 0:
            player.take_damage(dmg)

    # 3) 몸통끼리 겹치면 서로 통과 못하게
    resolve_body_block(player, enemy)
