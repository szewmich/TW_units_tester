import numpy as np
import math


LD_penalty_perm_hp_loss = {
      0:   0,
     10:  -2,
     20:  -4,
     30:  -7,
     40:  -11,
     50:  -16,
     60:  -22,
     70:  -32,
     80:  -47,
     90:  -74,
    100: -101
}


# BACKUP
LD_penalty_60sec_hp_loss = {
      0:   0,
     10:  -4,
     15:  -6,
     33:  -14,
     50:  -32,
     80:  -60,
    100: -101
}

LD_penalty_4sec_hp_loss = {
      0:   0,
      6:  -6,
     10: -12,
     15: -20,
     33: -44,
     50: -80,
    100: -99
}

# LD_modifier_net_hp_perc_trade = {
#     -100:   -8,
#      -40:   -3,
#      -20:    0,
#        5:    3,
#       10:    6,
#       30:    8
# }

LD_modifier_net_hp_perc_trade = {
    -100:   -8,
     -40:   -3,
     -5 :    0,
      10:    3,
      20:    6,
      30:    8
}

def get_shatter_perc_hp(LD):
    """Calculate the hp at which unit shatters permenently, based on its base LD and hp. Interpolate between thresholds"""
    hp_thresholds = list(LD_penalty_perm_hp_loss.keys())
    LD_thresholds = list(LD_penalty_perm_hp_loss.values())
    for k in range(10):
        if -LD_thresholds[k] < LD and -LD_thresholds[k+1] > LD:
            floor = -LD_thresholds[k]
            ceil = -LD_thresholds[k+1]

            perc_loss = hp_thresholds[k] + 10* (LD-floor) / (ceil-floor)
            break
    
    return round(1 - perc_loss/100, 3)


def get_hp_loss_perm_LD_penalty(damage_history, base_hp):
    dmg_tot = np.sum(list(damage_history.values()))
    hp_perc_loss_total = round(dmg_tot / base_hp * 100, 1)
    hp_perc_loss_total_threshold = max([k for k in LD_penalty_perm_hp_loss.keys() if k <= hp_perc_loss_total])
    hp_loss_perm_LD_penalty = LD_penalty_perm_hp_loss [hp_perc_loss_total_threshold]

    return hp_loss_perm_LD_penalty


def get_hp_loss_60sec_LD_penalty(damage_history, base_hp):
    time_60sec_ago = max(damage_history.keys()) - 60
    damage_history_60sec = {time: dmg for time, dmg in damage_history.items() if time > time_60sec_ago}

    dmg_60sec = np.sum(list(damage_history_60sec.values()))
    hp_perc_loss_60sec = round(dmg_60sec / base_hp * 100, 1)
    hp_loss_60sec_threshold = max([k for k in LD_penalty_60sec_hp_loss.keys() if k <= hp_perc_loss_60sec])
    hp_loss_60sec_LD_penalty = LD_penalty_60sec_hp_loss [hp_loss_60sec_threshold]

    return hp_loss_60sec_LD_penalty, hp_perc_loss_60sec

def get_hp_loss_4sec_LD_penalty(damage_history, base_hp):
    times = list(damage_history.keys())
    damages = list(damage_history.values())
    if len(times) > 1:
        last_time_interval = times[-1] - times[-2]
    else:
        # last_time_interval = times[0]
        # First registred damage interval after charge - do not consider this penalty because damage was not dealt proprtionally in time (most of it was done upon charge collison)
        return 0, 0
    
    dmg_last_interval = damages[-1]


    hp_perc_loss_4sec = round(4 / last_time_interval * dmg_last_interval / base_hp * 100, 1)
    hp_loss_4sec_threshold = max([k for k in LD_penalty_4sec_hp_loss.keys() if k <= hp_perc_loss_4sec])
    hp_loss_4sec_LD_penalty = LD_penalty_4sec_hp_loss [hp_loss_4sec_threshold]

    return hp_loss_4sec_LD_penalty, hp_perc_loss_4sec


