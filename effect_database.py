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
        "MBC": 0,
        "LD": 0,
        "phys_res": 0
    }
    return b_dic


class encourages:
    def __init__(self, name):
        self.name = name

    def condition(unit):
        return True

    def get_bonuses(unit):
        bonuses = create_bonuses_dict()
        bonuses['LD'] = 8
        return bonuses
    
class frenzy:
    def __init__(self, name):
        self.name = name

    def condition(unit):
        if unit.LD_current / unit.LD > 0.5:
            return True
        else:
            return False

    def get_bonuses(unit):
        bonuses = create_bonuses_dict()
        bonuses['MA'] = 10
        bonuses['dmg_base'] = 0.1 * unit.dmg_base
        bonuses['dmg_ap'] = 0.1 * unit.dmg_ap
        bonuses['CB'] = 0.1 * unit.CB
        return bonuses
    
# class encouraged:
#     def __init__(self, name):
#         self.name = name

#     def condition(unit):
#         if unit.CD / unit.hp < 0.5:
#             return True
#         else:
#             return False

#     def get_bonuses(unit):
#         bonuses = create_bonuses_dict()
#         bonuses['MA'] = 2
#         bonuses['dmg_base'] = 0.1 * unit.dmg_base
#         bonuses['dmg_ap'] = 0.1 * unit.dmg_ap
#         bonuses['CB'] = 0.1 * unit.CB
#         bonuses['LD'] = 8
#         return bonuses
    

class primal_instincts:
    def __init__(self, name):
        self.name = name

    def condition(unit):
        if unit.CD / unit.hp > 0.5:
            return True
        else:
            return False

    def get_bonuses(unit):
        bonuses = create_bonuses_dict()
        bonuses['MA'] = 5
        bonuses['CB'] = 0.15 * unit.CB
        bonuses['phys_res'] = 0.05
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


class fatigue:
    def __init__(self, name):
        self.name = name

    def get_penalties(unit):
        bonuses = create_bonuses_dict()

        if unit.fatigue_pts >= 27_000:
            state = "Exhausted"
            bonuses['MA'] = - 0.30 * unit.MA
            bonuses['MD'] = - 0.10 * unit.MD
            bonuses['dmg_ap'] = - 0.10 * unit.dmg_ap
            bonuses['CB'] = 0.30 * unit.CB
            bonuses['armour'] = - 0.25 * unit.armour
            bonuses['LD'] = - 6
            return bonuses, state
        
        if unit.fatigue_pts >= 18_000:
            state = "Very tired"
            bonuses['MA'] = - 0.25 * unit.MA
            bonuses['dmg_ap'] = - 0.10 * unit.dmg_ap
            bonuses['CB'] = 0.25 * unit.CB
            bonuses['armour'] = - 0.10 * unit.armour
            bonuses['LD'] = - 2
            return bonuses, state
        
        if unit.fatigue_pts >= 12_600:
            state = "Tired"
            bonuses['MA'] = - 0.15 * unit.MA
            bonuses['dmg_ap'] = - 0.10 * unit.dmg_ap
            bonuses['CB'] = 0.1 * unit.CB
            return bonuses, state
        
        if unit.fatigue_pts >= 6_600:
            state = "Winded"
            bonuses['MA'] = - 0.05 * unit.MA
            bonuses['dmg_ap'] = - 0.10 * unit.dmg_ap
            return bonuses, state
                
        if unit.fatigue_pts >= 2_800:
            state = "Active"
            bonuses['MA'] = - 0.05 * unit.MA
            return bonuses, state
                         
        if unit.fatigue_pts >= 0:
            state = "Fresh"
            return bonuses, state

class strength_in_numbers:
    def __init__(self, name):
        self.name = name

    def condition(unit):
        if unit.CD / unit.hp < 0.5:
            return True
        else:
            return False

    def get_bonuses(unit):
        bonuses = create_bonuses_dict()
        bonuses['MD'] = 8
        bonuses['LD'] = 6
        return bonuses
    
class rage:
    def __init__(self, name):
        self.name = name

    def condition(unit):
        return True


    def get_bonuses(unit):
        bonuses = create_bonuses_dict()
        bonuses['MA'] = 5
        bonuses['LD'] = 8
        bonuses['phys_res'] = 0.10
        return bonuses
    

class martial_prowess:
    def __init__(self, name):
        self.name = name

    def condition(unit):
        if unit.CD / unit.hp < 0.75:
            return True
        else:
            return False

    def get_bonuses(unit):
        bonuses = create_bonuses_dict()
        bonuses['MD'] = 12
        bonuses['MA'] = 2
        return bonuses
    

class harmonic_convergence:
    def __init__(self, name):
        self.name = name

    def duration():
        return 20
    
    def get_bonuses(unit):
        bonuses = create_bonuses_dict()
        bonuses['MA'] = 24
        bonuses['MD'] = 24
        return bonuses

        
class waagh:
    def __init__(self, name):
        self.name = name

    def duration():
        return 18
    
    def get_bonuses(unit):
        bonuses = create_bonuses_dict()
        bonuses['MA'] = 24
        bonuses['dmg_base'] = 0.25 * unit.dmg_base
        bonuses['dmg_ap'] = 0.25 * unit.dmg_ap
        return bonuses