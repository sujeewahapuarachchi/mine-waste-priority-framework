import pandas as pd
import numpy as np
from pathlib import Path

# ---------------------------------------------------------
# 1. Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "Data"

framework_path = (DATA_DIR / "final_mine_waste_priority_framework.csv")

screening_path = (DATA_DIR / "final_engineering_screening_table.csv")

# ---------------------------------------------------------
# 2. Check input files
# ---------------------------------------------------------

if not framework_path.exists():
    raise FileNotFoundError(f"Framework dataset not found:\n{framework_path}")

if not screening_path.exists():
    raise FileNotFoundError(f"Screening table not found:\n{screening_path}")

# ---------------------------------------------------------
# 3. Load datasets
# ---------------------------------------------------------

framework = pd.read_csv(framework_path)
screening = pd.read_csv(screening_path)

print("\n==============================================")
print("PROJECT 01 - VALIDATION")
print("==============================================")

# ---------------------------------------------------------
# 4. Basic dimensions
# ---------------------------------------------------------

print("\n--- 1. Dataset dimensions ---")

print("Framework shape:", framework.shape)
print("Screening shape:", screening.shape)

assert len(framework) == 760
assert len(screening) == 760

print("✓ Both datasets contain 760 features.")


# ---------------------------------------------------------
# 5. Expected screening columns
# ---------------------------------------------------------

expected_columns = ["Ftr_ID","Ftr_Type","Engineering_Group","Volume_Score","Priority_Band","Material","Geochemical","Geotechnical",
                    "Water_Containment","Investigation_Profile","Reclaimed","Superfund","Commodity","Commodity_Count","Boundary_Distance",
                    "Boundary_Flag"]

print("\n--- 2. Screening-table structure ---")

assert screening.columns.tolist() == expected_columns

print(f"✓ Screening table contains {len(expected_columns)} variables.")
print("✓ Column order is correct.")

# ---------------------------------------------------------
# 6. Feature ID integrity
# ---------------------------------------------------------

print("\n--- 3. Feature ID integrity ---")

assert framework["Ftr_ID"].is_unique
assert screening["Ftr_ID"].is_unique

assert set(framework["Ftr_ID"]) == set(screening["Ftr_ID"])

print("✓ Framework Ftr_ID values are unique.")
print("✓ Screening Ftr_ID values are unique.")
print("✓ Framework and screening feature sets are identical.")

# ---------------------------------------------------------
# 7. Missing-value check
# ---------------------------------------------------------

print("\n--- 4. Missing values ---")

missing_values = screening[expected_columns].isna().sum()

print(missing_values[missing_values > 0])

assert missing_values.sum() == 0

print("✓ No missing values in the final screening table.")

# ---------------------------------------------------------
# 8. Volume score validation
# ---------------------------------------------------------

print("\n--- 5. Volume Score validation ---")

assert screening["Volume_Score"].between(0, 1).all()

print("Minimum Volume Score:",screening["Volume_Score"].min())

print("Maximum Volume Score:",screening["Volume_Score"].max())

print("✓ All Volume Scores are within 0–1.")

# ---------------------------------------------------------
# 9. Priority-band validation
# ---------------------------------------------------------

print("\n--- 6. Priority-band validation ---")

expected_priority_counts = {"Higher": 253,"Intermediate": 253,"Lower": 254}

actual_priority_counts = (screening["Priority_Band"].value_counts().to_dict())

print("Observed:")
print(actual_priority_counts)

assert actual_priority_counts == expected_priority_counts

print("✓ Priority-band counts match the frozen framework.")

# ---------------------------------------------------------
# 10. Recalculate priority thresholds
# ---------------------------------------------------------

lower_cutoff = screening["Volume_Score"].quantile(1 / 3)
upper_cutoff = screening["Volume_Score"].quantile(2 / 3)

print("\nVolume Score cutoffs:")
print(f"Lower / Intermediate: {lower_cutoff:.6f}")
print(f"Intermediate / Higher: {upper_cutoff:.6f}")

