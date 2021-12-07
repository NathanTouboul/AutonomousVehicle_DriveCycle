import time

import matplotlib.pyplot as plt
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

    # Conversion mph to m/s
    new_df_columns = new_df.columns

    new_df.loc[:, new_df_columns[1]] *= 0.44704

    # Renaming columns
    columns = ["Time [s]", "Speed [m/s]"]
    new_df = new_df.rename({new_df_columns[0]: columns[0], new_df_columns[1]: columns[1]}, axis='columns')

    # Calculate acceleration
    columns.append(["Acceleration [m/s^2]"])
    new_df[columns[2]] = np.zeros((len(new_df), 1))

    for index, data in new_df.iterrows():
        if 0 < index < len(new_df) - 1:
            dv = (new_df.iloc[index][columns[1]] - new_df.iloc[index - 1][columns[1]])
            dt = (new_df.iloc[index][columns[0]] - new_df.iloc[index - 1][columns[0]])

            new_df.loc[index, columns[2]] = dv / dt

    # Saving csv
    csv_filename = "".join([filename.rstrip("txt"), "csv"])
    filepath = os.path.join(DATASET_DIRECTORY, csv_filename)
    new_df.to_csv(filepath)

    return new_df


def computing_absolute_distance(df, time_step):

    lead_speed = np.array(df[df.columns[1]])
    lead_pose = lead_speed * time_step  # Distance from origin

    lead_absolute_distance = np.zeros(lead_pose.shape)
    for p, _ in enumerate(lead_pose[1:]):
        lead_absolute_distance[p] = lead_pose[p] + lead_absolute_distance[p - 1]

    return lead_absolute_distance, lead_speed
