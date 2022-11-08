import pandas as pd
import numpy as np
import utils


class School:
    def __init__(self, school, student_dict, places_dict):

        self.dict = school
        self.place_unit = school["unit"]

        self.mdict = student_dict

        self.places_dict = places_dict

        self.vacant()

    def vacant(self):

        if self.places_dict["total"] > 0:
            self.vacant_ = True
        elif self.places_dict["total"] == 0:
            self.vacant_ = False

        return self.vacant_

    def accept_graduate(self, graduate_ratio_threshold):

        accepted_graduate_list = [
            self.mdict[e]["graduate"] for e in self.dict["accepted_student_rank"]
        ]
        self.graduate_ratio = (
            sum(accepted_graduate_list) / self.dict["place"]
            if self.dict["place"]
            else 0
        )

        if self.graduate_ratio > graduate_ratio_threshold:
            self.accept_graduate_ = False
        else:
            self.accept_graduate_ = True

        _graduate_programs = [
            "イェール大学(Fox International Fellowship Program)",
            "プリンストン大学（大学院）",
            "EHESS(社会科学高等研究院)",
        ]

        if self.dict["school_name"] in _graduate_programs:
            self.accept_graduate_ = True

        return self.accept_graduate_

    def modify_accepted_student_rank_list(self, student_dict, type="drop"):

        if type == "drop":
            self.dict["accepted_student_rank"].remove(student_dict["rank"])
            self.dict["accepted_period"].remove(student_dict["assigned_period_name"])
            self.dict["accepted_period_unit"].remove(student_dict["assigned_period_unit"])
        elif type == "add":
            self.dict["accepted_student_rank"].append(student_dict["rank"])
            self.dict["accepted_period"].append(student_dict["assigned_period_name"])
            self.dict["accepted_period_unit"].append(student_dict["assigned_period_unit"])
