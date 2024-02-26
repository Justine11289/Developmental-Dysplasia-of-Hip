import fnmatch
import serial
import csv
import re
import math
from datetime import datetime
import numpy as np

def auto_detect_serial_unix(preferred_list=['*']):
    # 自動檢測串口的函數，與原始程式碼相同
    import glob
    glist = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    ret = []

    for d in glist:
        for preferred in preferred_list:
            if fnmatch.fnmatch(d, preferred):
                ret.append(d)
    if len(ret) > 0:
        return ret

    for d in glist:
        ret.append(d)
    return ret


def kalman_filter(A, H, Q, R, measured_data):
    # 卡爾曼濾波器函數，將卡爾曼濾波器應用於加速度估計
    # A: 狀態轉移矩陣
    # H: 觀測模型矩陣
    # Q: 系統噪聲的協方差矩陣
    # R: 測量噪聲的協方差矩陣
    # measured_data: 測量的數據

    # 初始化狀態估計和協方差矩陣
    x = np.zeros((2, 1))  # 初始狀態估計
    P = np.eye(2)  # 初始協方差矩陣

    filtered_data = []

    for data in measured_data:
        # 預測步驟
        x = np.dot(A, x)
        P = np.dot(np.dot(A, P), A.T) + Q

        # 校正步驟
        y = data - np.dot(H, x)
        S = np.dot(np.dot(H, P), H.T) + R
        K = np.dot(np.dot(P, H.T), np.linalg.inv(S))
        x = x + np.dot(K, y)
        P = np.dot((np.eye(2) - np.dot(K, H)), P)

        filtered_data.append(x[0, 0])

    return filtered_data


def main():
    available_ports = auto_detect_serial_unix()
    port = serial.Serial(available_ports[0], baudrate= 115200,timeout=0.1)
    count_for_stop = 0
    compute = False
    pre_time, pre_vx, pre_vy, pre_vz, pre_px, pre_py, pre_pz = 0, 0, 0, 0, 0, 0, 0
    min_time, max_time = 9999999, -1
    count_data_num = 0
    pre_ax, pre_ay, pre_az = 0, 0, 0
    write_value = []
    now = datetime.now()
    hour = str(now.hour)
    minute = str(now.minute)
    csv_file = "result" + hour + minute + ".csv"

    with open(csv_file, mode='w+', newline='') as file:
        while True:
            rawdata = port.readline()
            data = rawdata.decode()
            if data.strip() == "MPU9250 is connected" or data.strip() == "MPU9250 dose is connected" or data.strip() == "Position you MPU9250 flat and don't move it - calibrating...":
                compute = False
                print(data)
            if compute:
                pattern = r'-?\d+\.\d+|-?\d+'
                result = re.findall(pattern, data)
                result = [float(num) for num in result]
                if len(result) == 7:
                    time, ax, ay, az, x_degree, y_degree, z_degree = result[0:7]
                    count_data_num += 1
                    print(result)

                    # 預測步驟
                    A = np.array([[1, time / 1000], [0, 1]])  # 狀態轉移矩陣
                    H = np.array([[1, 0]])  # 觀測模型矩陣
                    Q = np.eye(2) * 0.01  # 系統噪聲的協方差矩陣
                    R = np.array([[0.1]])  # 測量噪聲的協方差矩陣

                    filtered_ax = kalman_filter(A, H, Q, R, [ax])  # 應用卡爾曼濾波器估計加速度
                    filtered_ay = kalman_filter(A, H, Q, R, [ay])
                    filtered_az = kalman_filter(A, H, Q, R, [az])

                    ax = filtered_ax[0]  # 更新估計的加速度值
                    ay = filtered_ay[0]
                    az = filtered_az[0]

                    # 計算步驟
                    deltaTime = (time - pre_time) / 1000.0
                    dx = (pre_vx * deltaTime) + (0.5 * ax * deltaTime * deltaTime)
                    dy = (pre_vy * deltaTime) + (0.5 * ay * deltaTime * deltaTime)
                    dz = (pre_vz * deltaTime) + (0.5 * (az - 1) * deltaTime * deltaTime)
                    vx = pre_vx + (ax * deltaTime)
                    vy = pre_vy + (ay * deltaTime)
                    vz = pre_vz + ((az - 1) * deltaTime)
                    px = pre_px + dx
                    py = pre_py + dy
                    pz = pre_pz + dz

                    write_value[0:7] = time, ax, ay, az, vx, vy, vz
                    row = csv.writer(file)
                    row.writerow(write_value)

                    pre_time = time
                    pre_px = px
                    pre_py = py
                    pre_pz = pz
                    pre_vx = vx
                    pre_vy = vy
                    pre_vz = vz
                    print(px, py, pz)

                    if pre_ax == ax:
                        count_for_stop += 1
                    pre_ax = ax

            if data.strip() == "Done!":
                compute = True
                print("Start computing!")

            if count_for_stop == 3000:
                print("STOP!")
                port.write(b'STOP\n')
                port.close()
                dis = math.sqrt(px ** 2 + py ** 2 + pz ** 2)
                total_time = (max_time - min_time) / 1000
                print('Total data number:', count_data_num)
                print('Time (s):', total_time)
                print('Position x (m):', px)
                print('Distance (m):', dis)
                return 0


if __name__ == '__main__':
    main()
