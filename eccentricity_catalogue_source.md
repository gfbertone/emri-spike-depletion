# Published eccentricity catalogue

Davide Mancieri, Luca Broggi, Morgan Vinciguerra, Alberto Sesana and Matteo Bonetti. *Eccentricity distribution of extreme mass ratio inspirals*, dataset version 1, Zenodo, 11 December 2025. The data describe decoupling and plunge for a ten-solar-mass companion and five Schwarzschild primary masses. Each source row carries an astrophysical weight. The weighted results derived for this note are stored separately from the authors' five tables. [Dataset and source documentation](https://doi.org/10.5281/zenodo.17882705) [Companion article](https://doi.org/10.1103/vq2j-kbhs)

Retrieve the source from this directory and check the exact bytes used in the analysis.

```sh
curl --fail --location --output EMRI_ecc_distr.zip https://zenodo.org/records/17882705/files/EMRI_ecc_distr.zip
python -c "from pathlib import Path; import hashlib; p=Path('EMRI_ecc_distr.zip'); assert p.stat().st_size==1578589 and hashlib.md5(p.read_bytes()).hexdigest()=='6d80679de78d944469f8e3f184be0c2b'; print('Zenodo checksum verified')"
```

The authors give the field definitions, FEW integration endpoints and weighting scheme in the README inside the downloaded ZIP. Their high-mass table uses a 4-million-solar-mass primary. The Galactic Centre transport model in the research note uses 4.3 million solar masses.

Run `python replay_classes.py EMRI_ecc_distr.zip` to verify the reported 11-class weights for every host using only NumPy, SciPy, the published data and the supplied 5PN boundary grid. The replay interpolates log(1−e) against log(a) within the tabulated range. It recovers the direct-integrator class of every source orbit in the v1 file. To recompute the boundary grid from the underlying fluxes, see 5PN_mapping.md.
