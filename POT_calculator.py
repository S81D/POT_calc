import os, re              
import numpy as np
import uproot
import pandas as pd

# ------------------------------------------------- #
# modify accordingly

# BeamFetcherV2 root file location
directory = '/pnfs/annie/persistent/processed/processingData_EBV2/BeamFetcherV2/'
pattern = re.compile(r'beamfetcher_(\d+)\.root')

# enter range of runs to extract information
start_run = 5668 
end_run = 3207

which_metric = 'POT'   # 'POT' or 'HC'  (horn current)

# ------------------------------------------------- #

runs = []
for filename in os.listdir(directory):
    match = pattern.match(filename)
    if match:
        if end_run <= int(match.group(1)) <= start_run:
            runs.append(int(match.group(1)))

runs.sort()

if which_metric == 'POT':
    pot_875 = []; pot_875_er = []
    pot_860 = []; pot_860_er = []
elif which_metric == 'HC':
    horn_current = []; horn_current_er = []

run_files = []

count = 1
for file in range(len(file_list)):

    print('\n', file_list[file], ' (', count, '/', len(file_list), ') loading...\n')
    count += 1

    if which_metric == 'POT':
        POT_per_spill_860 = []; POT_per_spill_875 = []
        
    elif which_metric == 'HC':
        HC = []
    
    counter = 0

    try:

        root = uproot.open(directory + file_list[file])
        T = root['BeamTree']

        if which_metric == 'POT':
            TOR875 = T['E_TOR875'].array(library="np")
            TOR860 = T['E_TOR860'].array(library="np")
            for j in range(len(TOR860)):
                #if TOR860[j] >= 0:    # enable for more inclusive
                if 12 >= TOR860[j] >= 0.1:   # since we are taking the med and stdev, it helps to only include reasonable values
                    counter += 1
                    POT_per_spill_860.append(TOR860[j])
                    POT_per_spill_875.append(TOR875[j])
                    
        elif which_metric == 'HC':
            THCURR = T['E_THCURR'].array(library="np")
            for j in range(len(THCURR)):
                #if THCURR[j] >= 0:
                if 185 >= THCURR[j] >= 165:
                    HC.append(THCURR[j])

       
    # if it can't grab the information
    except uproot.exceptions.KeyInFileError:
        print(f"Warning: 'BeamTree' not found in {file}. Filling with zeros.")
    except Exception as e:
        print(f"Error processing {file}: {e}")


    # calculate the median and stdev per run
    if which_metric == 'POT':
        POT_per_spill_860 = np.array(POT_per_spill_860)
        POT_per_spill_875 = np.array(POT_per_spill_875)
        if len(POT_per_spill_860) > 0:
            med_POT_860 = np.median(POT_per_spill_860)
            std_POT_860 = np.std(POT_per_spill_860)   # standard deviation
            med_POT_875 = np.median(POT_per_spill_875)
            std_POT_875 = np.std(POT_per_spill_875)
        
        # print 860 stats
        print(f"median POT per spill: {med_POT_860:.3e} ± {std_POT_860:.3e} (std dev)")
        else:
            med_POT_860, std_POT_860, med_POT_875, std_POT_875 = 0, 0, 0, 0    # just assign as 0 if there is a hickup

        pot_860.append(med_POT_860); pot_860_er.append(std_POT_860)
        pot_875.append(med_POT_875); pot_875_er.append(std_POT_875)

    
    elif which_metric == 'HC':
        HC = np.array(HC)
        if len(HC) > 0:
            med_HC = np.median(HC)
            std_HC = np.std(HC)   # standard deviation
    
            print(f"median intensity per spill: {med_HC:.3e} ± {std_HC:.3e} (std dev)")
        else:
            med_HC, std_HC = 0, 0

        horn_current.append(med_HC); horn_current_er.append(std_HC)


    run_files.append(file_list[file])

    print('\n#########################################################\n')


# Create a pandas DataFrame from the collected data

if which_metric == 'POT':
    df_results = pd.DataFrame({
        'FILE': run_files,
        'SPILL_POT_TOR875[e12]': pot_875,
        'SPILL_POT_TOR875_ER[e12]': pot_875_er,
        'SPILL_POT_TOR860[e12]': pot_860,
        'SPILL_POT_TOR860_ER[e12]': pot_860_er
    })
    df_results.to_csv('POT_results.csv', index=False)   # modify name if needed

elif which_metric == 'HC':
    df_results = pd.DataFrame({
    'FILE': run_files,
    'HORN_CURRENT': horn_current,
    'HORN_CURRENT_ER': horn_current_er
    })
    df_results.to_csv('Horn_current_results.csv', index=False)   # modify name if needed


print(df_results)


# # # # # # # # # # # # # # # # # # #
# optional: print the total POT
if which_metric == 'POT':
    total_pot_875 = df_results['SPILL_POT_TOR875[e12]'].sum()   # Sum the POT values across all runs
    total_pot_860 = df_results['SPILL_POT_TOR860[e12]'].sum()

    # Convert from e12 to e20 by dividing by 10^8
    total_pot_875_e20 = total_pot_875 / 1e8
    total_pot_860_e20 = total_pot_860 / 1e8

    print(f'\nTotal E_TOR875[e20] across all runs: {total_pot_875}')
    print(f'Total E_TOR860[e20] across all runs: {total_pot_860}')

# # # # # # # # # # # # # # # # # # #

print('\n\ndone\n')
