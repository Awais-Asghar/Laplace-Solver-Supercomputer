#!/usr/bin/env python3
"""
Part I: HPC Cluster Visualization
Reads cluster_data.csv and generates:
  - Bar chart of node availability scores
  - CPU usage heatmap
  - RAM usage comparison
"""

import csv
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

CSV_FILE = "cluster_data.csv"

# Read data
nodes, statuses, scores, cpu_usages, free_rams, total_rams = [], [], [], [], [], []
load_1s, load_5s, load_15s, total_cores = [], [], [], []

try:
    with open(CSV_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            nodes.append(row["Node"])
            statuses.append(row["Status"])
            scores.append(float(row["Score"]) if row["Score"] else 0)
            cpu_usages.append(float(row["CPU_Usage_Percent"]) if row["CPU_Usage_Percent"] else 0)
            free_rams.append(float(row["Free_RAM_GB"]) if row["Free_RAM_GB"] else 0)
            total_rams.append(float(row["RAM_GB"]) if row["RAM_GB"] else 0)
            load_1s.append(float(row["Load_1min"]) if row["Load_1min"] else 0)
            load_5s.append(float(row["Load_5min"]) if row["Load_5min"] else 0)
            load_15s.append(float(row["Load_15min"]) if row["Load_15min"] else 0)
            total_cores.append(int(row["Total_Cores"]) if row["Total_Cores"] else 0)
except FileNotFoundError:
    print(f"ERROR: {CSV_FILE} not found. Run cluster_map.sh first.")
    sys.exit(1)

x = np.arange(len(nodes))
online_mask = [s == "ONLINE" for s in statuses]

# Color map: green = available, red = busy, gray = offline
colors = []
for i, s in enumerate(scores):
    if not online_mask[i]:
        colors.append('#888888')
    elif s >= 70:
        colors.append('#2ecc71')  # green: available
    elif s >= 40:
        colors.append('#f39c12')  # orange: moderate load
    else:
        colors.append('#e74c3c')  # red: busy

# ---- Figure 1: Availability Score Bar Chart ----
fig, ax = plt.subplots(figsize=(16, 5))
bars = ax.bar(x, scores, color=colors, edgecolor='black', linewidth=0.5)
ax.set_xticks(x)
ax.set_xticklabels([n.replace("compute-0-", "c-") for n in nodes], rotation=45, ha='right', fontsize=8)
ax.set_ylabel("Availability Score (0-100)")
ax.set_title("HPC Node Availability Ranking\n(Green=Available, Orange=Moderate, Red=Busy, Gray=Offline)")
ax.set_ylim(0, 105)
ax.axhline(70, color='green', linestyle='--', alpha=0.5, label='Available threshold (70)')
ax.axhline(40, color='orange', linestyle='--', alpha=0.5, label='Moderate threshold (40)')

# Add score labels on bars
for bar, score in zip(bars, scores):
    if score > 0:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{score:.0f}',
                ha='center', va='bottom', fontsize=6)

patches = [
    mpatches.Patch(color='#2ecc71', label='Available (Score >= 70)'),
    mpatches.Patch(color='#f39c12', label='Moderate (Score 40-70)'),
    mpatches.Patch(color='#e74c3c', label='Busy (Score < 40)'),
    mpatches.Patch(color='#888888', label='Offline'),
]
ax.legend(handles=patches, loc='upper right')
plt.tight_layout()
plt.savefig("node_availability.png", dpi=150)
print("Saved: node_availability.png")
plt.close()

# ---- Figure 2: CPU Usage vs Load Average ----
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 8))

online_x = [x[i] for i in range(len(nodes)) if online_mask[i]]
online_cpu = [cpu_usages[i] for i in range(len(nodes)) if online_mask[i]]
online_load1 = [load_1s[i] for i in range(len(nodes)) if online_mask[i]]
online_load5 = [load_5s[i] for i in range(len(nodes)) if online_mask[i]]
online_load15 = [load_15s[i] for i in range(len(nodes)) if online_mask[i]]
online_names = [nodes[i].replace("compute-0-", "c-") for i in range(len(nodes)) if online_mask[i]]

ax1.bar(range(len(online_x)), online_cpu, color='#3498db', label='CPU Usage %')
ax1.set_xticks(range(len(online_x)))
ax1.set_xticklabels(online_names, rotation=45, ha='right', fontsize=8)
ax1.set_ylabel("CPU Usage (%)")
ax1.set_title("CPU Usage Per Online Node")
ax1.set_ylim(0, 110)
ax1.legend()

ax2.plot(range(len(online_x)), online_load1, 'r-o', markersize=4, label='Load 1min')
ax2.plot(range(len(online_x)), online_load5, 'g-s', markersize=4, label='Load 5min')
ax2.plot(range(len(online_x)), online_load15, 'b-^', markersize=4, label='Load 15min')
ax2.set_xticks(range(len(online_x)))
ax2.set_xticklabels(online_names, rotation=45, ha='right', fontsize=8)
ax2.set_ylabel("Load Average")
ax2.set_title("System Load Averages Per Online Node (Lower = Better)")
ax2.legend()

plt.tight_layout()
plt.savefig("node_load.png", dpi=150)
print("Saved: node_load.png")
plt.close()

# ---- Figure 3: RAM Usage ----
fig, ax = plt.subplots(figsize=(16, 5))
online_total_ram = [total_rams[i] for i in range(len(nodes)) if online_mask[i]]
online_free_ram  = [free_rams[i]  for i in range(len(nodes)) if online_mask[i]]
online_used_ram  = [t - f for t, f in zip(online_total_ram, online_free_ram)]

ax.bar(range(len(online_x)), online_used_ram,  label='Used RAM', color='#e74c3c')
ax.bar(range(len(online_x)), online_free_ram,  label='Free RAM', color='#2ecc71',
       bottom=online_used_ram)
ax.set_xticks(range(len(online_x)))
ax.set_xticklabels(online_names, rotation=45, ha='right', fontsize=8)
ax.set_ylabel("RAM (GB)")
ax.set_title("RAM Usage Per Node (Green = Free, Red = Used)")
ax.legend()
plt.tight_layout()
plt.savefig("node_ram.png", dpi=150)
print("Saved: node_ram.png")
plt.close()

# ---- Print ranking ----
print("\nNODE RANKING BY AVAILABILITY SCORE:")
print(f"{'Rank':<5} {'Node':<20} {'Score':<8} {'CPU%':<8} {'Free RAM':<12} {'Status'}")
print("-" * 65)
ranked = sorted(zip(scores, nodes, cpu_usages, free_rams, statuses), reverse=True)
for rank, (score, node, cpu, ram, status) in enumerate(ranked, 1):
    print(f"{rank:<5} {node:<20} {score:<8.1f} {cpu:<8.1f} {ram:<12.1f} {status}")
