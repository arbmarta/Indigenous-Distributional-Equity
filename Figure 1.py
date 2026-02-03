import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('included_studies.csv', encoding='latin1')
print(df.columns)

# Convert Published Year to numeric
df["Published Year"] = pd.to_numeric(df["Published Year"], errors="coerce")


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
min_year = int(df["Published Year"].min())
max_year = int(df["Published Year"].max())
years = range(min_year, max_year + 1)

# Count studies by year and category
counts_by_category = {}
for category in category_order:
    category_counts = df[df["Category"] == category].groupby("Published Year").size()
    counts_by_category[category] = category_counts.reindex(years, fill_value=0)

# Create figure
fig, ax = plt.subplots(figsize=(12, 6))

# Define colors for each category
colors = [
    '#2b8cbe',  # Dark blue for includes Indigenous (first in category_order)
    '#74a9cf',  # Medium blue for aggregates Indigenous
    '#a6bddb',  # Light blue for excludes Indigenous
    '#d9d9d9'   # Light gray for no race/ethnicity (last in category_order)
]

# Create stacked bar chart
bottom = [0] * len(years)
for i, category in enumerate(category_order):
    ax.bar(
        years,
        counts_by_category[category].values,
        bottom=bottom,
        width=1,
        edgecolor="black",
        linewidth=0.5,
        color=colors[i],
        label=category
    )
    # Update bottom for next stack
    bottom = [b + c for b, c in zip(bottom, counts_by_category[category].values)]

# Formatting
ax.set_xlim(min_year - 0.5, max_year + 0.5)
ax.set_xticks(range(min_year, max_year + 1, 5))

ax.set_xlabel("Year", fontsize=24)
ax.set_ylabel("Number of Studies", fontsize=24)
ax.tick_params(axis="both", labelsize=20)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Place legend inside the plot area at top left
ax.legend(fontsize=14, frameon=False, loc='upper left')

plt.tight_layout()
plt.show()