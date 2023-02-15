### Measurement Scripts

This folder contains the measurement scripts used in the smart card and SIKA labs
by TUEISEC.

In order to record power traces, connect the oscilloscope to the computer and
attach the probe on channel A to the jumper connecting to the shunt resistor of
the smart card, and the probe on the external trigger to the trigger pin on the 
smart card. Both ground connectors have to be attached to the ground pin.

The jumpers, where you need to attach your probes, are the following:

|         | SmartCardv2 (Atmel AVR) |
| ------- | ----------------------- |
| Shunt   | JP9                     |
| Trigger | JP5                     |
| Ground  | JP8                     |

In order to figure out how many traces you need and how the amplitudes have to set,
you can use the PicoScope-Software. Consider to play around with different shunt
resistors in order to get the clearest traces.

Before running a measurement please adjust the settings in
'trace_measurement.py' to your needs. All constants are defined in 'pshelper_picosdk.py'

Then run a measurement by executing:
    python3 trace_measurement.py

To plot the first measured trace adjust the trace filename path in load_traces.py and then run:
	python3 plot_trace.py

    Contains the measuring scripts.
    
    pshelper_picosdk.py
        Available settings of the picoscope. Should not be modified.
    
    trace_measurement.py
        Measuring script that records the traces of your AES.
        Please modify the settings in the configuration settings of the main
        function to match the length of you AES encryption.
    
    load_traces.py
    	Loads a .h5 file.
    
    plot_trace.py
    	Plots the first recorded trace inside the .h5 trace file.

