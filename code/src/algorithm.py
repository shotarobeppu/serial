from school import School
from student import Student
import utils

import pandas as pd
import numpy as np


class Algorithm():

    def __init__(self, excel_path):
        self.excel_path = excel_path
    
    def create_student(self):

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
            graduate=lambda d: d["学部学生(U)/大学院生(G)"].apply(lambda x: 1 if x == "G" else 0)
        )

        self.graduate_ratio = _mdf["graduate"].sum() / len(_mdf["graduate"])

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

            school_period_columns = [column for column in _mdf.columns if "_希望\n学期" in column]
            school_period = row[school_period_columns].tolist()[:num_school]
            semester = [
                2 if s == "Autumn&Spring" else 1 if (s == "Autumn" or "Spring") else 0
                for s in school_period
            ]

            school_1sem_columns = [column for column in _mdf.columns if "_1学期のみ派遣可の場合" in column]
            school_1sem = row[school_1sem_columns].tolist()[:num_school]
            one_sem = [
                2 if s == "Autumn&Spring" else 1 if (s == "Autumn" or "Spring") else 0
                for s in school_1sem
            ]

            school_eligible_columns = [column for column in _mdf.columns if "_要件" in column]
            school_eligible = row[school_eligible_columns].tolist()[:num_school]

            head = [1 if isinstance(s, str) else 0 for s in school]

            mean_semester = np.mean(semester)
            mean_one_sem = np.mean(one_sem)

            student_type = (
                "length"
                if (mean_semester == 2 and one_sem[0] == 0)
                else "school"
                if (one_sem[0] != 1 and mean_semester != 2)
                else "whatever"
            )

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
                "head": head,
                "total_school": num_school,
                "student_type": student_type,
            }

        self.mdf = _mdf
        self.mdict = mdict

    def create_school(self):

        _sdf = (
            pd.read_excel(
                self.excel_path,
                sheet_name="B 割り振り先の枠数",
                header=1,
            )
            .set_index("大学名（和）")
            .assign(
                place=lambda d: d["20XX-20XX派遣枠"].apply(lambda x: 1 if x == "若干" else x),
                unit=lambda d: d["Unnamed: 3"].apply(
                    lambda x: "semester" if (x == "セメ" or "QP") else "head"
                ),
                exist_cond=lambda d: d["派遣枠補足"].apply(
                    lambda x: False
                    if (x == " " or (isinstance(x, float) and np.isnan(x)) == True)
                    else True
                ),
                school_name = lambda d: d.index
            )
        )

        self.sdf = _sdf
        self.sdict = _sdf.to_dict("index")

    


