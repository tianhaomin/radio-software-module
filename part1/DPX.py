"""
Tektronix RSA_API .h file Python Conversion
Author: Morgan Allison
Date created: 5/17
Date edited: 5/17
Windows 7 64-bit
RSA API version 3.9.0029
Python 3.6.0 64-bit (Anaconda 4.3.0)
Download Anaconda: http://continuum.io/downloads
Anaconda includes NumPy and MatPlotLib
Download the RSA_API: http://www.tek.com/model/rsa306-software
Download the RSA_API Documentation:
http://www.tek.com/spectrum-analyzer/rsa306-manual-6
YOU WILL NEED TO REFERENCE THE API DOCUMENTATION
"""

from ctypes import *
from enum import Enum
from ctypes import *
import os
from time import sleep
import numpy as np
import matplotlib.pyplot as plt

class RSAError(Exception):
    pass

class ReturnStatus(Enum):
    noError = 0

    # Connection
    errorNotConnected = 101
    errorIncompatibleFirmware = 102
    errorBootLoaderNotRunning = 103
    errorTooManyBootLoadersConnected = 104
    errorRebootFailure = 105

    # POST
    errorPOSTFailureFPGALoad = 201
    errorPOSTFailureHiPower = 202
    errorPOSTFailureI2C = 203
    errorPOSTFailureGPIF = 204
    errorPOSTFailureUsbSpeed = 205
    errorPOSTDiagFailure = 206

    # General Msmt
    errorBufferAllocFailed = 301
    errorParameter = 302
    errorDataNotReady = 304

    # Spectrum
    errorParameterTraceLength = 1101
    errorMeasurementNotEnabled = 1102
    errorSpanIsLessThanRBW = 1103
    errorFrequencyOutOfRange = 1104

    # IF streaming
    errorStreamADCToDiskFileOpen = 1201
    errorStreamADCToDiskAlreadyStreaming = 1202
    errorStreamADCToDiskBadPath = 1203
    errorStreamADCToDiskThreadFailure = 1204
    errorStreamedFileInvalidHeader = 1205
    errorStreamedFileOpenFailure = 1206
    errorStreamingOperationNotSupported = 1207
    errorStreamingFastForwardTimeInvalid = 1208
    errorStreamingInvalidParameters = 1209
    errorStreamingEOF = 1210

    # IQ streaming
    errorIQStreamInvalidFileDataType = 1301
    errorIQStreamFileOpenFailed = 1302
    errorIQStreamBandwidthOutOfRange = 1303

    # -----------------
    # Internal errors
    # -----------------
    errorTimeout = 3001
    errorTransfer = 3002
    errorFileOpen = 3003
    errorFailed = 3004
    errorCRC = 3005
    errorChangeToFlashMode = 3006
    errorChangeToRunMode = 3007
    errorDSPLError = 3008
    errorLOLockFailure = 3009
    errorExternalReferenceNotEnabled = 3010
    errorLogFailure = 3011
    errorRegisterIO = 3012
    errorFileRead = 3013

    errorDisconnectedDeviceRemoved = 3101
    errorDisconnectedDeviceNodeChangedAndRemoved = 3102
    errorDisconnectedTimeoutWaitingForADcData = 3103
    errorDisconnectedIOBeginTransfer = 3104
    errorOperationNotSupportedInSimMode = 3015

    errorFPGAConfigureFailure = 3201
    errorCalCWNormFailure = 3202
    errorSystemAppDataDirectory = 3203
    errorFileCreateMRU = 3204
    errorDeleteUnsuitableCachePath = 3205
    errorUnableToSetFilePermissions = 3206
    errorCreateCachePath = 3207
    errorCreateCachePathBoost = 3208
    errorCreateCachePathStd = 3209
    errorCreateCachePathGen = 3210
    errorBufferLengthTooSmall = 3211
    errorRemoveCachePath = 3212
    errorGetCachingDirectoryBoost = 3213
    errorGetCachingDirectoryStd = 3214
    errorGetCachingDirectoryGen = 3215
    errorInconsistentFileSystem = 3216

    errorWriteCalConfigHeader = 3301
    errorWriteCalConfigData = 3302
    errorReadCalConfigHeader = 3303
    errorReadCalConfigData = 3304
    errorEraseCalConfig = 3305
    errorCalConfigFileSize = 3306
    errorInvalidCalibConstantFileFormat = 3307
    errorMismatchCalibConstantsSize = 3308
    errorCalConfigInvalid = 3309

    # flash
    errorFlashFileSystemUnexpectedSize = 3401,
    errorFlashFileSystemNotMounted = 3402
    errorFlashFileSystemOutOfRange = 3403
    errorFlashFileSystemIndexNotFound = 3404
    errorFlashFileSystemReadErrorCRC = 3405
    errorFlashFileSystemReadFileMissing = 3406
    errorFlashFileSystemCreateCacheIndex = 3407
    errorFlashFileSystemCreateCachedDataFile = 3408
    errorFlashFileSystemUnsupportedFileSize = 3409
    errorFlashFileSystemInsufficentSpace = 3410
    errorFlashFileSystemInconsistentState = 3411
    errorFlashFileSystemTooManyFiles = 3412
    errorFlashFileSystemImportFileNotFound = 3413
    errorFlashFileSystemImportFileReadError = 3414
    errorFlashFileSystemImportFileError = 3415
    errorFlashFileSystemFileNotFoundError = 3416
    errorFlashFileSystemReadBufferTooSmall = 3417
    errorFlashWriteFailure = 3418
    errorFlashReadFailure = 3419
    errorFlashFileSystemBadArgument = 3420
    errorFlashFileSystemCreateFile = 3421

    # Aux monitoring
    errorMonitoringNotSupported = 3501,
    errorAuxDataNotAvailable = 3502

    # battery
    errorBatteryCommFailure = 3601
    errorBatteryChargerCommFailure = 3602
    errorBatteryNotPresent = 3603

    # EST
    errorESTOutputPathFile = 3701
    errorESTPathNotDirectory = 3702
    errorESTPathDoesntExist = 3703
    errorESTUnableToOpenLog = 3704
    errorESTUnableToOpenLimits = 3705

    # Revision information
    errorRevisionDataNotFound = 3801

    # alignment
    error112MHzAlignmentSignalLevelTooLow = 3901
    error10MHzAlignmentSignalLevelTooLow = 3902
    errorInvalidCalConstant = 3903
    errorNormalizationCacheInvalid = 3904
    errorInvalidAlignmentCache = 3905

    # acq status
    errorADCOverrange = 9000  # must not change the location of these error codes without coordinating with MFG TEST
    errorOscUnlock = 9001

    errorNotSupported = 9901

    errorPlaceholder = 9999
    notImplemented = -1


