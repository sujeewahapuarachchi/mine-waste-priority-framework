import pandas as pd
from pathlib import Path

# ---------------------------------------------------------
# 1. Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "Data"

screening_path = (DATA_DIR / "final_engineering_screening_table.csv")

appendix_path = (DATA_DIR / "Appendix_A_selected_records.csv")

# ---------------------------------------------------------
# 2. Load screening table
# ---------------------------------------------------------

if not screening_path.exists():
    raise FileNotFoundError(f"Screening table not found:\n{screening_path}")

df = pd.read_csv(screening_path)

# ---------------------------------------------------------
# 3. Columns retained for Appendix B
# ---------------------------------------------------------

appendix_columns = ["Ftr_ID","Ftr_Type","Engineering_Group","Volume_Score","Priority_Band","Material","Geochemical","Geotechnical",
                    "Water_Containment","Investigation_Profile","Reclaimed","Superfund","Commodity","Commodity_Count","Boundary_Distance",
                    "Boundary_Flag"]

# ---------------------------------------------------------
# 4. Store selected records
# ---------------------------------------------------------

selected = []

# ---------------------------------------------------------
# 5. Higher-priority representative records
# ---------------------------------------------------------

higher_groups = ["Leach-related","Tailings","Rock / overburden",]

for group in higher_groups:

    subset = df[(df["Priority_Band"] == "Higher") & (df["Engineering_Group"] == group)].sort_values("Volume_Score",ascending=False)

    if subset.empty:
        raise ValueError(f"No Higher-priority records found for: {group}")

    selected.append(subset.iloc[0])

# ---------------------------------------------------------
# 6. Intermediate-priority representative records
# ---------------------------------------------------------

intermediate_groups = ["Tailings","Rock / overburden","Leach-related",]

for group in intermediate_groups:

    subset = df[(df["Priority_Band"] == "Intermediate") & (df["Engineering_Group"] == group)].sort_values("Volume_Score",ascending=True)

    if subset.empty:
        raise ValueError(f"No Intermediate-priority records found for: {group}")

    selected.append(subset.iloc[0])

# ---------------------------------------------------------
# 7. Lower-priority representative records
# ---------------------------------------------------------

lower_groups = ["Tailings","Rock / overburden","Ore / mineralized stockpile"]

for group in lower_groups:

    subset = df[(df["Priority_Band"] == "Lower") & (df["Engineering_Group"] == group)].sort_values("Volume_Score",ascending=True)

    if subset.empty:
        raise ValueError(f"No Lower-priority records found for: {group}")

    selected.append(subset.iloc[0])

# ---------------------------------------------------------
# 8. Boundary-sensitive representative records
# ---------------------------------------------------------

boundary = (df[df["Boundary_Flag"] == True].sort_values("Boundary_Distance").head(3))

if len(boundary) < 3:
    raise ValueError("Fewer than three boundary-flagged features are available.")

for _, row in boundary.iterrows():
    selected.append(row)

# ---------------------------------------------------------
# 9. Create Appendix A table
# ---------------------------------------------------------

appendix_a = pd.DataFrame(selected)

appendix_a = appendix_a[appendix_columns].copy()

# ---------------------------------------------------------
# 10. Remove accidental duplicate features
# ---------------------------------------------------------

appendix_a = (appendix_a.drop_duplicates(subset="Ftr_ID").reset_index(drop=True))

# ---------------------------------------------------------
# 11. Add selection number
# ---------------------------------------------------------

appendix_a.insert(0,"Appendix_Record",range(1, len(appendix_a) + 1))

# ---------------------------------------------------------
# 12. Save Appendix A records
# ---------------------------------------------------------

appendix_a.to_csv(appendix_path,index=False)

# ---------------------------------------------------------
# 13. Report results
# ---------------------------------------------------------

print("\n==============================================")
print("APPENDIX A RECORD SELECTION")
print("==============================================")

print(f"Selected records: {len(appendix_a)}")

print(f"Saved to:\n{appendix_path}")

print("\nSelected records:")

print(appendix_a[
    ["Appendix_Record","Ftr_ID","Engineering_Group","Volume_Score","Priority_Band","Investigation_Profile","Boundary_Flag"]
    ].to_string(index=False))