import numpy as np
import string
import matplotlib.pyplot as plt

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

# Byte Hamming Weight Table
hamming_weight_8bit_table = np.array([
    0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4,
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5,
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
    4, 5, 5, 6, 5, 6, 6, 7, 5, 6, 6, 7, 6, 7, 7, 8
], np.uint8)

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


# Combined Lookup Table: "HamingWeight(S-Box(input))"
# hamming_s_box = np.array([int(hamming_weight_8bit_table[elem]) for elem in s_box],np.uint8)
# print hamming_s_box


def downsampling(iTraces, factor=10):
    numTraces = iTraces.shape[0]
    numSamples = iTraces.shape[1]
    newSamples = int(numSamples / factor)
    newTraces = np.zeros((numTraces, newSamples))

    for i in range(newSamples):
        newTraces[:, i] = np.mean(iTraces[:, i * factor:i * factor + factor], axis=1)

    return newTraces


def preprocessing(iTraces):
    numTraces = iTraces.shape[0]
    numSamples = iTraces.shape[1]
    exSamples = int(((numSamples - 1) * numSamples) / 2)
    exTraces = np.zeros((numTraces, exSamples))

    start = 0
    length = 0

    # Loop over all the samples
    for sample in range(numSamples - 1):
        start = start + length
        length = numSamples - (sample + 1)
        end = start + length

        # Take difference between the samples
        exTraces[:, start:end] = abs(iTraces[:, sample + 1:].T - iTraces[:, sample].T).T

    print("Finished Pre-processing")
    return exTraces


def calccorrcoef(H, Tdiff, TdiffSumSquared, numtraces):
    Hdiff = np.array((H - (np.sum(H, 0) / np.double(numtraces))).T, np.double)
    return np.dot(Hdiff, Tdiff) / np.sqrt(TdiffSumSquared * np.sum(Hdiff ** 2) + 0.0001)


def second_order_dpa(iPlaintext, iTraces, showPlot=True, fullPlot=False, silent=False):
   
    # Number of rounds
    round_key = np.zeros(16)
    maxCorrs = np.zeros(256)

    # Down sampling to get an adequate amount of traces
    newTraces = downsampling(iTraces, factor=200)  
    iTraces = newTraces
    numtraces = len(iTraces)

    # Getting the pre-processed traces
    P = preprocessing(iTraces)
    numSamples = P.shape[1]
    numtraces_p = len(P)

    # Taking the mean
    Pmean = np.sum(P, 0) / np.double(numtraces_p)

    # Calculating mean deviation
    Pdiff = P - Pmean
    PdiffSumSquared = np.sum(Pdiff ** 2, 0)

    if showPlot:
        limits = [0, numSamples, -0.025, 0.025]
        fig = plt.figure(figsize=(21.00, 11.20))  # big figure size for 4x4 subplot. Should fit to a slide.
        fig.subplots_adjust(left=0.04, bottom=0.04, right=0.96, top=0.96, wspace=0.2, hspace=0.25)
        rMaxValue = 0

    for bytenum in range(16):
        # calc hypothetical intermediate values and map them to consumption values
        key = np.array(range(256))
        Hyp = hamming_s_box[np.tile(iPlaintext[:, bytenum], (256, 1)).T ^ key.T]
        
        R = np.array(calccorrcoef(Hyp, Pdiff, PdiffSumSquared, numtraces), np.double)
        Rabs = abs(R)

        maxInd = np.unravel_index(Rabs.argmax(), Rabs.shape)
        keybyte = maxInd[0]
        Rmax = R[maxInd]
        tmax = maxInd[1]

        if not silent:
            print("keybyte %03d: 0x%02X\t(corr: %0.4f, t: %d)" % (bytenum, keybyte, Rmax, tmax))

        if showPlot:
            ax = plt.subplot(4, 4, bytenum + 1)
            ax.set_title("Keybyte %02d: 0x%0.2X" % (bytenum, keybyte))
            ax.axis(limits)
            if abs(Rmax) > rMaxValue:
                rMaxValue = abs(Rmax)

            if fullPlot:
                mask = np.ones(256, dtype=bool)
                mask[keybyte] = False
                upperCurve = np.amax(R[mask, :], axis=0)
                lowerCurve = np.amin(R[mask, :], axis=0)

                ax.plot(upperCurve, '0.8')
                ax.plot(lowerCurve, '0.8')
                ax.fill_between(range(R.shape[1]), upperCurve, lowerCurve, color='0.8')

            ax.plot(R[keybyte, :])
            ax.plot(tmax, Rmax, 'ro')

        round_key[bytenum] = keybyte

        # use "critical" keybyte 0x07 for further analysis
        if bytenum == 7:
            maxCorrs = np.amax(Rabs, axis=1)

    if showPlot:
        limits[2] = -rMaxValue
        limits[3] = rMaxValue
        for plotnum in range(16):
            ax = plt.subplot(4, 4, plotnum + 1)
            ax.axis(limits)
        plt.savefig('results/keys-all2.png')
        plt.savefig('results/keys-all2.pdf', format='pdf')
        plt.show()
    return (round_key, maxCorrs)
