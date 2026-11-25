# Reproducing the historical EMRI transport calculation

Unpack **EMRI_transport_numerics.zip** into an empty directory and run the commands below from that directory. Three sibling directories supply the inputs and analyses:

| Directory | Contents |
|---|---|
| `emri_research_work/` | Eleven 145-state inspiral trajectories with their original 36 states, two fine meshes, 22 fine-grid signed sparse class generators, 11 single-track and eight segment generators on the coarse Galactic Centre grid, normalized action-based shell projection, frozen-orbit controls, and circular weak-drag response code. The `regime/` subdirectory supplies the seed distribution and input ensemble. |
| `emri_population_work/` | Catalogue characteristic curves and class probabilities, independent formation models, rates, coherent-trajectory controls, fixed-count and Poisson-mean density profiles, and realized histories. Seven sparse replacement generators are in `checks/truncated/`. |
| `emri_paper/` | Thin numerical tables in `data/`, plotting programs, and independent validation programs. Run-time figures can go into `emri_paper/figures/` or a separate output directory. |

The principal checks use Python 3.12, NumPy, SciPy and Matplotlib. The clean replay used NumPy 2.4.2, SciPy 1.17.0 and Matplotlib 3.10.8. Other compatible numerical libraries can differ at floating-point roundoff. A new environment may be prepared with `python -m pip install numpy scipy matplotlib`. Precomputed sparse generators make the principal replay possible without FEW, a compiler, network access, a dense matrix cache, or further orbit sampling.

### Verify the inputs and reconstruct the fate budget

```sh
shasum -a 256 -c SHA256SUMS.txt
mkdir -p replay emri_paper/figures
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 MKL_NUM_THREADS=1
python emri_paper/data/endpoint_budget.py --root . --output replay --figure replay/phase_space.pdf
python emri_paper/validation/check_replay.py replay --reference emri_paper/data
```

On Linux, `sha256sum -c SHA256SUMS.txt` is an alternative. The program constructs each matrix exponential from the saved generator, averages over the catalogue classes, then propagates the initial cell masses and adjoint endpoint probabilities. It writes two CSV tables and one NPZ file. The budget contains 17 radial shells for each of GC \(N=270,330\) and lower-mass-host \(N=270\). The executable checks mass conservation, shell closure and agreement with the original fixed-count profiles.

### Reproduce the independent controls and plots

```sh
python emri_paper/validation/initial_shells.py emri_research_work emri_research_work/regime replay/initial_shells.csv
python emri_paper/validation/compare_frozen_survival.py emri_research_work emri_population_work emri_research_work/regime/emu/ens_60000.npz replay/frozen_comparison.csv
python emri_paper/validation/inner_slow_extrapolation.py --input emri_paper/data/lisa_slow_input.npz --output replay/inner_slow_extrapolation.csv
python emri_paper/validation/check_replay.py replay --reference emri_paper/data
python emri_paper/validation/extract_profiles.py .
python emri_paper/data/make_profiles.py
python emri_paper/data/make_geometry.py
```

`initial_shells.py` performs an independent local momentum integral. `compare_frozen_survival.py` uses the saved frozen-ensemble encounter hazards, the live finite-volume generators and their absorbing rows. `extract_profiles.py` rewrites the two thin plot tables from the supplied histories and means. It preserves their source data. The plot scripts create new figures. The endpoint figure alone can be redrawn with `python emri_paper/data/endpoint_budget.py --plot-only`.

### Repeat histories with fixed generators

The catalogue and maintained-cusp models share the same transport. The latter adds finite-volume probabilities for the unoccupied leading catalogue classes. These are the first three classes in the Galactic Centre and the first two in the lighter host. The saved configurations specify all weights, source count laws, and random seeds. To repeat the central profile and history calculations, using a reusable local cache for the 1,147-dimensional matrix exponentials:

