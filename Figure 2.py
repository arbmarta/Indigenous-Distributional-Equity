import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import blended_transform_factory

'''
included_studies.csv requires:
Citation, Country, n_cities, Finding, dep_var, ind_var
'''

# Load data (replace with pd.read_csv in real use)
df = pd.DataFrame({
    "Citation": [
        "Martin et al., 2025",
        "Chen et al., 2023",
        "Lopez et al., 2022",
        "Smith et al., 2024",
        "Garcia et al., 2021",
        "Nguyen et al., 2020",
        "Brown et al., 2019",
        "Wilson et al., 2018",
        "Anderson et al., 2017",
        "Taylor et al., 2016",
        "Hernandez et al., 2015",
        "Clark et al., 2014",
        "Lewis et al., 2013",
        "Walker et al., 2012",
        "Hall et al., 2011",
        "Young et al., 2010",
        "King et al., 2009",
        "Wright et al., 2008",
        "Lo et al., 2007"
    ],
    "Country": [
        "Canada", "Canada", "United States", "United States", "United States",
        "Canada", "United States", "Canada", "United States", "Canada",
        "United States", "Canada", "United States", "United States", "Canada",
        "United States", "Canada", "United States", "Canada"
    ],
    "n_cities": [
        12, 8, 25, 5, 18,
        10, 30, 6, 14, 9,
        22, 7, 16, 11, 4,
        19, 13, 27, 8
    ],
    "Finding": [
        "Equitable", "Mixed", "Inequitable", "n/s", "Equitable",
        "Mixed", "Inequitable", "Equitable", "Mixed", "n/s",
        "Equitable", "Inequitable", "Mixed", "Equitable", "n/s",
        "Inequitable", "Mixed", "Equitable", "n/s"
    ],
    "dep_var": [
        "Indigenous Identity;Tribal Identity",
        "American Indian and Alaska Native",
        "Indigenous Identity",
        "",
        "Tribal Identity",
        "Indigenous Identity",
        "American Indian and Alaska Native;Tribal Identity",
        "",
        "Native Hawaiian or Other Pacific Islander",
        "Indigenous Identity",
        "Tribal Identity",
        "",
        "American Indian and Alaska Native",
        "Indigenous Identity;Native Hawaiian or Other Pacific Islander",
        "",
        "Tribal Identity",
        "Indigenous Identity",
        "American Indian and Alaska Native",
        ""
    ],
    "ind_var": [
        "Canopy Cover %;Greenspace Use",
        "Distance to Greenspace",
        "Canopy Cover %",
        "Greenspace Use",
        "",
        "Distance to Greenspace;Canopy Cover %",
        "Greenspace Use",
        "Canopy Cover %",
        "Distance to Greenspace",
        "",
        "Greenspace Use",
        "Canopy Cover %",
        "",
        "Distance to Greenspace;Greenspace Use",
        "Canopy Cover %",
        "",
        "Greenspace Use",
        "Distance to Greenspace",
        ""
    ]
})

# Parse dependent / independent variables into sets
df["dep_var_set"] = df["dep_var"].fillna("").apply(
    lambda x: {v.strip() for v in x.split(";") if v.strip()}
)
df["ind_var_set"] = df["ind_var"].fillna("").apply(
    lambda x: {v.strip() for v in x.split(";") if v.strip()}
)

# --- Sort df so plotting assumptions are valid ---
# Ensure Country order is Canada first, then United States
df["Country"] = pd.Categorical(
    df["Country"],
    categories=["Canada", "United States"],
    ordered=True
)

# Sort by Country, then Author
df = df.sort_values(["Country", "Citation"]).reset_index(drop=True)

# Canonical variable lists (controls row order)
dep_vars = [
    "Indigenous Identity (CA)",
    "American Indian and Alaska Native (US)",
    "Native Hawaiian or Other Pacific Islander (US)",
    "Tribal Identity (US)"
]

indep_vars = [
    "Distance to Greenspace",
    "Greenspace Use",
    "Canopy Cover %"
]

categories = [
    ("Number of Cities", ["Number of Cities"]),
    ("Dependent Variable", dep_vars),
    ("Independent Variable", indep_vars),
    ("Finding", ["Finding"])
]

# Build plotting dataframe
rows = []
for cat, items in categories:
    for item in items:
        for _, r in df.iterrows():
            rows.append({
                "Category": cat,
                "Item": item,
                "Citation": r["Citation"],
                "Country": r["Country"],
                "n_cities": r["n_cities"],
                "Finding": r["Finding"]
            })

plot_df = pd.DataFrame(rows)

