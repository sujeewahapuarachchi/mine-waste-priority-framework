import pyogrio
import pandas as pd
import numpy as np
from pathlib import Path

#---------------------------------------------
# 1. Paths
#---------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "Data"

gdb_path = (DATA_DIR/ "USGS_Mine_Waste_US-geodatabase"/ "USGS_Mine_Waste.gdb")

output_path = (DATA_DIR/ "final_mine_waste_priority_framework.csv")

#---------------------------------------------
# 2. Load USGS mine-waste datasets
#---------------------------------------------

points = pyogrio.read_dataframe(gdb_path,layer="Waste_Points")

resources = pyogrio.read_dataframe(gdb_path,layer="Waste_Resources")

#---------------------------------------------
# 3. Feature-level volume calculation
#---------------------------------------------
# Resource records may contain multiple records for the same
# feature. The median calculated volume is used to obtain a
# single feature-level volume value.

feature_volume = (resources[["Ftr_ID", "Calc_Vol"]].groupby("Ftr_ID", as_index=False).median())

# Keep only physically meaningful positive volumes.

volume_valid = feature_volume[feature_volume["Calc_Vol"] > 0].copy()

# Log-transform volume to reduce the influence of extreme
# differences in feature size.

volume_valid["log_volume"] = np.log10(volume_valid["Calc_Vol"])

# Min-max normalization of log-transformed volume.

volume_valid["Volume_Score"] = (
    (volume_valid["log_volume"] - volume_valid["log_volume"].min())
    / (volume_valid["log_volume"].max() - volume_valid["log_volume"].min()))

#---------------------------------------------
# 4. Feature-level commodity information
#---------------------------------------------

feature_commodity = points[["Ftr_ID", "Commodity"]].copy()

# Split multi-commodity fields into individual entries.

commodity_long = (feature_commodity.assign(Commodity=feature_commodity["Commodity"].str.split(";")
                                           ).explode("Commodity"))

commodity_long["Commodity"] = (commodity_long["Commodity"].str.strip())

# Count commodity entries associated with each feature.

commodity_count = (commodity_long.groupby("Ftr_ID").size().reset_index(name="Commodity_Count"))

#---------------------------------------------
# 5. Engineering-group classification
#---------------------------------------------

feature_group_map = {
    "Tailings - pond": "Tailings",
    "Tailings - undifferentiated": "Tailings",
    "Tailings - mill": "Tailings",
    "Tailings - dredge": "Tailings",
    "Tailings - placer": "Tailings",

    "Leach pile - heap": "Leach-related",
    "Leach pile - dump": "Leach-related",
    "Leach pile - unknown": "Leach-related",

    "Mine dump": "Rock / overburden",
    "Waste rock stockpile": "Rock / overburden",
    "Overburden pile": "Rock / overburden",

    "Ore stockpile/storage": "Ore / mineralized stockpile",

    "Slag pile": "Process / metallurgical residue",
    "Gypsum stack": "Process / metallurgical residue",

    "Phosphate pond": "Water / process pond",
    "Settling pond": "Water / process pond",
    "Evaporation pond": "Water / process pond",

    "Other": "Other / unclassified"
}

feature_type_group = points[["Ftr_ID", "Ftr_Type"]].copy()

feature_type_group["Engineering_Group"] = (feature_type_group["Ftr_Type"].map(feature_group_map))

#----------------------------------------------------
# 6. Combine volume and engineering-group information
#----------------------------------------------------

feature_framework = feature_type_group.merge(volume_valid[["Ftr_ID","Calc_Vol","log_volume","Volume_Score",]],on="Ftr_ID",how="inner")

#----------------------------------------------------
# 7. Assign engineering-investigation domain scores
#----------------------------------------------------

feature_type_domain_map = {
    "Tailings": {
        "Material": 2,
        "Geochemical": 2,
        "Geotechnical": 2,
        "Water_Containment": 1,
    },

    "Leach-related": {
        "Material": 2,
        "Geochemical": 2,
        "Geotechnical": 1,
        "Water_Containment": 2,
    },

    "Rock / overburden": {
        "Material": 2,
        "Geochemical": 2,
        "Geotechnical": 2,
        "Water_Containment": 1,
    },

    "Water / process pond": {
        "Material": 1,
        "Geochemical": 2,
        "Geotechnical": 1,
        "Water_Containment": 2,
    },

    "Process / metallurgical residue": {
        "Material": 2,
        "Geochemical": 2,
        "Geotechnical": 1,
        "Water_Containment": 0,
    },

    "Ore / mineralized stockpile": {
        "Material": 2,
        "Geochemical": 1,
        "Geotechnical": 1,
        "Water_Containment": 0,
    },

    "Other / unclassified": {
        "Material": 0,
        "Geochemical": 0,
        "Geotechnical": 0,
        "Water_Containment": 0,
    }
}