```sh
cd emri_population_work/profiles
python population_profiles.py catalogue/config.json gc --output ../../replay/catalogue --slow-projector slow_fraction.npy --cache ../../replay/ops
python population_profiles.py catalogue/config.json low --output ../../replay/catalogue --slow-projector slow_fraction.npy --cache ../../replay/ops
python population_profiles.py tail_completion/support_completion/config.json gc --output ../../replay/maintained --slow-projector slow_fraction.npy --cache ../../replay/ops
python population_profiles.py tail_completion/config.json low --output ../../replay/maintained --slow-projector slow_fraction.npy --cache ../../replay/ops
cd ../..
```

For the catalogue coherence test, use `catalogue/coherent_tracks_config.json` in place of `catalogue/config.json`, add `--overrides ../checks/truncated` and choose a separate output directory. Do the same for the maintained-cusp configurations to test that scenario. The saved `profiles/catalogue/README.md` and `profiles/tail_completion/support_completion/README.md` describe the configuration and histories of each host. In the maintained-cusp projection, the model labels are `FV_empty_support` (GC) and `FV_tail` (lighter host). Each history includes the draws in their chronological order. The ensemble mean also integrates over the event count for a Poisson exposure.

The LISA example reuses the slower-than-circular component of each history. The inner-shell sensitivity can also reconstruct its small input file directly from the histories and response code with `python emri_paper/validation/inner_slow_extrapolation.py --catalogue emri_population_work/profiles/catalogue --lisa-code emri_research_work/lisa_control --input replay/lisa_slow_input.npz --output replay/inner_slow_extrapolation.csv`. To repeat the original calculation from the included tables, run `python emri_population_work/profiles/project_lisa.py --data emri_population_work/profiles/catalogue --archive`. This writes the projection tables in that scenario directory. Substitute `emri_population_work/profiles/tail_completion` without `--archive` for the maintained-cusp lighter host. Some named, historical diagnostics in the older directory READMEs refer to manuscript figures or optional matrix variants; the principal inputs and paths for this release are those given here.

### Test temporal overlap of long and short inspirals

The Galactic Centre control evolves a long inspiral with endpoint eccentricity 0.001 or 0.003 while other classes arrive as a Poisson process at 33 per Gyr. Initial distributions are the pristine spike and the mean state after 135 preceding inspirals. On the 28 × 16 grid, the warm transition matrix is rebuilt from class probabilities and the eleven shipped single-track generators. Eight more generators resolve the two long tracks into four successive intervals in log semimajor axis. The script checks SHA-256 hashes of these inputs, both track clocks, the projection, and the weights before computing the three time-order prescriptions.

```sh
python emri_paper/validation/overlapping_inspirals.py . --output replay/overlapping_inspirals.csv
python emri_paper/validation/check_replay.py replay --reference emri_paper/data --table overlapping_inspirals.csv
```

The replay covers 68 combinations of cold class, previous count, and shell. It compares simultaneous local evolution in each segment with placing the entire warm stream before or after the cold event. The warm events in this diagnostic are instantaneous, and the cold track is prescribed. It is a sensitivity test of event ordering at fixed population, rate and track geometry. The accompanying input manifest contains the exact commands to regenerate the coarse operators and shell projector.

### Rebuild more expensive inputs

Each generator integrates signed local flybys along a trajectory. To rebuild the nominal fine matrices instead of using the included ones, run these commands in a working copy because the programs write into their own directory:

```sh
cd emri_research_work/transport
python physical_transport.py gc_fine --q 0.000002325581395348837 --nx 44 --ny 26 --steps 72 --samples 320 --workers 3
python physical_transport.py low_fine --q 0.000033333333333333333 --nx 44 --ny 26 --steps 72 --samples 320 --workers 3
cd ../..
python emri_population_work/checks/truncate.py gc --workers 3
python emri_population_work/checks/truncate.py low --workers 3
python emri_research_work/profiles/make_projection.py emri_research_work/transport/transport_gc_fine.npz emri_research_work/regime replay/projection_fine.npz --order 10
```

The nominal impact-parameter multiplier is unity. Leave the optional `BMAX_FAC` environment setting unset, or set it to 1. The signed generators and the coherent-segment alternatives are supplied at their original floating-point precision. Dense exponential caches are local performance products and can be regenerated.

