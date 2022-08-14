# %%
import sys, os
import importlib

import numpy as np

sys.path.append(os.path.abspath("src"))
import school
import student
import algorithm


# %%
importlib.reload(school)
importlib.reload(student)
importlib.reload(algorithm)

# %%

DATA_PATH = "../data/"
EXCEL_PATH = DATA_PATH + "raw/UTMDへの提供データ（全学交換留学秋募集ダミーデータ）20220804更新.xlsx"

match = algorithm.Algorithm(EXCEL_PATH)
match.create_school()
match.create_student()


# %%

unassigned_list = list(match.mdict.keys())

while len(unassigned_list) > 0:

    # loop through unassigned students by rank
    for r in unassigned_list:

        applicant = student.Student(match.mdict[r])

        # loop through student's preferred schools
        for s in range(len(applicant['school'])):

            if r not in unassigned_list:
                continue

            school_name = applicant['school'][s]
            school_dict = match.sdict[school_name]
            applied_school = school.School(school_dict, match.mdict)

            if student.eligible_to_apply() is False:
                continue

            if applicant['graduate'] and (applied_school.accept_graduate() is False):
                continue

            if applied_school.vacant is False:
                continue

