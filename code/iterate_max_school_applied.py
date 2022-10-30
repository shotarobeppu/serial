# %%
import sys
import os
import copy
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(os.path.abspath("src"))
import school
import student
import algorithm
import validate

import importlib

importlib.reload(school)
importlib.reload(student)
importlib.reload(algorithm)
importlib.reload(validate)

DATA_PATH = "../data/"
EXCEL_PATH = DATA_PATH + "raw/UTMDへの提供データ（全学交換留学秋募集ダミーデータ）20221011更新.xlsx"

# %%
def blockPrint():
    sys.stdout = open(os.devnull, 'w')
def enablePrint():
    sys.stdout = sys.__stdout__
blockPrint()

results = []
max_school_applied_list = range(3, 10)

for _ in tqdm(range(10)):

    for max_school_applied in max_school_applied_list:

        match = algorithm.Algorithm(EXCEL_PATH)
        match.create_schools()

        applicants = student.Student(EXCEL_PATH)
        applicants.create_students()
        applicants.create_preference()
        applicants.add_preference(max_school_applied = max_school_applied)

        match.set_graduate_ratio_threshold(applicants)
        match.create_places()
        match.init_algorithm(applicants)

        match.do_matching(applicants)

        match.output_result(applicants)

        val = validate.Validate()
        val.get_overview(match)

        result = [max_school_applied, val.num_students_unmatched]
        results.append(result)


# %%

simulation = pd.DataFrame(results, columns = ['max_applied', 'unmatched_students'])

ax = sns.scatterplot(x="max_applied", y="unmatched_students", data=simulation)
ax.set(xlabel='Maximum Number of Schools Possible to Apply', ylabel='Number of Unmatched Students', title = "Changing Number of Listed Schools")
fig = ax.get_figure()
fig.savefig("../output/sim.png") 