class Cplx32(Structure):
    _fields_ = [('i', c_float), ('q', c_float)]


class CplxInt32(Structure):
    _fields_ = [('i', c_int32), ('q', c_int32)]


class CplxInt16(Structure):
    _fields_ = [('i', c_int16), ('q', c_int16)]


AcqDataStatus_ADC_OVERRANGE = 0x1
AcqDataStatus_REF_OSC_UNLOCK = 0x2
AcqDataStatus_LOW_SUPPLY_VOLTAGE = 0x10
AcqDataStatus_ADC_DATA_LOST = 0x20
AcqDataStatus_VALID_BITS_MASK = (AcqDataStatus_ADC_OVERRANGE or AcqDataStatus_REF_OSC_UNLOCK or AcqDataStatus_LOW_SUPPLY_VOLTAGE or AcqDataStatus_ADC_DATA_LOST)


class AcqDataStatus:
    def __init__(self):
        self.adcOverrange = 0x1
        self.refFreqUnlock = 0x2
        self.lo1Unlock = 0x4
        self.lo2Unlock = 0x8
        self.lowSupplyVoltage = 0x10
        self.adcDataLost = 0x20
        self.event1pps = 0x40
        self.eventTrig1 = 0x80
        self.eventTrig2 = 0x100


DEVSRCH_MAX_NUM_DEVICES = 20
DEVSRCH_SERIAL_MAX_STRLEN = 100
DEVSRCH_TYPE_MAX_STRLEN = 20
DEVINFO_MAX_STRLEN = 100


class DEVICE_INFO(Structure):
    _fields_ = [('nomenclature', c_char_p),
                ('serialNum', c_char_p),
                ('apiVersion', c_char_p),
                ('fwVersion', c_char_p),
                ('fpgaVersion', c_char_p),
                ('hwVersion', c_char_p)]


class TriggerMode:
    def __init__(self):
        self.freeRun = c_int(0)
        self.triggered = c_int(1)
TriggerMode = TriggerMode()


class TriggerSource:
    def __init__(self):
        self.TriggerSourceExternal = c_int(0)
        self.TriggerSourceIFPowerLevel = c_int(1)
TriggerSource = TriggerSource()


class TriggerTransition:
    def __init__(self):
        self.TriggerTransitionLH = c_int(1)
        self.TriggerTransitionHL = c_int(2)
        self.TriggerTransitionEither = c_int(3)
TriggerTransition = TriggerTransition()


DEVEVENT_OVERRANGE = c_int(0)
DEVEVENT_TRIGGER = c_int(1)
DEVEVENT_1PPS = c_int(2)


class RunMode:
    def __init__(self):
        self.stopped = c_int(0)
        self.running = c_int(1)
RunMode = RunMode()


IQBLK_STATUS_INPUT_OVERRANGE = (1 << 0)
IQBLK_STATUS_FREQREF_UNLOCKED = (1 << 1)
IQBLK_STATUS_ACQ_SYS_ERROR = (1 << 2)
IQBLK_STATUS_DATA_XFER_ERROR = (1 << 3)


