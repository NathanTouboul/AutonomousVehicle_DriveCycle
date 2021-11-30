from preprocessing import preprocess_dataframe
from plotting_saving import plotting_drive_cycle, plotting_powers
from autonomousvehicle import AutonomousVehicle


def main():

    # Importing Lead drive cycle
    df = preprocess_dataframe("HWY.txt", filtering="1hz")

    # Plotting drive Cycle
    plotting_drive_cycle(df, title=f"Drive Cycle")

    # Creating Autonomous AutonomousVehicle
    autonomous_vehicle = AutonomousVehicle()

    # Generating following speed


if __name__ == '__main__':
    main()
