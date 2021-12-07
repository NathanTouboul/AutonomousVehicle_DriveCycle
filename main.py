from preprocessing import preprocess_dataframe, computing_absolute_distance
from plotting_saving import plotting_drive_cycle, plotting_powers, plotting_speed_lead_follow, plotting_acceleration_decisions
from autonomousvehicle import AutonomousVehicle


def main():

    # Importing Lead drive cycle
    df = preprocess_dataframe("HWY.txt", filtering="1hz")

    # Plotting drive Cycle
    #plotting_drive_cycle(df, title=f"Drive Cycle")

    # Creating Autonomous AutonomousVehicle
    autonomous_vehicle = AutonomousVehicle()

    # Computing absolute distance of leading vehicle
    lead_absolute_distance, lead_speed = computing_absolute_distance(df, autonomous_vehicle.dt)

    # Classic Cruise Control method for computing drive cycle
    #following_speed, gap_vehicles = autonomous_vehicle.control_drive_cycle(lead_absolute_distance, kp=10, kd=1)

    # Plotting CCC's following and lead speed
    time = df[df.columns[0]].values
    #plotting_speed_lead_follow(time, lead_speed, following_speed, gap_vehicles, title="Classical Cruise Control")

    # Adaptive Cruise Control
    title = "Adaptive Cruise Control"


    following_distance, following_speed, following_acceleration, gap_vehicles = \
        autonomous_vehicle.adaptive_cruise_control_drive_cycle(lead_absolute_distance)


    # Plotting ACC's following and lead speeds
    lead_acceleration = df[df.columns[2]].values
    plotting_speed_lead_follow(time, lead_acceleration, following_acceleration, gap_vehicles, title=title)

    # Plotting histograms acceleration
    plotting_acceleration_decisions(following_acceleration, title="Acceleration inputs")


if __name__ == '__main__':
    main()
