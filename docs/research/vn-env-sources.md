# VN research cards: radiation and dust sources (for the environment panel)

Notes for readers:
- Every card says WHERE and WHEN a value was measured. Values from Gale crater or from Opportunity's site are NOT Jezero values.
- No numbers in this file were calculated by us. Each number is copied from the cited source.
- Accessed on 2026-11-14 for all cards.

## Part 1. Radiation

# Research card: Solar radiation measured at Jezero (Perseverance MEDA RDS)
- Finding: Perseverance's MEDA instrument includes a Radiation and Dust Sensor (RDS) on the rover top deck: eight upward-viewing photodiodes covering 190-1,200 nm, eight lateral photodiodes (20 degrees above the horizon, 45 degrees apart in azimuth), a dark-current reference photodiode and an upward-looking camera (SkyCam). RDS measures the downwelling solar flux between 0.2 and 1.2 micrometers; the MEDA paper says this band is about 78% of the entire short-wave flux. Measurements started on 19 Feb 2021 (Ls 6.1, Mars Year 36) and are ongoing. Calibrated RDS data are CSV tables in the PDS Atmospheres Node (calibrated set about 10 GB, derived set about 2.9 GB). This is sunlight (non-ionizing radiation), NOT cosmic-ray dose.
- Source URL: https://pds-atmospheres.nmsu.edu/data_and_services/atmospheres_data/PERSEVERANCE/meda.html ; https://link.springer.com/article/10.1038/s41561-022-01084-0
- Organization / author: NASA PDS Atmospheres Node (New Mexico State University); MEDA team (Nature Geoscience paper, author list not verified)
- Version / date: PDS page shows data from Feb 2021, "ongoing", no page version date; Nature Geoscience paper covers the first 250 sols
- Accessed on: 2026-11-14
- License: Not stated on these pages; general PDS data statements are in the CRISM license card (vn-crism.md)
- Confidence: high for what the instrument measures and where the data is; not yet checked: actual UV or irradiance values

# Research card: How to cite MEDA data
- Finding: The PDS page gives this citation for the data set: J. A. Rodriguez-Manfredi et al. (2021), The Mars Environmental Dynamics Analyzer, MEDA, NASA Planetary Data System, DOI 10.17189/1522849.
- Source URL: https://pds-atmospheres.nmsu.edu/data_and_services/atmospheres_data/PERSEVERANCE/meda.html
- Organization / author: NASA PDS Atmospheres Node
- Version / date: citation year 2021
- Accessed on: 2026-11-14
- License: Not stated on this page
- Confidence: high

# Research card: Surface pressure measured at Jezero
- Finding: MEDA measured the daily mean surface pressure at Jezero over the first 250 sols. It rose from 735 Pa (sols 15-20, Ls 13-16 degrees) to a maximum of 761 Pa (sols 99-110, Ls 52-57 degrees), then fell to 650 Pa at sol 250 (Ls 125 degrees) as the southern polar cap grew. This matters for radiation because modeling studies say surface pressure (atmospheric depth) influences the surface radiation level.
- Source URL: https://link.springer.com/article/10.1038/s41561-022-01084-0
- Organization / author: MEDA team, "The diverse meteorology of Jezero crater over the first 250 sols of Perseverance on Mars", Nature Geoscience (author list not verified)
- Version / date: online 2022, DOI 10.1038/s41561-022-01084-0
- Accessed on: 2026-11-14
- License: Not found on the page I checked
- Confidence: high

# Research card: Ionizing radiation dose - no direct measurement found at Jezero
- Finding: I did not find any measured cosmic-ray dose rate at Jezero. The only direct surface measurement is from Curiosity at Gale crater (see the Gale card below). Modeling work says surface radiation depends on atmospheric depth: surface pressure, which is related to altitude, influences the surface and subsurface radiation level, and deep craters with thicker air reduce the heavy-ion contribution. So the Gale value cannot simply be copied to Jezero. A public model tool (RADMAREE, from the Europlanet project) exists that could estimate dose, but I have not used or verified it. If the project needs a Jezero dose, it must be labeled as an analogy to Gale or as a model result.
- Source URL: https://e-docs.geo-leo.de/handle/11858/9954 (model study); https://www.swsc-journal.org/articles/swsc/pdf/2019/01/swsc180060.pdf (RADMAREE tool)
- Organization / author: Zhang, J., Guo, J., Dobynde, M. I., Wang, Y. (model study); Guo, J. et al. (SWSC paper, authors not fully checked)
- Version / date: not checked (repository record and journal PDF)
- Accessed on: 2026-11-14
- License: Not found on the pages I checked
- Confidence: medium for the qualitative statement; low for any use of these papers to produce a Jezero number

