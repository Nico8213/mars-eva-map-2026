# VN research cards: JMARS "Hydrous Mineral Detections" layer, Carter et al. 2013, CRISM TRDR product

Notes for readers:
- Question 1: which CRISM product is behind the JMARS "Hydrous Mineral Detections (CRISM)" layer, and what are JMARS's terms?
- Short answer: I found no JMARS page that describes this layer or gives a product ID or DOI. The JMARS panel cites Carter et al. 2013. That paper's CRISM data are targeted observations. Whether the JMARS layer is exactly the paper's detection list is NOT verified.
- Accessed on 2026-11-14 for all cards. I could not open the JMARS application itself.

# Research card: JMARS "Hydrous Mineral Detections (CRISM)" layer - what is known
- Finding: Xin En reports that the JMARS layer panel does not say whether the underlying data are MRDR, MTRDR or TER and cites Carter et al. (2013), JGR Planets 118(4), 831-858, DOI 10.1029/2012JE004145. In the JMARS online documentation I found a "CRISM Stamp Layer" page (a layer of CRISM image footprints) but no page describing a "Hydrous Mineral Detections" layer, and no product ID or DOI for it. Carter et al. 2013 present their detections as a list of sites (1,230 sites in their Figure 1: about 260 OMEGA-only, 800 CRISM-only and 170 seen by both), so the layer is probably a plot of that site list, but this is my inference and is not confirmed by any source. A published thesis also refers to "the database of detected hydrous mineral locations by Carter et al."
- Source URL: https://jmars.mars.asu.edu/compact-reconnaissance-imaging-spectrometer-mars-crism-stamp-layer (not opened; link from the JMARS menu) ; https://archives.esac.esa.int/psa/ftp/MARS-EXPRESS/OMEGA/MEX-M-OMEGA-5-DDR-GLOBAL-MAPS-V1.0/DOCUMENT/CARTER_JGR2013.PDF ; https://minds.wisc.edu/server/api/core/bitstreams/88ccd0cd-7161-42ef-8d20-bfd2ce975d18/content
- Organization / author: JMARS (Mars Space Flight Facility, Arizona State University); Carter, J., Poulet, F., Bibring, J.-P., Mangold, N., Murchie, S.
- Version / date: JMARS version not recorded; paper published 2013-04-24
- Accessed on: 2026-11-14
- License: Not found for the layer
- Confidence: high that no layer documentation was found in what I searched; low on the inference that the layer equals the paper's site list

# Research card: Which CRISM data Carter et al. 2013 used
- Finding: The paper uses CRISM targeted observations "better than 36 m/pixel" (FRT 18 m/pixel, HRL and HRS 36 m/pixel) as the major data source: 2,220 targeted observations analyzed out of about 9,500 at the time of the study. CRISM multispectral survey data (MSP, 100-200 m/pixel) were used only minimally (about 70 detections, to add coverage around targeted images) because their spectral sampling is too coarse. OMEGA data were used as well. The authors convert calibrated radiance to surface reflectance with a modified "volcano-scan" atmospheric correction, and use only the 1.1-2.65 micrometer range; the end products are spectral end-members and maps. Combined targeted coverage is under 2% of Mars. The survey largely excludes four regions (Sinus Meridiani, Valles Marineris, Nili Fossae, northern circum-polar gypsum deposits) and the main Mawrth Vallis deposit. I read the paper through section 8.3.3 and saw no mention of Jezero and no use of the word "TRDR" in that part.
- Source URL: https://archives.esac.esa.int/psa/ftp/MARS-EXPRESS/OMEGA/MEX-M-OMEGA-5-DDR-GLOBAL-MAPS-V1.0/DOCUMENT/CARTER_JGR2013.PDF ; https://agupubs.onlinelibrary.wustl.edu/doi/pdfdirect/10.1029/2012JE004145
- Organization / author: Carter, J., Poulet, F., Bibring, J.-P., Mangold, N., Murchie, S.
- Version / date: J. Geophys. Res. Planets 118, 831-858, published 2013-04-24, DOI 10.1029/2012JE004145
- Accessed on: 2026-11-14
- License: Copyright American Geophysical Union (as printed on the paper copy)
- Confidence: high for the data description (read in the paper); the part of the paper after section 8.3.3 was not read

