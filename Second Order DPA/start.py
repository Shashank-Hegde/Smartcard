from second_order_dpa import second_order_dpa
import numpy as np
import sys
import time
import h5py

hamming_s_box = np.array([
    4, 5, 6, 6, 5, 5, 6, 4, 2, 1, 5, 4, 7, 6, 5, 5,
    4, 2, 4, 6, 6, 4, 4, 4, 5, 4, 3, 6, 4, 3, 4, 2,
    6, 7, 4, 3, 4, 6, 7, 4, 3, 4, 5, 5, 4, 4, 3, 3,
    1, 5, 3, 4, 2, 4, 2, 4, 3, 2, 1, 4, 6, 4, 4, 5,
    2, 3, 3, 3, 4, 5, 4, 2, 3, 5, 5, 5, 3, 5, 5, 2,
    4, 4, 0, 6, 1, 6, 4, 5, 4, 5, 6, 4, 3, 3, 3, 6,
    3, 7, 4, 7, 3, 4, 4, 3, 3, 6, 1, 7, 2, 4, 6, 3,
    3, 4, 1, 5, 3, 5, 3, 6, 5, 5, 5, 2, 1, 8, 6, 4,
    5, 2, 3, 5, 6, 5, 2, 4, 3, 5, 6, 5, 3, 5, 3, 5,
    2, 2, 5, 5, 2, 3, 2, 2, 3, 6, 4, 2, 6, 5, 3, 6,
    3, 3, 4, 2, 3, 2, 2, 4, 3, 5, 4, 3, 3, 4, 4, 5,
    6, 3, 5, 5, 4, 5, 4, 4, 4, 4, 5, 5, 4, 5, 5, 1,
    5, 4, 3, 4, 3, 4, 4, 4, 4, 6, 4, 5, 4, 6, 4, 3,
    3, 5, 5, 4, 2, 2, 6, 3, 3, 4, 5, 5, 3, 3, 4, 5,
    4, 5, 3, 2, 4, 5, 4, 3, 5, 4, 4, 5, 5, 4, 2, 7,
    3, 3, 3, 3, 7, 5, 2, 3, 2, 4, 4, 4, 3, 3, 6, 3
], np.uint8)


def hexVector2number(row):
    result = 0x00
    for bytenum in range(16):
        result = result | (int(row[bytenum]) << (15 - bytenum) * 8)
    return result


drive_folder = "drive-download-20230118T224931Z-001/"
folder = "DPA_traces/Traces_resistenceB/"
trace_folder = "8k_traces/"
f = h5py.File(drive_folder + "traces_75k_1k_S2.h5", "r")
f = h5py.File("traces_75k_3k_withohne_shuffling_S1.h5", "r")
data_traces = f['traces']
num_traces = 3000
data_traces = data_traces[0:num_traces, :]

data_plaintext = f['plaintext']

data_plaintext = data_plaintext[0:num_traces, :]

start = time.time()
dpaResult = second_order_dpa(data_plaintext, data_traces, showPlot=True, fullPlot=True)
end = time.time()

masterKeyVec = dpaResult[0]
maxCorrsVec = dpaResult[1]

duration = end - start
print("\nDPA Result:")
print("\tTraces:\tn = %d (%d samples per trace)" % (data_traces.shape[0], data_traces.shape[1]))
print("\tTime:\t%0.2lfs (%0.2lfs per key byte)" % (duration, duration / 16))

masterKey = hexVector2number(masterKeyVec)
print("\tKey:\t0x%0.32X" % masterKey)
origKey = "0x64B94A44201E47A879DD4D1001493B40"
print(F"\tOriginal Key:\t{origKey}")
