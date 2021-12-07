import matplotlib.pyplot as plt
import numpy as np
import os

BLOCK = False
FIGURES_DIRECTORY = f"figures"


def plotting_drive_cycle(dataframe, title=f"Drive Cycle"):

    # Plot Speed vs time steps
    fig, axes = plt.subplots(nrows=1, ncols=1)
    fig.suptitle(title)
    plt.grid()
    speed = dataframe[dataframe.columns[1]].values
    time = dataframe[dataframe.columns[0]].values
    axes.plot(time, speed)
    axes.set_ylabel('Speed')
    axes.set_xlabel('Time')

    plt.show(block=True)

    filepath_figure = os.path.join(FIGURES_DIRECTORY, title)
    plt.savefig(filepath_figure)
    plt.close()


def plotting_speed_lead_follow(time, lead_speed, following_speed, gap_vehicles, title="Speed comparison"):

    # Plot Speed and gaps

    fig, axes = plt.subplots(nrows=2, ncols=1)
    fig.suptitle(title)

    axes[0].plot(time, lead_speed, color='b')
    axes[0].plot(time, following_speed, color='r', alpha=0.5)
    axes[0].set_ylabel('Speed [m/s]')
    axes[0].grid()
    axes[0].legend(["Leading", "Following"], loc="upper left")

    axes[1].plot(gap_vehicles)
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


def plotting_acceleration_decisions(accelerations, title):

    fig, axes = plt.subplots(nrows=1, ncols=1)
    fig.suptitle(title)
    plt.grid()
    plt.show(block=BLOCK)

    plt.hist(accelerations, bins=150, density=True)

    filepath_figure = os.path.join(FIGURES_DIRECTORY, title)
    plt.savefig(filepath_figure)
    plt.close()

