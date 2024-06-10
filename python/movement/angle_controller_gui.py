import math
import numpy as np
import matplotlib.pyplot as plt
import controller
import angle_calculator as angle_calculator

SEGMENT_LENGTH = 300.0
AX12_SHOULDER_MIN_ANGLE = -130
AX12_SHOULDER_MAX_ANGLE = 130
AX12_ELBOW_MIN_ANGLE = -150
AX12_ELBOW_MAX_ANGLE = 150
FORBIDDEN_RADIUS = 250.0
DOTS_PRECISION = 200
prev_elbow_angle = 0
prev_shoulder_angle = 0


# Generate reachable coordinates
shoulder_angles = np.radians(np.linspace(AX12_SHOULDER_MIN_ANGLE, AX12_SHOULDER_MAX_ANGLE, DOTS_PRECISION))  # Fine discretization
elbow_angles = np.radians(np.linspace(AX12_ELBOW_MIN_ANGLE, AX12_ELBOW_MAX_ANGLE, DOTS_PRECISION))     # Fine discretization
# Generate all possible combinations of shoulder and elbow angles
reachable_coordinates = [(SEGMENT_LENGTH * (np.cos(shoulder_angle) + np.cos(shoulder_angle + elbow_angle)),
                          SEGMENT_LENGTH * (np.sin(shoulder_angle) + np.sin(shoulder_angle + elbow_angle)))
                         for shoulder_angle in shoulder_angles
                         for elbow_angle in elbow_angles]


x_reach, y_reach = zip(*reachable_coordinates)


def on_hover(event):
    mouse_is_on_plot = event.inaxes
    if mouse_is_on_plot:
        x, y = event.xdata, event.ydata
        tooltip_text = f"x={x:.1f}, y={y:.1f}"
        annot1.xy = (x, y)
        annot1.set_text(tooltip_text)
        annot1.get_bbox_patch().set_facecolor("lightgray")
        annot1.get_bbox_patch().set_alpha(0.8)
        annot1.set_visible(True)
    else:
        annot1.set_visible(False)

def on_click(event):
    mouse_is_on_plot = event.inaxes
    if mouse_is_on_plot:
        mouse_x, mouse_y = event.xdata, event.ydata
        shoulder_angle, elbow_angle = angle_calculator.calculate_valid_angles(mouse_x, mouse_y)
        # If the angles are valid, move the arm to the new position
        if (shoulder_angle is not None) and (elbow_angle is not None):
            shoulder_angle_servo = angle_calculator.convert_to_servo_angle(shoulder_angle)
            controller.move_servos(shoulder_angle_servo, -elbow_angle)

            print(f"Angles: {shoulder_angle_servo:.1f}, {elbow_angle:.1f}")
            # Convert angles to radians
            shoulder_angle_rad = np.radians(shoulder_angle)
            elbow_angle_rad = np.radians(elbow_angle)

            # Calculate coordinates of the arm segments
            upper_arm_end_x = SEGMENT_LENGTH * np.cos(shoulder_angle_rad)
            upper_arm_end_y = SEGMENT_LENGTH * np.sin(shoulder_angle_rad)

            lower_arm_end_x = upper_arm_end_x + SEGMENT_LENGTH * np.cos(shoulder_angle_rad + elbow_angle_rad)
            lower_arm_end_y = upper_arm_end_y + SEGMENT_LENGTH * np.sin(shoulder_angle_rad + elbow_angle_rad)

            # Update the plot with new arm positions
            arm1_line.set_data([0, upper_arm_end_x], [0, upper_arm_end_y])
            arm2_line.set_data([upper_arm_end_x, lower_arm_end_x], [upper_arm_end_y, lower_arm_end_y])
            fig.canvas.draw_idle()
            
def plot():
    global fig, ax, arm1_line, arm2_line, annot1, annot2
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot(y_reach, x_reach, 'b.', markersize=1, label="Reachable Coordinates")
    ax.set(xlabel="y (mm)", ylabel="x (mm)", title="Reachable Coordinates of the Robot Arm (Reversed Axes)", aspect='equal')
    ax.grid(True)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)
    ax.legend()

    ax.axis('equal')

    # Initialize arm lines
    arm1_line, = ax.plot([0, 0], [0, 0], 'r-', linewidth=2, label='Arm 1')
    arm2_line, = ax.plot([0, 0], [0, 0], 'r-', linewidth=2, label='Arm 2')

    cid_click = fig.canvas.mpl_connect('button_press_event', on_click)
    cid_hover = fig.canvas.mpl_connect('motion_notify_event', on_hover)

    annot1 = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot1.set_visible(False)
    
    annot2 = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="lightblue", alpha=0.5),
                        arrowprops=dict(arrowstyle="->"))
    annot2.set_visible(False)

    plt.show()

    fig.canvas.mpl_disconnect(cid_hover)
    fig.canvas.mpl_disconnect(cid_click)

def main():
    plot()

if __name__ == "__main__":
    main()