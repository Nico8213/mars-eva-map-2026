# VN research cards: radiation and dust sources (for the environment panel)

Notes for readers:
- Every card says WHERE and WHEN a value was measured. Values from Gale crater or from Opportunity's site are NOT Jezero values.
- No numbers in this file were calculated by us. Each number is copied from the cited source.
- Accessed on 2026-11-14 for all cards.

## Part 1. Radiation

# Research card: Solar radiation measured at Jezero (Perseverance MEDA RDS)
- Finding: Perseverance's MEDA instrument includes a Radiation and Dust Sensor (RDS) on the rover top deck: eight upward-viewing photodiodes covering 190-1,200 nm, eight lateral photodiodes (20 degrees above the horizon, 45 degrees apart in azimuth), a dark-current reference photodiode and an upward-looking camera (SkyCam). RDS measures the downwelling solar flux between 0.2 and 1.2 micrometers; the MEDA paper says this band is about 78% of the entire short-wave flux. Measurements started on 19 Feb 2021 (Ls 6.1, Mars Year 36) and are ongoing. Calibrated RDS data are CSV tables in the PDS Atmospheres Node (calibrated set about 10 GB, derived set about 2.9 GB). This is sunlight (non-ionizing radiation), NOT cosmic-ray dose.
- Source URL: https://pds-atmospheres.nmsu.edu/data_and_services/atmospheres_data/PERSEVERANCE/meda.html ; https://link.springer.com/article/10.1038/s41561-022-01084-0
- Organization / author: NASA PDS Atmospheres Node (New Mexico State University); Rodriguez-Manfredi, J. A., et al., Nature Geoscience 16, 19-28 (2023)
- Version / date: PDS page shows data from Feb 2021, "ongoing", no page version date; the paper covers the first 250 sols
- Accessed on: 2026-11-14
- License: PDS page: not stated; paper: CC BY-NC-ND 4.0 (stated on the INTA repository record, https://digital.inta.es/entities/publication/633f6a5c-f6ae-43b0-9c2e-9f71845361b5/full); general PDS data statements are in the CRISM license card (vn-crism.md)
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
- Finding: MEDA measured the daily mean surface pressure at Jezero over the first 250 sols. It rose from 735 Pa (sols 15-20, Ls 13-16 degrees) to a maximum of 761 Pa (sols 99-110, Ls 52-57 degrees), then fell to 650 Pa at sol 250 (Ls 125 degrees) as the southern polar cap grew. This matters for radiation because the Gale measurements show dose rate is anticorrelated with atmospheric pressure (column depth).
- Source URL: https://link.springer.com/article/10.1038/s41561-022-01084-0
- Organization / author: Rodriguez-Manfredi, J. A., et al., "The diverse meteorology of Jezero crater over the first 250 sols of Perseverance on Mars", Nature Geoscience 16, 19-28
- Version / date: published 2023-01-09, DOI 10.1038/s41561-022-01084-0
- Accessed on: 2026-11-14
- License: CC BY-NC-ND 4.0 (INTA repository record)
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
- Finding: Curiosity's RAD instrument measured, over about 300 sols (7 Aug 2012 - 1 Jun 2013) at Gale crater (about -4.4 km elevation), near the maximum of solar cycle 24: an average galactic cosmic ray (GCR) absorbed dose rate of 0.210 +/- 0.040 mGy/day (daily values between 180 and 225 microGy/day), an average quality factor of 3.05 +/- 0.26, and a GCR dose-equivalent rate of 0.64 +/- 0.12 mSv/day. Inside the spacecraft during cruise the dose-equivalent rate was 1.84 +/- 0.30 mSv/day. Surface values per year (paper Table 3): 76 mGy/year absorbed and 232 mSv/year dose equivalent. The paper estimates about 1.01 Sv for a round trip with 180 days each way and 500 days on the surface. The average atmospheric column was about 21 g/cm2. One hard solar energetic particle event (sol 242, 12-13 Apr 2013) raised the surface dose rate by about 30% over the GCR rate. A press release quoted 0.67 mSv/day for the same period; that number is not in the paper, so use 0.64. These are Gale values and must NOT be shown as Jezero measurements.
- Source URL: https://typeset.io/pdf/mars-surface-radiation-environment-measured-with-the-mars-244eildtx0.pdf (repository copy of the paper)
- Organization / author: Hassler, D. M., Zeitlin, C., Wimmer-Schweingruber, R. F., et al. (Southwest Research Institute), "Mars' Surface Radiation Environment Measured with the Mars Science Laboratory's Curiosity Rover"
- Version / date: Science 343(6169), 1244797, 24 Jan 2014 (online 9 Dec 2013), DOI 10.1126/science.1244797
- Accessed on: 2026-11-14
- License: Copyright AAAS; the repository copy says it is for personal, non-commercial use only. Do not copy its figures or tables into the project; cite the numbers. The RAD data are archived in the PDS Planetary Plasma Interactions (PPI) node.
- Confidence: high (numbers read in the paper itself)

# Research card: Why radiation dose varies
- Finding: The RAD dose rate changes with (a) daily atmospheric pressure cycles (dose rate and pressure are anticorrelated), (b) Mars seasons, and (c) solar activity. Solar energetic particle (SEP) events produced dose rates several times higher than the quiet-time rate in one modeling study. A model fitted to the first Martian year of RAD data can predict dose rate from surface pressure and solar modulation. So a single number is only valid for one place, one time and one solar condition.
- Source URL: https://arxiv.org/pdf/1507.03473v1 ; https://typeset.io/pdf/mars-surface-radiation-environment-measured-with-the-mars-244eildtx0.pdf
- Organization / author: Guo, J., Zeitlin, C., Wimmer-Schweingruber, R. F., et al., "Modeling the variations of Dose Rate measured by RAD during the first MSL Martian year: 2012-2014"; Hassler et al. 2014 (pressure anticorrelation)
- Version / date: arXiv v1, 2015; Science 2014
- Accessed on: 2026-11-14
- License: Not found on the arXiv page; Hassler paper: see Gale card
- Confidence: high

## Part 2. Dust

# Research card: Typical optical depth measured at Jezero (clear season, first 250 sols)
- Finding: During the clear season covered by the MEDA paper (first 250 sols, Ls 6-121 degrees, northern spring to early summer), SkyCam optical depth at Jezero was persistently higher in the morning (about 0.5) than in the afternoon (about 0.4). The authors say it is likely that part of the afternoon opacity, and most of the morning-afternoon difference, is due to water-ice haze, so these values are not pure dust. SkyCam opacity uncertainty is about 0.07. The paper also says a low dust optical depth of 0.3-0.6 with low variability is typical of OTHER sites in this season. RDS data gave dust particle sizes of about 1.2 to 1.4 micrometers. This does not cover the dusty season; the only measured Jezero storm value we have is in the January 2022 storm card.
- Source URL: https://link.springer.com/article/10.1038/s41561-022-01084-0
- Organization / author: Rodriguez-Manfredi, J. A., et al., Nature Geoscience 16, 19-28
- Version / date: published 2023-01-09, DOI 10.1038/s41561-022-01084-0
- Accessed on: 2026-11-14
- License: CC BY-NC-ND 4.0 (INTA repository record)
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
- Finding: Three studies, with different periods and methods, so their numbers must not be mixed. (1) MEDA paper, first 250 sols: dust devils appear as slight drops (about 0.4-26.0%) in radiation sensor readings; Jezero shows the highest abundance of dust devils detected so far by a surface mission; pressure drops were about 0.3 to 6.5 Pa and lasted 1 to 200 s. (2) Hueso et al., 415 sols (Ls 6-213 degrees): modeled diameters 5.0 to 135 m, about 2-3 dust devils formed per km2 per sol; vortices larger than 100 m occur about 0.1 per km2 per sol and dominate dust lifting; two dust devils damaged part of the wind sensor hardware. (3) Toledo et al. (RDS), first 365 sols: 374 dust devils, formation frequency 1.3 to 3.4 per km2 per sol, average diameter about 29 m.
- Source URL: https://link.springer.com/article/10.1038/s41561-022-01084-0 ; https://searchworks.jioinstitute.edu.in/articles/edb__162055620 ; https://digital.inta.es:8443/jspui/handle/20.500.12666/868
- Organization / author: Rodriguez-Manfredi, J. A., et al., Nature Geoscience 16, 19-28 (2023); Hueso, R., Newman, C. E., et al., "Convective Vortices and Dust Devils Detected and Characterized by Mars 2020", JGR Planets 128(2), 2023, DOI 10.1029/2022JE007516; Toledo, D. et al., JGR Planets 2023 (repository record)
- Version / date: as listed
- Accessed on: 2026-11-14
- License: Nature Geoscience paper CC BY-NC-ND 4.0; others: Creative Commons (type not shown) for the INTA record, not found for the Hueso record
- Confidence: medium to high (Hueso and Toledo read from abstracts)

# Research card: Dust accumulation on the RDS and dust removal at Jezero
- Finding: Dust settling on the RDS photodiodes blocks sunlight, so a Dust Correction Factor (DCF) is used. After one Mars year, dust on the photodiode surface attenuated 25-30% of the incoming solar radiation. The DCF did not decrease steadily; a model of its evolution gave dust deposition and lifting rates, and showed that dust removal is 9 times larger at Jezero than at InSight's location in western Elysium Planitia. Related MEDA work on surface albedo found that the January 2022 dust storm (Ls about 155 degrees) lowered the surface albedo by 17%, about ten times more than the changes made by dust devils in quiet periods, and that albedo changes were linked to peak winds above 15 m/s. Albedo changed in 3.5% of dust devils with a pressure drop below 2.5 Pa, in 43% above 2.5 Pa, and in 100% above 4.5 Pa.
- Source URL: https://doaj.org/article/3f0aded7a789434e82a1774d04354f6c ; https://addi.ehu.es/handle/10810/61122?show=full ; https://www.aminer.org/pub/645d0359d68f896efa91a2fb/dust-lifting-through-surface-albedo-changes-at-jezero-crater-mars
- Organization / author: Vicente-Retortillo, A., Lemmon, M. T., Martinez, G. M., et al., "Dust Accumulation and Lifting at the Landing Site of the Mars 2020 Mission, Jezero Crater, as Observed From MEDA", Geophysical Research Letters 51(11), 2024; Vicente-Retortillo, A., Martinez, G. M., Lemmon, M. T., et al., "Dust Lifting Through Surface Albedo Changes at Jezero Crater, Mars" (year not checked)
- Version / date: GRL June 2024, DOI 10.1029/2023GL107975 (open access)
- Accessed on: 2026-11-14
- License: GRL: open access, license type not shown; albedo paper: CC BY-NC-ND 3.0 ES (as stated on the repository record)
- Confidence: high for the GRL abstract numbers; medium for the albedo paper (read from abstracts)

# Research card: Dust risk for solar-powered missions at Jezero
- Finding: The 2024 GRL paper says its projections show seasonal net dust removal at Jezero, which the authors call encouraging for the long-term survival of solar-powered missions to Jezero or similarly active dust-lifting regions. This is a model projection based on MEDA data, not a guarantee. Perseverance itself carries an RTG (see RTG card), so this concerns future solar-powered missions.
- Source URL: https://doaj.org/article/3f0aded7a789434e82a1774d04354f6c
- Organization / author: Vicente-Retortillo, A., Lemmon, M. T., et al., Geophysical Research Letters 51(11)
- Version / date: June 2024, DOI 10.1029/2023GL107975
- Accessed on: 2026-11-14
- License: Open access, license type not shown
- Confidence: medium (read from the abstract only)

# Research card: MEDA data cautions
- Finding: Dust builds up on MEDA's RDS and TIRS sensors, so readings need a correction. Per a 2025 conference abstract, MEDA TIRS data in the NASA PDS are corrected for dust, but RDS data are not; the Dust Correction Factor is used to quantify how much incoming radiation reaches the RDS top sensor. MEDA had measured for over 1450 sols (up to that abstract), and its wind sensor was damaged by sand and dust from sol 313 onward, so the best wind data are from the first 313 sols. A September 2025 abstract also says the dust deposited on the RDS sensors changes their optical response and needs calibration, and a September 2026 abstract reports ongoing work on RDS aerosol properties and dust deposition. Anyone using RDS irradiance must apply the correction or use corrected data.
- Source URL: https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-1461.html ; https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-680.html ; https://meetingorganizer.copernicus.org/EPSC2026/EPSC2026-378.html
- Organization / author: Vicente-Retortillo, A. (EPSC-DPS2025-1461); Rodriguez-Veloso, R. et al. (EPSC-DPS2025-680); EPSC2026-378 authors not checked
- Version / date: conference abstracts, Sep 2025 and Sep 2026
- Accessed on: 2026-11-14
- License: Not found on the pages I checked
- Confidence: medium (conference abstracts, not peer-reviewed papers)

# Research card: Perseverance RTG and the MEDA instrument
- Finding: The MEDA paper states that the rover carries a radioisotope thermoelectric generator (RTG) at the back, and that its heating effect on the ground seen by the TIRS sensor is negligible (less than 0.5 K). The Hassler paper also mentions that Curiosity's RTG adds a background dose rate that has to be subtracted from RAD readings.
- Source URL: https://link.springer.com/article/10.1038/s41561-022-01084-0 ; https://typeset.io/pdf/mars-surface-radiation-environment-measured-with-the-mars-244eildtx0.pdf
- Organization / author: Rodriguez-Manfredi, J. A., et al., Nature Geoscience 16, 19-28 (2023); Hassler et al., Science 2014
- Version / date: as listed
- Accessed on: 2026-11-14
- License: see the cards above
- Confidence: high for the RTG statements

# Research card: Dust storm tau at other sites (context only, NOT Jezero)
- Finding: For comparison only: NASA/JPL gives an average tau of 0.5 at Opportunity's location and 10.8 at the peak of the 2018 global storm. A NASA image caption says that at tau = 3 only about 5 percent of the sunlight directly reaches the surface. Opportunity's site is far from Jezero, so these numbers must not be shown as Jezero values.
- Source URL: https://jpl.nasa.gov/edu/news/2019/2/13/mars-rover-mission-comes-to-an-end-but-science-legacy-live-on ; https://science.nasa.gov/photojournal/mars-climate-sounder-studies-2018-dust-storm
- Organization / author: NASA/JPL-Caltech
- Version / date: 13 Feb 2019; image PIA22737 released 2018-10-30
- Accessed on: 2026-11-14
- License: Not found on the pages I checked
- Confidence: high for the numbers, but only for Opportunity's site

## Still to check
- Full-year Jezero tau range: download the Mastcam-Z data set and let a program compute it, separating storm and ice-cloud periods (do not estimate by hand); confirm the CC BY 4.0 licence on the Mendeley page
- Actual Jezero UV or solar irradiance values from MEDA RDS (calibrated data; RDS in the PDS is not dust-corrected, so apply the DCF)
- Any ionizing radiation dose measured or modeled specifically for Jezero (none found so far; one unverified lead: a Scientific Reports study on cosmogenic nuclide production in Jezero rocks using RAD neutron data, which is nuclide production, not human dose)
- License terms for the PDS MEDA data (the PDS page gives a citation and DOI but no license statement)
- Year of the Vicente-Retortillo albedo paper and which journal it appeared in
