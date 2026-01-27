import pandas as pd


def analyse_contingency(df, col_1, col_2, bins): 
    # Label Creation
    half_bins = int(bins / 2)
    if bins % 2 == 0:
        labels_list = list(range(-half_bins, 0)) + list(range(1, 1 + half_bins))
    else:
        labels_list = list(range(-half_bins, half_bins + 1))
        print(labels_list)

    # Discretisation and assinging categories
    df[f"{col_1}_cat"] = pd.qcut(df[col_1], q=bins, labels=labels_list)
    df[f"{col_2}_cat"] = pd.qcut(df[col_2], q=bins, labels=labels_list)

    # generate matrix
    matrix = pd.crosstab(df[f"{col_1}_cat"], df[f"{col_2}_cat"])

    return matrix