class IQBLK_ACQINFO(Structure):
    _fields_ = [('sample0Timestamp', c_uint64),
                ('triggerSampleIndex', c_uint64),
                ('triggerTimestamp', c_uint64),
                ('acqStatus', c_uint32)]


class IQHeader(Structure):
    _fields_ = [('acqDataStatus', c_uint16),
                ('acquisitionTimestamp', c_uint64),
                ('frameID', c_uint32),
                ('trigger1Index', c_uint16),
                ('trigger2Index', c_uint16),
                ('timeSyncIndex', c_uint16)]


class SpectrumWindows:
    def __init__(self):
        self.SpectrumWindow_Kaiser = c_int(0)
        self.SpectrumWindow_Mil6dB = c_int(1)
        self.SpectrumWindow_BlackmanHarris = c_int(2)
        self.SpectrumWindow_Rectangle = c_int(3)
        self.SpectrumWindow_FlatTop = c_int(4)
        self.SpectrumWindow_Hann = c_int(5)
SpectrumWindows = SpectrumWindows()


class SpectrumTraces:
    def __init__(self):
        self.SpectrumTrace1 = c_int(0)
        self.SpectrumTrace2 = c_int(1)
        self.SpectrumTrace3 = c_int(2)
SpectrumTraces = SpectrumTraces()


class SpectrumDetectors:
    def __init__(self):
        self.SpectrumDetector_PosPeak = c_int(0)
        self.SpectrumDetector_NegPeak = c_int(1)
        self.SpectrumDetector_AverageVRMS = c_int(2)
        self.SpectrumDetector_Sample = c_int(3)
SpectrumDetectors = SpectrumDetectors()


class SpectrumVerticalUnits:
    def __init__(self):
        self.SpectrumVerticalUnit_dBm = c_int(0)
        self.SpectrumVerticalUnit_Watt = c_int(1)
        self.SpectrumVerticalUnit_Volt = c_int(2)
        self.SpectrumVerticalUnit_Amp = c_int(3)
        self.SpectrumVerticalUnit_dBmV = c_int(4)
SpectrumVerticalUnits = SpectrumVerticalUnits()


class Spectrum_Settings(Structure):
    _fields_ = [('span', c_double),
                ('rbw', c_double),
                ('enableVBW', c_bool),
                ('vbw', c_double),
                ('traceLength', c_int),
                ('window', c_int),
                ('verticalUnit', c_int),
                ('actualStartFreq', c_double),
                ('actualStopFreq', c_double),
                ('actualFreqStepSize', c_double),
                ('actualRBW', c_double),
                ('actualVBW', c_double),
                ('actualNumIQSamples', c_double)]


class Spectrum_Limits(Structure):
    _fields_ = [('maxSpan', c_double),
                ('minSpan', c_double),
                ('maxRBW', c_double),
                ('minRBW', c_double),
                ('maxVBW', c_double),
                ('minVBW', c_double),
                ('maxTraceLength', c_int),
                ('minTraceLength', c_int)]


class Spectrum_TraceInfo(Structure):
    _fields_ = [('timestamp', c_int64),
                ('acqDataStatus', c_uint16)]


class DPX_FrameBuffer(Structure):
    _fields_ = [('fftPerFrame', c_int32),
                ('fftCount', c_int64),
                ('frameCount', c_int64),
                ('timestamp', c_double),
                ('acqDataStatus', c_uint32),
                ('minSigDuration', c_double),
                ('minSigDurOutOfRange', c_bool),
                ('spectrumBitmapWidth', c_int32),
                ('spectrumBitmapHeight', c_int32),
                ('spectrumBitmapSize', c_int32),
                ('spectrumTraceLength', c_int32),
                ('numSpectrumTraces', c_int32),
                ('spectrumEnabled', c_bool),
                ('spectrogramEnabled', c_bool),
                ('spectrumBitmap', POINTER(c_float)),
                ('spectrumTraces', POINTER(POINTER(c_float))),
                ('sogramBitmapWidth', c_int32),
                ('sogramBitmapHeight', c_int32),
                ('sogramBitmapSize', c_int32),
                ('sogramBitmapNumValidLines', c_int32),
                ('sogramBitmap', POINTER(c_uint8)),
                ('sogramBitmapTimestampArray', POINTER(c_double)),
                ('sogramBitmapContainTriggerArray', POINTER(c_double))]


class DPX_SogramSettingStruct(Structure):
    _fields_ = [('bitmapWidth', c_int32),
                ('bitmapHeight', c_int32),
                ('sogramTraceLineTime', c_double),
                ('sogramBitmapLineTime', c_double)]


class DPX_SettingStruct(Structure):
    _fields_ = [('enableSpectrum', c_bool),
                ('enableSpectrogram', c_bool),
                ('bitmapWidth', c_int32),
                ('bitmapHeight', c_int32),
                ('traceLength', c_int32),
                ('decayFactor', c_float),
                ('actualRBW', c_double)]


