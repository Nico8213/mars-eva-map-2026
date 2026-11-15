# VN research cards: license checks for MEDA RDS, MEDA derived data and the Curiosity RAD paper

Notes for readers:
- One source per item, as requested. Accessed on 2026-11-14 for all cards.

# Research card: License - MEDA RDS data
- Finding: RDS data are CSV tables in the MEDA bundle (urn:nasa:pds:mars2020_meda, version 6.0 in the release folder dated 2026-08-11). The bundle readme and the Atmospheres Node page give a citation and DOI (10.17189/1522849) but no license text. The general PDS statement (PDS Geosciences Node FAQ) is that data sets archived in the PDS are in the public domain and carry a TSPA classification; this FAQ belongs to the Geosciences Node, so I did not confirm that the Atmospheres Node (which hosts MEDA) publishes the same sentence. RDS data are not corrected for dust in the PDS (EPSC-DPS2025-1461).
- Source URL: https://pds-geosciences.wustl.edu/faq.html ; https://pds-atmospheres.nmsu.edu/data_and_services/atmospheres_data/PERSEVERANCE/meda.html ; https://pds.nasa.gov/data/pds4/releases/atmos/mars2020_meda-20260811/readme.txt
- Organization / author: NASA PDS (Geosciences Node FAQ; Atmospheres Node data page)
- Version / date: MEDA bundle version 6.0 (2026-08-11 release); FAQ last updated 2019-12-11
- Accessed on: 2026-11-14
- License: No MEDA-specific license text found; PDS general: public domain
- Confidence: medium

# Research card: License - MEDA derived data
- Finding: The derived level is part of the same MEDA bundle and the same DOI as the other levels; the readme only says the calibrated level should be checked if inconsistencies are found at the derived level, and has no separate license. So the same statement applies as for RDS data: no MEDA-specific license found; PDS general statement is public domain. (The team's earlier note, PRD section 7.7, says MEDA derived has no dust or radiation product; this card is about the license only.)
- Source URL: https://pds.nasa.gov/data/pds4/releases/atmos/mars2020_meda-20260811/readme.txt ; https://pds-geosciences.wustl.edu/faq.html
- Organization / author: NASA PDS
- Version / date: MEDA bundle version 6.0
- Accessed on: 2026-11-14
- License: No MEDA-specific license text found; PDS general: public domain
- Confidence: medium

# Research card: License - Curiosity RAD paper (Hassler et al. 2014)
- Finding: The paper (Science 343(6169), 1244797, 2014) is under AAAS copyright. The repository copy I used (typeset.io) says it is for personal, non-commercial use only. I did not find AAAS's official reuse policy page, so the safe use is to cite the numbers with a full citation and NOT copy the paper's figures or tables into the project. The RAD instrument data themselves are archived at the PDS (Planetary Plasma Interactions node) and fall under the general PDS statement; this card is about the paper only.
- Source URL: https://typeset.io/pdf/mars-surface-radiation-environment-measured-with-the-mars-244eildtx0.pdf ; https://ntrs.nasa.gov/citations/20180007641
- Organization / author: Hassler, D. M., Zeitlin, C., Wimmer-Schweingruber, R. F., et al.; AAAS (publisher)
- Version / date: Science, 24 Jan 2014, DOI 10.1126/science.1244797
- Accessed on: 2026-11-14
- License: Copyright AAAS; reuse of figures needs permission
- Confidence: medium (statement read on a repository copy; AAAS policy page not found)

Still to check:
- The AAAS/Science permissions page for reuse of figures
- Whether the PDS Atmospheres Node has its own data-use statement
