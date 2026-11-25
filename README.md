# Dark-matter spike evolution during extreme mass-ratio inspirals

Working material for the group. The population study asks how a sequence of inspirals changes the density profile of a dark-matter spike. The movies follow one 10-solar-mass companion from a semimajor axis of 720 gravitational radii to the end of stable inspiral around a Schwarzschild black hole of 4.30 million solar masses. In the vacuum runs only gravitational radiation drives the binary; all three runs evolve the dark matter through encounters with the companion.

## Group notes

- [PRD-style draft on the population calculation](EMRI_spike_transport.pdf) and [LaTeX source and figures](EMRI_spike_transport_source.zip)
- [Gf’s notes for Rodrigo](GR_setup_and_sampling.pdf) and [TeX source](GR_setup_and_sampling.tex). These describe the GR setup, sampling, impact parameters and loss cone for prescribed tracks.
- [Population research note and numerical supplement](https://github.com/gfbertone/emri-spike-depletion/releases/tag/research-v1). The release includes the research note, the replay archive for the PRD draft, and the later single-inspiral phase-space histories. See the [population replay instructions](REPRODUCE.md) and [catalogue provenance](eccentricity_catalogue_source.md).

## One inspiral in Sgr A*

| Orbit and binary evolution | Movie | Final frame | Four-year shell, in gravitational radii | Final shell density relative to initial |
|---|---|---|---:|---:|
| Eccentric, GW losses | [MP4](SgrA_eccentric_low_L_vacuum.mp4) | [PNG](SgrA_eccentric_low_L_vacuum_at_plunge.png) | 8.21863 | 0.933651 |
| Circular, GW losses | [MP4](SgrA_circular_low_L_vacuum.mp4) | [PNG](SgrA_circular_low_L_vacuum_at_plunge.png) | 7.75893 | 0.775071 |
| Circular, GW losses and sampled DM drag | [MP4](SgrA_circular_GW_DM_feedback.mp4) | [PNG](SgrA_circular_GW_DM_feedback_at_ISCO.png) | 7.75893 | 0.775172 |

The phase-space panel shows the change in the distribution over bound orbits with periapsis below 720 gravitational radii. The bottom-right panel integrates the evolved distribution at a single fixed radius, chosen separately for each track from the companion semimajor axis four source-frame years before plunge. The bars count the fraction of the initially shell-weighted population that has plunged or escaped. The purple marker follows the companion. In the eccentric movie the span in the orbit panel runs from periapsis to apoapsis.

The circular feedback calculation is a later extension to the manuscript. The [clock comparison](SgrA_circular_drag_clocks.png) and its [numerical table](SgrA_circular_three_clocks.csv) show the effect of two drag prescriptions on the elapsed inspiral time. Their spread is a modelling uncertainty. Fine structure in an individual phase-space cell should be interpreted with the grid resolution in mind.

## Check the density from the stored phase space

Download the three original NPZ files from the [data and source release](https://github.com/gfbertone/emri-spike-depletion/releases/tag/research-v1) into a directory named `data` beside `check_histories.py`. Python with NumPy is sufficient for the validation. Matplotlib is required to draw a figure.

```sh
python3 check_histories.py --data-dir data --output density.png
```

At each of the 609 stored epochs this script multiplies the occupancy ratio in each of the 226 × 156 cells by its initial contribution to the shell density, sums over the grid, and divides by the initial shell density. It checks the reconstructed ratio against the archived value and the four-year epoch against the companion track. The check tests projection and file consistency. The accuracy of the encounter model and convergence with grid spacing require separate physical and numerical tests.