# Assign y positions
y_table = plot_df[["Category", "Item"]].drop_duplicates().reset_index(drop=True)
y_table["y"] = range(len(y_table))
plot_df = plot_df.merge(y_table, on=["Category", "Item"])

# Flip y so Number of Cities is on top
plot_df["y"] = plot_df["y"].max() - plot_df["y"]
y_table["y"] = y_table["y"].max() - y_table["y"]

# X positions
x_labels = df["Citation"].tolist()
x_map = {lab: i for i, lab in enumerate(x_labels)}
plot_df["x"] = plot_df["Citation"].map(x_map)

# Figure
fig, ax = plt.subplots(figsize=(26, 9))

# Country shading
xmin, xmax = -0.5, len(x_labels) - 0.5
can_x = plot_df.loc[plot_df["Country"] == "Canada", "x"].unique()

ax.axvspan(xmin, can_x.max() + 0.5,
           color="#D62728", alpha=0.15, zorder=0)

ax.axvspan(can_x.max() + 0.5, xmax,
           color="#1F77B4", alpha=0.15, zorder=0)

# Plot content
for _, r in plot_df.iterrows():
    x, y = r["x"], r["y"]
    cit = r["Citation"]

    if r["Item"] == "Number of Cities":
        ax.text(x, y, str(r["n_cities"]),
                ha="center", va="center", fontsize=14)

    elif r["Item"] in dep_vars:
        used = df.loc[df["Citation"] == cit, "dep_var_set"].iloc[0]
        if r["Item"] in used:
            ax.scatter(x, y, color="black", s=90)

    elif r["Item"] in indep_vars:
        used = df.loc[df["Citation"] == cit, "ind_var_set"].iloc[0]
        if r["Item"] in used:
            ax.scatter(x, y, color="black", s=90)

    elif r["Item"] == "Finding":
        if r["Finding"] == "Equitable":
            ax.scatter(x, y, marker="^", color="green", s=140)
        elif r["Finding"] == "Inequitable":
            ax.scatter(x, y, marker="v", color="red", s=140)
        elif r["Finding"] == "Mixed":
            ax.scatter(x, y, marker="o", color="blue", s=115)
        else:
            ax.text(x, y, "n/s", ha="center", va="center", fontsize=14)

# Vertical separators
for i in range(len(x_labels) - 1):
    ax.axvline(i + 0.5, color="black", linewidth=0.8)

# X-axis ticks (manual labels)
ax.set_xticks(range(len(x_labels)))
ax.set_xticklabels([])

label_rot = 75
trans_label = blended_transform_factory(ax.transData, ax.transAxes)

ax.set_xticklabels(
    x_labels,
    rotation=75,
    ha="right",
    va="center",
    rotation_mode="anchor",
    fontsize=14
)

# Top country labels
ax_top = ax.twiny()
ax_top.set_xlim(ax.get_xlim())
ax_top.set_xticks([
    can_x.mean(),
    plot_df.loc[plot_df["Country"] == "United States", "x"].unique().mean()
])
ax_top.set_xticklabels(
    ["Canada", "United States"],
    fontsize=16,
    fontweight="bold"
)
ax_top.tick_params(axis="x", length=0)

# Y-axis labels
ax.set_yticks(y_table["y"])
ax.set_yticklabels(y_table["Item"], fontsize=14)

# Horizontal category separators
for cat, _ in categories[:-1]:
    ys = y_table.loc[y_table["Category"] == cat, "y"]
    ax.axhline(ys.min() - 0.5, color="black", linewidth=1.5)

# Floating category titles
trans = blended_transform_factory(ax.transAxes, ax.transData)
x_pos_axes = 1.02

dep_ys = y_table.loc[y_table["Category"] == "Dependent Variable", "y"]
ind_ys = y_table.loc[y_table["Category"] == "Independent Variable", "y"]

ax.text(x_pos_axes, (dep_ys.min() + dep_ys.max()) / 2,
        "Dependent\nVariable",
        transform=trans,
        rotation=270,
        ha="center", va="center",
        fontsize=16, fontweight="bold", clip_on=False)

ax.text(x_pos_axes, (ind_ys.min() + ind_ys.max()) / 2,
        "Independent\nVariable",
        transform=trans,
        rotation=270,
        ha="center", va="center",
        fontsize=16, fontweight="bold", clip_on=False)

# Limits and layout
ax.set_xlim(xmin, xmax)
ax.set_ylim(min(y_table["y"]) - 0.5, max(y_table["y"]) + 0.5)

plt.tight_layout()
plt.show()
