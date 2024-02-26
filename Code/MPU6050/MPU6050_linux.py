from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial.transform import Rotation as R
import fnmatch
import serial
import csv
import re
import math
import pylab
import threading
import os
import time

compute = False

class QuaternionHandler:
    def __init__(self):
        # Unit quaternion
        self.accumulated_quaternion = np.array([1.0, 0.0, 0.0, 0.0])
        
    def euler_to_quaternion(self, roll, pitch, yaw):
        roll = np.radians(roll)
        pitch = np.radians(pitch)
        yaw = np.radians(yaw)
        cr = np.cos(roll * 0.5)
        sr = np.sin(roll * 0.5)
        cp = np.cos(pitch * 0.5)
        sp = np.sin(pitch * 0.5)
        cy = np.cos(yaw * 0.5)
        sy = np.sin(yaw * 0.5)

        w = cy * cp * cr + sy * sp * sr
        x = cy * cp * sr - sy * sp * cr
        y = sy * cp * sr + cy * sp * cr
        z = sy * cp * cr - cy * sp * sr

        return np.array([w, x, y, z])
    
    def quaternion_multiply(self, q1, q2):
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2

        w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
        x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
        y = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
        z = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2

        return np.array([w, x, y, z])        

    def quaternion_to_euler(self, q):
        w, x, y, z = q
        # Roll
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x**2 + y**2)
        roll = np.arctan2(sinr_cosp, cosr_cosp)
        # Pitch
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = np.sign(sinp) * np.pi / 2  # use 90 degrees if out of range
        else:
            pitch = np.arcsin(sinp)
        # Yaw
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y**2 + z**2)
        yaw = np.arctan2(siny_cosp, cosy_cosp)

        return roll, pitch, yaw    
    
    def update_with_new_euler(self, roll, pitch, yaw):
        new_quaternion = self.euler_to_quaternion(roll, pitch, yaw)
        self.accumulated_quaternion = self.quaternion_multiply(new_quaternion, self.accumulated_quaternion)
        self.normalize_quaternion()
    
    def normalize_quaternion(self):
        norm = np.linalg.norm(self.accumulated_quaternion)
        if norm == 0: 
            return 
        self.accumulated_quaternion = self.accumulated_quaternion / norm


def euler_to_rotation_matrix(yaw, pitch, roll):
    # Yaw (about z-axis)
    R_z = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1]
    ])

    # Pitch (about y-axis)
    R_y = np.array([
        [np.cos(pitch), 0, np.sin(pitch)],
        [0, 1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])

    # Roll (about x-axis)
    R_x = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]
    ])

    # Combined rotation matrix
    R = R_z @ R_y @ R_x
    return R

class ExtendedKalmanFilter:
    def __init__(self, initial_state, initial_covariance, process_noise_cov, measurement_noise_cov):
        self.state = initial_state
        self.covariance = initial_covariance
        self.process_noise_cov = process_noise_cov
        self.measurement_noise_cov = measurement_noise_cov

    def predict(self):
        F = np.eye(3) 
        Q = self.process_noise_cov
        self.state = np.dot(F, self.state)
        self.covariance = np.dot(np.dot(F, self.covariance), F.T) + Q

    def update(self, measurement):
        H = np.eye(3) 
        R = self.measurement_noise_cov
        y = measurement - np.dot(H, self.state)
        S = np.dot(np.dot(H, self.covariance), H.T) + R
        K = np.dot(np.dot(self.covariance, H.T), np.linalg.inv(S))
        self.state = self.state + np.dot(K, y)
        self.covariance = np.dot(np.eye(3) - np.dot(K, H), self.covariance)

class DataThread(threading.Thread):
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.data_mpu1 = None
        self.data_mpu2 = None

    def run(self):
        # read data
        while True:
            global compute
            try:
                rawdata = self.port.readline()
                data = rawdata.decode('utf-8','ignore')
                if data.find("start computing!") != -1:
                    compute = True
                if compute == True :
                    pattern = r'-?\d+\.\d+|-?\d+'
                    result = re.findall(pattern,data)
                    result = [float(num) for num in result]
                    if len(result) == 6 :
                        pitch1,roll1,yaw1 = result[0:3]
                        pitch2,roll2,yaw2 = result[3:6]
                        self.data_mpu1 = pitch1, roll1, yaw1
                        self.data_mpu2 = pitch2, roll2, yaw2
                else:
                    self.data_mpu1 = None
                    self.data_mpu2 = None
            except serial.SerialException as e:
                print("error reading from serial port: " + str(e))

def auto_detect_serial_unix(preferred_list=['*']):
    '''try to auto-detect serial ports on win32'''
    import glob
    glist = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    ret = []

    # try preferred ones first
    for d in glist:
        for preferred in preferred_list:
            if fnmatch.fnmatch(d, preferred):
                ret.append(d)
    if len(ret) > 0:
        return ret
    # now the rest
    for d in glist:
        ret.append(d)
    return ret


