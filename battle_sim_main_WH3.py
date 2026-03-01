import random
from dataclasses import dataclass, fields
from typing import Any
import inspect
import copy
import pandas as pd
import math
import time
import timeit

import effect_database as edb
import leadership


ID_A = 1080
ID_B = 484

A_timed_effects = {
    'waagh': 20,
}

B_timed_effects = {
    
}

def run_sim(ID_A, ID_B):
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_rows', 1700)
    pd.set_option('display.max_columns', 20)
    pd.set_option('max_colwidth', 2000)

    # UNIT CHOICE
    by_name = False
    by_ID = True
    use_native_name = False

    # GAME PARAMETERS
    DEI = False
    WARHAMMER = True
    n_games = 100                       # number of simulations run for statistics
    missile_switch = 0                  # 1 = on, 0 = off
    melee_switch = 1                    # 1 = on, 0 = off
    attack_interval = 5                 # time between attacks (in seconds)
    charge_duration = 13                # time of charge bonus duration (in seconds)
    #combat_width = 30                  # number of models in formation width 
    combat_width_multiplier = 1.3       # combat width multiplier to account for units engaging with more or less models than their formation width (eg. 0.5 means that unit will fight with half of its formation width, 2 means it will fight with double of its formation width)
    missile_accuracy = 0.6              # fraction of missiles hitting their targets
    pursuit_damage_factor = 0.0         # factor of damage inflicted on fleeing unit after it is routed (0.2 = 20% of total hp left)

    multiple_opponents_factor_A = 1   # average number of opponents that models of unit A are fighting at once
    multiple_opponents_factor_B = 1   # average number of opponents that models of unit B are fighting at once 

    # ARMY BOOSTS
    A_army_boost = edb.army_boost(MA_perc = 0, MD_perc = 0, ammo_perc = 0, missile_dmg_base_perc = 0, missile_dmg_ap_perc = 0, MBC_perc = 0)
    B_army_boost = edb.army_boost(MA_perc = 0, MD_perc = 0, ammo_perc = 0, missile_dmg_base_perc = 0, missile_dmg_ap_perc = 0, MBC_perc = 0)


    # DATA PARAMETERS
    if WARHAMMER:
        path = 'warhammer_data.xlsx'
    if DEI:
        path = 'dei_data.xlsx'

    # PERKS
    handled_abilities = [
    name for name, cls in inspect.getmembers(edb, inspect.isclass)
    if cls.__module__ == edb.__name__
    ]
    # handled_abilities = inspect.getmembers(edb, inspect.isclass)

    # UNIT DATA CLASS DEFINITION
    @dataclass
    class unit:
        faction: str
        name: str
        cost: int
        cat: str
        size: int
        formation_width: int
        hp: int
        CD: int
        attributes: str
        abilities: list
        active_effects: list
        MA: int
        MD: int
        armour: int
        dmg_base: int
        dmg_ap: int
        CB: int
        bvINF: int
        bvLARGE: int
        MBC: float
        ammo: int
        ward: float
        phys_res: float
        mag_res: float
        fire_res: float
        fir_att: bool
        mag_att: bool
        fear: bool
        itp: bool
        missile_dmg_base: int
        missile_dmg_ap: int
        name_native: str
        range: int
        LD: int
        LD_current: int
        fatigue_pts: int
        fatigue_state: str
        fatigue_immune: int


    ######################################################################################################################
    # READ EXCEL DATA
    ######################################################################################################################
    df = pd.read_excel(path, sheet_name="DATA_v2", header = 0, index_col = 0)
    
    df['MBC'] = df['MBC']/100
    df['phys_res'] = df['phys_res']/100
    df['mag_res'] = df['mag_res']/100
    df['fire_res'] = df['fire_res']/100
    df['ward'] = df['ward']/100

    # unique_abilities = set()
    # for abilities in df['abilities']:
    #     if isinstance(abilities, str):
    #         abilities_list = abilities.split(',')
    #         unique_abilities.update(abilities_list)
    # unique_abilities_list = sorted(list(unique_abilities))
    # print(unique_abilities_list)
    # exit()

    # Find unit A
    A_data = df.query('ID == @ID_A').iloc[0]
    if pd.isna(A_data['abilities']):
        A_data['abilities'] = []
    else:
        A_data['abilities'] = A_data['abilities'].split(',')

    A_data['active_effects'] = []
    A_data['abilities'] = [perk for perk in A_data['abilities'] if perk in handled_abilities]
    # print(A_data)

    # Enforce correct types based on the dataclass
    typed_data = {f.name: f.type(A_data[f.name]) for f in fields(unit)}
    A = unit(**typed_data)

    if use_native_name:
        A.name = A.name_native  

    print('Unit A:')
    print(A)
    # print('\n')
    ########################################
    # Find unit B
    B_data = df.query('ID == @ID_B').iloc[0]
    if pd.isna(B_data['abilities']):
        B_data['abilities'] = []
    else:
        B_data['abilities'] = B_data['abilities'].split(',')

    B_data['active_effects'] = []
    B_data['abilities'] = [perk for perk in B_data['abilities'] if perk in handled_abilities]
    # print(B_data)

    # Enforce correct types based on the dataclass
    typed_data = {f.name: f.type(B_data[f.name]) for f in fields(unit)}
    B = unit(**typed_data)

    if use_native_name:
        B.name = B.name_native
    print('Unit B:')
    print(B)
    print('\n')


    if 'inf' in A.cat:
        A.cat = 'inf'
    else:
        A.cat = 'large'
    if 'inf' in B.cat:
        B.cat = 'inf'
    else:
        B.cat = 'large'

    combat_width = math.floor(min(A.formation_width, B.formation_width) * combat_width_multiplier)
    combat_width = min(combat_width, A.size, B.size)

    print(f'Combat width is set to {combat_width} models.\n')

    # TIMED EFFECTS
    if A_timed_effects:
        A.timed_effects = A_timed_effects
    else:
        A.timed_effects = {}

    if B_timed_effects:
        B.timed_effects = B_timed_effects
    else:
        B.timed_effects = {}


    # Create duplicate instances to go back to defaults if unit stats get modified during combat
    A_source = copy.deepcopy(A)
    B_source = copy.deepcopy(B)

    A.active_effects.append('A_army_boost')
    B.active_effects.append('B_army_boost')
    ######################################################################################################################
    # APPLY BONUS VS <UNIT TYPE>

    # Calculate ratio of base/ap damage to apply bonus proportionally
    A_dmg_ratio = A.dmg_base / (A.dmg_base + A.dmg_ap)
    B_dmg_ratio = B.dmg_base / (B.dmg_base + B.dmg_ap)

    # Apply bonus vs infantry (if applicable)
    if B.cat == 'inf':
        A.MA = A.MA + A.bvINF
        A.dmg_base = A.dmg_base + A.bvINF * A_dmg_ratio
        A.dmg_ap = A.dmg_ap + A.bvINF * (1 - A_dmg_ratio)
    if A.cat == 'inf':
        B.MA = B.MA + B.bvINF
        B.dmg_base = B.dmg_base + B.bvINF * B_dmg_ratio
        B.dmg_ap = B.dmg_ap + B.bvINF * (1 - B_dmg_ratio)

    # Apply bonus vs large (if applicable)
    if B.cat == 'large':
        A.MA = A.MA + A.bvLARGE
        A.dmg_base = A.dmg_base + A.bvLARGE * A_dmg_ratio
        A.dmg_ap = A.dmg_ap + A.bvLARGE * (1 - A_dmg_ratio)
    if A.cat == 'large':
        B.MA = B.MA + B.bvLARGE
        B.dmg_base = B.dmg_base + B.bvLARGE * B_dmg_ratio
        B.dmg_ap = B.dmg_ap + B.bvLARGE * (1 - B_dmg_ratio)

    ##################################################################################################################################################################
    # FUNCTIONS
    ##################################################################################################################################################################
    if WARHAMMER:
        def hit_chance (MA,MD):
            chance=(35+(MA-MD))/100
            if chance > 0.9:
                chance = 0.9
            if chance < 0.08:
                chance = 0.08
            return chance

        def armour_red (armour):
            red=(armour*random.uniform(0.5,1))/100
            if red > 1:
                red = 1
            return red

    if DEI:
        def hit_chance (MA,MD):
            chance = (25 + (MA - MD)) / 100
            if chance > 0.75:
                chance = 0.75
            if chance < 0.15:
                chance = 0.15
            return chance

        def armour_red (armour):
            red = random.randrange(0, armour)
            return red

    def other_red (fir_att,mag_att,ward,phys_res,mag_res,fire_res):
        tot_red = 0
        if fir_att == 1:
            tot_red = fire_res
        if mag_att == 1:
            tot_red = tot_red + mag_res
        if mag_att == 0:
            tot_red = tot_red + phys_res
        tot_red = tot_red + ward
        if tot_red > 0.9:
            tot_red = 0.9
        return tot_red

    # Used only for DEI missile phase (NOT VALID FOR WARHAMMER, TO BE REWORKED IF NEEDED)
    def avg_damage (dmg_base, dmg_ap, armour):
        t_dmg = 0
        for x in range (1, armour + 1):
            if dmg_base - x >= 0:
                dmg = dmg_base - x + dmg_ap
            else:
                dmg = dmg_ap
            t_dmg = t_dmg + dmg
        avg_dmg = t_dmg / armour
        return avg_dmg

    ##################################################################################################################################################################

    # STATISTICS - Global definitions
    games_played = 0
    attack_count_for_avg = 0
    exchange_rounds_for_avg = 0
    A_perc_hp_left_for_avg = 0
    B_perc_hp_left_for_avg = 0
    A_perc_hp_left_avg = 0
    B_perc_hp_left_avg = 0
    A_value_for_avg = 0
    B_value_for_avg = 0
    A_perc_hp_left_before_shatter_for_avg = 0
    B_perc_hp_left_before_shatter_for_avg = 0

    # player list = [A, B]
    player = [A, B]
    A_wins = 0
    B_wins = 0

    #################################################

    
    
    A_shatter_perc_hp = leadership.get_shatter_perc_hp(A.LD)
    B_shatter_perc_hp = leadership.get_shatter_perc_hp(B.LD)

    # START ALL GAMES
    while games_played < n_games:
        # NEW GAME BEGINS
        # Parameters to be reset:
        exchange_rounds = 0
        attack_count = 0
        ongoing = True
        CD_curr = 0
        CD_opp = 0
        A_perc_hp_left = 0
        B_perc_hp_left = 0
        A_pursuit_casaulties = 0
        B_pursuit_casaulties = 0

        # Reset accumulated damage (CD)
        A.CD = 0
        B.CD = 0

        # Calculate base hp per model
        A_model_hp_base = A.hp / A.size
        B_model_hp_base = B.hp / B.size

        # Create list of individual model's hp for models at the frontline (list length = combat width).
        # They should be already damaged after missile phase (hp_shot)
        A_models_hp = [A_model_hp_base] * combat_width
        B_models_hp = [B_model_hp_base] * combat_width

        # Counter of missile attacks done. When both players have done their missile attacks, it becomes 2 and the missile phase ends.
        # If missile switch is off, it is set to 2 from the beginning and the missile phase does not happen at all.
        if missile_switch:
            missile_attacks_done = 0
        else:
            missile_attacks_done = 2
            A_model_hp_shot = A_model_hp_base
            B_model_hp_shot = B_model_hp_base

        A_damage_history = {0: 0}
        B_damage_history = {0: 0}

        # While both units are alive (total hp > 0) and fighting
        while ongoing:

            # round of exchanged attacks - calculate damage to be inflicted -  start from player A, then B
            for p in player:
                # Determine which player is attacker (attacker = curr, defender = opp)
                curr = p
                if curr == A:
                    opp = B
                    CD_opp = B.CD
                    models_hp = B_models_hp             # List of frontline units with their remaining hp, eg. [52, 68, 78 ... 48]
                    model_hp_base = B_model_hp_base     # Base hp of undamaged unit (from unit card, integer), eg. 80
                    multiple_opponents_factor = multiple_opponents_factor_B     # How many times one entity B will be attacked by multiple entities of A 
                else:
                    opp = A
                    CD_opp = A.CD
                    models_hp = A_models_hp
                    model_hp_base = A_model_hp_base
                    multiple_opponents_factor = multiple_opponents_factor_A

                ##################################################################################
                # ACTIVATE / DEACTIVATE EFFECTS FOR CURR (ATTACKER)
                if curr.abilities:                                                     # If attacker unit has any abilities
                    for perk in curr.abilities:                                        # For each of its abilities
                        if getattr(edb, perk).condition(curr):                     # If conditions for effect activation are met
                            if str(perk) not in curr.active_effects:
                                curr.active_effects.append(str(perk))              # Add effect to active effects list (if not already there)
                        else:                                                      # If conditions for effect activation are NOT met
                            if str(perk) in curr.active_effects:
                                curr.active_effects.remove(str(perk))              # Remove effect from active effects list (if it was active) 

                # ACTIVATE / DEACTIVATE EFFECTS FOR OPP (DEFENDER)
                if opp.abilities:
                    for perk in opp.abilities:
                        if getattr(edb, perk).condition(opp):
                            if str(perk) not in opp.active_effects:
                                opp.active_effects.append(str(perk))
                        else:
                            if str(perk) in opp.active_effects:
                                opp.active_effects.remove(str(perk))
                
                # ACTIVATE / DEACTIVATE TIMED EFFECTS (SPELLS / ABILITIES) FOR CURR (ATTACKER)
                time_passed = exchange_rounds * attack_interval                 # measure of time passed in combat
                if curr.timed_effects:
                    for effect, activation_time in curr.timed_effects.items():
                        if time_passed >= activation_time and time_passed < (activation_time + getattr(edb, effect).duration()):   # If duration of currently considered timed effect is not over yet (compared to time passed in combat)
                            if str(effect) not in curr.active_effects:
                                curr.active_effects.append(str(effect))           # Add it to active effects list (if not already there)
                        else:
                            if str(effect) in curr.active_effects:
                                curr.active_effects.remove(str(effect))           # Remove it from active effects list (if it was active)

                ##################################################################################
                # CALCULATE EFFECT BONUSES FOR BOTH COMBATANTS

                # Create empty total bonuses dict
                tot_bonuses = edb.create_bonuses_dict()

                # For each active effect on attacker unit, accumulate its bonuses
                if curr.active_effects:
                    for effect in curr.active_effects:
                        if effect != "A_army_boost" and effect != "B_army_boost" and effect != "fear" and effect != "itp":
                            bonuses = getattr(edb, effect).get_bonuses(curr)
                        else:
                            bonuses = locals()[effect].get_bonuses(curr)

                        # Update total bonus values by adding up bonuses from currently considered active effect
                        for attribute, value in tot_bonuses.items():
                            tot_bonuses[attribute] = value + bonuses[attribute]


                # Add penalties from Fatigue
                if not curr.fatigue_immune == 1:
                    fatigue_penalties, curr.fatigue_state = edb.fatigue.get_penalties(curr)
                    for attribute, value in tot_bonuses.items():
                        tot_bonuses[attribute] = value + fatigue_penalties[attribute]


                # Attributes relevant for attacker in currently considered attack sequence, with added all bonuses from active effects
                CB = curr.CB + tot_bonuses['CB']
                MA = curr.MA + tot_bonuses['MA']
                dmg_base = curr.dmg_base + tot_bonuses['dmg_base']
                dmg_ap = curr.dmg_ap + tot_bonuses['dmg_ap']
                ammo = curr.ammo + tot_bonuses['ammo']
                missile_dmg_base = curr.missile_dmg_base + tot_bonuses['missile_dmg_base']
                missile_dmg_ap = curr.missile_dmg_ap + tot_bonuses['missile_dmg_ap']

                # Save total bonuses dict for A and B
                if curr == A:
                    tot_bonuses_A = copy.deepcopy(tot_bonuses)
                else:
                    tot_bonuses_B = copy.deepcopy(tot_bonuses)

                # Reset total bonuses dict
                tot_bonuses = edb.create_bonuses_dict()


                # For each active effect on defender unit, accumulate its bonuses
                if opp.active_effects:
                    for effect in opp.active_effects:
                        if effect != "A_army_boost" and effect != "B_army_boost" and effect != "fear" and effect != "itp":
                            bonuses = getattr(edb, effect).get_bonuses(opp)
                        else:
                            bonuses = locals()[effect].get_bonuses(curr)

                        # Update total bonus values by adding up bonuses from currently considered active effect
                        for attribute, value in tot_bonuses.items():
                            tot_bonuses[attribute] = value + bonuses[attribute]


                # Attributes relevant for defender in currently considered attack sequence, with added all bonuses from active effects
                armour = opp.armour + tot_bonuses['armour']
                MD = opp.MD + tot_bonuses['MD']
                MBC = opp.MBC + tot_bonuses['MBC']


                # If charge bonus is active, add it to attacker's stats
                time_passed = exchange_rounds * attack_interval                 # measure of time
                if time_passed < charge_duration:
                    CB_adj = CB * (1 - (time_passed / charge_duration))         # adjust charge bonus - it fades away linearly over charge duration
                    MA = MA + CB_adj                                            # Attacker's melee attack + adjusted charge bonus
                    perc_base = dmg_base / (dmg_base + dmg_ap)                  # Ratio of attacker's base damage vs (base+ap)
                    dmg_base = dmg_base + CB_adj * perc_base                    # Attacker's base damage with added charge bonus (proportional to perc_base)
                    dmg_ap = dmg_ap + CB_adj * (1-perc_base)                    # Attacker's ap damage with added charge bonus (counter-proportional to perc_base)
                    # print ("Charge bonus for ", curr.name, " = ", CB_adj)

                # If charge bonus inactive, take unadjusted attacker's stats
                else:
                    
                    #print("NO charge bonus for ", curr.name)
                    pass

                ##################################################################################
                # Parameters constant for all models (not affected by randomness)
                c = hit_chance(MA, MD)
                oth_red = other_red(curr.fir_att, curr.mag_att, opp.ward, opp.phys_res, opp.mag_res, opp.fire_res)

                n_opponents = math.floor(multiple_opponents_factor)                         # Opp entity will be attacked this many times
                multiple_opponents_dmg_factor = multiple_opponents_factor / n_opponents     # Damage dealt to Opp will be multiplied by this
                                                                                            # (way to account non-integer values of multiple_opponents_factor)

                ##################################################################################
                # MISSILE PHASE
                # Rough calculation of missile damage to be inflicted upon whole unit
                if missile_attacks_done != 2:
                    infl_missile_dmg = round(ammo * curr.size * missile_accuracy * (1 - MBC) *
                                    avg_damage(missile_dmg_base, missile_dmg_ap, armour))
                    infl_missile_dmg_per_model = round(infl_missile_dmg / opp.size)

                    # Inflict damage on defender's model
                    models_hp = [k - infl_missile_dmg_per_model for k in models_hp]
                    print(f'{str(curr.name)} inflict {infl_missile_dmg} missile damage to {opp.name} unit - {models_hp[0]} hp left.')

                    # Accumulate damage of whole unit
                    CD_opp = CD_opp + infl_missile_dmg

                    #Save model_hp_shot for either player A or B
                    if curr == A:
                        B_model_hp_shot = models_hp[0]
                        A_missile_dmg = infl_missile_dmg
                    else:
                        A_model_hp_shot = models_hp[0]
                        B_missile_dmg = infl_missile_dmg

                    # Save hp of a single model (first on list) after getting shot as model_hp_shot    
                    model_hp_shot = models_hp[0]

                    missile_attacks_done += 1

                if not missile_switch:
                    model_hp_shot = model_hp_base

                # If there is no melee phase, break loop and go to statistics with only missile damage data
                if not melee_switch:
                    break

                ##################################################################################
                # MELEE PHASE
                # Loop through all attacker's models in combat width
                infl_damage_all_models = 0
                for k in range (0, combat_width):
                    tot_dmg = 0
                    # Looping through all models attacking Opp simultaneously (their damage will be summated)
                    for n in range(n_opponents):
                        # If hit goes through (calculated hit chance checked against random function for each individual model)
                        if c > random.random():
                            arm_red = armour_red(armour)                                        # Armour reduction affected by randomness
                            if WARHAMMER:
                                dmg_adj = (dmg_base * (1 - arm_red) + dmg_ap) * (1 - oth_red)   # Total damage to be inflicted including all reductions
                            if DEI:
                                if arm_red > dmg_base:
                                    arm_red = dmg_base
                                dmg_adj = (dmg_base - arm_red + dmg_ap) * (1 - oth_red)         # Total damage to be inflicted including all reductions
                            dmg_adj = (round(dmg_adj))                                          # Total damage to be inflicted -> rounded
                        else:
                            dmg_adj = 0

                        tot_dmg += dmg_adj

                    tot_dmg = tot_dmg * multiple_opponents_dmg_factor

                    # Damage inflicted is limited by remaining hp of individual model (currently considered "k" position in combat width)
                    if tot_dmg < models_hp[k]:
                        infl_dmg = tot_dmg
                    else:
                        infl_dmg = models_hp[k]
                    infl_dmg = int(infl_dmg)                                                 # Not sure why it's needed

                    # Inflict damage on defender's model
                    models_hp[k] = models_hp[k] - infl_dmg
                    #print(f'{str(curr.name)} inflict {infl_dmg} damage to {opp.name} model in column {k+1} - {models_hp[k]} hp left.')
                    # If model hp is down to zero, kill it and reset model hp at this "k" position in combat width
                    if models_hp[k] == 0:
                        models_hp[k] = model_hp_shot

                    # Accumulate damage of whole unit (all time)
                    CD_opp = CD_opp + infl_dmg

                    # Accumulate damage of whole unit (this exchange)
                    infl_damage_all_models += infl_dmg

                    # Save temporary data of defender's models hp and accumulated damage as global data for either player A or B
                    if curr == A:                                               # If A is attacker, B is defender (save data for player B)
                        B_models_hp [k] = models_hp[k]
                        B.CD = CD_opp
                        B_last_infl = infl_dmg
                    else:                                                       # If B is attacker, A is defender (save data for player A)
                        A_models_hp [k] = models_hp[k]
                        A.CD = CD_opp
                        A_last_infl = infl_dmg

                    # Attack count (every single model attack) for statistics
                    attack_count += 1
                
                # Update damage history
                if curr == A:
                    B_damage_history [time_passed + attack_interval] =  infl_damage_all_models
                if curr == B:
                    A_damage_history [time_passed + attack_interval] =  infl_damage_all_models

                # Accumulate fatigue points
                curr.fatigue_pts += attack_interval * 190

            ##################################################################################
            # CURRENT ATTACK EXCHANGE ROUND FINISHED
            ##################################################################################
            
            # Update Leadership for A and B
            A.LD_current, B.LD_current = leadership.update_LD(A, B, A_damage_history, B_damage_history, tot_bonuses_A['LD'], tot_bonuses_B['LD'])

            if A.LD_current < 0 or B.LD_current < 0:
                if A.LD_current < B.LD_current:
                    B_wins += 1
                    ongoing = False
                    B_perc_hp_left = (B.hp - B.CD) / B.hp
                    A_perc_hp_left = (A.hp - A.CD) / A.hp * (1-pursuit_damage_factor)
                    B_value = (1 - A_perc_hp_left) * A.cost
                    A_value = (1 - B_perc_hp_left) * B.cost

                if B.LD_current < A.LD_current:
                    A_wins += 1
                    ongoing = False
                    A_perc_hp_left = (A.hp - A.CD) / A.hp
                    B_perc_hp_left = (B.hp - B.CD) / B.hp * (1-pursuit_damage_factor)
                    A_value = (1 - B_perc_hp_left) * B.cost
                    B_value = (1 - A_perc_hp_left) * A.cost
                
                A_perc_hp_left_before_shatter = A_perc_hp_left - A_shatter_perc_hp
                B_perc_hp_left_before_shatter = B_perc_hp_left - B_shatter_perc_hp

            # Count attack exchange rounds
            exchange_rounds += 1
            # print('Current balance:')
            # print(f'{str(opp.name)} unit: {round((opp.hp - opp.CD) / opp.hp * 100)} % hp left.')
            # print(f'{str(curr.name)} unit: {round((curr.hp - curr.CD) / curr.hp * 100)} % hp left.')

            # print(f'Total attack count is {attack_count}')
            # print(f'Total exchange rounds is {exchange_rounds}')
            ##################################################################################

        # CURRENT GAME FINISHED
        # Statistics section - these add up for final statistics over multiple games and do NOT reset between games
        attack_count_for_avg = attack_count_for_avg + attack_count
        exchange_rounds_for_avg = exchange_rounds_for_avg + exchange_rounds
        A_perc_hp_left_for_avg = A_perc_hp_left_for_avg + A_perc_hp_left
        B_perc_hp_left_for_avg = B_perc_hp_left_for_avg + B_perc_hp_left
        A_value_for_avg = A_value_for_avg + A_value
        B_value_for_avg = B_value_for_avg + B_value

        A_perc_hp_left_before_shatter_for_avg += A_perc_hp_left_before_shatter
        B_perc_hp_left_before_shatter_for_avg += B_perc_hp_left_before_shatter

        games_played += 1
        print (f'Finished game number {games_played}')
        ##################################################################################

    # ALL GAMES FINISHED
    # Statistics section
    average_attacks = attack_count_for_avg / n_games
    average_exchange_rounds = exchange_rounds_for_avg / n_games
    A_value_avg = round(A_value_for_avg / n_games)
    B_value_avg = round(B_value_for_avg / n_games)
    # if A_wins > 0:
    #     A_perc_hp_left_avg = round(A_perc_hp_left_for_avg / A_wins * 100)
    # if B_wins > 0:
    #     B_perc_hp_left_avg = round(B_perc_hp_left_for_avg / B_wins * 100)
    
    A_remaining_total_hp_perc = round(A_perc_hp_left_for_avg / n_games * 100)
    B_remaining_total_hp_perc = round(B_perc_hp_left_for_avg / n_games * 100)

    A_perc_hp_left_before_shatter_avg = round(max(A_perc_hp_left_before_shatter_for_avg / n_games * 100, 0))
    B_perc_hp_left_before_shatter_avg = round(max(B_perc_hp_left_before_shatter_for_avg / n_games * 100, 0))

    A_value_shatter_adjusted = round((100-B_perc_hp_left_before_shatter_avg)/100 * B.cost)
    B_value_shatter_adjusted = round((100-A_perc_hp_left_before_shatter_avg)/100 * A.cost)

    if missile_switch == 1:
        print(f'A_model_hp_shot is {A_model_hp_shot}')
        print(f'B_model_hp_shot is {B_model_hp_shot}')
        print(f'{A.name} inflict {A_missile_dmg} missile damage which is {round((A_missile_dmg / B.hp) * B.cost)} gold worth of value')
        print(f'{B.name} inflict {B_missile_dmg} missile damage which is {round((B_missile_dmg / A.hp) * A.cost)} gold worth of value')

    if melee_switch == 1:
        # print (f'{A.name} win count = {A_wins} with average {A_perc_hp_left_avg} % hp left for unit, killing {A_value_avg} gold worth of value')
        # print (f'{B.name} win count = {B_wins} with average {B_perc_hp_left_avg} % hp left for unit, killing {B_value_avg} gold worth of value')
        print (f'{A.name} win count = {A_wins} with average {A_remaining_total_hp_perc} % hp left for unit, killing {A_value_avg} gold worth of value ({A_perc_hp_left_before_shatter_avg} % remaining hp before shatter, {A_value_shatter_adjusted} adjusted gold value)')
        print (f'{B.name} win count = {B_wins} with average {B_remaining_total_hp_perc} % hp left for unit, killing {B_value_avg} gold worth of value ({B_perc_hp_left_before_shatter_avg} % remaining hp before shatter, {B_value_shatter_adjusted} adjusted gold value)')

        print(f'Average time of combat: {average_exchange_rounds*attack_interval}')

    A_gold_adv = A_value_avg - B_value_avg 
    A_wins_fraction = round(A_wins / n_games, 1)

    if A_gold_adv >= 0:
        A_gold_adv = A_gold_adv + A_wins_fraction / 10
    else:
         A_gold_adv = A_gold_adv - A_wins_fraction / 10

    # print(f'A_rout_dmg = {A_rout_dmg}')
    # print(f'B_rout_dmg = {B_rout_dmg}')


    return A_gold_adv

if __name__ == "__main__":
    run_sim(ID_A, ID_B)
    # run_sim(2, 22)