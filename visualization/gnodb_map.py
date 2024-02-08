import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import matplotlib.patches as patches

# Define gNodeBs and their positions
gNodeBs = {'W1140': (0, 0), 'W1320': (5, 0), 'W2018': (2.5, 4.33)}
gNodeB_radius = 1.5  # Radius of gNodeB circles

# Define cells for each gNodeB
cells = {
    'Ax1242': 'W1140', 'BX1453': 'W1140', 'CX1352': 'W1140',
    'AX1112': 'W1320', 'BX1334': 'W1320', 'CX1873': 'W1320',
    'AX9980': 'W2018', 'BX1230': 'W2018', 'CX5103': 'W2018'
}



# Define UEs and their allocated cells
UE_to_cell = {
    'UE1': 'CX1352', 'UE2': 'CX5103', 'UE3': 'Ax1242',
    'UE4': 'BX1230', 'UE5': 'BX1453', 'UE6': 'CX1352',
    'UE7': 'BX1230', 'UE8': 'AX9980', 'UE9': 'BX1230'
}


# Initialize plot
fig, ax = plt.subplots()
plt.title('UE to Cell Allocation in Network')
plt.xlim(-3, 8)
plt.ylim(-3, 8)
ax.set_aspect('equal', adjustable='datalim')
plt.grid(True)

# Draw gNodeBs with cells
for gNodeB, pos in gNodeBs.items():
    gNodeB_circle = patches.Circle(pos, gNodeB_radius, edgecolor='black', facecolor='white', lw=2)
    ax.add_patch(gNodeB_circle)
    for i, cell in enumerate([c for c in cells if cells[c] == gNodeB]):
        angle = np.deg2rad(120 * i)
        cell_pos = (pos[0] + gNodeB_radius/2 * np.cos(angle), pos[1] + gNodeB_radius/2 * np.sin(angle))
        ax.text(*cell_pos, cell, fontsize=8, verticalalignment='center', horizontalalignment='center')

# Function to update the positions of UEs
def update(frame):
    ax.clear()  # Clear previous drawings
    # Redraw gNodeBs and cells
    for gNodeB, pos in gNodeBs.items():
        gNodeB_circle = patches.Circle(pos, gNodeB_radius, edgecolor='black', facecolor='white', lw=2)
        ax.add_patch(gNodeB_circle)
        for i, cell in enumerate([c for c in cells if cells[c] == gNodeB]):
            angle = np.deg2rad(120 * i)
            cell_pos = (pos[0] + gNodeB_radius/2 * np.cos(angle), pos[1] + gNodeB_radius/2 * np.sin(angle))
            ax.text(*cell_pos, cell, fontsize=8, verticalalignment='center', horizontalalignment='center')

    # Update positions of UEs
    for UE in UE_to_cell:
        cell = UE_to_cell[UE]  # Get the cell associated with the UE
        gNodeB = cells[cell]
        gNodeB_pos = gNodeBs[gNodeB]
        angle = np.deg2rad(np.random.uniform(0, 360))
        UE_radius = gNodeB_radius + 0.3  # Radius for UEs around cell center
        UE_pos = (gNodeB_pos[0] + UE_radius * np.cos(angle), gNodeB_pos[1] + UE_radius * np.sin(angle))
        ax.plot(*UE_pos, '^', markersize=5, color='blue')
        ax.text(*UE_pos, UE, fontsize=7, verticalalignment='top')


# Create animation
ani = FuncAnimation(fig, update, frames=np.arange(0, 100), repeat=True)

plt.show()
