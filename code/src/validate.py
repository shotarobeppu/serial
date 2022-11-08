# %%

import pandas as pd

# %%

class Validate():

    def __init__(self):
        pass

    def get_overview(self, match):

        a_df = match.student_result_df.copy()

        accepted_preference_rank = []

        for index, row in a_df.iterrows():

            _assigned_school = row["assigned_school"]

            if _assigned_school is not None:
                _accepted_preference_rank = row["school"].index(row["assigned_school"]) if _assigned_school in row["school"] else len(row['school']) + 1 if (_assigned_school is not None) else None
            else:
                _accepted_preference_rank = None

            accepted_preference_rank.append(_accepted_preference_rank)

        accepted_preference_rank = [i + 1 for i in accepted_preference_rank if i is not None]

        print(
            "average preference of accepted: ",
            sum(accepted_preference_rank) / len(accepted_preference_rank),
        )

        self.num_students_unmatched = match.student_result_df.assigned_school.isnull().sum()

        print(
            "number of students not matched: ",
            self.num_students_unmatched,
        )