import numpy as np
from astropy.stats import LombScargle
from scipy.optimize import curve_fit
from typing import Tuple,List

from files import saveAmpSpectrumAndImage

def calculateAmplitudeSpectrum(data: np.ndarray, range: Tuple[float,float] = (0, 50)) -> np.ndarray:
    ls = LombScargle(data[0],data[1],normalization='psd')
    max_frequency = range[1] if range[1] < nyquistFrequency(data) else nyquistFrequency(data)
    f,p = ls.autopower(minimum_frequency=range[0],maximum_frequency=max_frequency,samples_per_peak=100)
    p = np.sqrt(4/len(data[0]))*np.sqrt(p)
    p = p[1:len(p)]
    f = f[1:len(f)]
    p = p[f < range[1]]
    f = f[f < range[1]]
    return np.array((f,p))

def nyquistFrequency(data: np.ndarray) -> float:
    return float(1/(2*np.mean(np.diff(data[0]))))

def findAndRemoveMaxFrequency(lightCurve: np.ndarray, ampSpectrum: np.ndarray) -> Tuple[List[float],np.ndarray]:
    maxY = max(ampSpectrum[1])
    maxX = ampSpectrum[0][abs(ampSpectrum[1] - max(ampSpectrum[1])) < 10**-4][0]

    arr = [maxY,maxX,0]

    popt,pcov = curve_fit(sin,lightCurve[0],lightCurve[1],p0 = arr)
    retLightCurve = np.array((lightCurve[0],lightCurve[1]-sin(lightCurve[0],*popt)))

    return popt,retLightCurve

def computeSignalToNoise(ampSpectrum: np.ndarray, windowSize: float) -> float:
    y = ampSpectrum[1]
    x = ampSpectrum[0]
    lowerMinima,upperMinima = findNextMinimas(y)
    singleStep = np.mean(np.diff(x))
    length_half = int(windowSize/singleStep)

    data = np.append(y[lowerMinima - length_half:lowerMinima],y[upperMinima:upperMinima+length_half])
    meanValue = np.mean(data)
    maxVal = y[abs(y - max(y)) < 10**-6][0]
    return float(maxVal/meanValue)


def findNextMinimas(yData: np.ndarray) -> Tuple[int,int]:
    index = int(np.where(abs(yData - max(yData)) < 10**-6)[0][0])
    minimaFound = False
    counter = 1
    lowerMinima = 0
    upperMinima = 0
    while(minimaFound == False):
        negCounter = index - counter
        posCounter = index + counter
        if checkMinima(yData,negCounter):
            lowerMinima = negCounter
        if checkMinima(yData,posCounter):
            upperMinima = posCounter

        if lowerMinima != 0 and upperMinima != 0:
            minimaFound = True
        counter += 1

    return lowerMinima,upperMinima



def checkMinima(yData: np.ndarray, counter: int) -> bool:
    return yData[counter] < yData[counter + 1] and yData[counter] < yData[counter- 1]

def sin(x: np.ndarray, amp:float, f: float, phase: float) -> np.ndarray:
    return amp * np.sin(2*np.pi * f * x + phase)

def recursiveFrequencyFinder(data: np.ndarray, frequencyRange: Tuple[float,float]
                             , snrCriterion: float, windowSize: float, path: str = "") -> List[Tuple[float,float]]:
    snr = 100
    frequencyList = []
    while(snr > snrCriterion):
        try:
            frequencyList.append((fit[1],snr))
            saveStuff = False
        except:
            saveStuff = True
        amp = calculateAmplitudeSpectrum(data,frequencyRange)
        snr = computeSignalToNoise(amp, windowSize)
        fit,data = findAndRemoveMaxFrequency(data,amp)
        print("Found frequency at "+str(fit[1])+" with snr "+str(snr))
        if saveStuff:
            saveAmpSpectrumAndImage(amp,path+"results/"+str(int(data[0][0]))+"_"+str(int(max(data[0])))+"/","First_amplitude_spectrum")

    saveAmpSpectrumAndImage(amp,path+"results/"+str(int(data[0][0]))+"_"+str(int(max(data[0])))+"/","Last_amplitude_spectrum")


    return frequencyList