class TraceType:
    def __init__(self):
        self.TraceTypeAverage = c_int(0)
        self.TraceTypeMax = c_int(1)
        self.TraceTypeMaxHold = c_int(2)
        self.TraceTypeMin = c_int(3)
        self.TraceTypeMinHold = c_int(4)
TraceType = TraceType()


class VerticalUnitType:
    def __init__(self):
        self.VerticalUnit_dBm = c_int(0)
        self.VerticalUnit_Watt = c_int(1)
        self.VerticalUnit_Volt = c_int(2)
        self.VerticalUnit_Amp = c_int(3)
VerticalUnitType = VerticalUnitType()


DPX_TRACEIDX_1 = c_int(0)
DPX_TRACEIDX_2 = c_int(1)
DPX_TRACEIDX_3 = c_int(2)


class AudioDemodMode:
    def __init__(self):
        self.ADM_FM_8KHZ = c_int(0)
        self.ADM_FM_13KHZ = c_int(1)
        self.ADM_FM_75KHZ = c_int(2)
        self.ADM_FM_200KHZ = c_int(3)
        self.ADM_AM_8KHZ = c_int(4)
        self.ADM_NONE = c_int(5)  # internal use only
AudioDemodMode = AudioDemodMode()


class StreamingMode:
    def __init__(self):
        self.StreamingModeRaw = c_int(0)
        self.StreamingModeFormatted = c_int(1)
StreamingMode = StreamingMode()


class IQSOUTDEST:
    def __init__(self):
        self.IQSOD_CLIENT = c_int(0)
        self.IQSOD_FILE_TIQ = c_int(1)
        self.IQSOD_FILE_SIQ = c_int(2)
        self.IQSOD_FILE_SIQ_SPLIT = c_int(3)
IQSOUTDEST = IQSOUTDEST()


class IQSOUTDTYPE:
    def __init__(self):
        self.IQSODT_SINGLE = c_int(0)
        self.IQSODT_INT32 = c_int(1)
        self.IQSODT_INT16 = c_int(2)
IQSOUTDTYPE = IQSOUTDTYPE()


IQSSDFN_SUFFIX_INCRINDEX_MIN = c_int(0)
IQSSDFN_SUFFIX_TIMESTAMP = c_int(-1)
IQSSDFN_SUFFIX_NONE = c_int(-2)

IFSSDFN_SUFFIX_INCRINDEX_MIN = c_int(0)
IFSSDFN_SUFFIX_TIMESTAMP = c_int(-1)
IFSSDFN_SUFFIX_NONE = c_int(-2)

IQSTRM_STATUS_OVERRANGE = (1 << 0)
IQSTRM_STATUS_XFER_DISCONTINUITY = (1 << 1)
IQSTRM_STATUS_IBUFF75PCT = (1 << 2)
IQSTRM_STATUS_IBUFFOVFLOW = (1 << 3)
IQSTRM_STATUS_OBUFF75PCT = (1 << 4)
IQSTRM_STATUS_OBUFFOVFLOW = (1 << 5)
IQSTRM_STATUS_NONSTICKY_SHIFT = 0
IQSTRM_STATUS_STICKY_SHIFT = 16

IQSTRM_MAXTRIGGERS = 100



class IQSTRMIQINFO(Structure):
    _fields_ = [('timestamp', c_uint64),
                ('triggerCount', c_int),
                ('triggerIndices', POINTER(c_int)),
                ('scaleFactor', c_double),
                ('acqStatus', c_uint32)]


class IQSTREAM_File_Info(Structure):
    _fields_ = [('numberSamples', c_uint64),
                ('sample0Timestamp', c_uint64),
                ('triggerSampleIndex', c_uint64),
                ('triggerTimestamp', c_uint64),
                ('acqStatus', c_uint32),
                ('filenames', c_wchar_p)]


class GNSS_SATSYS:
    def __init__(self):
        self.GNSS_NOSYS = c_int(0)
        self.GNSS_GPS_GLONASS = c_int(1)
        self.GNSS_GPS_BEIDOU = c_int(2)
        self.GNSS_GPS = c_int(3)
        self.GNSS_GLONASS = c_int(4)
        self.GNSS_BEIDOU = c_int(5)
GNSS_SATSYS = GNSS_SATSYS()


class POWER_INFO(Structure):
    _fields_ = [('externalPowerPresent', c_bool),
                ('batteryPresent', c_bool),
                ('batteryChargeLevel', c_double),
                ('batteryCharging', c_bool),
                ('batteryOverTemperature', c_bool),
('batteryHardwareError', c_bool)]

os.chdir("E:/项目/洪（私）/pro\RSA_API/lib/x64")
rsa = WinDLL("RSA_API.dll")


"""################CLASSES AND FUNCTIONS################"""
def err_check(rs):
    if ReturnStatus(rs) != ReturnStatus.noError:
        raise RSAError(ReturnStatus(rs).name)

