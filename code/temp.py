# %%
import pandas as pd
import numpy as np

DATA_PATH = "../data/"
excel_path = DATA_PATH + "raw/UTMDへの提供データ（全学交換留学秋募集ダミーデータ）20220804更新.xlsx"

# %%
mdf = pd.read_excel(
    excel_path,
    sheet_name="A 割り振り対象者",
    header=None,
    skiprows=2,
)

before = mdf.loc[0, :].fillna(method="ffill")

new_column = []
for i in range(len(mdf.loc[1, :])):

    current_variable = mdf.loc[1, i]
    prefix = before[i]

    if isinstance(prefix, float) and np.isnan(prefix):
        new_variable = current_variable
    else:
        new_variable = str(prefix) + "_" + str(current_variable)

    new_column.append(new_variable)

mdf = mdf.loc[2:, :]
mdf = mdf.set_axis(new_column, axis=1)

mdf = mdf.dropna(subset="学内選考順位").assign(
    graduate=lambda d: d["学部学生(U)/大学院生(G)"].apply(lambda x: 1 if x == "G" else 0)
)

GRADUATE_RATIO = mdf["graduate"].sum() / len(mdf["graduate"])

mdf.head()

# %%
mdict = {}
for index, row in mdf.iterrows():

    _id = row["ID"]
    rank = row["学内選考順位"]

    graduate = False
    if row["graduate"]:
        graduate = True

    school_columns = [column for column in mdf.columns if "_大学名（和文）" in column]
    school = row[school_columns].tolist()

    school_period_columns = [column for column in mdf.columns if "_希望\n学期" in column]
    school_period = row[school_period_columns].tolist()

    school_1sem_columns = [column for column in mdf.columns if "_1学期のみ派遣可の場合" in column]
    school_1sem = row[school_1sem_columns].tolist()

    school_eligible_columns = [column for column in mdf.columns if "_要件" in column]
    school_eligible = row[school_eligible_columns].tolist()

    semester = [
        2 if s == "Autumn&Spring" else 1 if (s == "Autumn" or "Spring") else 0
        for s in school_period
    ]
    one_sem = [
        2 if s == "Autumn&Spring" else 1 if (s == "Autumn" or "Spring") else 0
        for s in school_1sem
    ]
    head = [1 if isinstance(s, str) else 0 for s in school]

    total_school = np.sum(head)

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
        "total_school": total_school,
        "student_type": student_type,
    }


# %%

sdf = (
    pd.read_excel(
        data_path + "cleaned/UTMDへの提供データ（全学交換留学秋募集ダミーデータ）20220719更新.xlsx",
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
    )
)

sdict = sdf.to_dict("index")
sdf.head()

# %%
vacancy = sdict.copy()

assigned = {}

for i in range(1, len(mdict) + 1):

    person = mdict[i]
    id = person["id"]

    for j in range(3):

        if id in assigned.keys():
            break

        if isinstance(person["school_eligible"][j], str):
            continue

        considered_school = person["school"][j]

        if isinstance(considered_school, float) and np.isnan(considered_school):
            continue

        current_vacancy = vacancy[considered_school]["place"]
        current_vacancy_unit = vacancy[considered_school]["unit"]

        considered_slot = person[current_vacancy_unit][j]

        if current_vacancy >= considered_slot:
            assigned[id] = {
                "rank": i,
                "school": considered_school,
                "slot": considered_slot,
                "semester": person["school_period"][j],
            }

            vacancy[considered_school]["place"] -= considered_slot

        elif (
            person["student_type"] == "school"
            and person["one_sem"][j] == 1
            and current_vacancy_unit == "semester"
        ):

            if current_vacancy >= 1:
                assigned[id] = {
                    "rank": i,
                    "school": considered_school,
                    "slot": 1,
                    "semester": person["school_1sem"][j],
                }

                vacancy[considered_school]["place"] -= 1


# %%

assigned_df = pd.DataFrame.from_dict(assigned.copy(), orient="index")
