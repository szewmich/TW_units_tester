import openpyxl
import pandas as pd
import os
import gc

import battle_sim_main

DEI = True
WARHAMMER = False

# DATA PARAMETERS
if WARHAMMER:
    path = 'warhammer_data.xlsx'
if DEI:
    path = 'dei_data.xlsx'
# wb_obj = openpyxl.load_workbook(path)
# ex = wb_obj.active

out_dir = 'results_v02\\'

def cross_calc(faction_A, faction_B):
    """
    Function to calculate the cross comparison between two factions.
    """
    print(f"Calculating cross comparison for {faction_A} vs {faction_B}...")

    ######################################################################################################################
    # READ EXCEL DATA
    ######################################################################################################################

    A_faction_data = df.query('faction == @faction_A')
    B_faction_data = df.query('faction == @faction_B')
    # print(A_faction_data)


    A_unit_IDs = A_faction_data.index.tolist()
    A_unit_names = A_faction_data['name'].tolist()
    A_unit_dict = dict(zip(A_unit_IDs, A_unit_names))
    # print(A_unit_dict)

    B_unit_IDs = B_faction_data.index.tolist()
    B_unit_names = B_faction_data['name'].tolist()
    B_unit_dict = dict(zip(B_unit_IDs, B_unit_names))

    cols = ['A_unit']
    cols.extend(B_unit_names)

    results_df = pd.DataFrame(columns=cols)
    print(results_df)

    # c = 0
    for ID_A in A_unit_IDs:
        cat_A = A_faction_data.loc[ID_A, 'cat']
        
        current_row = [A_unit_dict[ID_A]]

        for ID_B in B_unit_IDs:
            cat_B = B_faction_data.loc[ID_B, 'cat']

            if cat_A == 'inf' and cat_B == 'inf':
                A_gold_adv = battle_sim_main.run_sim(ID_A, ID_B)
                #A_gold_adv = 1
            else:
                A_gold_adv = None
            
            current_row.append(A_gold_adv)
            
        print(current_row)
        results_df = pd.concat([results_df, pd.DataFrame([current_row], columns=cols)], ignore_index=True)
        # c +=1

        # if c == 2:
        #     break


    print(results_df)

    out_path = out_dir + faction_A + '_vs_' + faction_B + '_results.csv'
    results_df.to_csv(out_path, index=False)

if __name__ == "__main__":
    # faction_A = 'Iceni'
    # faction_B = 'Nabatea'
    # factions = ['Maurya', 'Macedon', 'Epirus', 'Bactria', 'Media', 'Odrysian', 'Getae', 'Boii', 'Scordisci', 'Lugii', 'Cimbri', 'Iceni', 'Caledones', 'Iweriu', 'Nabatea', 'Medewi']
    # factions = ['Cimbri']
    df = pd.read_excel(path, sheet_name="DATA", header = 0, index_col = 0)
    factions = df['faction'].unique().tolist()

    A_set = ['Armenia', 'Pontos', 'Caledones', 'Iweriu', 'Bosporus', 'Parthia', 'Athens', 'Sparta']
    # for faction_A in factions:
    # faction_A = 'Galatia'
    for faction_A in A_set:
        for faction_B in factions:
            if faction_A != faction_B:
                finished_results = os.listdir(out_dir)
                name_1 = faction_A + '_vs_' + faction_B + '_results.csv'
                name_2 = faction_B + '_vs_' + faction_A + '_results.csv'
                if name_1 not in finished_results and name_2 not in finished_results:
                    cross_calc(faction_A, faction_B)
                    print(f"Finished calculating {faction_A} vs {faction_B}")
                    gc.collect()
                    
                