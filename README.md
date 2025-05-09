# TW_units_tester

This script can be used to simulate and predict the outcome of combat between units in Total War games with statistical approach.
Current version 1.0 has the following games' base mechanics implemented:
- TW: Rome 2 with 'Divide Et Impera' mod
- TW: Warhammer 3

Both melee and missile combat is simulated. Besides basic combat mechanics (calculation of hit chance, damage reduction by armour, entity deaths), special effects can be conditionally activated for different units during combat, providing certain buffs/debuffs, according to the defined database.
 
Calculation accounts for cost of the unit (in multiplayer) to determine the cost-efficiency of deploying certain unit vs another.

"Unit cards" database is provided in excel file. "Effect database" is a python module, where activation conditions and bonuses to unit stats are defined.


There is lots of mechanics missing, like attack range, formation effects, impact damage... But this project was never meant to be a functional game engine - only a calculator that does the math behind unit stats.

Usage:
1. FILL DATABASE:
Neither of aforementioned databases is complete and matching any specific version of the game. Treat it as a sandbox for customized checks.
2. UNIT CHOICE:
Choose unit A and unit B. Decide if units are defined by_ID or by_name, and respectively define "choice_A" & "choice_B" or "ID_A" & "ID_B". Names/IDs must match those in excel file. Decide if basic (English) or native unit names will be used for printed output (Rome 2 DEI mod feature).
3. GAME PARAMETERS:
Set up battle conditions - more info on that in the script's comments 
