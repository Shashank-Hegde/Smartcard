#!/usr/bin/env python3
# -*- Mode: Python; tab-width: 4; coding: utf8 -*-

# Measurement script vSS20

# The output is a hdf5 file with three datasets (plaintext, ciphertext and traces)
# Each value of plain- and ciphertext is stored as a np.uint8-value
# Each value of the trace is stored as a np.int16-value

# PicoScope configuration:
# -CH A is the Data input
# -EXT is the trigger input

# Please note that matlab transposes the matrices while loading them

# load definitions for picoscope
from pshelper_picosdk import psc

####################################################################
# configuration start
verbose = True

direction = 1                       # 0 = encryption, 1 = decryption

n_traces = 1000                      # number of traces to capture
n_samples = 62500                   # number of samples per trace (before falling trigger edge)
sample_rate = psc.F_125_MHZ         # sample rate [S/sec]
channel_A_range = psc.V_200M        # voltage range for channel A of picoscope
o_directory = './'                  # output directory (has to exist!)
o_file_name = 'traces.h5'           # output file name

# defines the chunksize of the plaintext dataset in the hdf5 file
chunksize_plaintext = (n_traces, 16)
# defines the chunksize of the ciphertext dataset in the hdf5 file
chunksize_ciphertext = (n_traces, 16)
# defines the chunksize of the traces dataset in the hdf5 file
chunksize_traces = (n_traces, n_samples)

# compression settings for the HDF5 file output
compression = None  # no compression
compression_opts = None
# compression         =   "gzip"  # good compression
#compression_opts    =   4
# compression         =   "lzf"  # fast compression
# compression_opts    =   None


# configuration end
####################################################################


## import modules
import Crypto.Cipher.AES
from smartcard.CardRequest import CardRequest
from smartcard.CardConnection import CardConnection
from smartcard.ATR import ATR
from smartcard.CardType import ATRCardType
from smartcard.util import toHexString, toBytes, toASCIIString, bs2hl, hl2bs
import numpy as np
from array import array
import csv
import h5py
import _thread
import random
import os
import sys
import signal
import time
import ctypes
from functools import partial
from picosdk.ps5000 import ps5000 as ps
from picosdk.functions import adc2mV, assert_pico_ok, mV2adc



# define functions
def sc_connect():
    global cardservice
    # detect the smart card based on the content of the ATR (card-centric approach)
    print('Initializing card connection...')
    try:
        cardtype = ATRCardType(toBytes("3B 90 11 00"))
        cardrequest = CardRequest(timeout=5, cardType=cardtype)
        cardservice = cardrequest.waitforcard()
        print('Card connection established correctly')
    except:
        print('ERROR: Timeout exceeded')
        sys.exit(0)
    # connect to the card using T0 protocol.
    cardservice.connection.connect(CardConnection.T0_protocol)



def handler(signum, frame):
    raise Exception("Timeout")



def sc_decrypt(key):
    global cardservice
    # format the command to be sent to the card:
    DECRYPT_KEY = [0x88, 0x10, 0, 0, len(key)] + key + [0x10]
    GET_RESPONSE = [0x88, 0xc0, 0x00, 0x00, 0x10]
    # send the commands and retrieve the responses
    # detecting a transmission error
    # signal.alarm(2)
    try:
        time.sleep(0.01)    # this can prevent the transmission error
        response, sw1, sw2 = cardservice.connection.transmit(
            DECRYPT_KEY)    # This function doesn't terminate sometimes
    # wait and try again after a transmission error
    except Exception as exc:
        print(exc)
        response, sw1, sw2 = cardservice.connection.transmit(DECRYPT_KEY)
    response, sw1, sw2 = cardservice.connection.transmit(GET_RESPONSE)
    return response