# ---------------------------------------------------------
# 11. Boundary validation
# ---------------------------------------------------------

expected_boundary_distance = np.minimum(abs(screening["Volume_Score"] - lower_cutoff),abs(screening["Volume_Score"] - upper_cutoff))

assert np.allclose(screening["Boundary_Distance"],expected_boundary_distance,atol=1e-12)

expected_boundary_flag = (expected_boundary_distance < 0.02)

assert (screening["Boundary_Flag"]== expected_boundary_flag).all()

boundary_count = screening["Boundary_Flag"].sum()

print(f"\nBoundary-flagged features: {boundary_count}")

assert boundary_count == 76

print("✓ Boundary distance values are correct.")
print("✓ Boundary flags follow the < 0.02 rule.")
print("✓ 76 features are boundary-flagged.")

# ---------------------------------------------------------
# 12. Investigation-profile validation
# ---------------------------------------------------------

print("\n--- 7. Investigation-profile validation ---")

profile_map = {(2, 2, 2, 1): "P1",(2, 2, 1, 2): "P2",(1, 2, 1, 2): "P3",(2, 2, 1, 0): "P4",(2, 1, 1, 0): "P5",(0, 0, 0, 0): "P6",}

calculated_profiles = (screening[
    ["Material","Geochemical","Geotechnical","Water_Containment",]].apply(tuple, axis=1).map(profile_map))

assert (calculated_profiles == screening["Investigation_Profile"]).all()

expected_profile_counts = {"P1": 631,"P2": 89,"P3": 18,"P4": 14,"P5": 7,"P6": 1}

actual_profile_counts = (screening["Investigation_Profile"].value_counts().to_dict())

print("Observed:")
print(actual_profile_counts)

assert actual_profile_counts == expected_profile_counts

print("✓ All investigation profiles are correctly assigned.")
print("✓ Investigation-profile counts match the established result.")

# ---------------------------------------------------------
# 13. Check consistency between framework and screening
# ---------------------------------------------------------

print("\n--- 8. Framework-to-screening consistency ---")

shared_columns = ["Ftr_ID","Ftr_Type","Engineering_Group","Volume_Score","Priority_Band","Material","Geochemical","Geotechnical",
                  "Water_Containment","Reclaimed","Superfund","Commodity","Commodity_Count","Boundary_Distance","Boundary_Flag"]

framework_sorted = (framework[shared_columns].sort_values("Ftr_ID").reset_index(drop=True))

screening_sorted = (screening[shared_columns].sort_values("Ftr_ID").reset_index(drop=True))

pd.testing.assert_frame_equal( framework_sorted, screening_sorted, check_dtype=False, ) 
print( "✓ All shared framework variables are identical " "between the two final datasets." ) 

# --------------------------------------------------------- 
# 14. Check screening order 
# --------------------------------------------------------- 
print("\n--- 9. Screening order ---") 

priority_order = { "Higher": 0, "Intermediate": 1, "Lower": 2, } 
order_values = ( screening["Priority_Band"] .map(priority_order) ) 

assert order_values.is_monotonic_increasing 

for band in ["Higher", "Intermediate", "Lower"]: 
    subset = screening[ screening["Priority_Band"] == band ] 
    
    assert subset["Volume_Score"].is_monotonic_decreasing 

print( "✓ Features are ordered by Priority_Band " "and descending Volume_Score within each band." ) 

# --------------------------------------------------------- 
# 15. Final result
# --------------------------------------------------------- 

print("\n==============================================") 
print("VALIDATION RESULT") 
print("==============================================") 
print("✓ 760 features confirmed.") 
print("✓ 16 screening variables confirmed.") 
print("✓ Unique feature IDs confirmed.") 
print("✓ No missing values confirmed.") 
print("✓ Priority bands confirmed.") 
print("✓ Investigation profiles confirmed.") 
print("✓ Boundary flags confirmed.") 
print("✓ Framework and screening datasets are consistent.") 
print("✓ Screening order confirmed.") 
print("\nALL VALIDATION CHECKS PASSED.")
