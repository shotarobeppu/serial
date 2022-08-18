# %%
import sys
import os
import importlib

sys.path.append(os.path.abspath("src"))
import school
import student
import algorithm


# %%
importlib.reload(school)
importlib.reload(student)
importlib.reload(algorithm)

DATA_PATH = "../data/"
EXCEL_PATH = DATA_PATH + "raw/UTMDへの提供データ（全学交換留学秋募集ダミーデータ）20220804更新.xlsx"

match = algorithm.Algorithm(EXCEL_PATH)
match.create_schools()
match.create_students()
match.set_graduate_ratio_threshold()
match.create_places()
match.init_algorithm()

# while len(match.unassigned_list) > 0:

# loop through unassigned students by rank
for r in sorted(match.unassigned_list):

    applicant = student.Student(match.mdict[r])

    applicant.create_preference()

    # applicant_matched = []

    # loop through student's preferred schools
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

        # applicant_matched.append(match.matched_)

    # if sum(applicant_matched) == 0:

    #     match.unassigned_list.remove(r)
    #     match.failed_list.append(r)

match.output_result()

save_path = "../data/output/"

match.save_result(save_path)
# %%
