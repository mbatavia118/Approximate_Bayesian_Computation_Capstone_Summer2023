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
 

#Run the initialization, create workspace, open Julie's model
print("Initializing...")

nl4py.initialize("/apps/software/standard/compiler/gcc/9.2.0/netlogo/6.2.1") 
n = nl4py.create_headless_workspace() 
n.open_model("/home/vgg2zw/Full_Model_Abbreviated/Pulmonary_Histology_Python_7302023_abbreviated_no-endtick.nlogo") 


#sample parameter values for the experiment
as_et_values = np.random.beta(1, 1, size=20)
as_et_values = np.round((as_et_values*5), 3) #multiply by 5 (max for this model) and round to 3 decimal places


# Loop through each value in the original list and duplicate it 36 times
as_et_values_dup = []
for value in as_et_values:
    as_et_values_dup.extend([value] * 36)

#check
#print(as_et_values_dup)
print("Parameter values sampled...")

#Get parameter names
parNames = n.get_param_names() 
#print(parNames)
#'thy1ps-count', 'thy1ns-count', 'set-tnf-thresh', 'set-il1b-thresh', 'transition?', 'transition-threshold', 'tgfbint', 'colvar', 'as-entry-threshold']

#Iterate through sampled values
print("Running simulations...")

#Empty lists to collect results
Ticks = []
Fibrosis_score = []
Alv_count = []
Final_thy1n = []
Final_thy1p = []
setup = []

for val in as_et_values_dup:
    
    #Get the simulation ready to run
    n.command("reset-ticks") #might not need this here, but won't hurt
    n.command("setup")

    #set all params, with as-entry-threshold to the randomly sampled value
    parValues = [90, 10, 50, 50, 1, 0.2, 700, 166.8, val]
    for name, value in zip(parNames,parValues):
        cmd = 'set {0} {1}'.format(name, value)
        n.command(cmd)

  
    #Run the model for 1095 time steps
    n.command("repeat 1095 [go]")

    #Collect metrics at the end of the simulation's run
    ticks = n.report("ticks")
    fibrosis_score = n.report("fibrosis-score")
    alv_count = n.report("alv-count")
    final_thy1n = n.report("final-thy1n")
    final_thy1p = n.report("final-thy1p")
    
    Ticks.append(ticks)
    Fibrosis_score.append(fibrosis_score)
    Alv_count.append(alv_count)
    Final_thy1n.append(final_thy1n)
    Final_thy1p.append(final_thy1p)
    setup.append(parValues)


#save the results
final_results = {'Param Val': as_et_values_dup, 'ticks': Ticks, 'fibrosis-score': Fibrosis_score, 
'alv-count': Alv_count, 'final-thy1n': Final_thy1n, 'final-thy1p': Final_thy1p, 'Setup Commands': setup}

df = pd.DataFrame(final_results)
df.to_csv("0.2_no_parallel2.csv", index=False)


#Use the approximate Bayesian computation Jupyter notebook to generate a posterior distribution with these results.





