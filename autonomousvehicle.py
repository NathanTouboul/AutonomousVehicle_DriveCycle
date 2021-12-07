import numpy as np


class AutonomousVehicle:

    def __init__(self):

        # AutonomousVehicle
        self.test_weight = 2000     # Test weight (kg)
        self.target_abc = [23.3637, 0.3946, 0.01245]

        # Battery
        self.v0 = 0
        self.res = 0

        # Motor
        self.efficiency = 1
        self.standby_losses = 0.

        # Experiment
        self.dt = 0.5
        
        # Space and time gaps
        self.gap_target, self.gap_min = 5., 1  # meters
        self.headway_target, self.headway_min = 5., 1.  # seconds
        
        # Acceleration min and max
        self.acceleration_min, self.acceleration_max = -3, 3.     # m.s^2
        
    def control_drive_cycle(self, lead_vehicle_distance, kp=1, kd=1):

        # Perfect access to the position of the lead vehicle (perfect range sensor)
        # Computation of speed and acceleration of the lead

        lead_vehicle_speed, lead_vehicle_acceleration = self.compute_speed_acceleration(lead_vehicle_distance)

        # Initializing the speed of the autonomous vehicle
        following_speed = np.zeros(lead_vehicle_distance.shape)

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

            elif following_speed[s + 1] - following_speed[s] > - 0.5 * self.acceleration_max * self.dt:
                following_speed[s + 1] = following_speed[s] + 0.5 * self.acceleration_max * self.dt

            e_prev = e

        return following_speed, gap_vehicles

    def adaptive_cruise_control_drive_cycle(self, lead_distance, headway=False):
        # We can only use the distance between the vehicles up to the current time
        # We impose the distance target

        # Lead speed and acceleration
        lead_speed, lead_acceleration = self.compute_speed_acceleration(lead_distance)

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
                                       self.headway_target - follow_speed[d]) / (1 + (self.dt ** 2) * self.headway_target)

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

    def get_power_wheel(self, speed, acceleration):

        a, b, c = self.target_abc

        # Road load forces
        force_road_load = a + b * speed + c * speed ** 2

        # Modeled mass (taking into account rotational inertia)
        modeled_mass = 1.03 * self.test_weight

        # Power at the wheel
        power_wheel = (modeled_mass * acceleration + force_road_load) * speed

        return force_road_load, power_wheel

    def compute_speed_acceleration(self, lead_vehicle_distance):

        lead_vehicle_speed = np.zeros(lead_vehicle_distance.shape)
        lead_vehicle_acceleration = np.zeros(lead_vehicle_distance.shape)

        # Computing speed of the leading vehicle
        for p, _ in enumerate(lead_vehicle_distance[:-1]):
            lead_vehicle_speed[p + 1] = (lead_vehicle_distance[p + 1] - lead_vehicle_distance[p]) / self.dt

        # Computing acceleration of the leading vehicle
        for s, _ in enumerate(lead_vehicle_speed[:-1]):
            dv = lead_vehicle_speed[s + 1] - lead_vehicle_speed[s]
            lead_vehicle_acceleration[s] = dv / self.dt

        return lead_vehicle_speed, lead_vehicle_acceleration

    @staticmethod
    def bound_acceleration(x, y, z):
        return np.maximum((np.minimum(x, y)), z)
