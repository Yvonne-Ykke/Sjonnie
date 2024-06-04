import numpy as np
import discorpy.losa.loadersaver as io
import discorpy.prep.preprocessing as prep
import discorpy.prep.linepattern as lprep
import discorpy.proc.processing as proc
import discorpy.post.postprocessing as post
import os

# Initial parameters
file_path = "C:/Users/joels/Documents/NHL/Jaar 2/Robotica/Sjonnie/python/camera/chessboard-distorted.jpg"
output_base = ""
num_coef = 5  # Number of polynomial coefficients
mat0 = io.load_image(file_path) # Load image
(height, width) = mat0.shape

# Convert the chessboard image to a line-pattern image
mat1 = lprep.convert_chessboard_to_linepattern(mat0)
file_name = "line_pattern_converted.jpg"
directory = "C:/Users/joels/Documents/NHL/Jaar 2/Robotica/Sjonnie/python/camera/"
file_path = os.path.join(directory, file_name)
io.save_image(file_path, mat1)

# Calculate slope and distance between lines
slope_hor, dist_hor = lprep.calc_slope_distance_hor_lines(mat1, radius=15, sensitive=0.5)
slope_ver, dist_ver = lprep.calc_slope_distance_ver_lines(mat1, radius=15, sensitive=0.5)
print("Horizontal slope: ", slope_hor, " Distance: ", dist_hor)
print("Vertical slope: ", slope_ver, " Distance: ", dist_ver)