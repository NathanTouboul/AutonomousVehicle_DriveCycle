import numpy as np


class Vehicle:

    def __init__(self, test_weight: float, abc: list, nominal_voltage: float, resistance: float, capacity: float, 
                 efficiency_transmission: float, efficiency_motor: float, standby_losses, dt=0.5):

        # Vehicle
        self.test_weight = test_weight
        self.target_abc = abc

        # Battery
        self.voltage_nominal = nominal_voltage
        self.resistance = resistance
        self.capacity = capacity
        self.soc_initial = 0.5

        # Transmission
        self.efficiency_transmission = efficiency_transmission

        # Motor
        self.efficiency_motor = efficiency_motor
        self.standby_losses = standby_losses

        # Experiment
        self.dt = dt

    def compute_speed_acceleration(self, vehicle_distance: np.ndarray) -> tuple:

        vehicle_speed = np.zeros(vehicle_distance.shape)
        vehicle_acceleration = np.zeros(vehicle_distance.shape)

        # Computing speed of the vehicle
        for p, _ in enumerate(vehicle_distance[:-1]):
            vehicle_speed[p + 1] = (vehicle_distance[p + 1] - vehicle_distance[p]) / self.dt

        # Computing acceleration of the vehicle
        for s, _ in enumerate(vehicle_speed[:-1]):
            dv = vehicle_speed[s + 1] - vehicle_speed[s]
            vehicle_acceleration[s] = dv / self.dt

        return vehicle_speed, vehicle_acceleration

    def get_power_wheel(self, speed: np.ndarray, acceleration: np.ndarray) -> tuple:

        a, b, c = self.target_abc

        # Speed conversion [mph]
        speed_mph = 2.23694 * speed

        # Road load forces [N]
        force_road_load = (a + b * speed_mph + c * speed_mph ** 2) * 4.44822

        # Modeled mass (taking into account rotational inertia)
        modeled_mass = 1.03 * self.test_weight

        # Power at the wheel
        power_wheel = (modeled_mass * acceleration + force_road_load) * speed

        return force_road_load, power_wheel

    @staticmethod
    def get_mpge(time: np.ndarray, total_distance: np.ndarray, power_battery: np.ndarray) -> float:

        total_distance = np.nan_to_num(total_distance)
        power_battery = np.nan_to_num(power_battery)
        time = np.nan_to_num(time)
        t_end = np.max(time)

        # Net power battery - conversion to equivalent gallon
        distance = np.max(total_distance) * 0.000621371
        power_net_consumption = (t_end / 3600) * 0.001 * np.sum(power_battery) / 33.7

        return distance / power_net_consumption

    def get_state_of_charge(self, power_wheel: np.ndarray) -> tuple:

        power_battery = np.zeros(power_wheel.shape)
        capacity_supplied = np.zeros(power_battery.shape)
        state_of_charge = np.zeros(power_battery.shape)

        # Initial State of Charge
        state_of_charge[0] = self.soc_initial

        efficiency_drivetrain = self.efficiency_transmission * self.efficiency_motor

        for t, p_w in enumerate(power_wheel):

            if p_w >= 0:
                power_battery[t] = (1 / efficiency_drivetrain) * p_w + self.standby_losses
            else:
                power_battery[t] = efficiency_drivetrain * p_w + self.standby_losses

            # Battery current (A)
            if self.voltage_nominal ** 2 - 4 * self.resistance * power_battery[t] >= 0:
                battery_current = (self.voltage_nominal -
                                   np.sqrt(self.voltage_nominal ** 2 - 4 * self.resistance * power_battery[t])) \
                                  / (2 * self.resistance)
            else:
                # Previous value is chosen
                battery_current = 3600 * capacity_supplied[t - 1] / self.dt

            # Capacity supplied (Ah)
            capacity_supplied[t] = battery_current * self.dt / 3600

            # State of charge (%)
            if t > 0:
                state_of_charge[t] = state_of_charge[t - 1] - capacity_supplied[t] / self.capacity

        return power_battery, state_of_charge