def get_penalty_for_stronger_enemy (A, B):
    A_left_hp_perc = (A.hp - A.CD) / A.hp
    B_left_hp_perc = (B.hp - B.CD) / B.hp

    factor = max(A_left_hp_perc / B_left_hp_perc, B_left_hp_perc / A_left_hp_perc)

    if factor >= 1.3:
        penalty = -math.floor(factor / 0.4)
    else: 
        return 0, 0
    
    if A_left_hp_perc > B_left_hp_perc:
        A_penalty = 0
        B_penalty = penalty
    else:
        A_penalty = penalty
        B_penalty = 0
    
    return A_penalty, B_penalty



def update_LD(A, B, A_damage_history, B_damage_history, A_total_LD_bonus, B_total_LD_bonus, extended_output = False):
    A_base_LD = A.LD
    A_base_hp = A.hp

    A_hp_loss_perm_LD_penalty = get_hp_loss_perm_LD_penalty(A_damage_history, A_base_hp)
    A_hp_loss_60sec_LD_penalty, A_hp_perc_loss_60sec = get_hp_loss_60sec_LD_penalty(A_damage_history, A_base_hp)
    A_hp_loss_4sec_LD_penalty, A_hp_perc_loss_4sec = get_hp_loss_4sec_LD_penalty(A_damage_history, A_base_hp)

    A_fear_LD_penalty = 0
    if B.fear == True and A.fear == False:
        if A.itp == False and "frenzy" not in A.active_effects:
            A_fear_LD_penalty = -8

    B_base_LD = B.LD
    B_base_hp = B.hp

    B_hp_loss_perm_LD_penalty = get_hp_loss_perm_LD_penalty(B_damage_history, B_base_hp)
    B_hp_loss_60sec_LD_penalty, B_hp_perc_loss_60sec = get_hp_loss_60sec_LD_penalty(B_damage_history, B_base_hp)
    B_hp_loss_4sec_LD_penalty, B_hp_perc_loss_4sec = get_hp_loss_4sec_LD_penalty(B_damage_history, B_base_hp)

    B_fear_LD_penalty = 0
    if A.fear == True and B.fear == False:
        if B.itp == False and "frenzy" not in B.active_effects:
            B_fear_LD_penalty = -8

    A_net_perc_hp_trade = B_hp_perc_loss_60sec - A_hp_perc_loss_60sec
    B_net_perc_hp_trade = - A_net_perc_hp_trade

    A_hp_trade_threshold = max([k for k in LD_modifier_net_hp_perc_trade.keys() if k <= A_net_perc_hp_trade])
    A_hp_trade_LD_modifier = LD_modifier_net_hp_perc_trade [A_hp_trade_threshold]
    B_hp_trade_threshold = max([k for k in LD_modifier_net_hp_perc_trade.keys() if k <= B_net_perc_hp_trade])
    B_hp_trade_LD_modifier = LD_modifier_net_hp_perc_trade [B_hp_trade_threshold]

    A_stronger_enemy_penalty, B_stronger_enemy_penalty = get_penalty_for_stronger_enemy (A, B)

    A_LD_penalty_sum = A_hp_loss_perm_LD_penalty + A_hp_loss_60sec_LD_penalty + A_hp_loss_4sec_LD_penalty + A_fear_LD_penalty + A_stronger_enemy_penalty
    B_LD_penalty_sum = B_hp_loss_perm_LD_penalty + B_hp_loss_60sec_LD_penalty + B_hp_loss_4sec_LD_penalty + B_fear_LD_penalty + B_stronger_enemy_penalty

    A_updated_LD = A_base_LD + A_total_LD_bonus + A_LD_penalty_sum + A_hp_trade_LD_modifier
    B_updated_LD = B_base_LD + B_total_LD_bonus + B_LD_penalty_sum + B_hp_trade_LD_modifier

    if A_updated_LD < 0 or B_updated_LD < 0:
        pass

    if extended_output == True:
        return A_updated_LD, A_hp_loss_perm_LD_penalty + A_hp_loss_60sec_LD_penalty, A_stronger_enemy_penalty, A_hp_trade_LD_modifier, B_updated_LD, B_hp_loss_perm_LD_penalty + B_hp_loss_60sec_LD_penalty, B_stronger_enemy_penalty, B_hp_trade_LD_modifier

    return A_updated_LD, B_updated_LD


    