def search_connect():
    numFound = c_int(0)
    intArray = c_int * DEVSRCH_MAX_NUM_DEVICES
    deviceIDs = intArray()
    deviceSerial = create_string_buffer(DEVSRCH_SERIAL_MAX_STRLEN)
    deviceType = create_string_buffer(DEVSRCH_TYPE_MAX_STRLEN)
    apiVersion = create_string_buffer(DEVINFO_MAX_STRLEN)

    rsa.DEVICE_GetAPIVersion(apiVersion)
    print('API Version {}'.format(apiVersion.value.decode()))

    err_check(rsa.DEVICE_Search(byref(numFound), deviceIDs,
                                deviceSerial, deviceType))

    if numFound.value < 1:
        # rsa.DEVICE_Reset(c_int(0))
        print('No instruments found. Exiting script.')
        exit()
    elif numFound.value == 1:
        print('One device found.')
        print('Device type: {}'.format(deviceType.value.decode()))
        print('Device serial number: {}'.format(deviceSerial.value.decode()))
        err_check(rsa.DEVICE_Connect(deviceIDs[0]))
    else:
        # corner case
        print('2 or more instruments found. Enumerating instruments, please wait.')
        for inst in deviceIDs:
            rsa.DEVICE_Connect(inst)
            rsa.DEVICE_GetSerialNumber(deviceSerial)
            rsa.DEVICE_GetNomenclature(deviceType)
            print('Device {}'.format(inst))
            print('Device Type: {}'.format(deviceType.value))
            print('Device serial number: {}'.format(deviceSerial.value))
            rsa.DEVICE_Disconnect()
        # note: the API can only currently access one at a time
        selection = 1024
        while (selection > numFound.value - 1) or (selection < 0):
            selection = int(input('Select device between 0 and {}\n> '.format(numFound.value - 1)))
        err_check(rsa.DEVICE_Connect(deviceIDs[selection]))
    rsa.CONFIG_Preset()


"""################SPECTRUM EXAMPLE################"""
def config_spectrum(cf=1e9, refLevel=0, span=40e6, rbw=300e3):
    rsa.SPECTRUM_SetEnable(c_bool(True))
    rsa.CONFIG_SetCenterFreq(c_double(cf))
    rsa.CONFIG_SetReferenceLevel(c_double(refLevel))

    rsa.SPECTRUM_SetDefault()
    specSet = Spectrum_Settings()
    rsa.SPECTRUM_GetSettings(byref(specSet))
    specSet.window = SpectrumWindows.SpectrumWindow_Kaiser
    specSet.verticalUnit = SpectrumVerticalUnits.SpectrumVerticalUnit_dBm
    specSet.span = span
    specSet.rbw = rbw
    rsa.SPECTRUM_SetSettings(specSet)
    rsa.SPECTRUM_GetSettings(byref(specSet))
    return specSet


def create_frequency_array(specSet):
    # Create array of frequency data for plotting the spectrum.
    freq = np.arange(specSet.actualStartFreq, specSet.actualStartFreq
                     + specSet.actualFreqStepSize * specSet.traceLength,
                     specSet.actualFreqStepSize)
    return freq


def acquire_spectrum(specSet):
    ready = c_bool(False)
    traceArray = c_float * specSet.traceLength
    traceData = traceArray()
    outTracePoints = c_int(0)
    traceSelector = SpectrumTraces.SpectrumTrace1

    rsa.DEVICE_Run()
    rsa.SPECTRUM_AcquireTrace()
    while not ready.value:
        rsa.SPECTRUM_WaitForDataReady(c_int(100), byref(ready))
    rsa.SPECTRUM_GetTrace(traceSelector, specSet.traceLength, byref(traceData),
                          byref(outTracePoints))
    rsa.DEVICE_Stop()
    return np.array(traceData)


def spectrum_example():
    print('\n\n########Spectrum Example########')
    search_connect()
    cf = 2.4453e9
    refLevel = -30
    span = 40e6
    rbw = 10e3
    specSet = config_spectrum(cf, refLevel, span, rbw)
    trace = acquire_spectrum(specSet)
    freq = create_frequency_array(specSet)
    peakPower, peakFreq = peak_power_detector(freq, trace)

    plt.figure(1, figsize=(15, 10))
    ax = plt.subplot(111, facecolor='k')
    ax.plot(freq, trace, color='y')
    ax.set_title('Spectrum Trace')
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Amplitude (dBm)')
    ax.axvline(peakFreq)
    ax.text((freq[0] + specSet.span / 20), peakPower,
            'Peak power in spectrum: {:.2f} dBm @ {} MHz'.format(
                peakPower, peakFreq / 1e6), color='white')
    ax.set_xlim([freq[0], freq[-1]])
    ax.set_ylim([refLevel - 100, refLevel])
    plt.tight_layout()
    plt.show()
    rsa.DEVICE_Disconnect()


