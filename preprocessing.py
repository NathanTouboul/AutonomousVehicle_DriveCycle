import pandas as pd
import numpy as np
import os
import json

DATASET_DIRECTORY = f"dataset"
if DATASET_DIRECTORY not in os.listdir():
    os.mkdir(DATASET_DIRECTORY)


def preprocess_dataframe(filename: str, filtering: str):

    # Importing Cycles
    filepath = os.path.join(DATASET_DIRECTORY, filename)
    df = pd.read_csv(filepath, delimiter="\t")

    # Converting speed column to numeric values
    columns = df.columns
    df[columns[1]] = pd.to_numeric(df[columns[1]], errors='coerce')

    # Adding rows to create new time and new speed
    new_df = df.copy()

    # 1Hz filtering
    if filtering == "1hz":
        for index, data in df.iterrows():
            if index < len(df) - 1:
                columns = df.columns
                new_time = (df.iloc[index + 1][columns[0]] + df.iloc[index][columns[0]]) / 2
                new_speed = (df.iloc[index + 1][columns[1]] + df.iloc[index][columns[1]]) / 2

                inserting_row = [new_time, new_speed]

                new_df = pd.DataFrame(np.insert(new_df.values, 2 * index + 1, inserting_row, axis=0))

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


def computing_absolute_distance(df: pd.DataFrame, time_step: float) -> tuple:

    lead_speed = np.array(df[df.columns[1]])
    lead_pose = lead_speed * time_step  # Distance from origin

    lead_absolute_distance = np.zeros(lead_pose.shape)
    for p, _ in enumerate(lead_pose[1:]):
        lead_absolute_distance[p] = lead_pose[p] + lead_absolute_distance[p - 1]

    return lead_absolute_distance, lead_speed


def parameters_vehicle(vehicle_filename: str) -> tuple:

    # Defining the vehicle studied
    vehicle_filepath = os.path.join(DATASET_DIRECTORY, vehicle_filename)
    with open(vehicle_filepath, 'r') as vehicle_file:
        data = vehicle_file.read()
        vehicle_parameters = json.loads(data)

    test_weight = vehicle_parameters["test_weight"]
    abc = [vehicle_parameters["a"], vehicle_parameters["b"], vehicle_parameters["c"]]
    nominal_voltage = vehicle_parameters["nominal_voltage"]
    resistance = vehicle_parameters["resistance"]
    cap = vehicle_parameters["capacity"]

    eff_tr = vehicle_parameters["efficiency_transmission"]
    eff_mot = vehicle_parameters["efficiency_motor"]
    standby_losses = vehicle_parameters["standby_losses"]

    return test_weight, abc, nominal_voltage, resistance, cap, eff_tr, eff_mot, standby_losses
