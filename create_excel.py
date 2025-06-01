import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm

font_size = 10
header_height = 0.6
cell_width = 0.05

out_dir = 'results_v02\\'

faction_A = 'Galatia'
faction_B = 'Odrysian'

path = out_dir + faction_A + "_vs_" + faction_B + "_results.csv"

# Read CSV
df = pd.read_csv(path, index_col=0)
df = df.dropna(axis=0, how='all')  # Remove rows with all NaN
df = df.dropna(axis=1, how='all')  # Remove columns with all NaN

print(df)

# df = df.astype(float)

##########################################################
def create_table(df, ax, font_size=font_size, header_height=header_height, cell_width=cell_width, first=True, second=False):
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
            
            
    # Apply green-to-red colormap to all data cells (skip row indices and column headers)
    numeric_data = df.values
    norm = plt.Normalize(numeric_data.min(), numeric_data.max())
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

##########################################################
fig, ax1 = plt.subplots(2, 1, figsize=(14,10))
ax1 = ax1[0]

create_table(df, ax1, font_size=font_size, header_height=header_height, cell_width=cell_width, first=True, second=False)

###########################################################    
# Duplicate the table in the second subplot
ax2 = plt.gca().figure.axes[1]

df2 = df.T * -1

create_table(df2, ax2, font_size=font_size, header_height=header_height, cell_width=cell_width, first=False, second=True)


plt.tight_layout()
plt.show()