"""################BLOCK IQ EXAMPLE################"""
def config_block_iq(cf=1e9, refLevel=0, iqBw=40e6, recordLength=10e3):
    recordLength = int(recordLength)
    rsa.CONFIG_SetCenterFreq(c_double(cf))
    rsa.CONFIG_SetReferenceLevel(c_double(refLevel))

    rsa.IQBLK_SetIQBandwidth(c_double(iqBw))
    rsa.IQBLK_SetIQRecordLength(c_int(recordLength))

    iqSampleRate = c_double(0)
    rsa.IQBLK_GetIQSampleRate(byref(iqSampleRate))
    # Create array of time data for plotting IQ vs time
    time = np.linspace(0, recordLength / iqSampleRate.value, recordLength)
    time1 = []
    step = recordLength / iqSampleRate.value / (recordLength - 1)
    for i in range(recordLength):
        time1.append(i * step)
    return time


def acquire_block_iq(recordLength=10e3):
    recordLength = int(recordLength)
    ready = c_bool(False)
    iqArray = c_float * recordLength
    iData = iqArray()
    qData = iqArray()
    outLength = 0
    rsa.DEVICE_Run()
    rsa.IQBLK_AcquireIQData()
    while not ready.value:
        rsa.IQBLK_WaitForIQDataReady(c_int(100), byref(ready))
    rsa.IQBLK_GetIQDataDeinterleaved(byref(iData), byref(qData),
                                     byref(c_int(outLength)), c_int(recordLength))
    rsa.DEVICE_Stop()

    return np.array(iData) + 1j * np.array(qData)


def block_iq_example():
    print('\n\n########Block IQ Example########')
    search_connect()
    cf = 1e9
    refLevel = 0
    iqBw = 40e6
    recordLength = 1e3

    time = config_block_iq(cf, refLevel, iqBw, recordLength)
    IQ = acquire_block_iq(recordLength)

    fig = plt.figure(1, figsize=(15, 10))
    fig.suptitle('I and Q vs Time', fontsize='20')
    ax1 = plt.subplot(211, facecolor='k')
    ax1.plot(time * 1000, np.real(IQ), color='y')
    ax1.set_ylabel('I (V)')
    ax1.set_xlim([time[0] * 1e3, time[-1] * 1e3])
    ax2 = plt.subplot(212, facecolor='k')
    ax2.plot(time * 1000, np.imag(IQ), color='c')
    ax2.set_ylabel('I (V)')
    ax2.set_xlabel('Time (msec)')
    ax2.set_xlim([time[0] * 1e3, time[-1] * 1e3])
    plt.tight_layout()
    plt.show()
    rsa.DEVICE_Disconnect()


"""################DPX EXAMPLE################"""
def config_DPX(cf=1e9, refLevel=0, span=40e6, rbw=300e3):
    yTop = refLevel
    yBottom = yTop - 100
    yUnit = VerticalUnitType.VerticalUnit_dBm

    dpxSet = DPX_SettingStruct()
    rsa.CONFIG_SetCenterFreq(c_double(cf))
    rsa.CONFIG_SetReferenceLevel(c_double(refLevel))

    rsa.DPX_SetEnable(c_bool(True))
    rsa.DPX_SetParameters(c_double(span), c_double(rbw), c_int(801), c_int(1),
                          yUnit, c_double(yTop), c_double(yBottom), c_bool(False),
                          c_double(1.0), c_bool(False))
    rsa.DPX_SetSogramParameters(c_double(1e-3), c_double(1e-3),
                                c_double(refLevel), c_double(refLevel - 100))
    rsa.DPX_Configure(c_bool(True), c_bool(True))

    rsa.DPX_SetSpectrumTraceType(c_int32(0), c_int(2))
    rsa.DPX_SetSpectrumTraceType(c_int32(1), c_int(4))
    rsa.DPX_SetSpectrumTraceType(c_int32(2), c_int(0))

    rsa.DPX_GetSettings(byref(dpxSet))
    dpxFreq = np.linspace((cf - span / 2), (cf + span / 2), dpxSet.bitmapWidth)
    dpxAmp = np.linspace(yBottom, yTop, dpxSet.bitmapHeight)
    return dpxFreq, dpxAmp


def acquire_dpx_frame():
    frameAvailable = c_bool(False)
    ready = c_bool(False)
    fb = DPX_FrameBuffer()

    rsa.DEVICE_Run()
    rsa.DPX_Reset()

    while not frameAvailable.value:
        rsa.DPX_IsFrameBufferAvailable(byref(frameAvailable))
        while not ready.value:
            rsa.DPX_WaitForDataReady(c_int(100), byref(ready))
    rsa.DPX_GetFrameBuffer(byref(fb))
    rsa.DPX_FinishFrameBuffer()
    rsa.DEVICE_Stop()
    return fb


