import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib import cm
from matplotlib.patches import FancyArrow

# Constants
PI = np.pi
one_by_sqrt6 = 0.40824829
one_by_sqrt2 = 0.70710678
sqrt2_by_sqrt3 = 0.816496581
pi_by_3 = PI / 3
one_by_pi_by_3 = 3 / PI
one_by_sqrt3 = 0.577350269

# Styling
plt.rcParams.update({
    'font.family': "sans-serif",
    'animation.html': 'jshtml',
    'mathtext.fontset': 'cm',
    'figure.figsize': [9, 9],
})

# SVPWM Function
def svPWM(Ud, Uq, theta, U_dc):
    U_max = U_dc * one_by_sqrt3
    Ud = np.clip(Ud, U_max * 0.1, U_max)
    Uq = min(Uq, U_max)

    u_alfa = Ud * np.cos(theta) - Uq * np.sin(theta)
    u_beta = Ud * np.sin(theta) + Uq * np.cos(theta)

    sektor = int(theta * one_by_pi_by_3) % 6

    if sektor == 0:
        u_alfa_1, u_beta_1 = sqrt2_by_sqrt3 * U_dc, 0
        u_alfa_2, u_beta_2 = one_by_sqrt6 * U_dc, one_by_sqrt2 * U_dc
    elif sektor == 1:
        u_alfa_1, u_beta_1 = one_by_sqrt6 * U_dc, one_by_sqrt2 * U_dc
        u_alfa_2, u_beta_2 = -one_by_sqrt6 * U_dc, one_by_sqrt2 * U_dc
    elif sektor == 2:
        u_alfa_1, u_beta_1 = -one_by_sqrt6 * U_dc, one_by_sqrt2 * U_dc
        u_alfa_2, u_beta_2 = -sqrt2_by_sqrt3 * U_dc, 0
    elif sektor == 3:
        u_alfa_1, u_beta_1 = -sqrt2_by_sqrt3 * U_dc, 0
        u_alfa_2, u_beta_2 = -one_by_sqrt6 * U_dc, -one_by_sqrt2 * U_dc
    elif sektor == 4:
        u_alfa_1, u_beta_1 = -one_by_sqrt6 * U_dc, -one_by_sqrt2 * U_dc
        u_alfa_2, u_beta_2 = one_by_sqrt6 * U_dc, -one_by_sqrt2 * U_dc
    elif sektor == 5:
        u_alfa_1, u_beta_1 = one_by_sqrt6 * U_dc, -one_by_sqrt2 * U_dc
        u_alfa_2, u_beta_2 = sqrt2_by_sqrt3 * U_dc, 0

    time1_vector = (u_alfa * u_beta_2 - u_beta * u_alfa_2) / (u_alfa_1 * u_beta_2 - u_beta_1 * u_alfa_2)
    time2_vector = (-u_alfa * u_beta_1 + u_beta * u_alfa_1) / (u_alfa_1 * u_beta_2 - u_beta_1 * u_alfa_2)
    time0_vector = 1 - time1_vector - time2_vector

    return {
        "d1d4": time1_vector,
        "d2d5": time2_vector,
        "d3d6": time0_vector,
        "u_alfa": u_alfa,
        "u_beta": u_beta,
        "u_alfa1": u_alfa_1,
        "u_beta1": u_beta_1,
        "u_alfa2": u_alfa_2,
        "u_beta2": u_beta_2,
        "sector": sektor,
        "t1_vector": time1_vector,
        "t2_vector": time2_vector,
    }

# Parameters
U_dc = 600
Ud = 300
Uq = 0
frames = 300
angle_values = np.linspace(0, 2 * PI, frames)
data = [svPWM(Ud, Uq, angle, U_dc) for angle in angle_values]

# Colors
colors = cm.tab10.colors

# Set up the plot
fig, ax = plt.subplots()
ax.set_xlim(-1.2 * U_dc, 1.2 * U_dc)
ax.set_ylim(-1.2 * U_dc, 1.2 * U_dc)
ax.set_aspect('equal')
ax.grid(alpha=0.4)
ax.set_title(r"SVPWM Animation with Highlighted Switching Vectors", size=16)

