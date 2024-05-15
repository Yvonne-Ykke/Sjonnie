# Open the OBJ file for reading
with open("ImageToStl.com_opstelling_robotica_2024 (1).obj", "r") as file:
    lines = file.readlines()

# Open a new file for writing the scaled vertices
with open("scaled_table.obj", "w") as file:
    for line in lines:
        if line.startswith("v "):
            # Split the line and extract the vertex coordinates
            parts = line.split()
            x = float(parts[1]) / 1000
            y = float(parts[2]) / 1000
            z = float(parts[3]) / 1000
            # Write the scaled vertex coordinates to the new file
            file.write(f"v {x} {y} {z}\n")
        else:
            # Write other lines unchanged
            file.write(line)
