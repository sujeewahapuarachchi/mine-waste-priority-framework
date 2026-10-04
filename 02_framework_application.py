import pandas as pd
from pathlib import Path

# ---------------------------------------------------------
# 1. Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "Data"

framework_path = (DATA_DIR / "final_mine_waste_priority_framework.csv")

output_path = (DATA_DIR / "final_engineering_screening_table.csv")

# ---------------------------------------------------------
# 2. Load final framework dataset
# ---------------------------------------------------------

final_framework = pd.read_csv(framework_path)

# ---------------------------------------------------------
# 3. Create investigation-priority screening table
# ---------------------------------------------------------

screening_table = final_framework[["Ftr_ID","Ftr_Type","Engineering_Group","Volume_Score","Priority_Band","Material","Geochemical",
                                   "Geotechnical","Water_Containment","Reclaimed","Superfund","Commodity","Commodity_Count",
                                   "Boundary_Distance","Boundary_Flag"]].copy()

# ---------------------------------------------------------
# 4. Assign investigation profiles
# ---------------------------------------------------------

profile_map = {(2, 2, 2, 1): "P1",(2, 2, 1, 2): "P2",(1, 2, 1, 2): "P3",(2, 2, 1, 0): "P4",(2, 1, 1, 0): "P5",(0, 0, 0, 0): "P6"}


screening_table["Investigation_Profile"] = (screening_table[
    ["Material","Geochemical","Geotechnical","Water_Containment",]].apply(tuple, axis=1).map(profile_map))

# ---------------------------------------------------------
# 5. Order features for engineering screening
# ---------------------------------------------------------

priority_order = {"Higher": 0,"Intermediate": 1,"Lower": 2,}

screening_table["Priority_Order"] = (screening_table["Priority_Band"].map(priority_order))

screening_table = (screening_table.sort_values(["Priority_Order", "Volume_Score"],ascending=[True, False]
                                               ).drop(columns="Priority_Order").reset_index(drop=True))

# ---------------------------------------------------------
# 6. Define final column order
# ---------------------------------------------------------

final_columns = ["Ftr_ID","Ftr_Type","Engineering_Group","Volume_Score","Priority_Band","Material","Geochemical","Geotechnical",
                 "Water_Containment","Investigation_Profile","Reclaimed","Superfund","Commodity","Commodity_Count","Boundary_Distance",
                 "Boundary_Flag"]


screening_table = screening_table[final_columns]

# ---------------------------------------------------------
# 7. Final integrity checks
# ---------------------------------------------------------

assert screening_table["Ftr_ID"].is_unique, ("Ftr_ID values are not unique.")

assert len(screening_table) == 760, (f"Expected 760 features, found {len(screening_table)}.")

assert screening_table["Priority_Band"].notna().all(), ("Some features have no Priority_Band.")

assert screening_table["Investigation_Profile"].notna().all(), ("Some features could not be assigned an Investigation_Profile.")

assert screening_table["Boundary_Flag"].notna().all(), ("Some features have missing Boundary_Flag values.")

# ---------------------------------------------------------
# 8. Save final engineering screening table
# ---------------------------------------------------------

screening_table.to_csv(output_path,index=False)

# ---------------------------------------------------------
# 9. Report results
# ---------------------------------------------------------

print(f"Final screening table saved to:\n{output_path}")

print(f"Number of features: {len(screening_table)}")

print("\nPriority-band counts:")
print(screening_table["Priority_Band"].value_counts().sort_index())

print("\nInvestigation-profile counts:")
print(screening_table["Investigation_Profile"].value_counts().sort_index())