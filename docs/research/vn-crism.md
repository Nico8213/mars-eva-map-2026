# Research card: CRISM instrument and mission timeline
- Finding: CRISM (Compact Reconnaissance Imaging Spectrometer for Mars) is a visible/near-infrared imaging spectrometer on the Mars Reconnaissance Orbiter. It collected hyperspectral images of the Martian surface and atmosphere from 27 Sep 2006 to 7 May 2022. The dataset is therefore fixed (no new CRISM observations after May 2022), and the archive is in the PDS.
- Source URL: https://authors.library.caltech.edu/records/h6pv6-fhf02
- Organization / author: Seelos, F. P. et al. (JHU/APL), "The CRISM investigation in Mars orbit: Overview, history, and delivered data products"
- Version / date: Icarus paper (2023), Caltech repository record
- Accessed on: 2026-11-14
- License: Not found on the page I checked
- Confidence: high

# Research card: CRISM archive location and current versions
- Finding: CRISM data are archived at the PDS Geosciences Node (Washington University in St. Louis). The MRO page lists CRISM Archive and CRISM Type Spectra Library. Version 4 of the CRISM MRDRs (map-projected multispectral products) was posted on 29 Jun 2022, with more version 4 MRDRs added on 13 Apr 2023. Release 19 of MTRDR and TER (targeted map-projected products) was posted on 24 Jan 2022.
- Source URL: https://pds-geosciences-test.wustl.edu/missions/mro/default.htm
- Organization / author: PDS Geosciences Node, Washington University in St. Louis (NASA)
- Version / date: page lists events from 2022-2024; this is a "test" mirror URL, so re-check on the main site https://pds-geosciences.wustl.edu/missions/mro/
- Accessed on: 2026-11-14
- License: See license card below
- Confidence: medium (found on a mirror/test page; confirm on the main page)

# Research card: CRISM product types and file naming
- Finding: The official data product specification (CRISM DPSIS, version 1.3.7.7) describes the product levels: EDR (raw), CDR (calibration), TRDR (targeted reduced), DDR (derived/ancillary geometry), MRDR (map-projected multispectral), MTRDR (map-projected targeted). The PDS4 bundles for DDR and MTRDR are published at pds.nasa.gov. In file names, TRR3 means a calibrated reflectance (I/F) cube, DDR1 is the companion cube with latitude/longitude and viewing angles, and the last letter S or L means the short-wavelength (VNIR) or long-wavelength (IR) detector.
- Source URL: https://pds-geosciences.wustl.edu/mro/mro-m-crism-2-edr-v1/mrocr_0001/document/crism_dpsis.htm
- Organization / author: S. Murchie (JHU/APL), T. Stein, J. Ward (PDS Geosciences Node)
- Version / date: DPSIS v1.3.7.7, change log shows updates through Oct 2024
- Accessed on: 2026-11-14
- License: See license card below
- Confidence: high for product types; medium for the file-name rule (taken from the MarsSI wiki, https://marssi.univ-lyon1.fr/wiki/+show/+be447917540c4993beaecf1064dfe593/CRISM)

# Research card: CRISM spectral range and spatial resolution
- Finding: Targeted hyperspectral observations have 544 bands covering 362-3920 nm. Full Resolution Targeted (FRT) images are about 18 m/pixel (the same wiki also says "20 m/px" in one sentence). Half-resolution targeted types (HRS, HRL) are about 36 m/pixel. Survey products are coarser: multispectral survey (MSP) 200 m/pixel with 55 channels, hyperspectral survey (HSP) 200 m/pixel with 154 channels, multispectral window (MSW) 100 m/pixel.
- Source URL: https://marssi.univ-lyon1.fr/wiki/+show/+2f33b53ea4bc4b828d6f93c001c4538e/CRISM
- Organization / author: MarsSI platform wiki, Univ. Lyon 1
- Version / date: wiki page, no version date shown
- Accessed on: 2026-11-14
- License: Not found on the page I checked
- Confidence: medium (secondary source; should be confirmed against the official SIS or Murchie et al. 2007, JGR 112(E5))

# Research card: CRISM coverage of Jezero
- Finding: Published studies used full-resolution CRISM coverage of Jezero crater, the Jezero watershed and the area just north of it. Examples of images over the western delta are HRL40FF and FRT47A3, and long multispectral strips cover the watershed. Targeted images are small patches, not a continuous map, so Jezero is NOT fully covered at the highest resolution.
- Source URL: https://arxiv.org/pdf/1904.11414
- Organization / author: Brown, A. J., Viviano, C. E., Goudge, T. A., "Olivine-Carbonate Mineralogy of the Jezero Crater Region"
- Version / date: J. Geophys. Res. Planets, published 2020-02-21, DOI 10.1029/2019je006011
- Accessed on: 2026-11-14
- License: Not found on the page I checked (journal article; arXiv copy)
- Confidence: high that coverage exists; low on exactly which areas are covered (needs a coverage map check)

# Research card: CRISM license and citation rules
- Finding: PDS data sets are classified TSPA (Technology and Software Publicly Available) and may be exported as public open literature. JPL-supplied documents, images and data in the PDS may be used by any person for any purpose without prior permission, subject to the JPL policy. The PDS Geosciences Node metadata for a CRISM DDR coverage file states there are no access or use limits and points to its citations page. Citations should name "NASA Planetary Data System" as the publisher; PDS4 citation guidance is on the PDS site.
- Source URL: https://pds-geosciences.wustl.edu/jplcopyright.html (JPL policy); https://pds-geosciences.wustl.edu/geocopy/test/ddr/mars_mro_crism_ddr_na.shp.xml (use limit statement); https://pds.nasa.gov/datastandards/citing (how to cite); https://search-pdsppi.igpp.ucla.edu/faq.jsp (TSPA statement)
- Organization / author: NASA PDS Geosciences Node; PDS Planetary Plasma Interactions Node (FAQ)
- Version / date: no version shown; metadata file generated 2025-02-06
- Accessed on: 2026-11-14
- License: No access or use limits stated for CRISM data; JPL policy applies to JPL-supplied material. Attribution to the data provider and PDS is expected.
- Confidence: medium (no single page says "CRISM license: X"; the statements above are for PDS data in general and for one CRISM metadata file). Ask Nico to confirm against the Space Apps rules.

# Research card: CRISM known issues and cautions
- Finding: (1) Spectral parameter maps are not mineral maps; the spectra themselves must be checked. (2) Detection labels are evidence, not proof, and instrument artifacts can look like real results. (3) Ratioing procedures can create inverted or false features if the reference spectrum is not featureless. (4) Targeted data have column-dependent noise and residual atmospheric absorption that need correction. These cautions come from the MarsSI wiki, not from the CRISM team.
- Source URL: https://marssi.univ-lyon1.fr/wiki/+show/+648c1e70c6bc44919be4bd17366f458f/CRISM
- Organization / author: MarsSI platform wiki, Univ. Lyon 1
- Version / date: wiki page, parameters described "as in April 2018"
- Accessed on: 2026-11-14
- License: Not found on the page I checked
- Confidence: medium

Still to check:
- Official CRISM team page (JHU/APL) for the latest recommended calibration version
- Whether a CRISM MTRDR or MRDR product covers our Jezero crop, and its file size
- Direct download links for the Jezero products (ask Xin En which product he needs)
- Confirm the official FRT resolution in Murchie et al. 2007
