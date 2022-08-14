import pandas as pd
import numpy as np

class Student:

    def __init__(self, student):
        self.student = student

    def eligible_to_apply(self, school_name):

        self.eligible_to_apply = True

        _preference_index = self.student['school'].index(school_name)
        _eligibility = self.student['school_eligible'][_preference_index]

        if isinstance(_eligibility, str):
            self.eligible_to_apply = False
        
        return self.eligible_to_apply



