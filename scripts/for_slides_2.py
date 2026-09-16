import matplotlib.pyplot as plt

# Data from your table
algorithms = [
    "bottom-k MinHash",
    "FracMinHash",
    "MaxGeomHash",
    "α-MaxGeomHash"
]

cpu_time = [0.01, 20.64, 0.04, 0.94]   # seconds
memory = [4.203, 977.621, 5.836, 43.953]  # MB

# Create plot
plt.figure()

# Scatter plot
plt.scatter(cpu_time, memory)

# Annotate each point
for i, label in enumerate(algorithms):
    plt.annotate(label, (cpu_time[i], memory[i]))

# Log-log scale
plt.xscale('log')
plt.yscale('log')

# Labels and title
plt.xlabel("CPU Time (s) [log scale]")
plt.ylabel("Memory (MB) [log scale]")
plt.title("Time vs Memory Usage (Log-Log Scale)")

# Show plot
plt.show()