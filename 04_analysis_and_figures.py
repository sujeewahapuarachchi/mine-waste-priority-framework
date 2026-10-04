import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ---------------------------------------------------------
# 1. Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "Data"

FIGURES_DIR = PROJECT_ROOT / "Figures"

FIGURES_DIR.mkdir(parents=True,exist_ok=True)

screening_path = (DATA_DIR / "final_engineering_screening_table.csv")

# ---------------------------------------------------------
# 2. Load screening table
# ---------------------------------------------------------

if not screening_path.exists():
    raise FileNotFoundError(f"Screening table not found:\n{screening_path}")

df = pd.read_csv(screening_path)

# ---------------------------------------------------------
# 3. Common settings
# ---------------------------------------------------------

priority_order = ["Higher","Intermediate","Lower"]


# ---------------------------------------------------------
# Figure 1
# Priority-band distribution
# ---------------------------------------------------------

priority_counts = (df["Priority_Band"].value_counts().reindex(priority_order))

fig, ax = plt.subplots(figsize=(7, 5))

priority_counts.plot(kind="bar",ax=ax)

ax.set_title("Distribution of Features by Priority Band")

ax.set_xlabel("Priority Band")

ax.set_ylabel("Number of Features")

ax.tick_params(axis="x",rotation=0)

fig.tight_layout()

fig.savefig(FIGURES_DIR / "01_priority_band_distribution.png", dpi=300,bbox_inches="tight")

plt.close(fig)

# ---------------------------------------------------------
# Figure 2
# Volume Score distribution and thresholds
# ---------------------------------------------------------

lower_cutoff = df["Volume_Score"].quantile(1 / 3)
upper_cutoff = df["Volume_Score"].quantile(2 / 3)

fig, ax = plt.subplots(figsize=(8, 5))

ax.hist(df["Volume_Score"],bins=30)

ax.axvline(lower_cutoff,linestyle="--",label=f"Lower / Intermediate = {lower_cutoff:.6f}")

ax.axvline(upper_cutoff,linestyle="--",label=f"Intermediate / Higher = {upper_cutoff:.6f}")

ax.set_title("Distribution of Volume Score")

ax.set_xlabel("Volume Score")

ax.set_ylabel("Number of Features")

ax.legend()

fig.tight_layout()

fig.savefig(FIGURES_DIR / "02_volume_score_distribution.png",dpi=300,bbox_inches="tight")

plt.close(fig)

# ---------------------------------------------------------
# Figure 3
# Engineering Group × Priority
# ---------------------------------------------------------

group_priority = pd.crosstab(df["Engineering_Group"],df["Priority_Band"])

group_priority = (group_priority.reindex(columns=priority_order, fill_value=0))

fig, ax = plt.subplots(figsize=(10, 6))

group_priority.plot(kind="bar",ax=ax)

ax.set_title("Engineering Group by Priority Band")

ax.set_xlabel("Engineering Group")

ax.set_ylabel("Number of Features")

ax.tick_params(axis="x",rotation=35)

ax.legend(title="Priority Band")

fig.tight_layout()

fig.savefig(FIGURES_DIR / "03_engineering_group_by_priority.png",dpi=300,bbox_inches="tight")

plt.close(fig)

# ---------------------------------------------------------
# Figure 4
# Investigation Profile × Priority
# ---------------------------------------------------------

profile_priority = pd.crosstab(df["Investigation_Profile"],df["Priority_Band"])

profile_priority = (profile_priority.reindex(columns=priority_order, fill_value=0))

profile_order = ["P1","P2","P3","P4","P5","P6"]

profile_priority = (profile_priority.reindex(profile_order, fill_value=0))

fig, ax = plt.subplots(figsize=(9, 6))

profile_priority.plot(kind="bar",ax=ax)

ax.set_title("Investigation Profile by Priority Band")

ax.set_xlabel("Investigation Profile")

ax.set_ylabel("Number of Features")

ax.tick_params(axis="x",rotation=0)

ax.legend(title="Priority Band")

fig.tight_layout()

fig.savefig(FIGURES_DIR / "04_investigation_profile_by_priority.png",dpi=300,bbox_inches="tight")

plt.close(fig)

# ---------------------------------------------------------
# Figure 5
# Within-group priority composition
# ---------------------------------------------------------

within_group = pd.crosstab(df["Engineering_Group"],df["Priority_Band"],normalize="index")

within_group = (within_group.reindex(columns=priority_order, fill_value=0))

fig, ax = plt.subplots(figsize=(10, 6))

within_group.plot(kind="bar",stacked=True,ax=ax)

ax.set_title("Priority Composition Within Engineering Groups")

ax.set_xlabel("Engineering Group")

ax.set_ylabel("Proportion of Features")

ax.tick_params(axis="x",rotation=35)

ax.legend(title="Priority Band")

fig.tight_layout()

fig.savefig(FIGURES_DIR / "05_within_group_priority_composition.png",dpi=300,bbox_inches="tight")

plt.close(fig)


# ---------------------------------------------------------
# Final output
# ---------------------------------------------------------

print("\n==============================================")
print("FIGURE GENERATION COMPLETE")
print("==============================================")

print(f"Figures saved to:\n{FIGURES_DIR}")

print("\nGenerated files:")

for figure_path in sorted(FIGURES_DIR.glob("*.png")):
    print("-", figure_path.name)
