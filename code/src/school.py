import pandas as pd
import numpy as np

class School:

    def __init__(self, school, student_dict):

        self.school = school
        self.place_unit = school["unit"]

        self.mdict = student_dict

        self.is_vacant()
    
    def is_vacant(self):

        if self.school['place'] > 0:
            self.vacant = True
        elif self.school['place'] == 0:
            self.vacant = False

    def accept_graduate(self, graduate_ratio_threshold):

        accepted_graduate_list = [self.mdict[e]['graduate'] for e in self.school['accepted_studet_rank']]
        self.school.graduate_ratio = sum(accepted_graduate_list)/len(accepted_graduate_list)

        if self.school.graduate_ratio > graduate_ratio_threshold:
            self.accept_graduate = False
        else:
            self.accept_graduate = True

        return self.no_more_graduate

    def assign_student(self, add_student):

        self.school['accepted_studet_rank'].append(add_student['rank'])
        self.school['place'] -= add_student['accepted_period']
    
    def unassign_student(self, drop_student):

        self.school['accepted_student_rank'].remove(drop_student['rank'])
        self.school['place'] += drop_student['accepted_period']
