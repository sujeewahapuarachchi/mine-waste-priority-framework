# Mine-Waste Priority Framework

## Overview

This project develops a reproducible data-driven framework for screening and prioritizing mine-waste features using publicly available mine-waste data from the U.S. Geological Survey (USGS).

The framework combines estimated waste volume with engineering-domain characteristics to classify mine-waste features into three priority bands and assign investigation profiles. The objective is to provide a transparent first-stage screening approach that can support the identification of mine-waste features requiring further engineering investigation.

The workflow is implemented entirely in Python and is designed to be reproducible from the prepared input data through final screening outputs, validation, figures, and representative appendix records.

---

## Project Objectives

The project aims to:

* Prepare and standardize mine-waste feature data.
* Develop a volume-based scoring system for mine-waste features.
* Classify features into Lower, Intermediate, and Higher priority bands.
* Group mine-waste feature types according to relevant engineering domains.
* Assign engineering-domain profiles to support investigation planning.
* Identify features located close to priority-band boundaries.
* Validate the resulting framework programmatically.
* Generate figures and representative records for reporting.

---

## Data

The analysis uses mine-waste information from the U.S. Geological Survey (USGS).

The framework uses feature-level information including:

* Mine-waste feature identifiers
* Feature types
* Estimated waste volumes
* Commodity information
* Engineering-group classifications
* Reclamation and environmental attributes
* Spatial/boundary-related information

The original USGS source data are not reproduced in this repository unless redistribution is permitted. The final processed datasets included in the project represent the outputs required for the reproducible analysis workflow.

---

## Methodology

### 1. Volume processing

Waste-volume information is aggregated at feature level using the median calculated volume for each feature.

Because mine-waste volumes span a wide range, the volume values are transformed using:

```text
log10(Calc_Volume)
```

The transformed values are then normalized using min-max normalization to produce a `Volume_Score` ranging from 0 to 1.

---

### 2. Priority classification

The normalized volume score is divided into three priority bands using tertile thresholds.

The final thresholds obtained from the dataset are:

| Boundary              | Volume Score |
| --------------------- | -----------: |
| Lower / Intermediate  |     0.413620 |
| Intermediate / Higher |     0.660208 |

The resulting feature counts are:

| Priority Band | Number of Features |
| ------------- | -----------------: |
| Lower         |                254 |
| Intermediate  |                253 |
| Higher        |                253 |
| **Total**     |            **760** |

The three bands are intended as screening categories rather than direct measures of environmental risk, economic value, or regulatory priority.

---

### 3. Engineering classification

Mine-waste feature types are mapped into broader engineering groups:

* Tailings
* Leach-related
* Rock / overburden
* Ore / mineralized stockpile
* Process / metallurgical residue
* Water / process pond
* Other / unclassified

Each engineering group was assigned a combination of engineering-domain relevance levels covering material, geochemical, geotechnical, and water/containment considerations. These combinations were subsequently mapped to six investigation profiles.

* Material
* Geochemical
* Geotechnical
* Water/Containment

These domain assignments are used to characterize the type of investigation that may be relevant to each feature.

---

### 4. Investigation profiles

The engineering-domain combinations are mapped to six investigation profiles based on the following predefined rules:

| Profile | Material | Geochemical | Geotechnical | Water / Containment |
|---|---:|---:|---:|---:|
| P1 | 2 | 2 | 2 | 1 |
| P2 | 2 | 2 | 1 | 2 |
| P3 | 1 | 2 | 1 | 2 |
| P4 | 2 | 2 | 1 | 0 |
| P5 | 2 | 1 | 1 | 0 |
| P6 | 0 | 0 | 0 | 0 |

The final profile distribution is:

| Profile | Number of Features |
|---|---:|
| P1 | 631 |
| P2 | 89 |
| P3 | 18 |
| P4 | 14 |
| P5 | 7 |
| P6 | 1 |
| **Total** | **760** |

---

### 5. Boundary analysis

A boundary-distance measure is calculated from each feature's volume score to the nearest priority-band threshold.

Features with:

```text
Boundary_Distance < 0.02
```

are flagged as boundary cases.

A total of **76 features** are identified as being close to a priority-band boundary.

These records are useful for sensitivity awareness because small changes in the underlying score or data could potentially affect their assigned priority band.

---

## Repository Structure

