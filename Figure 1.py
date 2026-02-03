import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

# Load data
df = pd.read_csv('included_studies.csv', encoding='latin1')
print(df.columns)

# Convert Published Year to numeric
df["Published Year"] = pd.to_numeric(df["Published Year"], errors="coerce")

CUTOFF_YEAR = 1995
years_raw = df["Published Year"].dropna().astype(int)
n_pre_1995 = len(years_raw[years_raw <= CUTOFF_YEAR])

# Create category column based on your classification logic
def classify_study(row):
    """
    Classify each study into one of four categories:
    1. Study does not include race/ethnicity
    2. Study includes race/ethnicity but excludes Indigenous Peoples
    3. Study includes race/ethnicity but aggregates Indigenous Peoples
    4. Study includes Indigenous Peoples
    """
    includes_race = str(row.get("Includes Race?", "")).strip().lower()
    indigenous_mentioned = str(row.get("Indigenous Variable Mentioned", "")).strip().lower()
    indigenous_vars = str(row.get("Indigenous Variables - included, excluded, aggregated", "")).strip().lower()

    # Category 1: Does not include race/ethnicity
    if includes_race != "yes":
        return "Does not include race/ethnicity"

    # Category 2-4: Includes race/ethnicity
    # Check if Indigenous mentioned
    if indigenous_mentioned != "yes":
        return "Includes race/ethnicity but excludes Indigenous Peoples"

    # If Indigenous mentioned, check how they're handled
    if "Excluded" in indigenous_vars or "exclude" in indigenous_vars:
        return "Includes race/ethnicity but excludes Indigenous Peoples"
    elif "Aggregated" in indigenous_vars or "aggregate" in indigenous_vars:
        return "Includes race/ethnicity but aggregates Indigenous Peoples"
    elif "Included" in indigenous_vars or "include" in indigenous_vars:
        return "Includes Indigenous Peoples"
    else:
        # Default if Indigenous mentioned but treatment unclear
        return "Includes race/ethnicity but excludes Indigenous Peoples"

# Apply classification
df["Category"] = df.apply(classify_study, axis=1)

# Define category order for stacking (bottom to top)
category_order = [
    "Includes Indigenous Peoples",
    "Includes race/ethnicity but aggregates Indigenous Peoples",
    "Includes race/ethnicity but excludes Indigenous Peoples",
    "Does not include race/ethnicity",
]

# Set up year range
min_year = CUTOFF_YEAR
max_year = years_raw.max()
years = list(range(min_year, max_year + 1))

# Count studies by year and category
counts_by_category = {}

for category in category_order:
    # Get years for this category
    yrs = df.loc[df["Category"] == category, "Published Year"].dropna().astype(int)

    # Count papers ≤ 1995
    n_before = (yrs <= CUTOFF_YEAR).sum()

    # Count papers ≥ 1995 normally
    counts = yrs[yrs >= CUTOFF_YEAR].value_counts().reindex(years, fill_value=0)

    # Add pre-1995 papers into the 1995 bin
    counts.loc[CUTOFF_YEAR] += n_before

    counts_by_category[category] = counts


# Create figure
fig, ax = plt.subplots(figsize=(12, 6))

# Define colors for each category
colors = [
    '#0072B2',  # Blue – Includes Indigenous Peoples
    '#D55E00',  # Orange – Aggregates Indigenous Peoples
    '#009E73',  # Green – Excludes Indigenous Peoples
    '#BDBDBD'   # Gray – Does not include race/ethnicity
]


# Create stacked bar chart
bottom = [0] * len(years)

for i, category in enumerate(category_order):
    ax.bar(
        years,
        counts_by_category[category].values,
        bottom=bottom,
        width=0.85,
        edgecolor="black",
        linewidth=0.3,
        color=colors[i],
        label=category
    )

    bottom = bottom + counts_by_category[category].values

# Ticks every 5 years
xticks = list(range(CUTOFF_YEAR, max_year + 1, 5))

# Custom labels with ≤ 1995
xlabels = []
for y in xticks:
    if y == CUTOFF_YEAR:
        xlabels.append('\u2264 1995')  # Unicode ≤
    else:
        xlabels.append(str(y))

ax.set_xticks(xticks)
ax.set_xticklabels(xlabels)

ax.set_xlabel("Year", fontsize=24)
ax.set_ylabel("Number of Studies", fontsize=24)
ax.tick_params(axis="both", labelsize=20)
ax.set_xlim(CUTOFF_YEAR - 0.25, max_year + 0.75)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Place legend inside the plot area at top left
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[::-1], labels[::-1],
          fontsize=16, frameon=True, loc='upper left')

# Y-axis: majors at 10, minors at 5
ax.yaxis.set_major_locator(MultipleLocator(10))
ax.yaxis.set_minor_locator(MultipleLocator(5))

# Major gridlines only
ax.grid(axis='y', which='major', linestyle='--',
        linewidth=0.6, alpha=0.6)

# Minor ticks, no gridlines
ax.tick_params(axis='y', which='minor', length=4, width=1)
ax.tick_params(axis='y', which='major', length=8, width=1.5)

ax.set_axisbelow(True)

plt.tight_layout()
plt.show()

print(f"{n_pre_1995} studies published in or before {CUTOFF_YEAR} aggregated into '≤ {CUTOFF_YEAR}' bin")

total_studies = len(df)
print(f"\nTotal number of studies: {total_studies}")

total_studies_with_year = df["Published Year"].notna().sum()
print(f"Total number of studies with a published year: {total_studies_with_year}")

print("\nTotal number of studies by category:")
category_totals = df["Category"].value_counts()

for category in category_order:
    print(f"  {category}: {category_totals.get(category, 0)}")

print("\nTotal counts used in the plot:")
for category in category_order:
    print(
        f"  {category}: {counts_by_category[category].sum()}"
    )