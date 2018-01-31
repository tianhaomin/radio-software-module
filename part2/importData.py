import pandas
import matplotlib.pyplot as plt
path = input()
print(path)
df = pandas.read_csv(path)
list_feq = df['frequence']
list_pow = df['power']
plt.plot (list_feq,list_pow)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude (dBm)')
plt.title('Spectrum')
plt.show()
