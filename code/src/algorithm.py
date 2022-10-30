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

    def create_schools(self):

        semester_list = ['セメ', 'QP']

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
                    lambda x: "semester" if x in semester_list else "head"
                ),
                exist_cond=lambda d: d["派遣枠補足"].apply(
                    lambda x: False
                    if (x == " " or (isinstance(x, float) and np.isnan(x)) == True)
                    else True
                ),
                school_name=lambda d: d.index,
                accepted_student_rank=lambda d: [[] for _ in range(len(d))],
                accepted_period=lambda d: [[] for _ in range(len(d))],
                accepted_period_unit = lambda d: [[] for _ in range(len(d))]
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

            else:
                _slot_dict = {
                    "total": _total_slots,
                    "Autumn&Spring": _total_slots,
                    "Autumn": _total_slots,
                    "Spring": _total_slots,
                }

            if _school_dict["school_name"] == "スウァスモアカレッジ":
                _slot_dict = {
                    "total": 4,
                    "Autumn&Spring": 4,
                    "Autumn": 4,
                    "Spring": 4,
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

    def init_algorithm(self, student):

        self.unassigned_list = list(student.mdict.keys())
        self.failed_list = []

    def set_graduate_ratio_threshold(self, student):

        self.graduate_ratio = student.mdf["graduate"].sum() / len(student.mdf["graduate"])

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

            if _accepted_period_name in _school_place.keys():
                _school_place[_accepted_period_name] -= 1

            if _accepted_period_name == "Autumn&Spring":
                _school_place["Autumn"] -= 1
                _school_place["Spring"] -= 1

        elif type == "drop":

            _school_place["total"] += _accepted_period_unit
            if _accepted_period_name in _school_place.keys():
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

    def output_result(self, students):

        _student_result = {}

        for key in students.mdict.keys():

            _student_result[key] = {}
            _student = students.mdict[key]

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
                "accepted_period_unit",
                "unit",
                "place",
                "派遣枠補足",
            ]

            _assigned_school_info = {
                the_key: _school[the_key] for the_key in _school_values
            }

            _assigned_school_info['total_slots_used'] = self.places[key]['total']

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
