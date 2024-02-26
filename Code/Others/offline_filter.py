import math
import csv
import numpy as np
from scipy.signal import butter,filtfilt,savgol_filter
from scipy.fft import fft,ifft
import matplotlib.pyplot as plt

pre_vx,pre_vy,pre_vz,pre_px,pre_py,pre_pz,pre_time = 0,0,0,0,0,0,0
total_distance = 0
pre_ax, pre_ay, pre_az = 0,0,0
fs = 200

# Find position
def compute(time,ax,ay,az,x_degree,y_degree,z_degree):
    global pre_vx,pre_vy,pre_vz,pre_px,pre_py,pre_pz,pre_time,total_distance
    #compute 
    deltaTime = time - pre_time
    # Distant : dx = v*t + 1/2*a*t^2 
    dx = (pre_vx * deltaTime) + (0.5 * ax * deltaTime * deltaTime) 
    dy = (pre_vy * deltaTime) + (0.5 * ay * deltaTime * deltaTime)
    dz = (pre_vz * deltaTime) + (0.5 * (az - 1) * deltaTime * deltaTime)
    # velocity : v2 = v1 + at
    vx = pre_vx + (ax * deltaTime)
    vy = pre_vy + (ay * deltaTime)
    vz = pre_vz + (az * deltaTime)
    # position : p2 = p1 + dinstant
    px = pre_px + dx
    py = pre_py + dy
    pz = pre_pz + dz
    # update
    pre_time = time
    pre_px = px
    pre_py = py
    pre_pz = pz
    pre_vx = vx
    pre_vy = vy
    pre_vz = vz
    total_distance += math.sqrt(dx ** 2 + dy ** 2 + dz ** 2 )
    return px,py,pz

# Standard
def STD(data):
    threshold = 2
    mask = []
    filtered_data = [d[1:7] for d in data]
    mean = np.mean(filtered_data, axis=0)
    std_devs = np.std(filtered_data, axis=0)
    for i,row in enumerate(filtered_data):
        std_range = np.all(np.abs(row - mean) <= threshold * std_devs)
        if std_range:
            mask.append(i)
    filtered_data = [data[i] for i in mask]
    return filtered_data

# Butterworth Filter
def butterworth(data):
    std_devs = np.std(data, axis=0)
    cutoff_frequency = std_devs * 3
    nyquist = 0.5 * fs
    normal_cutoff = cutoff_frequency / nyquist
    b, a = butter(7, normal_cutoff, btype='high', analog=False)
    filtered_data = filtfilt(b, a, data)
    return filtered_data

# Savitzky-Golay Filter
def savgol(data):
    window_length = 55
    poly_order = 11
    smoothed_data = savgol_filter(data,window_length,poly_order,axis = 0,mode='nearest')
    return smoothed_data

# Fourier Filter
def fourier_filter(data):
    data_freq = fft(data)
    cutoff_frequency = 20
    freqs = np.fft.fftfreq(len(data), d=1/fs)
    data_freq[np.abs(freqs) > cutoff_frequency] = 0
    filtered_data = ifft(data_freq)
    return np.real(filtered_data)

# Weight Moving Average Filter
def weight_moving_average_filter(data):
    window_size = 11
    weight = np.arange(1,window_size+1)
    pad_data = np.pad(data,(window_size//2,window_size//2),mode='edge')
    smooth_data = np.convolve(pad_data,weight/weight.sum(),mode='valid')
    return smooth_data

# Exponential Weight Moving Average Filter
def exponential_weight_moving_average_filter(data):
    alpha = np.std(data, axis=0)
    weight = (1 - alpha) ** np.arange(0,len(data),1)
    smooth_data = np.convolve(data,weight/weight.sum(),mode='full')[:len(data)]
    return smooth_data

# Hampel_filter
def hampel_filter(data):
    window_size = 13
    n = len(data)
    threshold = 3
    smoothed_data = np.zeros(n)

    for i in range(n):
        start = max(0, i - window_size)
        end = min(n, i + window_size + 1)
        window = data[start:end]
        median = np.median(window)
        deviation = np.abs(window - median)
        mad = np.median(deviation)
        
        if deviation[i - start] > threshold * mad:
            smoothed_data[i] = median
        else:
            smoothed_data[i] = data[i]

    return smoothed_data



def write_file(data,csv_file):
    with open(csv_file, mode = 'a+',newline='' ) as file:
        writer = csv.writer(file)
        writer.writerow(data)

def main():
    csv_path = "result.csv"
    data = []
    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            row = [float(value) for value in row]
            row[0] /= 1000.0
            data.append(row)
    mean = np.mean(data, axis=0)
    data = data - mean
    time,ax,ay,az,x_degree,y_degree,z_degree = zip(*data)
     
    
    
    


if __name__ == '__main__':
    main()


