from school import School
from student import Student
import utils

import pandas as pd
import numpy as np
import os
import random


class Algorithm(School, Student):
    def __init__(self, excel_path):
        self.excel_path = excel_path

    def create_students(self):

        _mdf = pd.read_excel(
            self.excel_path,
            sheet_name="A 割り振り対象者",
            header=None,
            skiprows=2,
        )

        before = _mdf.loc[0, :].fillna(method="ffill")

        new_column = []
        for i in range(len(_mdf.loc[1, :])):

            current_variable = _mdf.loc[1, i]
            prefix = before[i]

            if isinstance(prefix, float) and np.isnan(prefix):
                new_variable = current_variable
            else:
                new_variable = str(prefix) + "_" + str(current_variable)

            new_column.append(new_variable)

        _mdf = _mdf.loc[2:, :]
        _mdf = _mdf.set_axis(new_column, axis=1)

        _mdf = _mdf.dropna(subset="学内選考順位").assign(
            graduate=lambda d: d["学部学生(U)/大学院生(G)"].apply(
                lambda x: 1 if x == "G" else 0
            ),
            student_type=lambda d: d["志望校優先/期間優先"].apply(
                lambda x: "length"
                if x == "期間優先"
                else "school"
                if x == "志望校優先"
                else "whatever"
            ),
        )

        mdict = {}
        for index, row in _mdf.iterrows():

            _id = row["ID"]
            rank = row["学内選考順位"]

            graduate = False
            if row["graduate"]:
                graduate = True

            school_columns = [column for column in _mdf.columns if "_大学名（和文）" in column]
            school = row[school_columns].tolist()
            school = [x for x in school if utils.check_nan(x) == False]

            num_school = len(school)

            school_period_columns = [
                column for column in _mdf.columns if "_希望\n学期" in column
            ]
            school_period = row[school_period_columns].tolist()[:num_school]

            'Other（AQ-WQ-SQ）'

            one_sem_list = [
                "Autumn",
                "Spring",
                "Other（Term3-Term1）",
                "Other（AQ）",
                "Other（AQ)",
                "Other（T3-T1）",
            ]

            two_sem_list = [
                'Other（WQ-SQ）',
                'Other（AQ-WQ）',
                'Other（T3-T1-T2）'
            ]

            three_sem_list = ['Other（AQ-WQ-SQ）']

            for i in range(len(school_period)):
                if school_period[i] == (
                    "Spring&Autumn"
                ):
                    school_period[i] = "Autumn&Spring"

            semester = [
                2 if s in two_sem_list else 1 if s in one_sem_list else 3 if s in three_sem_list else 0
                for s in school_period
            ]

            school_1sem_columns = [
                column for column in _mdf.columns if "_1学期のみ派遣可の場合" in column
            ]
            school_1sem = row[school_1sem_columns].tolist()[:num_school]
            one_sem = [
                2 if s in two_sem_list else 1 if (s == "Autumn" or "Spring") else 0
                for s in school_1sem
            ]

            school_eligible_columns = [
                column for column in _mdf.columns if "_要件" in column
            ]
            school_eligible = row[school_eligible_columns].tolist()[:num_school]

            head = [1 if isinstance(s, str) else 0 for s in school]

            student_type = row["student_type"]

            period_preference = list(zip(school_period, school_1sem))
            period_preference_unit = list(zip(semester, one_sem))

            mdict[rank] = {
                "rank": rank,
                "id": _id,
                "graduate": graduate,
                "school": school,
                "school_period": school_period,
                "school_1sem": school_1sem,
                "school_eligible": school_eligible,
                "semester": semester,
                "one_sem": one_sem,
                "period_preference": period_preference,
                "period_preference_unit": period_preference_unit,
                "head": head,
                "total_school": num_school,
                "student_type": student_type,
                "assigned_school": None,
                "assigned_period_name": None,
                "assigned_period_unit": None,
            }

        self.mdf = _mdf
        self.mdict = mdict

    def create_schools(self):

        _sdf = (
            pd.read_excel(
                self.excel_path,
                sheet_name="B 割り振り先の枠数",
                header=1,
            )
            .set_index("大学名（和）")
            .assign(
                place=lambda d: d["20XX-20XX派遣枠"].apply(
                    lambda x: 10 if x == "若干" else x
                ),
                unit=lambda d: d["Unnamed: 3"].apply(
                    lambda x: "semester" if x == ("セメ" or "QP") else "head"
                ),
                exist_cond=lambda d: d["派遣枠補足"].apply(
                    lambda x: False
                    if (x == " " or (isinstance(x, float) and np.isnan(x)) == True)
                    else True
                ),
                school_name=lambda d: d.index,
                accepted_student_rank=lambda d: [[] for _ in range(len(d))],
                accepted_period=lambda d: [[] for _ in range(len(d))],
            )
        )

        self.sdf = _sdf
        self.sdict = _sdf.to_dict("index")

    def create_places(self):

        place_dict = {}

        for school in list(self.sdict.keys()):

            place_dict[school] = {}

            _school_dict = self.sdict[school]

            _condition = _school_dict["exist_cond"]
            _total_slots = _school_dict["place"]

            if _condition:

                if _school_dict["unit"] == "semester":

                    _slot_dict = {
                        "total": _total_slots,
                        "Autumn&Spring": _total_slots,
                        "Autumn": _total_slots / 2,
                        "Spring": _total_slots / 2,
                    }

                if _school_dict["school_name"] == "スウァスモアカレッジ":

                    _slot_dict = {
                        "total": 4,
                        "Autumn&Spring": 4,
                        "Autumn": 4,
                        "Spring": 4,
                    }

            else:
                _slot_dict = {
                    "total": _total_slots,
                    "Autumn&Spring": _total_slots,
                    "Autumn": _total_slots,
                    "Spring": _total_slots,
                }

            place_dict[school] = _slot_dict

        self.places = place_dict

    def create_additional_preference(self, max_school=6):
        def _generate_all_preferences(self):

            for i in range(1, len(self.mdict) + 1):

                pass

        pref_dict = {}
        d_idx = 0

        for i in range(1, len(self.mdict) + 1):

            _mdict = self.mdict[i]
            _student = Student(_mdict)

            _student.create_preference()

            for p in range(len(_student.pref)):

                pref_dict[d_idx] = _student.pref[p]

                d_idx += 1

        for i in range(1, len(self.mdict) + 1):

            _mdict = self.mdict[i]
            max_additional_school = max_school - _mdict["total_school"]

    def init_algorithm(self):

        self.unassigned_list = list(self.mdict.keys())
        self.failed_list = []

    def set_graduate_ratio_threshold(self):

        self.graduate_ratio = self.mdf["graduate"].sum() / len(self.mdf["graduate"])

    def accept_student(self, school, student):
        """
        Match school to student given its constraints and also the rankings.
        Remove students that is inferior to the incoming students. Inferior
        meaning graduates, rank, semester constraints.

        school and student is instance of School and Student respectively
        """

        self.matched_ = False

        _student_rank = student.dict["rank"]
        print(_student_rank)
        _school_name = school.dict["school_name"]
        print(_school_name)

        # check student is already assigned or not from the unassigned list
        if _student_rank not in self.unassigned_list:
            print("not in unassigned")
            return

        # check all the students with lower rank are removed for the better incoming student to allow his/her best choice
        _current_student_assigned_to_school = school.dict["accepted_student_rank"]
        _worst_rank_students = [
            i for i in _current_student_assigned_to_school if i > _student_rank
        ]
        print(f"worst rank in assigned to school {_worst_rank_students}")

        if len(_worst_rank_students) != 0:
            for _rank in _worst_rank_students:
                dropped_student = self.mdict[_rank].copy()
                print(dropped_student)
                school.modify_accepted_student_rank_list(dropped_student, type="drop")
                self.modify_unassigned(dropped_student, type="add")
                self.modify_place(school, dropped_student, type="drop")

                print("dropped worst rank")

        if school.vacant() is False:
            print("no more place")
            return

        student.filter_preference_by_slot(
            places_dict=self.places, school_name=_school_name
        )

        if student.possible_to_assign_:
            student.get_best_choice()
            student.assign_school_to_student()

            school.modify_accepted_student_rank_list(student.dict, type="add")

            self.modify_place(school, student.dict, type="add")
            self.modify_unassigned(student.dict, type="drop")

            self.matched_ = True

            print("matched!")

    def modify_place(self, school, student_dict, type="drop"):

        _school_name = school.dict["school_name"]

        _accepted_period_name = student_dict["assigned_period_name"]
        _accepted_period_unit = student_dict["assigned_period_unit"]

        _school_place = self.places[_school_name].copy()

        if type == "add":

            _school_place["total"] -= _accepted_period_unit
            _school_place[_accepted_period_name] -= 1

            if _accepted_period_name == "Autumn&Spring":
                _school_place["Autumn"] -= 1
                _school_place["Spring"] -= 1

        elif type == "drop":

            _school_place["total"] += _accepted_period_unit
            _school_place[_accepted_period_name] += 1

            if _accepted_period_name == "Autumn&Spring":
                _school_place["Autumn"] += 1
                _school_place["Spring"] += 1

        self.places[_school_name] = _school_place

    def modify_unassigned(self, student_dict, type="drop"):

        if type == "drop":
            self.unassigned_list.remove(student_dict["rank"])
        elif type == "add":
            self.unassigned_list.append(student_dict["rank"])

    def output_result(self):

        _student_result = {}

        for key in self.mdict.keys():

            _student_result[key] = {}
            _student = self.mdict[key]

            _student_values = [
                "rank",
                "school",
                "assigned_school",
                "assigned_period_name",
                "assigned_period_unit",
            ]

            _assigned_student_info = {
                the_key: _student[the_key] for the_key in _student_values
            }

            _student_result[key] = _assigned_student_info

        _school_result = {}

        for key in self.sdict.keys():

            _school_result[key] = {}
            _school = self.sdict[key]

            _school_values = [
                "accepted_student_rank",
                "accepted_period",
                "unit",
                "place",
                "派遣枠補足",
            ]

            _assigned_school_info = {
                the_key: _school[the_key] for the_key in _school_values
            }

            _school_result[key] = _assigned_school_info

            self.student_result = _student_result
            self.school_result = _school_result

            self.student_result_df = pd.DataFrame.from_dict(
                _student_result, orient="index"
            )
            self.school_result_df = pd.DataFrame.from_dict(
                _school_result, orient="index"
            )

    def save_result(self, path):

        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)

        self.student_result_df.to_pickle(path + "student.pkl")
        self.school_result_df.to_pickle(path + "school.pkl")

        writer = pd.ExcelWriter(path + "result.xlsx", engine="xlsxwriter")
        self.student_result_df.to_excel(writer, sheet_name="student", index=False)
        self.school_result_df.to_excel(writer, sheet_name="school")
        writer.save()
