import os                  
import numpy as np
import uproot
import pandas as pd

directory = '/pnfs/annie/persistent/processed/BeamFetcherV2/'

# uncomment if manually entering runs
#runs = [4763, 4764, 4765, 4766]
#file_list = ['beamfetcher_' + str(runs[i]) + '.root' for i in range(len(runs))]

# comment if manually entering runs
df = pd.read_csv('/exp/annie/app/users/doran/scripts/grid_runs_processing/ANNIE_SQL_RUNS.csv')
file_list = []
for runnum in df['runnum']:
    root_file = f'beamfetcher_{runnum}.root'
    if os.path.exists(directory + root_file):
        file_list.append(root_file)

# -------------------------------------- #

pot_875 = []; pot_860 = []; run_files = []

count = 1
for file in range(len(file_list)):

    print('\n', file_list[file], ' (', count, '/', len(file_list), ') loading...\n')
    count += 1

    cumulative_POT = 0; other_POT = 0; counter = 0

    root = uproot.open(directory + file_list[file])
    T = root['BeamTree']
    TOR875 = T['E_TOR875'].array(library="np")
    TOR860 = T['E_TOR860'].array(library="np")

    for j in range(len(TOR875)):

        if TOR875[j] >= 0:
            counter += 1
            cumulative_POT += TOR875[j]

        if TOR860[j] >= 0:
            other_POT += TOR860[j]

    print(cumulative_POT, 'e12 POT (E:TOR875)')
    print(other_POT, 'e12 POT (E:TOR860)')
    print('\n#########################################################\n')

    pot_875.append(cumulative_POT); pot_860.append(other_POT); run_files.append(file_list[file])


# Create a pandas DataFrame from the collected data
df_results = pd.DataFrame({
    'FILE': run_files,
    'E_TOR875[e12]': pot_875,
    'E_TOR860[e12]': pot_860
})


print(df_results)

# Sum the POT values across all runs
total_pot_875 = df_results['E_TOR875[e12]'].sum()
total_pot_860 = df_results['E_TOR860[e12]'].sum()

# Convert from e12 to e20 by dividing by 10^8
total_pot_875_e20 = total_pot_875 / 1e8
total_pot_860_e20 = total_pot_860 / 1e8

# Print the summed POT values
print(f'\nTotal E_TOR875[e20] across all runs: {total_pot_875_e20}')
print(f'Total E_TOR860[e20] across all runs: {total_pot_860_e20}')

df_results.to_csv('POT_2024_results.csv', index=False)

print('\n\ndone\n')
