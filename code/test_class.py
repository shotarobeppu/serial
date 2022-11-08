# %%
import sys
import os
import copy

sys.path.append(os.path.abspath("src"))
import school
import student
import algorithm

import importlib

importlib.reload(school)
importlib.reload(student)
importlib.reload(algorithm)

DATA_PATH = "../data/"
EXCEL_PATH = DATA_PATH + "raw/UTMDへの提供データ（全学交換留学秋募集ダミーデータ）20221011更新.xlsx"

match = algorithm.Algorithm(EXCEL_PATH)
match.create_schools()

applicants = student.Student(EXCEL_PATH)
applicants.create_students()
applicants.create_preference()
applicants.add_preference(max_school_applied = 3)

match.set_graduate_ratio_threshold(applicants)
match.create_places()
match.init_algorithm(applicants)

# %%

for r in sorted(match.unassigned_list):

    applicant = applicants.select_student(r)

    schools_applied = list(dict.fromkeys([d['pref_school_name'] for d in applicant.pref.values()]))

    for s in range(len(schools_applied)):

        if r not in match.unassigned_list:
            continue

        school_name = schools_applied[s]
        school_dict = match.sdict[school_name]
        place_dict = match.places[school_name]
        applied_school = school.School(school_dict, applicants.mdict, place_dict)

        if not applicant.is_eligible(school_name):
            continue

        if applicant.dict["graduate"] and (
            applied_school.accept_graduate(match.graduate_ratio) is False
        ):
            continue

        match.accept_student(applied_school, applicant)

match.output_result(applicants)
save_path = "../data/output/"
match.save_result(save_path)


# %%

a_df = match.student_result_df.copy()

accepted_preference_rank = []

for index, row in a_df.iterrows():

    _assigned_school = row["assigned_school"]

    if _assigned_school is not None:
        _accepted_preference_rank = row["school"].index(row["assigned_school"]) if _assigned_school in row["school"] else len(row['school']) + 1 if (_assigned_school is not None) else None
    else:
        _accepted_preference_rank = None

    accepted_preference_rank.append(_accepted_preference_rank)

accepted_preference_rank = [i + 1 for i in accepted_preference_rank if i is not None]

print(
    "average preference of accepted: ",
    sum(accepted_preference_rank) / len(accepted_preference_rank),
)

print(
    "number of students not matched: ",
    match.student_result_df.assigned_school.isnull().sum(),
)
