import pytest
from files import *
import numpy as np

def getSin(offset,amp,frequency):
    t = np.linspace(0, 1, 2000)
    y = offset + amp*np.sin(2*np.pi*frequency*t)
    return np.array((t,y))

testCasesDataReduction = [getSin(0,1,5),getSin(5,1,5),getSin(0,1,5) + getSin(0,2,10),np.loadtxt("betaPic_BTrBHr_all_2col.dat").T]

@pytest.mark.parametrize("value",["file1","file2"])
def testReadDataFailed(value):
    with pytest.raises(IOError):
        readData(value)


def testReadData():
    data = readData("betaPic_BTrBHr_all_2Col.dat")
    assert isinstance(data,np.ndarray)
    assert len(data) == 2

@pytest.mark.parametrize("value",testCasesDataReduction)
def testRemoveMean(value):
    data = normalizeData(value)
    assert np.mean(data[1]) < 10**-6
    assert data[0][0] == 0

@pytest.mark.parametrize("value",testCasesDataReduction)
def testGetSlits(value):
    value = normalizeData(value)
    timeRange = max(value[0])/10
    overlap = max(value[0])/50
    dataList = getSplits(value,timeRange,overlap)
    expectedLength = int((max(value[0])-timeRange)/(timeRange-overlap)) +1

    assert len(dataList) == expectedLength

    for i in range(0,len(dataList)-1):
        assert dataList[i+1][0][0]-max(dataList[i][0]) - overlap < 10**-3
