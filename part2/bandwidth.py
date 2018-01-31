# 经过验证可行
import numpy as np
from part2 import connect
def bandwidth(peakPower,peakFreq,trace,freq):
    peak_index1 = np.argmax(trace)
    peak_index2 = np.argmax(trace)
    a1 = 0
    a2 = len(trace) - 1
    while peak_index1>0:
        if trace[peak_index1]>peakPower-3:
            pass
        else:
            a1 = peak_index1
            break
        peak_index1 -= 1
    while peak_index2<len(trace):
        if trace[peak_index2]>peakPower-3:
            pass
        else:
            a2 = peak_index2
            break
        peak_index2 += 1
    bandWidth = freq[a2] - freq[a1]
    return bandWidth
