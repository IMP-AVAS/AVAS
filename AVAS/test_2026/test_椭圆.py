import numpy as np
import matplotlib.pyplot as plt
def plot_twiss_ellipse(alpha, beta, emit, n=800, **plot_kwargs):

    theta = np.linspace(0, 2 * np.pi, n)
    xe = np.sqrt(emit * beta) * np.cos(theta)
    xpe = -np.sqrt(emit / beta) * (alpha * np.cos(theta) + np.sin(theta))

    default_kwargs = {"color": "r"}
    default_kwargs.update(plot_kwargs)

    plt.plot(xe, xpe, **default_kwargs)
    return xe, xpe


alpha = -0.003096
beta = 0.001855
emit =  342.33474122238385

plot_twiss_ellipse(alpha, beta, emit, color='r', lw=2)


plt.show()