```text
Project 01_Final/
│
├── README.md
├── requirements.txt
│
├── 01_data_preparation.py
├── 02_framework_application.py
├── 03_validation.py
├── 04_figures.py
├── 05_appendix_records.py
│
├── Data/
│   ├── final_mine_waste_priority_framework.csv
│   ├── final_engineering_screening_table.csv
│   └── Appendix_A_selected_records.csv
│
└── Figures/
    ├── 01_priority_band_distribution.png
    ├── 02_volume_score_distribution.png
    ├── 03_engineering_group_by_priority.png
    ├── 04_investigation_profile_by_priority.png
    └── 05_within_group_priority_composition.png
```

---

## Python Workflow

The five scripts form a sequential workflow.

### `01_data_preparation.py`

Prepares the feature-level framework dataset.

Main functions include:

* loading the required USGS mine-waste layers
* aggregating feature-level volume
* calculating the normalized volume score
* processing commodity information
* assigning engineering groups
* assigning engineering-domain characteristics
* calculating priority bands
* calculating boundary distance and boundary flags
* exporting the final framework dataset

Output:

```text
Data/final_mine_waste_priority_framework.csv
```

---

### `02_framework_application.py`

Applies the investigation-profile framework to the prepared dataset and produces the final engineering screening table.

Output:

```text
Data/final_engineering_screening_table.csv
```

---

### `03_validation.py`

Performs automated quality-control checks on the final datasets.

The validation script checks:

* dataset dimensions
* required columns
* feature uniqueness
* feature-set consistency
* missing values
* volume-score range
* priority-band counts
* priority thresholds
* boundary-distance calculations
* boundary flags
* investigation-profile assignments
* consistency between framework and screening datasets
* final sorting/order

The final validation run completed successfully with all checks passed.

---

### `04_figures.py`

Generates the project figures:

1. Priority-band distribution
2. Volume-score distribution
3. Engineering group by priority
4. Investigation profile by priority
5. Within-group priority composition

The figures are saved in the `Figures/` directory.

---

### `05_appendix_records.py`

Selects representative records from the final screening table for inclusion in the report appendix.

The selected records include examples from different:

* priority bands
* engineering groups
* investigation profiles
* boundary conditions

Output:

```text
Data/Appendix_A_selected_records.csv
```

---

## Reproducibility

The intended workflow is:

```text
USGS / prepared source data
        ↓
01_data_preparation.py
        ↓
final_mine_waste_priority_framework.csv
        ↓
02_framework_application.py
        ↓
final_engineering_screening_table.csv
        ↓
03_validation.py
        ↓
04_figures.py
        ↓
05_appendix_records.py
```

The final pipeline was validated using 760 mine-waste features.

---

## Validation Result

The final validation confirmed:

* 760 features in the framework
* 760 features in the screening table
* unique feature identifiers
* identical feature sets between datasets
* no missing values in the final screening table
* valid volume-score range
* expected priority-band distribution
* correct priority thresholds
* 76 boundary-flagged features
* correct investigation-profile assignments
* consistency between framework and screening outputs
* correct final ordering

**All validation checks passed.**

---

## Limitations

This framework is intended as a screening and prioritization methodology rather than a substitute for detailed site investigation.

Important limitations include:

* The analysis depends on the quality and completeness of the source database.
* Estimated waste volumes may contain uncertainty.
* Priority bands are based on the normalized volume score and should not be interpreted as direct environmental-risk rankings.
* Engineering-domain assignments are rule-based classifications.
* The framework does not replace field investigation, laboratory testing, detailed geotechnical assessment, geochemical characterization, resource estimation, or regulatory assessment.
* Boundary cases indicate classification sensitivity but do not necessarily represent higher risk.

Further investigation would be required before engineering, environmental, economic, or regulatory decisions are made for individual sites.

---

## Tools

The project was developed using:

* Python
* Pandas — data processing and tabular analysis
* NumPy — numerical calculations
* Matplotlib — figure generation
* Pyogrio — reading geospatial source data


---

## Data Source

This project uses the U.S. Geological Survey (USGS) National Mine Waste Inventory.

- **Dataset:** National Mine Waste Inventory
- **DOI:** https://doi.org/10.5066/P148EEUA
- **Source:** https://www.usgs.gov/data/national-mine-waste-inventory

The data processing, prioritization framework, engineering classification, validation, and visualizations were developed as part of this project.

---

## Author

Hapuarachchi H.D.S.C.K.

Mining Engineering Graduate
University of Moratuwa, Sri Lanka
