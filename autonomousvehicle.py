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

    def generate_speed_trace(self, leading_speed, distance_target=5):
        pass

    def get_acceleration(self, speed):
        pass

    def get_power_wheel(self, speed, acceleration):

        a, b, c = self.target_abc

        # Road load forces
        force_road_load = a + b * speed + c * speed ** 2

        # Modeled mass (taking into account rotational inertia)
        modeled_mass = 1.03 * self.test_weight

        # Power at the wheel
        power_wheel = (modeled_mass * acceleration + force_road_load) * speed

        return force_road_load, power_wheel
