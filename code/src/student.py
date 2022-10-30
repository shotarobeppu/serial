import pandas as pd
import numpy as np
import utils


class Student:
    def __init__(self, excel_path):

        _mdf = pd.read_excel(
            excel_path,
            sheet_name="A 割り振り対象者",
            header=None,
            skiprows=2,
        )

        self.mdf = _mdf

        return

    def create_students(self):

        _mdf = self.mdf.copy()

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

            one_sem_list = [
                "Autumn",
                "Spring",
                "Other（Term3-Term1）",
                "Other（AQ）",
                "Other（AQ)",
                "Other（T3-T1）",
            ]

            two_sem_list = ["Autumn&Spring", "Other（WQ-SQ）", "Other（AQ-WQ）", "Other（T3-T1-T2）"]

            three_sem_list = ["Other（AQ-WQ-SQ）"]

            for i in range(len(school_period)):
                if school_period[i] == ("Spring&Autumn"):
                    school_period[i] = "Autumn&Spring"

            semester = [
                2
                if s in two_sem_list
                else 1
                if s in one_sem_list
                else 3
                if s in three_sem_list
                else 0
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

    def select_student(self, student_rank):

        self.dict = self.mdict[student_rank]

        return self

    def is_eligible(self, school_name):

        _preference_index = self.dict["school"].index(school_name)
        _eligibility = self.dict["school_eligible"][_preference_index]

        if isinstance(_eligibility, str):
            self.is_eligible_ = False
        else:
            self.is_eligible_ = True

        return self.is_eligible_

    def create_preference(self):

        _type = self.dict["student_type"]

        pref = {}

        i = 0

        if _type == "whatever" or "school":

            for s in range(len(self.dict["school"])):

                _school = self.dict["school"][s]
                _period_preference = self.dict["period_preference"][s]
                _period_preference_unit = self.dict["period_preference_unit"][s]

                if self.is_eligible(_school) is False:
                    continue

                for p in range(len(_period_preference)):

                    if _period_preference[p] == 0:
                        continue

                    pref[i] = {
                        "pref_school_name": _school,
                        "pref_school_rank": s,
                        "pref_period_rank": p,
                        "pref_period": _period_preference[p],
                        "pref_period_unit": _period_preference_unit[p],
                        "head": 1,
                    }

                    i += 1

        elif _type == "length":

            for p in range(2):
                for s in range(len(self.dict["school"])):

                    _school = self.dict["school"][s]
                    _period_preference = self.dict["period_preference"][s][p]

                    if _period_preference == 0:
                        continue

                    _period_preference_unit = self.dict["period_preference_unit"][s][p]

                    pref[i] = {
                        "pref_school_name": _school,
                        "pref_school_rank": s,
                        "pref_period_rank": p,
                        "pref_period": _period_preference,
                        "pref_period_unit": _period_preference_unit,
                        "head": 1,
                    }

                    i += 1

        self.pref = pref

    def filter_preference_by_slot(self, places_dict, school_name):
        """
        Dict of available slots with respect to
        "total", "Autumn", "Spring" and "Autumn&Spring"
        """

        _eligible_pref = self.pref.copy()

        place_dict = places_dict[school_name]

        for d in list(self.pref.keys()):

            if _eligible_pref[d]["pref_school_name"] != school_name:
                del _eligible_pref[d]
                continue

            _preferred_period = self.pref[d]["pref_period"]

            if place_dict["total"] < _eligible_pref[d]["pref_period_unit"]:
                del _eligible_pref[d]
                continue

            if _preferred_period in place_dict.keys() and place_dict[_preferred_period] == 0:
                del _eligible_pref[d]
                continue

        if len(_eligible_pref) == 0:
            self.possible_to_assign_ = False
        else:
            self.possible_to_assign_ = True

        self.eligible_pref = _eligible_pref

    def get_best_choice(self):

        _pref = self.pref.copy()

        self.best_pref = _pref[min(self.eligible_pref)]

    def assign_school_to_student(self):

        self.dict["assigned_school"] = self.best_pref["pref_school_name"]
        self.dict["assigned_period_name"] = self.best_pref["pref_period"]
        self.dict["assigned_period_unit"] = self.best_pref["pref_period_unit"]
        self.dict["pref"] = self.pref

    def unassign_school_from_student(self):

        self.dict["assigned_school"] = None
        self.dict["assigned_period_name"] = None
        self.dict["assigned_period_unit"] = None
        self.dict["pref"] = None