For the independent stellar-remnant capture flux, use `emri_population_work/formation/run_burst_checks.py`; its `burst` case produces the reference two host fits. The formation method, stochastic capture comparator (C++17), stellar supply calculation and binary-channel calculations are documented in their individual directories. The original tests used the cached outputs in this release. The complete disk of alternative intermediate matrices and event realization tables is not required for the principal replay; optional studies have their own regeneration scripts.

### FEW trajectories and the external source catalogue

The original 36-state trajectories were computed in FEW 2.2.1 with the equatorial Jacobian and dimensionless regulator spin \(10^{-6}\). The 145-state reconstruction used the FEW 1.4.10 scalar energy flux at the same regulator spin. The independent reintegration and class-edge mapping used FEW 1.4.10 scalar energy and angular-momentum fluxes, a Schwarzschild Jacobian and flux spin \(10^{-9}\). The latter checks used the interpreter compatible with that installed FEW binary. The source switches between a current FEW Python scalar-flux interface and an optional explicitly provided, compatible older shared library. The supplied trajectories and tables bypass this dependency for density calculations.

```sh
python emri_research_work/tracks/phasing_tracks.py --output replay/tracks
python emri_paper/data/binary_validation.py emri_research_work/tracks --output replay/binary_validation.csv
```

For a compatible older FEW build use `--legacy-dso /absolute/path/to/pyInspiral.so` on the first command and `--dso /absolute/path/to/pyInspiral.so` on the second. The independent check integrates the 5PN balance equations and radial periods anew. It can also be repeated with `--order 24` to test its clock quadrature.

The original raw catalogue is an external, versioned dataset, by D. Mancieri, L. Broggi, M. Vinciguerra, A. Sesana and M. Bonetti, *Eccentricity distribution of extreme mass ratio inspirals*, v1 (2025), DOI [10.5281/zenodo.17882705](https://doi.org/10.5281/zenodo.17882705). Derived class probabilities, boundaries, and source-row class indices for the two target masses accompany this bundle. To verify the weights against the authors’ data, use:

```sh
curl -fL -o replay/EMRI_ecc_distr.zip https://zenodo.org/records/17882705/files/EMRI_ecc_distr.zip
python -c 'import hashlib,pathlib; p=pathlib.Path("replay/EMRI_ecc_distr.zip"); assert p.stat().st_size==1578589 and hashlib.md5(p.read_bytes()).hexdigest()=="6d80679de78d944469f8e3f184be0c2b"'
python emri_population_work/catalogue/replay_classes.py replay/EMRI_ecc_distr.zip
```

To recompute the boundary curves from the fluxes, use `python emri_population_work/catalogue/map_decoupling_orbits.py replay/EMRI_ecc_distr.zip` in a FEW environment, adding `--dso` as above if necessary. This updates the derived catalogue files in the working copy. The source data at \(4\times10^6\,M_\odot\) supply a proxy for the Galactic Centre transport at \(4.3\times10^6\,M_\odot\).

### Release verification

The release check used a temporary extraction and recalculated the endpoint budget for both hosts directly from the packaged generators, independently of any cached exponentials. All 51 shell budgets and three full-domain budgets passed. The maximum absolute change in survival relative to the released tables was \(4.0\times10^{-13}\). The largest absolute change in any bound final cell mass was \(4.4\times10^{-13}\,M_\odot\). The frozen-orbit comparison reproduced all 66 rows byte for byte. The independently normalized shell checks differed by less than \(8\times10^{-14}\) in absolute units. The clean temporal-overlap replay verified all 23 solver input hashes and reproduced every column of the 68-row time-order comparison. The external v1 source replay reproduced the eleven class weights at all five catalogue masses. The independent FEW track check reproduced its archived CSV and the quadrature refinement changed the reported fractional clock errors by less than \(10^{-7}\).

Packaging reused the previously computed flyby kernels, radial and speed-cut projectors, original FEW 2.2.1 cached trajectories, remnant-source parameter scans, stochastic captures and population realizations. Those expensive stages were not run again during this release verification. All random seeds used by the supplied nominal generators and population scripts remain in those files.
