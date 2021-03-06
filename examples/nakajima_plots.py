from collections import defaultdict

import numpy as np
import unyt as u
from cycler import cycler
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from labellines import labelLines
from prepic import GaussianBeam, Laser, Plasma, matched_laser_plasma

line_styles = ["-", "--", ":", "-."]
line_colors = ["C0", "C1", "C3", "C4"]

cyl = cycler(linestyle=line_styles) * cycler(color=line_colors)
loop_cy_iter = cyl()
STYLE = defaultdict(lambda: next(loop_cy_iter))

fig = Figure(figsize=(6.4, 6.4))
canvas = FigureCanvas(fig)
ax = fig.add_subplot(111)

beam = GaussianBeam(w0=15.0 * u.micrometer, λL=0.8 * u.micrometer)
electron_densities = np.logspace(-2, 2, 20) * 1e18 / (u.cm ** 3)

for a0 in np.linspace(2.0, 8.0, 7) * u.dimensionless:
    laser = Laser.from_a0(a0=a0, τL=30.0 * u.femtosecond, beam=beam)

    x_data = []
    y_data = []
    for npe in electron_densities:
        plasma = Plasma(n_pe=npe, laser=laser)
        x_data.append(plasma.npe)
        y_data.append(plasma.ΔE)

    h_axis = u.unyt_array(x_data)
    v_axis = u.unyt_array(y_data)

    a0_val = a0.to_value("dimensionless")
    ax.plot(
        h_axis.value,
        v_axis.value,
        color=STYLE[str(a0_val)]["color"],
        linestyle=STYLE[str(a0_val)]["linestyle"],
        label=f"$a_0$={a0_val}",
    )

    matched_plasma = matched_laser_plasma(
        a0=a0, beam=GaussianBeam(λL=0.8 * u.micrometer)
    )

    ax.scatter(
        matched_plasma.npe.value,
        matched_plasma.ΔE.value,
        marker="o",
        color=STYLE[str(a0_val)]["color"],
    )

    ax.set(
        ylabel=f"$\\Delta E$ [${v_axis.units.latex_repr}$]",
        xlabel=f"$n_e$ [${h_axis.units.latex_repr}$]",
        xlim=[electron_densities[0].value, electron_densities[-1].value],
    )
    ax.set_yscale("log")
    ax.set_xscale("log")

labelLines(ax.get_lines(), align=False, fontsize=8)

# Note: the figure only depends on λL.
# Different combinations of (w0, τL, ɛL) can give the same a0
fig.suptitle(f"λL={beam.λL}")
canvas.print_png(f"energy_scaling_vs_density.png")
