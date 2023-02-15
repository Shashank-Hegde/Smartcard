import numpy as np
import string
import matplotlib.pyplot as plt
import h5py
import math
from itertools import product
import time

#reading the .h5 file
f = h5py.File("traces_75k_3k_S2.h5", "r")
data_traces = f['traces']
data_traces1 = f['traces']
print("data_traces")

#print(data_traces.shape)
#print("data_traces[1])")

data_plaintext1 = f['plaintext']
data_plaintext = f['plaintext']
numSamples = data_traces.shape[1]
print("num samples", numSamples)
#print(data_plaintext[1])
print("data_plaintext")
print(len(data_plaintext[1]))
#print(list(data_plaintext.shape))
#print(len(data_plaintext))
numberMean = 48
## Lookup Tables
# S-BOX
s_box = np.array([
0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
], np.uint8)


haming_s_box = []
for i in s_box:
    binary = bin(i)
    ham_wt = binary.count('1')
    haming_s_box.append(ham_wt)
haming_s_box = np.array(haming_s_box,np.uint8)

# data_traces compress
T = list(range(data_traces.shape[1]))
ix = []
for x in T:
    ix.append(math.floor(x/numberMean))
#print("ix")
#print(ix)
ix=np.array(ix)

print("data_traces before compress shape")
print(data_traces.shape[1])

traces_empty=[]
traces_empty = np.array(traces_empty)


final_op_Pt=[]

for j in range (len(data_traces)):
    traces_empty = np.bincount(ix,data_traces[j])
    traces_empty = traces_empty.tolist()
    final_op_Pt.append(traces_empty)

final_op_Pt = np.array(final_op_Pt)
print("final op shape")
print(final_op_Pt.shape)

def pearson_corr(H, Tdiff, TdiffSumSquared, numtraces):
    # np.sum(H,0)-> sum rows of an array
    Hdiff = np.array((H - (np.sum(H, 0) / np.double(numtraces))).T, np.double)
    #rint("Hdiff")
    #print(Hdiff)
    return np.dot(Hdiff, Tdiff) / np.sqrt(TdiffSumSquared * np.sum(Hdiff**2))

def dpa(plaintext, traces, showPlot=True, fullPlot=False,comp=True):
    round_key = np.zeros(16)
    maxCorrs = np.zeros(256)

    #calculations for correlation
    numtraces = len(traces)
    #print(traces)


    Tmean = np.sum(traces,0) / np.double(numtraces)
    #print("Tmean")
    #print(Tmean)
    Tdiff = traces - Tmean
    TdiffSumSquared = np.sum(Tdiff**2, 0)

    if showPlot:
        limits = [0, numSamples, -0.1, 0.1]
        fig = plt.figure(figsize=(20.00,10.00)) # big figure size for 4x4 subplot. Should fit to a slide.
        fig.subplots_adjust(left=0.04, bottom=0.04, right=0.96, top=0.96, wspace=0.2, hspace=0.25)
        rMaxValue = 0

    for j in range(16):
        #calc the hypothetical H matrix
        key = np.array(range(256))
        #print("np.tile(plaintext[:,j], (256,1))")
        #print(np.tile(plaintext[:,j], (256,1)))
        #print()
        H = haming_s_box[np.tile(plaintext[:,j], (256,1)).T^key.T]
        #print("H")
        #print(H)
        #print(j)

        R = np.array(pearson_corr(H, Tdiff, TdiffSumSquared, numtraces), np.double)
        Rabs = abs(R)

        maxInd = np.unravel_index(Rabs.argmax(), Rabs.shape)
        keybyte = maxInd[0]
        Rmax = R[maxInd]
        tmax = maxInd[1]

        print("Rmax", rMaxValue)
        print("sample number -", maxInd[1])

        if showPlot:
            ax = plt.subplot(4,4,j + 1)
            ax.set_title("Keybyte %02d: 0x%0.2X" % (j, keybyte))
            ax.axis(limits)
            if abs(Rmax) > rMaxValue:
                rMaxValue = abs(Rmax)

            if fullPlot:
                mask = np.ones(256, dtype=bool)
                mask[keybyte] = False
                upperCurve = np.amax(R[mask,:], axis=0)
                lowerCurve = np.amin(R[mask,:], axis=0)

                ax.plot(upperCurve, '0.8')
                ax.plot(lowerCurve, '0.8')
                ax.fill_between(range(R.shape[1]), upperCurve, lowerCurve, color='0.8')

            ax.plot(R[keybyte,:])
            ax.plot(tmax, Rmax, 'ro')

        round_key[j] = keybyte

        # use "critical" keybyte 0x07 for further analysis
        #if j == 7:
        #    maxCorrs = np.amax(Rabs, axis=1)
    if(comp==False):
        if showPlot:
            limits[2] = -rMaxValue
            limits[3] = rMaxValue
            for plotnum in range(16):
                ax = plt.subplot(4,4,plotnum + 1)
                ax.axis(limits)
            plt.savefig('keys_uncompressed.png')
            plt.savefig('keys_uncompressed.pdf', format='pdf')
            plt.show(block=False)
            plt.pause(3)
            plt.close()

    if(comp==True):
        if showPlot:
            limits = [0, numSamples/numberMean, -0.1, 0.1]
            limits[2] = -rMaxValue
            limits[3] = rMaxValue
            for plotnum in range(16):
                ax = plt.subplot(4,4,plotnum + 1)
                ax.axis(limits)
            plt.savefig('keys_compressed.png')
            plt.savefig('keys_kompressed.pdf', format='pdf')
            plt.show(block=False)
            plt.pause(3)
            plt.close()

    return (round_key, maxCorrs)

start = time.time()
dpa(data_plaintext1,data_traces1 , showPlot=True, fullPlot=False,comp=False)
print("time before compression")
end = time.time()
print("time is ")
print(end - start)

start1 = time.time()
#dpa(pt_divide,final_op_Pt.astype(int), showPlot=True, fullPlot=False)
dpa(data_plaintext1,final_op_Pt.astype(int), showPlot=True, fullPlot=False,comp=True)
print("time after compression")
end1 = time.time()
print("time is ")
print(end1 - start1)
end = time.time()