def scope_init(sample_rate, n_samples, channel_A_range):
    print('Initializing oscilloscope...')
    try:
        # Create chandle and status ready for use
        chandle = ctypes.c_int16()
        status = {}

        # Open 5000 series PicoScope
        # Returns handle to chandle for use in future API functions
        status["openunit"] = ps.ps5000OpenUnit(ctypes.byref(chandle))
        assert_pico_ok(status["openunit"])

        # Set up channel A
        # handle = chandle
        channel = ps.PS5000_CHANNEL[psc.CH_A]
        # enabled = 1
        coupling_type = psc.AC # AC=0, DC=1
        chARange = ps.PS5000_RANGE[channel_A_range]
        # analogue offset = 0 V
        status["setChA"] = ps.ps5000SetChannel(chandle, channel, 1, coupling_type, chARange)
        assert_pico_ok(status["setChA"])

        # find maximum ADC count value
        # handle = chandle
        # pointer to value = ctypes.byref(maxADC)
        maxADC = ctypes.c_int16(32512)

        # Set up single trigger
        # handle = chandle
        # enabled = 1
        source = ps.PS5000_CHANNEL[psc.CH_EXT]
        chEXTRange = ps.PS5000_RANGE[psc.V_5]
        threshold = int(mV2adc(1000, chEXTRange, maxADC))
        direction = psc.TR_FALLING
        # delay = 0 s
        # auto Trigger = 10000 ms
        status["trigger"] = ps.ps5000SetSimpleTrigger(chandle, 1, source, threshold, direction, 0, 10000)
        assert_pico_ok(status["trigger"])

        # Set number of pre and post trigger samples to be collected
        preTriggerSamples = n_samples
        postTriggerSamples = 0
        maxSamples = preTriggerSamples + postTriggerSamples

        # Get timebase information
        # handle = chandle
        timebase = sample_rate
        # noSamples = maxSamples
        # pointer to timeIntervalNanoseconds = ctypes.byref(timeIntervalns)
        oversample = 1
        # pointer to maxSamples = ctypes.byref(returnedMaxSamples)
        # segment index = 0
        timeIntervalns = ctypes.c_float()
        returnedMaxSamples = ctypes.c_int32()
        status["getTimebase"] = ps.ps5000GetTimebase(chandle, timebase, maxSamples, ctypes.byref(timeIntervalns), oversample, ctypes.byref(returnedMaxSamples), 0)
        assert_pico_ok(status["getTimebase"])

        print('Scope correctly initialized')
        return chandle, maxSamples, maxADC, preTriggerSamples, postTriggerSamples, timebase, oversample, chARange, status
    except:
        print('ERROR: Problem initializing scope: ', sys.exc_info()[0])
        sys.exit(0)



def scope_close(chandle, status):
    #ps.close_unit()
    
    # Close unit Disconnect the scope
    # handle = chandle
    status["close"]=ps.ps5000CloseUnit(chandle)
    assert_pico_ok(status["close"])



def scope_stop(chandle, status):
    # Stop the scope
    # handle = chandle
    status["stop"] = ps.ps5000Stop(chandle)
    assert_pico_ok(status["stop"])



def scope_run(chandle, preTriggerSamples, postTriggerSamples, timebase, oversample, status):
    # Run block capture
    # handle = chandle
    # number of pre-trigger samples = preTriggerSamples
    # number of post-trigger samples = PostTriggerSamples
    # timebase = 8 = 80 ns (see Programmer's guide for mre information on timebases)
    # oversample = 1
    # time indisposed ms = None (not needed in the example)
    # segment index = 0
    # lpReady = None (using ps5000IsReady rather than ps5000BlockReady)
    # pParameter = None
    status["runBlock"] = ps.ps5000RunBlock(chandle, preTriggerSamples, postTriggerSamples, timebase, oversample, None, 0, None, None)
    assert_pico_ok(status["runBlock"])



def scope_get_trace(chandle, maxSamples, chARange, maxADC, status):
    # Check for data collection to finish using ps5000IsReady
    ready = ctypes.c_int16(0)
    check = ctypes.c_int16(0)
    while ready.value == check.value:
        status["isReady"] = ps.ps5000IsReady(chandle, ctypes.byref(ready))

    # Create buffers ready for assigning pointers for data collection
    bufferAMax = (ctypes.c_int16 * maxSamples)()
    bufferAMin = (ctypes.c_int16 * maxSamples)() # used for downsampling 

    # Set data buffer location for data collection from channel A
    # handle = chandle
    source = ps.PS5000_CHANNEL[psc.CH_A]
    # pointer to buffer max = ctypes.byref(bufferAMax)
    # pointer to buffer min = ctypes.byref(bufferAMin)
    # buffer length = maxSamples
    status["setDataBuffersA"] = ps.ps5000SetDataBuffers(chandle, source, ctypes.byref(bufferAMax), ctypes.byref(bufferAMin), maxSamples)
    assert_pico_ok(status["setDataBuffersA"])

    # create overflow loaction
    overflow = ctypes.c_int16()
    # create converted type maxSamples
    cmaxSamples = ctypes.c_int32(maxSamples)

    # Retried data from scope to buffers assigned above
    # handle = chandle
    # start index = 0
    # pointer to number of samples = ctypes.byref(cmaxSamples)
    # downsample ratio = 1
    # downsample ratio mode = PS5000_RATIO_MODE_NONE
    # pointer to overflow = ctypes.byref(overflow))
    status["getValues"] = ps.ps5000GetValues(chandle, 0, ctypes.byref(cmaxSamples), 1, 0, 0, ctypes.byref(overflow))
    assert_pico_ok(status["getValues"])

    # convert ADC counts data to mV
    adc2mVChAMax =  adc2mV(bufferAMax, chARange, maxADC)
    return adc2mVChAMax