def extract_dpx_spectrum(fb):
    # When converting a ctypes pointer to a numpy array, we need to
    # explicitly specify its length to dereference it correctly
    dpxBitmap = np.array(fb.spectrumBitmap[:fb.spectrumBitmapSize])
    dpxBitmap = dpxBitmap.reshape((fb.spectrumBitmapHeight,
                                   fb.spectrumBitmapWidth))

    # Grab trace data and convert from W to dBm
    # http://www.rapidtables.com/convert/power/Watt_to_dBm.htm
    # Note: fb.spectrumTraces is a pointer to a pointer, so we need to
    # go through an additional dereferencing step
    traces = []
    for i in range(3):
        traces.append(10 * np.log10(1000 * np.array(
            fb.spectrumTraces[i][:fb.spectrumTraceLength])) + 30)
    # specTrace2 = 10 * np.log10(1000*np.array(
    #     fb.spectrumTraces[1][:fb.spectrumTraceLength])) + 30
    # specTrace3 = 10 * np.log10(1000*np.array(
    #     fb.spectrumTraces[2][:fb.spectrumTraceLength])) + 30

    # return dpxBitmap, specTrace1, specTrace2, specTrace3
    return dpxBitmap, traces


def extract_dpxogram(fb):
    # When converting a ctypes pointer to a numpy array, we need to
    # explicitly specify its length to dereference it correctly
    dpxogram = np.array(fb.sogramBitmap[:fb.sogramBitmapSize])
    dpxogram = dpxogram.reshape((fb.sogramBitmapHeight,
                                 fb.sogramBitmapWidth))
    dpxogram = dpxogram[:fb.sogramBitmapNumValidLines, :]

    return dpxogram


def dpx_example():
    print('\n\n########DPX Example########')
    search_connect()
    cf = 2.4453e9
    refLevel = -30
    span = 40e6
    rbw = 100e3

    dpxFreq, dpxAmp = config_DPX(cf, refLevel, span, rbw)
    fb = acquire_dpx_frame()

    dpxBitmap, traces = extract_dpx_spectrum(fb)
    dpxogram = extract_dpxogram(fb)
    numTicks = 11
    plotFreq = np.linspace(cf - span / 2.0, cf + span / 2.0, numTicks) / 1e9

    """################PLOT################"""
    # Plot out the three DPX spectrum traces
    fig = plt.figure(1, figsize=(15, 10))
    ax1 = fig.add_subplot(131)
    ax1.set_title('DPX Spectrum Traces')
    ax1.set_xlabel('Frequency (GHz)')
    ax1.set_ylabel('Amplitude (dBm)')
    dpxFreq /= 1e9
    st1, = plt.plot(dpxFreq, traces[0])
    st2, = plt.plot(dpxFreq, traces[1])
    st3, = plt.plot(dpxFreq, traces[2])
    ax1.legend([st1, st2, st3], ['Max Hold', 'Min Hold', 'Average'])
    ax1.set_xlim([dpxFreq[0], dpxFreq[-1]])

    # Show the colorized DPX display
    ax2 = fig.add_subplot(132)
    ax2.imshow(dpxBitmap, cmap='gist_stern')
    ax2.set_aspect(7)
    ax2.set_title('DPX Bitmap')
    ax2.set_xlabel('Frequency (GHz)')
    ax2.set_ylabel('Amplitude (dBm)')
    xTicks = map('{:.4}'.format, plotFreq)
    plt.xticks(np.linspace(0, fb.spectrumBitmapWidth, numTicks), xTicks)
    yTicks = map('{}'.format, np.linspace(refLevel, refLevel - 100, numTicks))
    plt.yticks(np.linspace(0, fb.spectrumBitmapHeight, numTicks), yTicks)

    # Show the colorized DPXogram
    ax3 = fig.add_subplot(133)
    ax3.imshow(dpxogram, cmap='gist_stern')
    ax3.set_aspect(12)
    ax3.set_title('DPXogram')
    ax3.set_xlabel('Frequency (GHz)')
    ax3.set_ylabel('Trace Lines')
    xTicks = map('{:.4}'.format, plotFreq)
    plt.xticks(np.linspace(0, fb.sogramBitmapWidth, numTicks), xTicks)

    plt.tight_layout()
    plt.show()
    rsa.DEVICE_Disconnect()


"""################IF STREAMING EXAMPLE################"""
def config_if_stream(cf=1e9, refLevel=0, fileDir='C:\SignalVu-PC Files', fileName='if_stream_test', durationMsec=100):
    rsa.CONFIG_SetCenterFreq(c_double(cf))
    rsa.CONFIG_SetReferenceLevel(c_double(refLevel))
    rsa.IFSTREAM_SetDiskFilePath(c_char_p(fileDir.encode()))
    rsa.IFSTREAM_SetDiskFilenameBase(c_char_p(fileName.encode()))
    rsa.IFSTREAM_SetDiskFilenameSuffix(IFSSDFN_SUFFIX_NONE)
    rsa.IFSTREAM_SetDiskFileLength(c_long(durationMsec))
    rsa.IFSTREAM_SetDiskFileMode(StreamingMode.StreamingModeFormatted)
    rsa.IFSTREAM_SetDiskFileCount(c_int(1))


