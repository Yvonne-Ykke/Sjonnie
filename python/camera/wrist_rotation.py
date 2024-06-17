# De shouder input heeft een hoek tussen -130 en 130 graden en de elbow input is tussen de -150 en 150.
# De tweede hoek is gebaseerd op de eerste hoek. als beide op 0 zijn, staat de robot arm recht naar voren. 
WRIST = 88

def calculate_wrist_rotation(shoulder_angle, elbow_angle, target_rotation):
    
    # Calculate the end effector angle based on shoulder and elbow angles
    end_effector_angle = shoulder_angle + elbow_angle
    
    # Calculate the required wrist rotation
    wrist_rotation = target_rotation - end_effector_angle
    
    # Ensure the wrist rotation is within [-180, 180] degrees
    wrist_rotation = (wrist_rotation + 180) % 360 - 180
    
    return wrist_rotation