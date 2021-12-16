import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

BLOCK = False
FIGURES_DIRECTORY = f"figures"
if FIGURES_DIRECTORY not in os.listdir():
    os.mkdir(FIGURES_DIRECTORY)


def plotting_drive_cycle(dataframe: pd.DataFrame, title=f"Drive Cycle"):

    # Plot Speed vs time steps
    fig, axes = plt.subplots(nrows=1, ncols=1)
    fig.suptitle(title)
    plt.grid()
    speed = dataframe[dataframe.columns[1]].values
    time = dataframe[dataframe.columns[0]].values
    axes.plot(time, speed)
    axes.set_ylabel('Speed')
    axes.set_xlabel('Time')

    plt.show(block=BLOCK)

    filepath_figure = os.path.join(FIGURES_DIRECTORY, title)
    plt.savefig(filepath_figure)
    plt.close()


def plotting_speed_lead_follow(time: np.ndarray, lead_speed: np.ndarray, following_speed: np.ndarray,
                               gap_vehicles: np.ndarray, title="Speed comparison"):

    # Plot Speed and gaps

    fig, axes = plt.subplots(nrows=2, ncols=1)
    fig.suptitle(title)

    axes[0].plot(time, lead_speed, color='b')
    axes[0].plot(time, following_speed, color='r', alpha=0.5)
    axes[0].set_ylabel('Speed [m/s]')
    axes[0].grid()
    axes[0].legend(["Leading", "Following"], loc="upper left")

    axes[1].plot(gap_vehicles[:-10])
    axes[1].set_ylabel('Gap [m]')
    axes[1].set_xlabel('Time [s]')

    axes[1].grid()

    plt.show(block=BLOCK)

    filepath_figure = os.path.join(FIGURES_DIRECTORY, title)
    plt.savefig(filepath_figure)
    plt.close()


def plotting_powers(powers: list, title=f"Powers"):

    # Plot loss vs epochs
    fig, axes = plt.subplots(nrows=1, ncols=1)
    fig.suptitle(title)
    plt.grid()

    for power in powers:
        axes.plot(power)

    axes.set_ylabel('Powers')
    axes.set_xlabel('Time')

    plt.show(block=BLOCK)

    filepath_figure = os.path.join(FIGURES_DIRECTORY, title)
    plt.savefig(filepath_figure)
    plt.close()


def plotting_acceleration_decisions(accelerations: np.ndarray, title="Acceleration Decisions Histogram"):

    fig, axes = plt.subplots(nrows=1, ncols=1)
    fig.suptitle(title)
    plt.grid()
    plt.show(block=BLOCK)

    plt.hist(accelerations, bins=150, density=True)
    axes.set_ylabel('Decisions')
    axes.set_xlabel('Accelerations [m/s^2]')
    filepath_figure = os.path.join(FIGURES_DIRECTORY, title)
    plt.savefig(filepath_figure)
    plt.close()


def plotting_soc(soc: list, legend_handles: list, title=f"State of charge"):

    fig, axes = plt.subplots(nrows=1, ncols=1)
    fig.suptitle(title)
    plt.grid()
    plt.show(block=BLOCK)

    alpha = 1
    for s in soc:
        axes.plot(s, alpha=alpha)
        alpha -= 0.2

    axes.set_ylabel('State of charge')
    axes.set_xlabel('Time')
    axes.set_ylim([0.25, 0.75])
    axes.legend(legend_handles)

    plt.show(block=BLOCK)
    filepath_figure = os.path.join(FIGURES_DIRECTORY, title)
    plt.savefig(filepath_figure)
    plt.close()


def plotting_comparison(speeds: list, legend_handles: list, title="Comparison drive cycle"):

    fig, axes = plt.subplots(nrows=1, ncols=1, dpi=500)
    fig.suptitle(title)
    plt.grid()
    plt.show(block=BLOCK)

    for s, speed in enumerate(speeds):
        axes.plot(speed, linewidth=0.4)

    axes.set_ylabel('Speed')
    axes.set_xlabel('Time')
    axes.legend(legend_handles)

    plt.show(block=BLOCK)
    filepath_figure = os.path.join(FIGURES_DIRECTORY, title)
    plt.savefig(filepath_figure)
    plt.close()


