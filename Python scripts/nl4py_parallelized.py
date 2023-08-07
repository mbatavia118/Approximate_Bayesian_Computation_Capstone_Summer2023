#Packages
print("Loading packages...")

import random 
import sys 
import time 
import os 
import pandas as pd 
import numpy as np 
import multiprocessing 
import matplotlib.pyplot as plt 
from deap import base, creator, tools, algorithms 
import py4j 
import nl4py 
from scipy.stats import chi2_contingency
from typing import List

 

#initialize netlogo
print("Initializing...")
nl4py.initialize("/apps/software/standard/compiler/gcc/9.2.0/netlogo/6.2.1") #path to netlogo program file

#sample parameter values for the experiment
as_et_values = np.random.beta(1, 1, size=100)
as_et_values = np.round((as_et_values*5), 3) #multiply by 5 (max for this model) and round to 3 decimal places


# Loop through each value in the original list and duplicate it 36 times
# 36 is the same size as the validation data set
as_et_values_dup = []
for value in as_et_values:
    as_et_values_dup.extend([value] * 36)

#check
#print(as_et_values_dup)
print("Parameter values sampled...")

#define the model
model = "./Full_Model_Abbreviated/Pulmonary_Histology_Python_7302023_abbreviated_no-endtick.nlogo"

#define simulation callback function that returns a list of setup commands
def run_simulation(etval) -> List[str]:
    
    #Define parameters - can be changed depending what you want to test
    thy1ps_count = 90
    thy1ns_count = 10
    tnf_thresh = 50
    il1b_thresh = 50
    transition = 1
    transition_threshold = 0.2
    tgfbint = 700
    colvar = 166.8
    as_entry_threshold = etval
    
    #Define setup commands
    setup_commands = ["reset-ticks", "setup", f"set thy1ps-count {thy1ps_count}", f"set thy1ns-count {thy1ns_count}",
     f"set set-tnf-thresh {tnf_thresh}", f"set set-il1b-thresh {il1b_thresh}", f"set transition? {transition}", 
     f"set transition-threshold {transition_threshold}", f"set tgfbint {tgfbint}", 
     f"set colvar {colvar}", f"set as-entry-threshold {as_entry_threshold}"]
    
    return setup_commands
    

#metrics to report
reporters = ["ticks", "fibrosis-score", "alv-count", "final-thy1n", "final-thy1p"]


#use run_experiment to run n simulations and return results
#this configuration will run 3 sets of 365 steps and report metrics at 365, 730, and 1095
#stop_at_tick=365 will output reporters for every single tick point
print("Running simulations and collecting results...")
results = nl4py.run_experiment(model, run_simulation, as_et_values_dup, reporters, go_command = "repeat 365 [go]", stop_at_tick = 3)
print("Finished running simulations...")

#save the results in a data frame
print("Saving results...")
df = pd.DataFrame(results)

# Define a regular expression pattern to extract the numeric values after "-threshold "
pattern = r'as-entry-threshold (\d+(?:\.\d+)?)'

# Use str.extract() to extract the numeric values from the 'Setup Commands' column using the defined pattern
df['Param Value'] = df['Setup Commands'].str.extract(pattern)

# Convert the extracted numeric values to floats in the new column
df['Param Value'] = df['Param Value'].astype(float)

#Sort by the Param Value to group all runs of the same value together
df_sorted = df.sort_values(by='Param Value', ascending=True)

#save
df_sorted.to_csv("experiment1_reduced_data.csv", index=False)

#check
#print(results)

#once CSV is generated, move to local machine
#use the approximate bayesian computation jupyter notebook to generate a posterior distribution










