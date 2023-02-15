import matplotlib.pyplot as plt  # Add support for drawing figures
import load_traces  # Loads traces

# LOAD DATA AND TRACES
# open input file (path defined in load_traces)
input_data = load_traces.load_traces()

# Load measured traces into a matrix: trace-number x trace-length
traces = input_data.get_traces()

# PLOT FIRST POWER TRACE
plt.figure(1)
plt.plot(traces[0], lw=.5)
plt.xlabel('Samples')
plt.xlim(0, traces.shape[1])
plt.ylabel('Power Consumption')
plt.ylim(-200, 200)
plt.grid('on')
plt.title('Power trace')
plt.savefig('power_trace.pdf', format='pdf')

plt.show()
