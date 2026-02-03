import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import blended_transform_factory

# Load data (replace with pd.read_csv in real use)
df = pd.read_csv('Figure 2.csv')

df = df.rename(columns={
    "Number of Cities": "n_cities",
    "Independent Variable": "ind_var",
    "Dependent Variable": "dep_var",
    "Result": "Finding"
})

df["dep_var_set"] = df["dep_var"].fillna("").apply(
    lambda x: {v.strip() for v in x.split(";") if v.strip()}
)

df["ind_var_set"] = df["ind_var"].fillna("").apply(
    lambda x: {v.strip() for v in x.split(";") if v.strip()}
)

# Ensure Country order is Canada first, then United States
df["Country"] = pd.Categorical(
    df["Country"],
    categories=["Canada", "United States"],
    ordered=True
)

# Sort by Country, then Author
df = df.sort_values(["Country", "Citation"]).reset_index(drop=True)

# Canonical variable lists (controls row order)
indep_vars = [
    "Indigenous Identity",
    "American Indian or Alaska Native",
    "Native Hawaiian or Other Pacific Islander",
    "Tribal Origins"
]

dep_vars = [
    "Park Availability / Quantity",
    "Park Access / Proximity",
    "Greenness / Vegetation",
    "Walkability / Built Environment",
    "Park Quality"
]

categories = [
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
fig, ax = plt.subplots(figsize=(16, 9))

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

    if r["Item"] in dep_vars:
        used = df.loc[df["Citation"] == cit, "dep_var_set"].iloc[0]
        if r["Item"] in used:
            ax.scatter(x, y, color="black", s=150)

    elif r["Item"] in indep_vars:
        used = df.loc[df["Citation"] == cit, "ind_var_set"].iloc[0]
        if r["Item"] in used:
            ax.scatter(x, y, color="black", s=150)

    elif r["Item"] == "Finding":
        if r["Finding"] == "Equitable":
            ax.scatter(x, y, marker="^", color="green", edgecolors='black', s=200)
        elif r["Finding"] == "Inequitable":
            ax.scatter(x, y, marker="v", color="red", edgecolors='black', s=200)
        elif r["Finding"] == "Mixed":
            ax.scatter(x, y, marker="o", color="blue", edgecolors='black', s=200)
        else:
            ax.text(x, y, "n/s", ha="center", va="center", fontsize=16)

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
    fontsize=16
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
ax.set_yticklabels(y_table["Item"], fontsize=16)

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
        "Urban Greening Var.",
        transform=trans,
        rotation=270,
        ha="center", va="center",
        fontsize=16, fontweight="bold", clip_on=False)

ax.text(x_pos_axes, (ind_ys.min() + ind_ys.max()) / 2,
        "Census Var.",
        transform=trans,
        rotation=270,
        ha="center", va="center",
        fontsize=16, fontweight="bold", clip_on=False)

# Limits and layout
ax.set_xlim(xmin, xmax)
ax.set_ylim(min(y_table["y"]) - 0.5, max(y_table["y"]) + 0.5)

plt.tight_layout()
plt.show()