def if_stream_example():
    print('\n\n########IF Stream Example########')
    search_connect()
    durationMsec = 100
    waitTime = durationMsec / 10 / 1000
    config_if_stream(fileDir='C:\\SignalVu-PC Files',
                     fileName='if_stream_test', durationMsec=durationMsec)
    writing = c_bool(True)

    rsa.DEVICE_Run()
    rsa.IFSTREAM_SetEnable(c_bool(True))
    while writing.value:
        sleep(waitTime)
        rsa.IFSTREAM_GetActiveStatus(byref(writing))
    print('Streaming finished.')
    rsa.DEVICE_Stop()
    rsa.DEVICE_Disconnect()


"""################IQ STREAMING EXAMPLE################"""
def config_iq_stream(cf=1e9, refLevel=0, bw=10e6, fileDir='C:\\SignalVu-PC Files',
                     fileName='iq_stream_test', dest=IQSOUTDEST.IQSOD_FILE_SIQ,
                     suffixCtl=IQSSDFN_SUFFIX_NONE,
                     dType=IQSOUTDTYPE.IQSODT_INT16,
                     durationMsec=100):
    filenameBase = fileDir + '\\' + fileName
    bwActual = c_double(0)
    sampleRate = c_double(0)
    rsa.CONFIG_SetCenterFreq(c_double(cf))
    rsa.CONFIG_SetReferenceLevel(c_double(refLevel))

    rsa.IQSTREAM_SetAcqBandwidth(c_double(bw))
    rsa.IQSTREAM_SetOutputConfiguration(dest, dType)
    rsa.IQSTREAM_SetDiskFilenameBase(c_char_p(filenameBase.encode()))
    rsa.IQSTREAM_SetDiskFilenameSuffix(suffixCtl)
    rsa.IQSTREAM_SetDiskFileLength(c_int(durationMsec))
    rsa.IQSTREAM_GetAcqParameters(byref(bwActual), byref(sampleRate))
    rsa.IQSTREAM_ClearAcqStatus()


def iqstream_status_parser(iqStreamInfo):
    # This function parses the IQ streaming status variable
    status = iqStreamInfo.acqStatus
    if status == 0:
        print('\nNo error.\n')
    if bool(status & 0x10000):  # mask bit 16
        print('\nInput overrange.\n')
    if bool(status & 0x40000):  # mask bit 18
        print('\nInput buffer > 75{} full.\n'.format('%'))
    if bool(status & 0x80000):  # mask bit 19
        print('\nInput buffer overflow. IQStream processing too slow, ',
              'data loss has occurred.\n')
    if bool(status & 0x100000):  # mask bit 20
        print('\nOutput buffer > 75{} full.\n'.format('%'))
    if bool(status & 0x200000):  # mask bit 21
        print('Output buffer overflow. File writing too slow, ',
              'data loss has occurred.\n')


def iq_stream_example():
    print('\n\n########IQ Stream Example########')
    search_connect()

    bw = 40e6
    dest = IQSOUTDEST.IQSOD_FILE_SIQ_SPLIT
    durationMsec = 100
    waitTime = 0.1
    iqStreamInfo = IQSTREAM_File_Info()

    complete = c_bool(False)
    writing = c_bool(False)

    config_iq_stream(bw=bw, dest=dest, durationMsec=durationMsec)

    rsa.DEVICE_Run()
    rsa.IQSTREAM_Start()
    while not complete.value:
        sleep(waitTime)
        rsa.IQSTREAM_GetDiskFileWriteStatus(byref(complete), byref(writing))
    rsa.IQSTREAM_Stop()
    print('Streaming finished.')
    rsa.IQSTREAM_GetFileInfo(byref(iqStreamInfo))
    iqstream_status_parser(iqStreamInfo)
    rsa.DEVICE_Stop()
    rsa.DEVICE_Disconnect()


"""################MISC################"""
def config_trigger(trigMode=TriggerMode.triggered, trigLevel=-10,
                   trigSource=TriggerSource.TriggerSourceIFPowerLevel):
    rsa.TRIG_SetTriggerMode(trigMode)
    rsa.TRIG_SetIFPowerTriggerLevel(c_double(trigLevel))
    rsa.TRIG_SetTriggerSource(trigSource)
    rsa.TRIG_SetTriggerPositionPercent(c_double(10))


def peak_power_detector(freq, trace):
    peakPower = np.amax(trace)
    peakFreq = freq[np.argmax(trace)]

    return peakPower, peakFreq


def main():
    # uncomment the example you'd like to run
    spectrum_example()
    # block_iq_example()
    # dpx_example()
    # if_stream_example()
    # iq_stream_example()

if __name__ == '__main__':
    main()