def main():
    # Initialization-quaternion
    handler1 = QuaternionHandler()
    handler2 = QuaternionHandler()

    # Initialization-EKF
    initial_state1 = np.array([0.0, 0.0, 0.0])  # Sensor1 initial_state
    initial_state2 = np.array([0.0, 0.0, 0.0])  # Sensor2 initial_state
    initial_covariance = np.eye(3)  
    process_noise_cov = np.eye(3) * 0.01  
    measurement_noise_cov = np.eye(3) * 0.1  
    ekf1 = ExtendedKalmanFilter(initial_state1,initial_covariance,process_noise_cov,measurement_noise_cov)
    ekf2 = ExtendedKalmanFilter(initial_state2,initial_covariance,process_noise_cov,measurement_noise_cov)
    
    # csv file
    now = datetime.now()
    date = str(now.year).zfill(2) + str(now.month).zfill(2) + str(now.day).zfill(2)
    hour = str(now.hour)
    minute = str(now.minute)
    folder_path = "/mnt/hgfs/onlineResult/"+ date 
    file_name = "result_" + hour + minute + ".csv"
    csv_file = os.path.join(folder_path, file_name)
    os.makedirs(folder_path, exist_ok = True)
    write_value = []

    # Detect
    available_ports = auto_detect_serial_unix()
    port = serial.Serial(available_ports[0], baudrate= 115200,timeout=2.0)
    print("please wait")
    time.sleep(5)
    port.write(b's')

    # Thread
    data_thread = DataThread(port)
    data_thread.start()

    with open(csv_file, mode='w+', newline='') as file:
        # csv title
        write_value[0:7] = 'time','roll(x)(degree)','pitch(y)(degree)','yaw(z)(degree)','roll(x)(degree)','pitch(y)(degree)','yaw(z)(degree)'
        row = csv.writer(file)
        row.writerow(write_value)

        # 3D Image
        plt.ion()  # interactive mode
        fig = plt.figure()
        ax_subplot = fig.add_subplot(111, projection='3d')

        # Initialization-arrow
        x_arrow1 = ax_subplot.quiver(0, 0, 0, 1, 0, 0, color='r', label='X-axis MPU1')
        y_arrow1 = ax_subplot.quiver(0, 0, 0, 0, 1, 0, color='g', label='Y-axis MPU1')
        z_arrow1 = ax_subplot.quiver(0, 0, 0, 0, 0, 1, color='b', label='Z-axis MPU1')
        x_arrow2 = ax_subplot.quiver(0, 0, 0, 1, 0, 0, color='r', linestyle='--', label='X-axis MPU2')
        y_arrow2 = ax_subplot.quiver(0, 0, 0, 0, 1, 0, color='g', linestyle='--', label='Y-axis MPU2')
        z_arrow2 = ax_subplot.quiver(0, 0, 0, 0, 0, 1, color='b', linestyle='--', label='Z-axis MPU2')

        # Image label & title
        ax_subplot.set_xlabel('Y')
        ax_subplot.set_ylabel('X')
        ax_subplot.set_zlabel('Z')
        ax_subplot.set_title('3D Sensor Data')
        

        print("into loop")
        try:
            while True:
                if data_thread.data_mpu1 is not None and data_thread.data_mpu2 is not None:
                    # Sensor data
                    pitch1, roll1, yaw1 = data_thread.data_mpu1
                    pitch2, roll2, yaw2 = data_thread.data_mpu2
                    
                    # Sensor 1
                    ekf1.predict()
                    ekf1.update(np.array([roll1, pitch1, yaw1]))
                    roll1, pitch1, yaw1 = ekf1.state[0:3]
                    handler1.update_with_new_euler(roll1, pitch1, yaw1)
                    sum_roll1, sum_pitch1, sum_yaw1 = handler1.quaternion_to_euler(handler1.accumulated_quaternion)
                    
                    # Sensor 2
                    ekf2.predict()
                    ekf2.update(np.array([roll2, pitch2, yaw2]))
                    roll2, pitch2, yaw2 = ekf2.state[0:3]
                    handler2.update_with_new_euler(roll2, pitch2, yaw2)
                    sum_roll2, sum_pitch2, sum_yaw2 = handler2.quaternion_to_euler(handler2.accumulated_quaternion)

                    # Relative Angle
                    pitch ,roll ,yaw = sum_pitch2 - sum_pitch1, sum_roll2 - sum_roll1, sum_yaw2 - sum_yaw1
                    pitch *= 2
                    roll *= 2
                    yaw *= 2
                    print("sum: ",pitch ,roll ,yaw)  
                    
                    # Rotation Matrix
                    rotation = euler_to_rotation_matrix(yaw,pitch,roll)
                    rotation_x,rotation_y,rotation_z = rotation[0:3]
                       
                    # record time
                    current_time = datetime.now()
                    current_time = current_time.strftime("%H:%M:%S.%f")

                    # write file
                    write_value[0:4] = current_time,roll,pitch,yaw
                    row.writerow(write_value)

                    # Update arrow
                    x_arrow1.set_segments([[np.zeros(3), rotation_x * -0.04]])
                    y_arrow1.set_segments([[np.zeros(3), rotation_y * -0.04]])
                    z_arrow1.set_segments([[np.zeros(3), rotation_z * 0.08]])
                    
                    x_arrow2.set_segments([[np.zeros(3),  np.array([1.0, 0.0, 0.0]) * -0.04]])
                    y_arrow2.set_segments([[np.zeros(3),  np.array([0.0, 1.0, 0.0]) * -0.04]])
                    z_arrow2.set_segments([[np.zeros(3),  np.array([0.0, 0.0, 1.0]) * 0.08]])


                    # re fig
                    fig.canvas.flush_events()
        except KeyboardInterrupt:
            print("-----end-----")
        finally:
            data_thread._stop()
            data_thread.join()
            port.write(b'e')
            time.sleep(1)
            port.close()
            print("port close")
            print(csv_file)


if __name__ == '__main__':
    main()