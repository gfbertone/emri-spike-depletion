"""Reconstruct shell densities from the three released Sgr A* phase-space histories.

For initial shell contributions w_ij and stored occupancies F_ij(t) = f_ij(t)/f_ij(0),
the static-observer density ratio is S(t) = sum_ij w_ij F_ij(t) / sum_ij w_ij.
The weights are local to the specified four-year shell. F spans the full bound grid.
"""

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np


CASES = {
    "SgrA_eccentric_focused_phase_history.npz": "Eccentric, vacuum",
    "SgrA_circular_focused_phase_history.npz": "Circular, vacuum",
    "SgrA_circular_feedback_phase_history.npz": "Circular, GW + DM drag",
}
DEFAULT_DATA = Path(__file__).resolve().parent / "data"


@dataclass
class History:
    label: str
    shell: float
    semimajor: np.ndarray
    density: np.ndarray
    max_error: float


def reconstruct(path, label):
    with np.load(path, allow_pickle=False) as data:
        occupancy = data["f_over_f0"]
        weights = data["shell_weights_msun_pc3"]
        saved = data["density_ratio"]
        if "companion_a_rg" in data:
            semimajor = data["companion_a_rg"]
            shell = float(data["radius_rg"])
            years = data["years_left"]
            four_year = int(data["index_four_year"])
        else:
            semimajor = data["companion_radius_rg"]
            shell = float(data["shell_radius_rg"])
            years = data["years_to_ISCO"]
            four_year = int(data["four_year_epoch"])

    if occupancy.ndim != 3 or weights.shape != occupancy.shape[1:]:
        raise ValueError("phase-space and shell-weight grids have incompatible shapes")
    epochs = occupancy.shape[0]
    if any(a.shape != (epochs,) for a in (saved, semimajor, years)):
        raise ValueError("inconsistent numbers of epochs")
    for values in (weights, occupancy, saved, semimajor, years):
        if not np.isfinite(values).all():
            raise ValueError("nonfinite number in history")
    if np.min(weights) < 0 or weights.sum() <= 0 or np.min(occupancy) < 0:
        raise ValueError("invalid shell weights or occupations")
    if not 0 <= four_year < epochs or not np.isclose(years[four_year], 4, rtol=0, atol=1e-10):
        raise ValueError("invalid four-year epoch")
    np.testing.assert_allclose(semimajor[four_year], shell, rtol=1e-12)
    if (np.diff(semimajor) >= 0).any() or (np.diff(years) >= 0).any():
        raise ValueError("orbital radius and time to plunge must decrease")
    np.testing.assert_allclose(occupancy[0], 1.0, rtol=0, atol=1e-12)
    normalized_weights = weights.ravel() / weights.sum()
    density = occupancy.reshape(epochs, -1) @ normalized_weights
    np.testing.assert_allclose(density, saved, rtol=8e-13, atol=5e-14)
    return History(label, shell, semimajor, density, float(np.abs(density - saved).max()))


def plot(histories, output):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4.8), layout="constrained")
    colors = ["#253049", "#bb572c", "#147773"]
    for history, color, style in zip(histories, colors, ["-", "-", "--"]):
        ax.loglog(history.semimajor, history.density, color=color, linestyle=style,
                  linewidth=2.2, label=rf"{history.label} ($r_*/r_g={history.shell:.5f}$)")
    ax.invert_xaxis()
    ax.set_xticks([720, 300, 100, 30, 10, 6], labels=["720", "300", "100", "30", "10", "6"])
    ax.set_yticks([0.8, 0.85, 0.9, 0.95, 1.0], labels=["0.80", "0.85", "0.90", "0.95", "1.00"])
    ax.tick_params(axis="y", which="minor", labelleft=False)
    ax.set(xlabel=r"Companion semimajor axis $a/r_g$",
           ylabel=r"Shell density $\rho(r_*,t)/\rho(r_*,0)$",
           title="Density at the four-year shell during a single Sgr A* inspiral")
    ax.grid(alpha=0.2)
    ax.legend(frameon=False, fontsize=9)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA,
                        help="directory with the three original NPZ archives (default: repository data/)")
    parser.add_argument("--output", type=Path, help="optional density figure, e.g. density.png or density.pdf")
    args = parser.parse_args()
    histories = []
    for filename, label in CASES.items():
        path = args.data_dir / filename
        try:
            history = reconstruct(path, label)
        except (OSError, KeyError, ValueError, AssertionError) as error:
            parser.exit(1, f"{path}: {error}\n")
        histories.append(history)
        print(f"{label}: {history.density.size} epochs, r*/rg={history.shell:.9f}, "
              f"final rho/rho0={history.density[-1]:.10f}, max |reconstructed - saved|={history.max_error:.2e}")
    if args.output:
        plot(histories, args.output)


if __name__ == "__main__":
    main()