# Initialize elements
main_vector, = ax.plot([], [], 'ro-', label="Main Voltage Vector", lw=3)
t1_arrow, = ax.plot([], [], 'b-', label="T1 Vector", lw=2.5)
t2_arrow, = ax.plot([], [], 'g-', label="T2 Vector", lw=2.5)
uniform_color = 'gray'  # Define the color for all lines
switching_lines = [ax.plot([], [], '-', color=uniform_color, lw=1)[0] for _ in range(6)]
actual_sector_a, = ax.plot([], [], color=uniform_color, label="Actual Sector A",  lw=1.5)
actual_sector_b, = ax.plot([], [], color=uniform_color, label="Actual Sector B",  lw=1.5)

ax.legend()

# Create placeholder arrows (these will be replaced dynamically)
t1_arrow_patch = None
t2_arrow_patch = None
Voltage_arrow = None

# Switching Vector Endpoints
switching_points = [
    (sqrt2_by_sqrt3 * U_dc, 0),
    (one_by_sqrt6 * U_dc, one_by_sqrt2 * U_dc),
    (-one_by_sqrt6 * U_dc, one_by_sqrt2 * U_dc),
    (-sqrt2_by_sqrt3 * U_dc, 0),
    (-one_by_sqrt6 * U_dc, -one_by_sqrt2 * U_dc),
    (one_by_sqrt6 * U_dc, -one_by_sqrt2 * U_dc),
]

# Animation update function
def update(frame):
    global t1_arrow_patch, t2_arrow_patch, Voltage_arrow  # Access the global arrow patches

    # Remove previous arrows
    if t1_arrow_patch:
        t1_arrow_patch.remove()
    if t2_arrow_patch:
        t2_arrow_patch.remove()
    if Voltage_arrow:
        Voltage_arrow.remove()

    u_alfa = data[frame]["u_alfa"]
    u_beta = data[frame]["u_beta"]
    u_alfa_1 = data[frame]["u_alfa1"]
    u_beta_1 = data[frame]["u_beta1"]
    u_alfa_2 = data[frame]["u_alfa2"]
    u_beta_2 = data[frame]["u_beta2"]
    t1_vector = data[frame]["t1_vector"]
    t2_vector = data[frame]["t2_vector"]
    sector = data[frame]["sector"]

    # Main rotating vector
    main_vector.set_data([0, u_alfa], [0, u_beta])

    # Create new arrows for T1, T2, and Main Voltage
    t1_arrow_patch = FancyArrow(
        0, 0, t1_vector * u_alfa_1, t1_vector * u_beta_1,
        color="blue", width=10, head_width=30, head_length=30
    )
    t2_arrow_patch = FancyArrow(
        t1_vector * u_alfa_1, t1_vector * u_beta_1,
        u_alfa - t1_vector * u_alfa_1, u_beta - t1_vector * u_beta_1,
        color="green", width=10, head_width=30, head_length=30
    )
    Voltage_arrow = FancyArrow(
        0, 0, u_alfa, u_beta,
        color="red", width=10, head_width=30, head_length=30
    )

    ax.add_patch(t1_arrow_patch)
    ax.add_patch(t2_arrow_patch)
    ax.add_patch(Voltage_arrow)

    # Highlight two active switching lines
    for i, line in enumerate(switching_lines):
        if i == sector:
            line.set_linewidth(1.0)
            line.set_alpha(0.4)
        else:
            line.set_linewidth(1.0)
            line.set_alpha(0.4)

        start = switching_points[i]
        end = switching_points[(i + 1) % 6]
        line.set_data([start[0], end[0]], [start[1], end[1]])

    actual_sector_a.set_data([0, u_alfa_1], [0, u_beta_1])
    actual_sector_b.set_data([0, u_alfa_2], [0, u_beta_2])

    return main_vector, *switching_lines, actual_sector_a, actual_sector_b

# Create animation
ani = FuncAnimation(fig, update, frames=frames, interval=50, blit=True)

# Save as GIF
ani.save("StyledSVPWM_Highlighted.gif", writer=PillowWriter(fps=30))