def hdf5_file_init(o_file, n_traces, n_samples, chunksize_plaintext, chunksize_ciphertext, chunksize_traces, compression, compression_opts):
    if os.path.isfile(o_file):
        print("WARNING: File " + o_file + " already exists, overwriting...")
        os.remove(o_file)
    filehandle = h5py.File(o_file, mode='a')

    FHplaintext = filehandle.create_dataset("plaintext", (n_traces, 16), chunks=chunksize_plaintext,
                                            dtype=np.uint8, compression=compression, compression_opts=compression_opts)
    FHciphertext = filehandle.create_dataset("ciphertext", (n_traces, 16), chunks=chunksize_ciphertext,
                                             dtype=np.uint8, compression=compression, compression_opts=compression_opts)
    FHtraces = filehandle.create_dataset("traces", (n_traces, n_samples), chunks=chunksize_traces,
                                         dtype=np.int16, compression=compression, compression_opts=compression_opts)

    return(filehandle, FHplaintext, FHciphertext, FHtraces)



def hdf5_file_close(filehandle):
    filehandle.close()



def hdf5_add_data(plaintext, ciphertext, trace_number, FHplaintext, FHciphertext, FHtraces, trace_data):
    FHplaintext[trace_number, :] = plaintext
    FHciphertext[trace_number, :] = ciphertext
    FHtraces[trace_number, :] = trace_data



def signal_handler( chandle, status, filehandle, start_time, signal, frame):
    print('\nClosing connections...')
    scope_stop(chandle, status)
    scope_close(chandle, status)
    hdf5_file_close(filehandle)
    end_time = time.time()
    print("Elapsed time: ", end_time - start_time)
    print('Done!')
    sys.exit(0)



def main(direction, n_traces, n_samples, sample_rate, channel_A_range, o_directory, o_file_name, chunksize_plaintext, chunksize_ciphertext, chunksize_traces, compression, compression_opts):
    global verbose
    start_time = time.time()

    # verbose mode
    if (len(sys.argv) == 2):
        if ('-ver' in sys.argv[1]):
            verbose = True
    
    # establish connection with the card
    sc_connect()
    
    # initialize the scope
    chandle, maxSamples, maxADC, preTriggerSamples, postTriggerSamples, timebase, oversample, chARange, status = scope_init(sample_rate, n_samples, channel_A_range)
    
    # open output file
    o_file = o_directory + o_file_name
    filehandle, FHplaintext, FHciphertext, FHtraces = hdf5_file_init(
        o_file, n_traces, n_samples, chunksize_plaintext, chunksize_ciphertext, chunksize_traces, compression, compression_opts)
    
    # connect signal handler
    signal.signal(signal.SIGINT, partial(signal_handler, chandle, status, filehandle, start_time))
    
    # start collecting power traces
    print("Starting capture... ")
    for i in range(0, n_traces+1):
        # start the scope
        scope_run(chandle, preTriggerSamples, postTriggerSamples, timebase, oversample, status)
        if(i == 0):  # wait three seconds the first time to prevent unusable measurements
            print("Initial measurement for calibration")
            time.sleep(3)
        if(verbose and i != 0):
            print("Trace number: %8d/%d" % (i, n_traces))
        # generate a new random data vector
        data = [random.randint(0, 255) for x in range(16)]
        ciphertext_data = data
        # send data to the card to be decrypted
        plaintext_data = sc_decrypt(data)
        # get the power trace
        trace_data = scope_get_trace(chandle, maxSamples, chARange, maxADC, status)
        # save trace, plain-text and cipher-text into an hdf5 file (first trace only for calibration)
        if(i != 0):
            if(direction == 0):
                hdf5_add_data(ciphertext_data,
                    plaintext_data, i-1, FHplaintext, FHciphertext, FHtraces, trace_data)
            else:
                hdf5_add_data(plaintext_data,
                    ciphertext_data, i-1, FHplaintext, FHciphertext, FHtraces, trace_data)
    print('Done!')
    
    # close and exit
    scope_stop(chandle, status)
    scope_close(chandle, status)
    hdf5_file_close(filehandle)
    end_time = time.time()
    print("Elapsed time: ", end_time - start_time)
    sys.exit(0)



# run program
if __name__ == "__main__":
    main(direction, n_traces, n_samples, sample_rate, channel_A_range, o_directory, o_file_name,
         chunksize_plaintext, chunksize_ciphertext, chunksize_traces, compression, compression_opts)