# Research card: Suggested wording for the citation table (CRISM spectral layer)
- Finding: Wording that matches what is verified: "CRISM targeted-mode observations (FRT/HRL/HRS), processed to mineral detections by Carter et al. (2013); the PDS product class for targeted observations is TRDR (inferred, the paper does not name the product class); the exact product IDs behind the JMARS layer are not verified." Do not write "TRDR" as the product behind the JMARS layer until JMARS confirms it. Detections in the paper are site points, not a continuous map.
- Source URL: see the two cards above
- Organization / author: n/a (summary by VN)
- Version / date: n/a
- Accessed on: 2026-11-14
- License: see the JMARS terms card
- Confidence: medium

# Research card: JMARS Terms of Use and Citation Policy
- Finding: The JMARS page titled "Terms of Use & Citation Policy" contains only a citation policy and a privacy note. The citation policy asks that papers acknowledge JMARS and links to a "How to Cite JMARS" section; the privacy note says the site is governed by the Arizona State University privacy policy. It has no license text for the data layers. The JMARS software is open source under the GPL, and ASU describes JMARS as free to use. So there is no data license for the hydrous-mineral layer on these pages.
- Source URL: https://jmars.mars.asu.edu/how-should-jmars-be-cited-published-works ; https://jmars.mars.asu.edu/open_source ; https://christensen.asu.edu/instrument/jmars
- Organization / author: Mars Space Flight Facility, Arizona State University
- Version / date: pages have no version date
- Accessed on: 2026-11-14
- License: JMARS software: GPL; data layers: not stated
- Confidence: high that the page says this; "How to Cite JMARS" (https://jmars.mars.asu.edu/citations/#how-to-cite) was not opened

# Research card: CRISM TRDR product - DOI and use statement
- Finding: The CRISM Targeted Reduced Data Record (TRDR) is a radiometrically calibrated spectral image cube from a single observation, in sensor space (NOT map-projected), with radiance and I/F files plus summary products. PDS3 data set MRO-M-CRISM-3-RDR-TARGETED-V1.0 has DOI 10.17189/1519573. The PDS4 bundles mro_crism_trdr_2101 to 2116 each have their own DOI (for example 2115, data from 9 Nov 2020 to 8 Nov 2021: DOI 10.17189/dmnn-6g28). The product pages (PDS readme, ODE product primer) contain no license text. The U.S. government data catalog record for the PDS3 TRDR data set (harvested from NASA's data.json) lists the license "usa.gov/publicdomain/label/1.0" (U.S. government work public domain label). Because TRDR is not map-projected, a map overlay for the website needs map-projected products (MTRDR, see vn-crism.md).
- Source URL: https://ode.rsl.wustl.edu/mars/pagehelp/Content/Missions_Instruments/Mars%20Reconnaissance%20Orbiter%20(MRO)/CRISM/CRISM%20Product%20Primer/CRISM%20TRDR.htm ; https://pds-geosciences.wustl.edu/mro/mro-m-crism-3-rdr-targeted-v1/mrocr_2115/readme.txt ; https://catalog.data.gov/dataset/mro-crism-targeted-reduced-data-record-v1-0 ; https://data.amerigeoss.org/dataset/mro-crism-targeted-reduced-data-record-v1-0-d3ee3
- Organization / author: NASA PDS Geosciences Node; CRISM team (JHU/APL)
- Version / date: DOI 10.17189/1519573 (PDS3); catalog record modified 2025-07-17
- Accessed on: 2026-11-14
- License: Public domain label in the data.gov record; PDS FAQ says PDS data sets are in the public domain (see vn-crism.md)
- Confidence: medium to high (the license line comes from a catalog record, not from the data pages)

Still to check:
- Ask the JMARS team (https://jmars.mars.asu.edu/contact) which data or product the Hydrous Mineral Detections layer shows and whether it has a DOI; also look at the layer's info or settings inside the JMARS application
- Read the rest of Carter et al. 2013 (after section 8.3.3), and check whether any Jezero sites are in their list
- Open the "How to Cite JMARS" section
- Which exact CRISM product (TRDR, MTRDR or MRDR) Xin En downloads for the map, and its bundle DOI
