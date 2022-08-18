import pandas as pd
import numpy as np


class Student:
    def __init__(self, student):
        self.dict = student

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

                _school = self.dict['school'][s]
                _period_preference = self.dict['period_preference'][s]
                _period_preference_unit = self.dict['period_preference_unit'][s]

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
                        "head": 1
                    }

                    i += 1

        elif _type == "length":

            for p in range(2):
                for s in range(len(self.dict["school"])):

                    _school = self.dict['school'][s]
                    _period_preference = self.dict['period_preference'][s][p]

                    if _period_preference == 0:
                        continue

                    _period_preference_unit = self.dict['period_preference_unit'][s][p]

                    pref[i] = {
                        "pref_school_name": _school,
                        "pref_school_rank": s,
                        "pref_period_rank": p,
                        "pref_period": _period_preference,
                        "pref_period_unit": _period_preference_unit,
                        "head": 1
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

            if _eligible_pref[d]['pref_school_name'] != school_name:
                del _eligible_pref[d]
                continue

            _preferred_period = self.pref[d]['pref_period']

            if place_dict['total'] < _eligible_pref[d]['pref_period_unit']:
                del _eligible_pref[d]
                continue

            if place_dict[_preferred_period] == 0:
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

        self.dict['assigned_school'] = self.best_pref['pref_school_name']
        self.dict['assigned_period_name'] = self.best_pref['pref_period']
        self.dict['assigned_period_unit'] = self.best_pref['pref_period_unit']
        self.dict['pref'] = self.pref

    def unassign_school_from_student(self):

        self.dict['assigned_school'] = None
        self.dict['assigned_period_name'] = None
        self.dict['assigned_period_unit'] = None
        self.dict['pref'] = None
        




            