# %%
import sys
import os
sys.path.append(os.path.abspath("src"))
import school
import student
import algorithm

DATA_PATH = "../data/"
EXCEL_PATH = DATA_PATH + "raw/UTMDへの提供データ（全学交換留学秋募集ダミーデータ）20220824更新.xlsx"

match = algorithm.Algorithm(EXCEL_PATH)
match.create_schools()
match.create_students()
match.set_graduate_ratio_threshold()
match.create_places()
match.init_algorithm()

# %%

for r in sorted(match.unassigned_list):

    applicant = student.Student(match.mdict[r])

    applicant.create_preference()

    for s in range(len(applicant.dict["school"])):

        if r not in match.unassigned_list:
            continue

        school_name = applicant.dict["school"][s]
        school_dict = match.sdict[school_name]
        place_dict = match.places[school_name]
        applied_school = school.School(school_dict, match.mdict, place_dict)

        if not applicant.is_eligible(school_name):
            continue

        if applicant.dict["graduate"] and (
            applied_school.accept_graduate(match.graduate_ratio) is False
        ):
            continue

        match.accept_student(applied_school, applicant)

match.output_result()
save_path = "../data/output/"
# match.save_result(save_path)


# %%

a_df = match.student_result_df.copy()

accepted_preference_rank = []

for index, row in a_df.iterrows():

    _assigned_school = row['assigned_school']

    if _assigned_school is not None:
        _accepted_preference_rank = row['school'].index(row['assigned_school'])
    else:
        _accepted_preference_rank = None

    accepted_preference_rank.append(_accepted_preference_rank)

accepted_preference_rank = [i+1 for i in accepted_preference_rank if i is not None]

print("average preference of accepted: ", sum(accepted_preference_rank)/len(accepted_preference_rank))

print("number of students not matched: ", match.student_result_df.assigned_school.isnull().sum())