for domain in ["Material","Geochemical","Geotechnical","Water_Containment"
               ]:feature_framework[domain] = (feature_framework["Engineering_Group"].map(
                   lambda group: feature_type_domain_map[group][domain]))

#----------------------------------------------------
# 8. Add feature context
#----------------------------------------------------
feature_framework = feature_framework.merge(points[
    ["Ftr_ID","Ftr_Type","Commodity","State","County","Land_Mng","Reclaimed","Superfund","Mine_Name","Mine_Dist"]],on="Ftr_ID",
    how="left",suffixes=("_group", ""))

# Remove the duplicate Ftr_Type created by the merge.

if "Ftr_Type_group" in feature_framework.columns:feature_framework = feature_framework.drop(columns="Ftr_Type_group")

#----------------------------------------------------
# 9. Add commodity count
#----------------------------------------------------

feature_framework = feature_framework.merge(commodity_count[["Ftr_ID", "Commodity_Count"]],on="Ftr_ID",how="left")

#----------------------------------------------------
# 10. Calculate candidate priority bands
#----------------------------------------------------
# Priority is determined from Volume_Score using tertile
# thresholds.

tertile_thresholds = (feature_framework["Volume_Score"].quantile([1 / 3, 2 / 3]))

lower_cutoff = tertile_thresholds.iloc[0]
higher_cutoff = tertile_thresholds.iloc[1]


feature_framework["Priority_Band"] = pd.cut(feature_framework["Volume_Score"],bins=[-np.inf,lower_cutoff,higher_cutoff,np.inf],
                                            labels=["Lower","Intermediate","Higher",],include_lowest=True)

#----------------------------------------------------
# 11. Calculate boundary distance
#----------------------------------------------------

feature_framework["Boundary_Distance"] = (feature_framework["Volume_Score"].apply(lambda score: min(abs(score - lower_cutoff),
                                                                                                    abs(score - higher_cutoff),)))

#----------------------------------------------------
# 12. Identify borderline features
#----------------------------------------------------
# Established rule:
# Boundary_Distance < 0.02 -> True
# Boundary_Distance >= 0.02 -> False

boundary_threshold = 0.02

feature_framework["Boundary_Flag"] = (feature_framework["Boundary_Distance"]< boundary_threshold)

#----------------------------------------------------
# 13. Construct final framework dataset
#----------------------------------------------------

final_framework = feature_framework[["Ftr_ID","Ftr_Type","Engineering_Group","Volume_Score","Priority_Band","Material","Geochemical",
                                     "Geotechnical","Water_Containment","Reclaimed","Superfund","Commodity","Commodity_Count",
                                     "Boundary_Distance","Boundary_Flag",]].copy()

#----------------------------------------------------
# 14. Final intergrity checks
#----------------------------------------------------
assert len(final_framework) == 760

assert final_framework["Ftr_ID"].is_unique

assert final_framework["Priority_Band"].notna().all()

assert final_framework[["Material","Geochemical","Geotechnical","Water_Containment",]].notna().all().all()

assert final_framework["Boundary_Distance"].notna().all()

assert final_framework["Boundary_Flag"].notna().all()

# Verify expected priority-band counts.

priority_counts = (final_framework["Priority_Band"].value_counts().reindex(["Higher", "Intermediate", "Lower"],fill_value=0,))

assert priority_counts["Higher"] == 253
assert priority_counts["Intermediate"] == 253
assert priority_counts["Lower"] == 254

#----------------------------------------------------
# 15. Save final framework dataset
#----------------------------------------------------

final_framework.to_csv(output_path,index=False,)

#----------------------------------------------------
# 16. Confirmation
#----------------------------------------------------

print("Final framework dataset created successfully.")
print(f"Output: {output_path}")
print(f"Features: {len(final_framework)}")

print("\nPriority-band distribution:")
print(priority_counts)

print("\nVolume Score cutoffs:")
print(f"Lower / Intermediate: {lower_cutoff:.6f}")
print(f"Intermediate / Higher: {higher_cutoff:.6f}")

print("\nBoundary-flagged features:",int(final_framework["Boundary_Flag"].sum()))