# Research card: Surface radiation dose measured at Gale crater (NOT Jezero)
- Finding: Curiosity's RAD instrument measured an average galactic cosmic ray (GCR) absorbed dose rate of 0.210 +/- 0.040 mGy/day at Gale crater (about -4.4 km elevation) over about 300 sols (7 Aug 2012 - 1 Jun 2013), near the maximum of solar cycle 24. Daily values varied between about 180 and 225 microGy/day. The dose equivalent rate is reported as 0.64 +/- 0.12 mSv/day in Scientific American, a NASA slide deck and a Space Weather and Space Climate paper table, but the SwRI press release gives 0.67 mSv/day for the same period; the original paper must be checked to see which number applies to which quantity. On the cruise to Mars the dose equivalent rate was about 1.84 mSv/day. Scientific American also reports about 1.01 Sv for a 180-day cruise, 500-day stay and 180-day return. These are Gale values and must NOT be shown as Jezero measurements.
- Source URL: https://typeset.io/pdf/mars-surface-radiation-environment-measured-with-the-mars-244eildtx0.pdf (copy of the paper, absorbed dose); https://ntrs.nasa.gov/citations/20180007641 (record and abstract); https://www.scientificamerican.com/article/radiation-on-mars-managea/ ; https://www.sciencedaily.com/releases/2013/12/131209181133.htm (SwRI press release)
- Organization / author: Hassler, D. M., Zeitlin, C., et al. (Southwest Research Institute), "Mars' Surface Radiation Environment Measured with the Mars Science Laboratory's Curiosity Rover"
- Version / date: Science 343(6169), 1244797, 24 Jan 2014 (online 9 Dec 2013), DOI 10.1126/science.1244797
- Accessed on: 2026-11-14
- License: Not found on the pages I checked
- Confidence: high for the absorbed dose rate (read in the paper copy); medium for the dose equivalent (two values reported by secondary sources)

# Research card: Why radiation dose varies
- Finding: The RAD dose rate changes with (a) daily atmospheric pressure cycles, (b) Mars seasons, and (c) solar activity. Solar energetic particle (SEP) events produced dose rates several times higher than the quiet-time rate. A model fitted to the first Martian year of RAD data can predict dose rate from surface pressure and solar modulation. So a single number is only valid for one place, one time and one solar condition.
- Source URL: https://arxiv.org/pdf/1507.03473v1
- Organization / author: Guo, J., Zeitlin, C., Wimmer-Schweingruber, R. F., et al., "Modeling the variations of Dose Rate measured by RAD during the first MSL Martian year: 2012-2014"
- Version / date: arXiv v1, 2015
- Accessed on: 2026-11-14
- License: Not found on the page I checked
- Confidence: high

## Part 2. Dust

# Research card: Typical optical depth measured at Jezero (clear season, first 250 sols)
- Finding: During the clear season covered by the MEDA paper (first 250 sols, Ls 6-121 degrees, northern spring to early summer), SkyCam optical depth at Jezero was persistently higher in the morning (about 0.5) than in the afternoon (about 0.4). The authors say it is likely that part of the afternoon opacity, and most of the morning-afternoon difference, is due to water-ice haze, so these values are not pure dust. SkyCam opacity uncertainty is about 0.07. The paper also says a low dust optical depth of 0.3-0.6 with low variability is typical of OTHER sites in this season. RDS data gave dust particle sizes of about 1.2 to 1.4 micrometers. This does not cover the dusty season; the only measured Jezero storm value we have is in the January 2022 storm card.
- Source URL: https://link.springer.com/article/10.1038/s41561-022-01084-0
- Organization / author: MEDA team, "The diverse meteorology of Jezero crater over the first 250 sols of Perseverance on Mars", Nature Geoscience (author list not verified)
- Version / date: online 2022, DOI 10.1038/s41561-022-01084-0
- Accessed on: 2026-11-14
- License: Not found on the page I checked
- Confidence: high for the values quoted; they apply only to Ls 6-121 degrees

# Research card: Dust storm optical depth measured at Jezero (January 2022 storm)
- Finding: Over 5-11 January 2022 (Ls 153-156 degrees), a large regional dust storm passed over the Perseverance site in Jezero crater. Peak visible optical depth (tau) was about 2, and visibility across the crater was briefly reduced. Winds up to 20 m/s were recorded before the wind sensor was damaged. The rover imaged 21 dust-lifting events (gusts and dust devils) in one 25-minute period. Optical depth was measured with Mastcam-Z sun imaging, SkyCam, and the MEDA Radiation and Dust Sensor.
- Source URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9540647/ ; https://digital.inta.es:8443/jspui/handle/20.500.12666/842?locale=en
- Organization / author: Lemmon, M. T., Smith, M. D., et al., "Dust, Sand, and Winds Within an Active Martian Storm in Jezero Crater", Geophysical Research Letters 49(17), e2022GL100126
- Version / date: published 2022-09-09, DOI 10.1029/2022GL100126
- Accessed on: 2026-11-14
- License: Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 (as stated on the INTA repository record)
- Confidence: high