class AutonomousVehicle(Vehicle):

    def __init__(self, test_weight: float, abc: list, nominal_voltage: float, resistance: float, capacity: float,
                 efficiency_transmission: float, efficiency_motor: float, standby_losses, dt=0.5):

        super().__init__(test_weight, abc, nominal_voltage, resistance, capacity, efficiency_transmission,
                         efficiency_motor, standby_losses, dt)

        # Space and time gaps
        self.gap_target, self.gap_min = 5., 1.  # meters
        self.headway_target, self.headway_min = 5., 1.  # seconds
        
        # Acceleration min and max
        self.acceleration_min, self.acceleration_max = -3, 3.     # m.s^2
        
    def control_drive_cycle(self, lead_vehicle_distance: np.ndarray, kp=1, kd=1, df=None) -> tuple:

        # Perfect access to the position of the lead vehicle (perfect range sensor)
        # Computation of speed and acceleration of the lead

        if df is None:
            lead_vehicle_speed, lead_vehicle_acceleration = self.compute_speed_acceleration(lead_vehicle_distance)
        else:
            lead_vehicle_speed = df[df.columns[1]].values
            lead_vehicle_acceleration = df[df.columns[2]].values

        # Initializing the speed of the autonomous vehicle
        following_speed = np.zeros(lead_vehicle_distance.shape)

        # Initializing the acceleration of the autonomous vehicle

        following_acceleration = np.zeros(lead_vehicle_distance.shape)

        # Initializing gap between vehicle
        gap_vehicles = np.zeros(lead_vehicle_speed.shape)
        gap_vehicles[0] = 1     # gap initial in meter
        e_prev = 1

        for s, lead_speed in enumerate(lead_vehicle_speed[:-1]):

            if lead_speed == 0. or lead_speed is np.nan:
                continue

            # New gap between vehicles
            gap_vehicles[s + 1] = gap_vehicles[s] + (lead_speed - following_speed[s]) * self.dt
        
            # Errors
            velocity_error = (lead_speed - following_speed[s])
            gap_error = self.gap_target - gap_vehicles[s + 1]
        
            tw = self.gap_target / lead_speed    
            e = gap_vehicles[s + 1] - tw * following_speed[s]
            e_dot = (e - e_prev) / self.dt
            
            following_speed[s + 1] = following_speed[s] + kp * e + kd * e_dot
            
            # Acceleration bounds
            if following_speed[s + 1] - following_speed[s] < - 0.5 * self.acceleration_max * self.dt:
                following_speed[s + 1] = following_speed[s] - 0.5 * self.acceleration_max * self.dt

            elif following_speed[s + 1] - following_speed[s] > self.acceleration_max * self.dt:
                following_speed[s + 1] = following_speed[s] + 0.5 * self.acceleration_max * self.dt

            # Computing acceleration
            dv = following_speed[s + 1] - following_speed[s]
            following_acceleration[s] = dv / self.dt

            e_prev = e

        return following_speed, following_acceleration, gap_vehicles

    def adaptive_cruise_control_drive_cycle(self, lead_distance: np.ndarray, headway=False, df=None) -> tuple:

        # Lead speed and acceleration
        # if df is None, we don't have access to true speed --> need to recalculate
        if df is None:
            lead_speed, lead_acceleration = self.compute_speed_acceleration(lead_distance)
        else:
            lead_speed = df[df.columns[1]].values
            lead_acceleration = df[df.columns[2]].values

        # Initializing gap between vehicle
        gap = np.zeros(lead_speed.shape)
        gap[0] = 1    # gap initial in meter

        # Initializing following absolute distance, speed and acceleration
        follow_distance = np.zeros(lead_speed.shape)
        follow_distance[0] = lead_distance[0] - gap[0]
        follow_speed = np.zeros(lead_speed.shape)
        follow_acceleration = np.zeros(lead_acceleration.shape)

        # Taking into account headway target
        if headway:
            for d, _ in enumerate(lead_distance[:-1]):

                # Constraint on te gap - imposed by space (gap min) or time (headway_min)
                gap_constraint = np.maximum(self.gap_min, follow_speed[d] * self.headway_min)

                # Next acceleration needed to reach the minimum safe distance
                acceleration_safe = gap[d] / (self.dt ** 2) + \
                                    (lead_speed[d] - follow_speed[d]) / self.dt - gap_constraint / (self.dt ** 2)

                # Acceleration needed to reach the target gap
                acceleration_target = ((gap[d] + (lead_speed[d] - follow_speed[d]) * self.dt) *
                                       self.headway_target - follow_speed[d]) / (1 + (self.dt ** 2) *
                                                                                 self.headway_target)

                # Computing next acceleration
                if gap[d] < self.gap_min:
                    follow_acceleration[d + 1] = self.bound_acceleration(acceleration_safe, self.acceleration_max,
                                                                         self.acceleration_min)
                else:
                    follow_acceleration[d + 1] = self.bound_acceleration(acceleration_target, self.acceleration_max,
                                                                         self.acceleration_min)

                # Computing speed
                follow_speed[d + 1] = follow_speed[d] + follow_acceleration[d + 1] * self.dt

                # Computing absolute distance
                follow_distance[d + 1] = follow_distance[d] + follow_speed[d + 1] * self.dt

                # Computing gap
                gap[d + 1] = lead_distance[d + 1] - follow_distance[d + 1]

        # Only considering gap target
        else:
            for d, _ in enumerate(lead_distance[:-1]):

                # Next acceleration needed to reach the minimum safe distance
                acceleration_safe = gap[d] / (self.dt ** 2) + \
                                    (lead_speed[d] - follow_speed[d]) / self.dt - self.gap_min / (self.dt ** 2)

                # Acceleration needed to reach the target gap
                acceleration_target = gap[d] / (self.dt ** 2) + \
                                    (lead_speed[d] - follow_speed[d]) / self.dt - self.gap_target / (self.dt ** 2)

                # Computing next acceleration
                if gap[d] < self.gap_min:
                    follow_acceleration[d + 1] = self.bound_acceleration(acceleration_safe, self.acceleration_max,
                                                                         self.acceleration_min)
                else:
                    follow_acceleration[d + 1] = self.bound_acceleration(acceleration_target, self.acceleration_max,
                                                                         self.acceleration_min)

                # Computing speed
                next_follow_speed = follow_speed[d] + follow_acceleration[d + 1] * self.dt
                follow_speed[d + 1] = next_follow_speed

                # Computing absolute distance
                next_follow_x = follow_distance[d] + follow_speed[d + 1] * self.dt
                follow_distance[d + 1] = follow_distance[d] + follow_speed[d + 1] * self.dt

                # Computing gap
                next_gap = lead_distance[d + 1] - follow_distance[d + 1]
                gap[d + 1] = next_gap

        return follow_distance, follow_speed, follow_acceleration, gap

    @staticmethod
    def bound_acceleration(x: float, y: float, z: float):
        return np.maximum((np.minimum(x, y)), z)
