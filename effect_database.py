def create_bonuses_dict ():
    b_dic = {
        "MA": 0,
        "MD": 0,
        "armour": 0,
        "dmg_base": 0,
        "dmg_ap": 0,
        "CB": 0,
        "ammo": 0,
        "missile_dmg_base": 0,
        "missile_dmg_ap": 0,
        "MBC": 0
    }
    return b_dic


class encouraged:
    def __init__(self, name):
        self.name = name

    def condition(unit):
        if unit.CD / unit.hp < 0.5:
            return True
        else:
            return False

    def get_bonuses(unit):
        bonuses = create_bonuses_dict()
        bonuses['MA'] = 2
        bonuses['dmg_base'] = 0.1 * unit.dmg_base
        bonuses['dmg_ap'] = 0.1 * unit.dmg_ap
        bonuses['CB'] = 0.1 * unit.CB
        return bonuses

class army_boost:
    def __init__(self, MA_perc, MD_perc, ammo_perc, missile_dmg_base_perc, missile_dmg_ap_perc, MBC_perc):
        self.MA_perc = MA_perc
        self.MD_perc = MD_perc
        self.ammo_perc = ammo_perc
        self.missile_dmg_base_perc = missile_dmg_base_perc
        self.missile_dmg_ap_perc = missile_dmg_ap_perc
        self.MBC_perc = MBC_perc

    def condition(unit):
            return True

    def get_bonuses(self, unit):
        bonuses = create_bonuses_dict()
        bonuses['MA'] = self.MA_perc / 100 * unit.MA
        bonuses['MD'] = self.MD_perc / 100 * unit.MD
        bonuses['ammo'] = self.ammo_perc / 100 * unit.ammo
        bonuses['missile_dmg_base'] = self.missile_dmg_base_perc / 100 * unit.missile_dmg_base
        bonuses['missile_dmg_ap'] = self.missile_dmg_ap_perc / 100 * unit.missile_dmg_ap
        bonuses['MBC'] = self.MBC_perc / 100 * unit.MBC
        return bonuses


def frenzy_condition (hp_base,CD):
    if CD < hp_base/2:
        return True
    else:
        return False

def str_in_numbers_condition (hp_base,CD):
    if CD < hp_base/2:
        return True
    else:
        return False

def cloud_of_flies_condition(hp_base, CD):
    return True

def frenzy_available (curr):
    if curr.perks:
        if 'frenzy' in curr.perks:
            return True
        else:
            return False
    else:
        return False

def str_in_numbers_available (curr):
    if curr.perks:
        if 'str_in_numbers' in curr.perks:
            return True
        else:
            return False
    else:
        return False



def frenzy_bonus (MA,MD, armour, dmg_base, dmg_ap, CB):
    bonuses = create_bonuses_dict()
    bonuses ['MA'] = 10
    bonuses ['dmg_base'] = 0.1 * dmg_base
    bonuses ['dmg_ap'] = 0.1 * dmg_ap
    bonuses['CB'] = 0.1 * CB
    return bonuses

def str_in_numbers_bonus (MA,MD, armour, dmg_base, dmg_ap, CB):
    bonuses = create_bonuses_dict()
    bonuses ['MD'] = 8
    return bonuses

def cloud_of_flies_bonus (MA,MD, armour, dmg_base, dmg_ap, CB):
    bonuses = create_bonuses_dict()
    bonuses ['MD'] = 9
    return bonuses

def korozja_condition (hp_base,CD):
    if CD > hp_base*0.2:
        return True
    else:
        return False

def korozja_bonus (MA, MD, armour, dmg_base, dmg_ap, CB):
    bonuses = create_bonuses_dict()
    bonuses['armour'] = -50
    return bonuses