import os
import re
import pandas as pd
from dataclasses import dataclass, fields

path = "db_temp.txt"

with open(path, 'r', encoding='utf-8') as file:
    file_lines = file.readlines()
    lines = [line.strip() for line in file_lines if line.strip()]
print(lines)

@dataclass
class unit:
    faction: str
    name: str
    cost: int
    cat: str
    size: int
    hp: int
    CD: int
    perks: str
    active_effects: str
    MA: int
    MD: int
    armour: int
    dmg_base: int
    dmg_ap: int
    CB: int
    bvINF: int
    bvCAV: int
    MBC: float
    ammo: int
    ward: int
    phys_res: int
    mag_res: int
    fire_res: int
    fir_att: int
    mag_att: int
    missile_dmg_base: int
    missile_dmg_ap: int
    name_native: str
    range: int
    morale: int


size_indices = [i for i, line in enumerate(lines) if line.startswith("Class:")]
name_indices = [i - 1 for i in size_indices]
stats_indices = [i + 4 for i in size_indices]

print(lines[size_indices[0]])
print(lines[name_indices[0]])
print(lines[stats_indices[0]])

units_info = []

for k in range(len(size_indices)):
    size = int(lines[size_indices[k]].split(": ")[2].strip())
    name_native = lines[name_indices[k]].split("(")[0].strip()
    name = lines[name_indices[k]].split("(")[-1].split(")")[0].strip()
    stats = re.split(r'[\t/]', lines[stats_indices[k]])
    stats_cleaned = [int(c) if c.isdigit() else 0 for c in stats]

    CB, MA, MD, armour, morale, dmg_base, dmg_ap, shield, MBC, missile_dmg_base, missile_dmg_ap, range, ammo = stats_cleaned

    if size <=120:
        if size < 100:
            cat = 'other'
            hp = 10000
        else:
            cat = 'cav'
            hp = size * 80
    elif ammo < 6:
        cat = 'inf'
        hp = size * 60
    else:
        cat = 'missile'
        hp = size * 60
    
    print(MA)

    x = unit(
        faction='',
        name=name,
        cost=1000,
        cat=cat,
        size=size,
        hp=hp,
        CD=0,
        perks='',
        active_effects='',
        MA=MA,
        MD=MD + shield,
        armour=armour,
        dmg_base=dmg_base,
        dmg_ap=dmg_ap,
        CB=CB,
        bvINF=0,
        bvCAV=0,
        MBC=MBC / 100,
        ammo=ammo,
        ward=0,
        phys_res=0,
        mag_res=0,
        fire_res=0,
        fir_att=0,
        mag_att=0,
        missile_dmg_base=missile_dmg_base,
        missile_dmg_ap=missile_dmg_ap,
        name_native=name_native,
        range=range,
        morale=morale,
    )
    print(x)
    units_info.append(x)
# print(units_info)

units_df = pd.DataFrame([vars(u) for u in units_info])
print(units_df)

units_df.to_csv("db_read.csv", index=False)














exit()
# k = '16\t6\t8\t15\t36\t20/3\t4/65\t-/-\tâ€“\t0'
# print(k)

# # k_cleaned = [c for c in k if c.isdigit() or c == ';']

# k_cleaned = re.split(r'[\t/]', k)
# # k_cleaned = k.split("\t", "/")
# print(k_cleaned)



# for id,item in enumerate(k_cleaned):
#     if item.isalnum():
#         k_cleaned[id] = int(item)
#     else:
#         k_cleaned[id] = 0

# print(k_cleaned)