import numpy as np
import matplotlib.pyplot as plt
import math
import controller

link = [300, 300]
angle = [0, 0]
target = [0, 0, 0]

fig = plt.figure()
ax = fig.add_subplot(1,1,1)

def draw_axis(ax, scale=1.0, A=np.eye(4), style='-', draw_2d=True):
    xaxis = np.array([[0, 0, 0, 1],
                      [scale, 0, 0, 1]]).T
    yaxis = np.array([[0, 0, 0, 1],
                      [0, scale, 0, 1]]).T
    zaxis = np.array([[0, 0, 0, 1],
                      [0, 0, scale, 1]]).T

    xc = A.dot( xaxis )
    yc = A.dot( yaxis )
    zc = A.dot( zaxis )

    if draw_2d:
        ax.plot(xc[0,:], xc[1,:], 'r' + style)
        ax.plot(yc[0,:], yc[1,:], 'g' + style)
    else:
        ax.plot(xc[0,:], xc[1,:], xc[2,:], 'r' + style)
        ax.plot(yc[0,:], yc[1,:], yc[2,:], 'g' + style)
        ax.plot(zc[0,:], zc[1,:], zc[2,:], 'b' + style)

def rotateZ(theta):
    rz = np.array([[math.cos(theta), - math.sin(theta), 0, 0],
                   [math.sin(theta), math.cos(theta), 0, 0],
                   [0, 0, 1, 0],
                   [0, 0, 0, 1]])
    return rz

def translate(dx, dy, dz):
    t = np.array([[1, 0, 0, dx],
                  [0, 1, 0, dy],
                  [0, 0, 1, dz],
                  [0, 0, 0, 1]])
    return t

def FK(angle, link):
    n_links = len(link)
    P = []
    P.append(np.eye(4))
    for i in range(0, n_links):
        R = rotateZ(angle[i]/180*math.pi)
        T = translate(link[i], 0, 0)
        P.append(P[-1].dot(R).dot(T))
    return P

def IK(target, angle, link, max_iter = 10000, err_min = 0.1):
    solved = False
    err_end_to_target = math.inf

    for loop in range(max_iter):
        for i in range(len(link)-1, -1, -1):
            P = FK(angle, link)
            end_to_target = target - P[-1][:3, 3]
            err_end_to_target = np.linalg.norm(end_to_target[:2])
            if err_end_to_target < err_min:
                solved = True
                break

            cur_to_end = P[-1][:3, 3] - P[i][:3, 3]
            cur_to_end_mag = np.linalg.norm(cur_to_end)
            cur_to_target = target - P[i][:3, 3]
            cur_to_target_mag = np.linalg.norm(cur_to_target)

            end_target_mag = cur_to_end_mag * cur_to_target_mag

            if end_target_mag <= 0.0001:    
                cos_rot_ang = 1
                sin_rot_ang = 0
            else:
                cos_rot_ang = np.dot(cur_to_end, cur_to_target) / end_target_mag
                sin_rot_ang = np.cross(cur_to_end[:2], cur_to_target[:2]) / end_target_mag

            rot_ang = math.acos(max(-1, min(1,cos_rot_ang)))

            if sin_rot_ang < 0.0:
                rot_ang = -rot_ang

            angle[i] = angle[i] + (rot_ang * 180 / math.pi)

            if angle[i] >= 360:
                angle[i] = angle[i] - 360
            if angle[i] < 0:
                angle[i] = 360 + angle[i]

        # Check if end effector is within desired range
        end_effector_pos = P[-1][:3, 3]
        distance_to_origin = np.linalg.norm(end_effector_pos)
        if distance_to_origin < 150 or distance_to_origin > 600:
            solved = False
            break

        if solved:
            break
            
    return angle, err_end_to_target, solved, loop

def ck(event):
    global target, link, angle, ax
    target[0] = event.xdata
    target[1] = event.ydata

    print("Target Position : ", target)
    plt.cla()
    plot_reachable_area()

    angle, err, solved, iteration = IK(target, angle, link, max_iter=1000)
    P = FK(angle, link)

    if solved:
        for i in range(len(link)):
            start_point = P[i]
            end_point = P[i+1]
            ax.plot([start_point[0,3], end_point[0,3]], [start_point[1,3], end_point[1,3]], 'ro-')
            draw_axis(ax, scale=50, A=P[i+1], draw_2d=True)
            
        print("\nIK solved\n")
        print("Iteration :", iteration)
        print("Angle :", angle)
        print("Target :", target)
        print("End Effector :", P[-1][:3, 3])
        print("Error :", err)
        controller.move_servos(angle[0], angle[1])
    else:
        print("\nIK error\n")
        print("Angle :", angle)
        print("Target :", target)
        print("End Effector :", P[-1][:3, 3])
        print("Error :", err)
    fig.canvas.draw()

def plot_reachable_area():
    shoulder_angles = np.radians(np.linspace(-150, 150, 300))
    elbow_angles = np.radians(np.linspace(-150, 150, 300))

    reachable_coordinates = []

    for shoulder_angle in shoulder_angles:
        for elbow_angle in elbow_angles:
            x = link[0] * np.cos(shoulder_angle) + link[1] * np.cos(shoulder_angle + elbow_angle)
            y = link[0] * np.sin(shoulder_angle) + link[1] * np.sin(shoulder_angle + elbow_angle)
            distance = np.hypot(x, y)
            if 0 < distance <= sum(link):
                reachable_coordinates.append((x, y))

    x_reach, y_reach = zip(*reachable_coordinates)

    ax.plot(y_reach, x_reach, 'b.', markersize=1, label="Reachable Coordinates")
    ax.set_xlabel("y (mm)")

def main():
    fig.canvas.mpl_connect('button_press_event', ck)
    fig.suptitle("Cyclic Coordinate Descent - Inverse Kinematics", fontsize=12)
    plot_reachable_area()
    plt.show()

if __name__ == "__main__":
    main()