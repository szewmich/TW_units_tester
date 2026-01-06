import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
import os

pd.set_option('display.max_rows', 100)

font_size = 10
header_height = 0.6
cell_width = 0.05

out_dir = 'results_v02\\'

faction_A = 'Bactria'
faction_B = 'Odrysian'

path = out_dir + faction_A + "_vs_" + faction_B + "_results.csv"

# Read CSV
try:
    df = pd.read_csv(path, index_col=0)
except FileNotFoundError:
    path = out_dir + faction_B + "_vs_" + faction_A + "_results.csv"
    try:
        df = pd.read_csv(path, index_col=0)
    except FileNotFoundError:
        print(f"File not found: {path}")
        exit()

df = df.dropna(axis=0, how='all')  # Remove rows with all NaN
df = df.dropna(axis=1, how='all')  # Remove columns with all NaN

# print(df)

# df = df.astype(float)

##########################################################
def create_cross_calc_table(df, ax, font_size=font_size, header_height=header_height, cell_width=cell_width, first=True, second=False):
    # Create the table with increased font size
    table = ax.table(
        cellText=df.values,
        rowLabels=df.index,
        colLabels=df.columns,
        loc='center',
        cellLoc='center',
        colLoc='center'
    )

    # Set font size for all cells
    table.auto_set_font_size(False)
    table.set_fontsize(font_size)

    # Rotate column headers vertically
    for key, cell in table.get_celld().items():
        row, col = key
        cell.set_width(cell_width)
        if row == 0:
            cell.set_height(header_height)  # Increase header row height
            cell.set_text_props(rotation=90, ha='center', va='center', fontsize=font_size)
            
    # numeric_data = df.values
    # norm = plt.Normalize(numeric_data.min(), numeric_data.max())
    # cmap = plt.get_cmap('RdYlGn')           
    # Apply green-to-red colormap with 0 as the center (neutral color)
    numeric_data = df.values
    abs_max = max(abs(numeric_data.min()), abs(numeric_data.max()))
    norm = plt.Normalize(vmin=-abs_max, vmax=abs_max)
    cmap = plt.get_cmap('RdYlGn')

    for (row, col), cell in table.get_celld().items():
        # Skip header row and row indices
        if row == 0 or col == -1:
            continue
        value = df.iloc[row-1, col]
        color = cmap(norm(value))
        cell.set_facecolor(color)

        if value >= 0:
            n_wins = value % 1
        else: 
            n_wins = -value % 1
        n_wins = round(n_wins, 2)  # Round to two decimal places
        if first:
            if n_wins > 0.005 or n_wins < -0.005:
                cell.set_text_props(fontweight='bold')
        if second:
            n_wins = 0.010 - abs(n_wins)
            if value >= 0:
                value = float(round(value, 0) + n_wins)
            else:
                value = float(round(value, 0) - n_wins)

            cell.get_text().set_text(str(value))
            if n_wins > 0.005:
                cell.set_text_props(fontweight='bold')
        value = int(value)
        cell.get_text().set_text(str(value))

    ax.axis('off')


def find_good_counters(unit_name, faction_name, out_dir = out_dir):
    """Finds good counters for a given unit name from all results CSV files."""

    results_files = [f for f in os.listdir(out_dir) if (f.endswith('_results.csv') and faction_name in f)]

    dtypes = {'gold_adv': float, 'winning': bool, 'counter_unit_name': str, 'faction': str}
    good_counters = pd.DataFrame(columns=['gold_adv', 'winning', 'counter_unit_name', 'faction'])
    good_counters = good_counters.astype(dtypes)

    threshold = 50

    for file in results_files:
        counter_faction = file.removesuffix('_results.csv').split('_vs_')
        counter_faction.remove(faction_name)
        counter_faction = counter_faction[0]


        df = pd.read_csv(os.path.join(out_dir, file), index_col=0)
        if unit_name not in df.index:
            df = -df.T
            threshold = -threshold


        df = df.loc[unit_name]
        df = df.loc[df < threshold]  # Keep only negative values
        
        for counter_unit_name, gold_adv in df.items():
            if abs(gold_adv) % 1 >= 0.05:
                win = True
            else:
                win = False
            good_counters = good_counters._append({
                'gold_adv': gold_adv,
                'winning': win,
                'counter_unit_name': counter_unit_name,
                'faction': counter_faction
            }, ignore_index=True)

        # if unit_name in df.columns:
        #     df = df.loc[unit_name]
        #     df = df.loc[df < 50]  # Keep only negative values
            
        #     for counter_unit_name, gold_adv in df.items():
        #         if abs(gold_adv) % 1 >= 0.05:
        #             win = True
        #         else:
        #             win = False
        #         good_counters = good_counters._append({
        #             'gold_adv': gold_adv,
        #             'winning': win,
        #             'counter_unit_name': counter_unit_name,
        #             'faction': counter_faction
        #         }, ignore_index=True)

            # print(df)

    print(f"Good counters for {unit_name} from faction {faction_name}:")
    print(good_counters.sort_values(by='gold_adv', ascending=True))


# ##########################################################
# # SHOW CROSS-CALC TABLES
# ##########################################################
fig, ax1 = plt.subplots(2, 1, figsize=(14,10))
ax1 = ax1[0]

create_cross_calc_table(df, ax1, font_size=font_size, header_height=header_height, cell_width=cell_width, first=True, second=False)

###########################################################    
# Duplicate the table in the second subplot
ax2 = plt.gca().figure.axes[1]

df2 = df.T * -1

create_cross_calc_table(df2, ax2, font_size=font_size, header_height=header_height, cell_width=cell_width, first=False, second=True)

plt.tight_layout()
plt.show()
# ##########################################################


##########################################################
# FIND COUNTERS FOR A UNIT
##########################################################

find_good_counters(unit_name = 'Cimbri Heavy Axemen', faction_name = 'Cimbri', out_dir = out_dir)
#find_good_counters(unit_name = 'Thracian Thureos Infantry', faction_name = 'Odrysian', out_dir = out_dir)

##########################################################