# Research card: Jezero optical depth data set (Mastcam-Z record)
- Finding: A public data set contains Perseverance Mastcam-Z measurements of visible aerosol optical depth at Jezero (77.5 E, 18.4 N) in four channels centered at 480, 544, 630 and 880 nm, derived from solar images. The authors say it shows typical Martian seasonal patterns, including several dust storms and ice clouds, so storm and ice-cloud periods must be separated when computing a "typical" dust value. A readme.txt in the download describes the file structure. I have NOT downloaded it, so I do not know the full-year tau range or the exact time range.
- Source URL: https://data.mendeley.com/datasets/gktjp9jptb/2
- Organization / author: Lemmon, M. (Space Science Institute, Boulder, CO), Mendeley Data
- Version / date: Version 2, published 7 April 2026, DOI 10.17632/gktjp9jptb.2
- Accessed on: 2026-11-14
- License: CC BY 4.0 (the "Licence" field on the page; please confirm by eye before relying on it)
- Confidence: high that the data set exists and what it contains; unknown: its actual values

# Research card: Dust devils and dust lifting at Jezero
- Finding: In the first 250 sols, MEDA saw dust devils as slight drops (about 0.4-26.0%) in radiation sensor readings; the paper says Jezero shows the highest abundance of dust devils detected so far by a surface mission on Mars. Pressure drops from dust devils were about 0.3 to 6.5 Pa and lasted 1 to 200 s; where wind data were available, diameters were 5 to 135 m. A separate RDS study counted 374 dust devils in the first 365 sols and estimated a formation frequency of 1.3 to 3.4 dust devils per km2 per sol, with average diameter about 29 m.
- Source URL: https://link.springer.com/article/10.1038/s41561-022-01084-0 ; https://digital.inta.es:8443/jspui/handle/20.500.12666/868
- Organization / author: MEDA team (Nature Geoscience paper, author list not verified); Toledo, D. et al. (JGR Planets 2023, repository record)
- Version / date: Nature Geoscience 2022 (first 250 sols); JGR Planets 2023 (first 365 sols)
- Accessed on: 2026-11-14
- License: The INTA repository record states a Creative Commons license (type not shown); Springer page: not found
- Confidence: medium to high (read from the paper text and a repository abstract)

# Research card: MEDA data cautions
- Finding: Dust builds up on MEDA's RDS and TIRS sensors, so readings need a correction. Per a 2025 conference abstract, MEDA TIRS data in the NASA PDS are corrected for dust, but RDS data are not; a "Dust Correction Factor" is used to quantify how much incoming radiation reaches the RDS top sensor. MEDA had measured for over 1450 sols (up to that abstract), and its wind sensor was damaged by sand and dust from sol 313 onward, so the best wind data are from the first 313 sols. A September 2025 abstract also says the dust deposited on the RDS sensors changes their optical response and needs calibration, and a September 2026 abstract reports ongoing work on RDS aerosol properties and dust deposition. Anyone using RDS irradiance must apply the correction or use corrected data.
- Source URL: https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-1461.html ; https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-680.html ; https://meetingorganizer.copernicus.org/EPSC2026/EPSC2026-378.html
- Organization / author: Vicente-Retortillo, A. (EPSC-DPS2025-1461); Rodriguez-Veloso, R. et al. (EPSC-DPS2025-680); EPSC2026-378 authors not checked
- Version / date: conference abstracts, Sep 2025 and Sep 2026
- Accessed on: 2026-11-14
- License: Not found on the pages I checked
- Confidence: medium (conference abstracts, not peer-reviewed papers)

# Research card: Perseverance RTG and the MEDA instrument
- Finding: The MEDA paper states that the rover carries a radioisotope thermoelectric generator (RTG) at the back, and that its heating effect on the ground seen by the TIRS sensor is negligible (less than 0.5 K). The paper does not discuss dust risk for solar-powered missions, so no "dust risk" statement can be sourced from it.
- Source URL: https://link.springer.com/article/10.1038/s41561-022-01084-0
- Organization / author: MEDA team (Nature Geoscience paper, author list not verified)
- Version / date: online 2022
- Accessed on: 2026-11-14
- License: Not found on the page I checked
- Confidence: high for the RTG statements; no source yet for solar-power dust risk at Jezero

# Research card: Dust storm tau at other sites (context only, NOT Jezero)
- Finding: For comparison only: NASA/JPL gives an average tau of 0.5 at Opportunity's location and 10.8 at the peak of the 2018 global storm. A NASA image caption says that at tau = 3 only about 5 percent of the sunlight directly reaches the surface. Opportunity's site is far from Jezero, so these numbers must not be shown as Jezero values.
- Source URL: https://jpl.nasa.gov/edu/news/2019/2/13/mars-rover-mission-comes-to-an-end-but-science-legacy-live-on ; https://science.nasa.gov/photojournal/mars-climate-sounder-studies-2018-dust-storm
- Organization / author: NASA/JPL-Caltech
- Version / date: 13 Feb 2019; image PIA22737 released 2018-10-30
- Accessed on: 2026-11-14
- License: Not found on the pages I checked
- Confidence: high for the numbers, but only for Opportunity's site
