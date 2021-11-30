import matplotlib.pyplot as plt
import numpy as np
import os

BLOCK = False
FIGURES_DIRECTORY = f"figures"


def plotting_drive_cycle(dataframe, title=f"Drive Cycle"):

    # Plot loss vs epochs
    fig, axes = plt.subplots(nrows=1, ncols=1)
    fig.suptitle(title)
    plt.grid()
    speed = dataframe['mph'].values
    axes.plot(speed)
    axes.set_ylabel('Speed')
    axes.set_xlabel('Time')

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
