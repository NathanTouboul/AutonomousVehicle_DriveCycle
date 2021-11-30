import pandas
import numpy as np
import os


DATASET_DIRECTORY = f"dataset"


def preprocess_dataframe(filename, filtering: str):

    # Importing Cycles
    filepath = os.path.join(DATASET_DIRECTORY, filename)
    df = pandas.read_csv(filepath, delimiter="\t")

    # Converting speed column to numeric values
    columns = df.columns
    df[columns[1]] = pandas.to_numeric(df[columns[1]], errors='coerce')

    # Adding rows to create new time and new speed
    new_df = df.copy()

    # 1Hz filtering
    if filtering == "1hz":

        for index, data in df.iterrows():

            if index < len(df) - 1:
                new_time = (df.iloc[index + 1]['time'] + df.iloc[index]['time']) / 2
                new_speed = (df.iloc[index + 1]['mph'] + df.iloc[index]['mph']) / 2
                inserting_row = [new_time, new_speed]
                new_df = pandas.DataFrame(np.insert(new_df.values, 2 * index + 1, inserting_row, axis=0))

    # Renaming columns
    new_df_columns = new_df.columns
    new_df = new_df.rename({new_df_columns[0]: "time", new_df_columns[1]: "mph"}, axis='columns')

    # Calculate acceleration
    new_df["acceleration"] = np.zeros((len(new_df), 1))

    for index, data in df.iterrows():
        if 0 < index < len(df) - 1:
            dv = (new_df.iloc[index + 1]["mph"] - new_df.iloc[index - 1]["mph"])
            dt = (new_df.iloc[index + 1]["time"] - new_df.iloc[index - 1]["time"])

            new_df.loc[index, "acceleration"] = dv / dt
    # Saving csv
    csv_filename = "".join([filename.rstrip("txt"), "csv"])
    filepath = os.path.join(DATASET_DIRECTORY, csv_filename)
    new_df.to_csv(filepath)

    return new_df
