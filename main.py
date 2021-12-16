from preprocessing import preprocess_dataframe, computing_absolute_distance, parameters_vehicle
from plotting_saving import plotting_drive_cycle, plotting_powers, plotting_speed_lead_follow, \
    plotting_acceleration_decisions, plotting_soc, plotting_comparison
from vehicles import Vehicle, AutonomousVehicle


def main():

    # Importing Lead drive cycle
    df = preprocess_dataframe("HWY.txt", filtering="1hz")

    # Plotting drive Cycle
    plotting_drive_cycle(df, title=f"Drive Cycle")

    # Defining the parameters of the studied vehicle: Chevrolet Spark
    vehicle_filename = "spark.json5"
    test_weight, abc, nominal_voltage, resistance, capacity, eff_tr, eff_mot, standby_losses = \
        parameters_vehicle(vehicle_filename)

    # Computing Powers and consumption of the following EV as if it was not autonomous: std vehicle
    vehicle_std = Vehicle(test_weight, abc, nominal_voltage, resistance, capacity, eff_tr, eff_mot, standby_losses)
    speed_std, acceleration_std = df[df.columns[1]].values, df[df.columns[2]].values

    # Power at the wheel for the vehicle for std drive cycle
    _, power_wheel_std = vehicle_std.get_power_wheel(speed_std, acceleration_std)

    # State of charge for the vehicle for std drive cycle
    power_battery_std, state_of_charge_std = vehicle_std.get_state_of_charge(power_wheel_std)

    # Computing absolute distance of leading vehicle
    lead_absolute_distance, lead_speed = computing_absolute_distance(df, vehicle_std.dt)

    # Saving state of charge and mpge
    soc = [state_of_charge_std]
    mpge = [vehicle_std.get_mpge(df[df.columns[0]].values, lead_absolute_distance, power_battery_std)]

    # Creating Autonomous Vehicle
    autonomous_vehicle = AutonomousVehicle(test_weight, abc, nominal_voltage, resistance, capacity, eff_tr, eff_mot,
                                           standby_losses)

    # # # # # # # # # # # # # #
    # CLASSIC CRUISE CONTROL  #
    # # # # # # # # # # # # # #

    following_speed_ccc, following_acceleration_ccc, gap_vehicles_ccc = \
        autonomous_vehicle.control_drive_cycle(lead_absolute_distance, kp=0.1, kd=1, df=df)

    # Plotting CCC's following and lead speed
    plotting_speed_lead_follow(df[df.columns[0]].values, lead_speed, following_speed_ccc, gap_vehicles_ccc,
                               title="Classical Cruise Control")

    # Power at the wheel for the following vehicle for CCC drive cycle
    _, power_wheel_ccc = autonomous_vehicle.get_power_wheel(following_speed_ccc, following_acceleration_ccc)

    # State of charge and mpge for the vehicle for following vehicle for CCC drive cycle
    power_battery_ccc, state_of_charge_ccc = autonomous_vehicle.get_state_of_charge(power_wheel_ccc)
    soc.append(state_of_charge_ccc)
    follow_absolute_distance_ccc = lead_absolute_distance - gap_vehicles_ccc
    mpge.append(autonomous_vehicle.get_mpge(df[df.columns[0]].values, follow_absolute_distance_ccc, power_battery_ccc))

    # Plotting histograms acceleration
    plotting_acceleration_decisions(following_acceleration_ccc, title="Acceleration inputs CCC")

    # # # # # # # # # # # # # #
    # ADAPTIVE CRUISE CONTROL #
    # # # # # # # # # # # # # #

    headway = False
    following_distance_acc, following_speed_acc, following_acceleration_acc, gap_vehicles_acc = \
        autonomous_vehicle.adaptive_cruise_control_drive_cycle(lead_absolute_distance, headway=headway, df=df)

    # Plotting ACC's following and lead speeds
    title = "Adaptive Cruise Control"
    if headway:
        title += " considering headway"
    plotting_speed_lead_follow(df[df.columns[0]].values, df[df.columns[1]].values, following_speed_acc,
                               gap_vehicles_acc, title=title)

    # Power at the wheel for the following vehicle for CCC drive cycle
    _, power_wheel_acc = autonomous_vehicle.get_power_wheel(following_speed_acc, following_acceleration_acc)

    # State of charge and mpge for the vehicle for following vehicle for CCC drive cycle
    power_battery_acc, state_of_charge_acc = autonomous_vehicle.get_state_of_charge(power_wheel_acc)
    soc.append(state_of_charge_acc)

    follow_absolute_distance_acc = lead_absolute_distance - gap_vehicles_acc
    mpge.append(autonomous_vehicle.get_mpge(df[df.columns[0]].values, follow_absolute_distance_acc, power_battery_acc))

    # Plotting histograms acceleration
    plotting_acceleration_decisions(following_acceleration_acc, title="Acceleration inputs ACC")

    # Plotting State of Charge
    legend_handles = ["Standard DC", " Autonomous DC - CCC", " Autonomous DC - ACC"]
    plotting_soc(soc, legend_handles)

    # Plotting all drive cycles
    speeds = [lead_speed, following_speed_ccc, following_speed_acc]
    legend_handles = ["lead_speed", "following_speed_ccc", "following_speed_acc"]
    plotting_comparison(speeds, legend_handles)


if __name__ == '__main__':
    main()
