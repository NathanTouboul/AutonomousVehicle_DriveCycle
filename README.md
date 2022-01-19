# autonomous_drive_cycle

## Building an autonomous drive cycle vehicle by implementing following-controls of a standard EPA drive cycle

The objective of this project is to create a new "Standard EPA Drive Cycle" used for consumption analysis, specifically for autonomous vehicle.
The existing drive cycles (UDDS, HWY, and such) are only relevant for studying the consumption of human-driven vehicle.
To generate this drive cycle, the idea is to have an autonomous vehicle follow a human-driven vehicle (driven under a standard EPA drive cycle) and 
control it to obtain an autonomous drive cycle. This new drive cycle must present a cruise optimization typical of such vehicle, as well as
realistic  performances.

Assumptions made when generating an AV drive cycle :
- One dimensional simulation, lateral control is ignored
- Road is straight
- A minimum distance and a fixed initial distance are to be determined
- Lead vehicle follows an EPA drive cycle for UDDS or HWY

Two type of controls:
- Classic Cruise Control (PID Control)
- Adaptive Cruise Control

## Classic Cruise Control (PID Control)

Simple PID Control of the gap between lead and following vehicles, with thresholds on accelerations.

![Image Caption](figures/Classical%20Cruise%20Control.png)
![Image Caption](figures/Acceleration%20inputs%20CCC.png)

Results:
- Transitory dynamics on the target gap between 2 vehicles
- Over-fitting of the standard drive cycle
- Acceleration inputs not really smooth (histogram)
- Could add an LQR to improve 


## Adaptive Cruise control

More "State of the art" way of creating the AV drive cycle, implementing one of the method of Adaptive Cruise Control in [2]


![Image Caption](figures/Adaptive%20Cruise%20Control%20considering%20headway.png)
![Image Caption](figures/Acceleration%20inputs%20ACC.png)

Results:
- Smoother accelerations inputs
- Taking into account headway (time between vehicle)
- Gap proportional to speed, still over-fitting of standard EPA drive Cycle
- Could be improved by adding other equations from the literature. 

___ 
### References:

[1] Niket Prakash, Anna G. Stefanopoulou, Andrew J. Moskalik and Matthew J. Brusstar: “Use of the Hypothetical Lead (HL) Vehicle
Trace: A new method for Evaluating Fuel Consumption in Automated Driving*”. American Control Conference ACC 2016,
Boston,USA.

[2] Mersky A.C., Samaras C. (2016). Fuel Economy Testing of Autonomous Vehicles, Transportation Research Part C: Emerging
Technologies 65, 31-48.

[3] Niket Prakash, Younki Kim, Anna G Stefapoulou :”A Comparative Study of Different Objectives Functions for the Minimal Fuel
Drive Cycle Optimization in Autonomous Vehicles” in Journal of Dynamic Systems, Measurement and Control. July 2019