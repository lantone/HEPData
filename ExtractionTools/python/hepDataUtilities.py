#!/usr/bin/env python
import sys
import os
import fileinput
from array import *
from math import floor, log10
from optparse import OptionParser
from operator import itemgetter, attrgetter
import numpy
from decimal import *


from hepDataClasses import *


import ROOT

NSIGFIGS = 2

###############################################################################
###############################################################################
###############################################################################


###############################################################################

# BEGIN HELPER FUNCTIONS TO FORMAT OUTPUT TABLES

###############################################################################

# function for making tables with columns aligned
def fancyTable(arrays):

    def areAllEqual(lst):
        return not lst or [lst[0]] * len(lst) == lst

    if not areAllEqual(map(len, arrays)):
        exit('Cannot print a table with unequal array lengths.')

    verticalMaxLengths = ([max(value) 
                           for value in map(lambda * x:x, *[map(len, a) 
                                                            for a in arrays])]
                          )

    spacedLines = []

    for array in arrays:
        spacedLine = ''
        for i, field in enumerate(array):
            diff = verticalMaxLengths[i] - len(field)
            spacedLine += field + ' ' * diff + '\t'
        spacedLines.append(spacedLine)

    return '\n'.join(spacedLines)

###############################################################################

# function for formatting numbers for putting into text files
def format_number(num, sig_figs=-99):

    if num < 0:
        num = abs(num)

    # round to appropriate number of sig_figs
    if num != 0 and sig_figs != -99:
        precision = -int(floor(log10(abs(num))) - (sig_figs - 1))
        num = round(num, precision)

    # remove trailing zeros
    num = str(num)
    if num.find(".0") is len(num)-2 and num.find(".0") is not -1:
        num = num[0:len(num)-2]

    return str(num)

###############################################################################


# END HELPER FUNCTIONS TO FORMAT OUTPUT TABLES

###############################################################################
###############################################################################
###############################################################################

###############################################################################

def remove_trailing_zero(number):
    valueString = str(number)
    if (valueString.find(".0") is len(valueString)-2 and 
        valueString.find(".0") is not -1):
        number = Decimal(valueString[0:len(valueString)-2])            
    return number

###############################################################################

def set_sigfigs(number, nSigFigs):
    if number > 0:
        number = round(number, -int(floor(log10(abs(number))) - (nSigFigs - 1)))
    return number

###############################################################################

def get_precision(number):
    number = remove_trailing_zero(number)
    valueString = str(number)
    if "." not in valueString:
        # count significant digits before "."
        nZeros = len(valueString) - len(valueString.rstrip("0"))
        return -nZeros
    else:
        # count digits after "."
        return len(valueString.split(".")[1])

###############################################################################

def extractData_TGraphAsymmErrors(graph):
    data = []
    xs = graph.GetX()
    ys = graph.GetY()
    for index in range(graph.GetN()):
        x = xs[index]
        y = ys[index]
        errorDown = graph.GetErrorYlow(index)
        errorUp = graph.GetErrorYhigh(index)
        errorLeft = graph.GetErrorXlow(index)
        errorRight = graph.GetErrorXhigh(index)
        data.append(Datum(x,
                          y,
                          errorDown,
                          errorUp,
                          errorLeft,
                          errorRight))

    return data

###############################################################################

def extractData_TGraph(graph):
    data = []
    xs = graph.GetX()
    ys = graph.GetY()
    for index in range(graph.GetN()):
        x = xs[index]
        y = ys[index]
        data.append(Point(x,y))

    return data

###############################################################################

def extractData_TF1(function):
    name = function.GetName()
    if len(function.GetExpFormula("p")):  # check if it's empty
        print
        print "function for '" + name + "' = " + str(function.GetExpFormula("p"))
        print
    else:
        print "no valid function for '" + name + "'"

    return


###############################################################################

def extractData_TH1(histo):
    data = []
    for index in range(1,histo.GetNbinsX()+1):
        x = histo.GetBinCenter(index)
        y = histo.GetBinContent(index)
        errorDown = errorUp = histo.GetBinError(index)
        errorLeft = errorRight = histo.GetBinWidth(index)/2.
        data.append(Datum(x,
                          y,
                          errorDown,
                          errorUp,
                          errorLeft,
                          errorRight))

    return data


###############################################################################


def write_limit_table(datasets):

    lines = []

    #use the exp. data to set x-axis points
    nPoints = len(datasets["exp"].data)
    testData = datasets["exp"].data

    for binIndex in range(nPoints):

        x = remove_trailing_zero(testData[binIndex].xValue)
        obs = set_sigfigs(datasets["obs"].data[binIndex].yValue, NSIGFIGS)
        exp = set_sigfigs(datasets["exp"].data[binIndex].yValue, NSIGFIGS)

        if "1sigma" in datasets and "2sigma" in datasets:
            plus1 = set_sigfigs(datasets["1sigma"].data[binIndex].errorUp, NSIGFIGS)
            minus1 = set_sigfigs(datasets["1sigma"].data[binIndex].errorDown, NSIGFIGS)
            plus2 = set_sigfigs(datasets["2sigma"].data[binIndex].errorUp, NSIGFIGS)
            minus2 = set_sigfigs(datasets["2sigma"].data[binIndex].errorDown, NSIGFIGS)
        elif "plus1sigma" in datasets and "plus2sigma" in datasets:
            plus1 = set_sigfigs(datasets["plus1sigma"].data[binIndex].yValue - exp, NSIGFIGS)
            minus1 = set_sigfigs(exp - datasets["minus1sigma"].data[binIndex].yValue, NSIGFIGS)
            plus2 = set_sigfigs(datasets["plus2sigma"].data[binIndex].yValue - exp, NSIGFIGS)
            minus2 = set_sigfigs(exp - datasets["minus2sigma"].data[binIndex].yValue, NSIGFIGS)
        else:
            print "error parsing limits"
            return

        line = []
        # add column of x-axis points
        line.append(" " + str(x) + ";")
        # add column of observed limits
        line.append(str(obs) + ";")
        # add column of expected +- 1 sigma
        line.append(str(exp) + " +" + str(plus1) + "," + "-" + str(minus1) + ";")
        # add column of expected +- 2 sigma
        line.append(str(exp) + " +" + str(plus2) + "," + "-" + str(minus2) + ";")      

        lines.append(line)       

    print "*qual: . : Observed Limit : ",
    print "Median +- 1 sigma Expected Limit : ",
    print "Median +- 2 sigma Expected Limit"
    print "*data: x : y : y : y"
    print fancyTable(lines)      
    print "*dataend:"

###############################################################################


def write_histogram_table(datasets):

    lines = []

    dataset_line = "*qual: ."
    header = "*data: x"

    for dataset in datasets:
        dataset_line += " : " + dataset.legendEntry
        header += " : y"


    #use the first dataset to set x-axis bins
    testData = datasets[0].data
    nPoints = len(testData)
    for binIndex in range(nPoints):

        line = []

        # calculate bin limits
        binLow  = remove_trailing_zero(testData[binIndex].xValue - testData[binIndex].errorLeft)
        binHigh = remove_trailing_zero(testData[binIndex].xValue + testData[binIndex].errorRight)
        
        line.append(" " + str(binLow) + " TO " + str(binHigh) + ";")

        # get value and error for each dataset
        for dataset in datasets:
            datum = dataset.data[binIndex]

            # for data, just put the number of observed events
            if is_data(dataset.legendEntry):
                if datum.yValue > 0:
                    line.append(str(remove_trailing_zero(datum.yValue)) + ";")
                else:
                    line.append("-;")
            # for signal and background, match the precision of central value and error
            else:
                yError = remove_trailing_zero(set_sigfigs(datum.errorUp, NSIGFIGS))
                precision = get_precision(yError)
                yValue = remove_trailing_zero(round(datum.yValue,precision))
                if yValue > 0:
                    line.append(str(yValue) + " +- " + str(yError) + ";")
                else:
                    line.append("-;")

        lines.append(line)

    print dataset_line
    print header
    print fancyTable(lines)      
    print "*dataend:"

###############################################################################

def print_dataset_table(legend, datasetsToIgnore):

    lines = []
    line = ["legend entry","object name"]
    lines.append(line)
    line = ["------------","-----------"]
    lines.append(line)

    nDatasets = len(legend.GetListOfPrimitives())
    for index in range(nDatasets):

        legendEntry = legend.GetListOfPrimitives()[index]

        # get relevant info for this dataset
        label = legendEntry.GetLabel()
        object_ = legendEntry.GetObject()
        if object_:
            objectName = object_.GetName()
        else:
            objectName = "NOT FOUND"

        # decide whether to ignore this dataset
        ignore = False
        for dataset in datasetsToIgnore:
            if dataset in label or dataset in objectName:
                ignore = True
        if ignore:
            continue

        # add a line to the output table for this dataset
        line = []
        line.append(label)
        line.append(objectName)
        lines.append(line)

    print
    print fancyTable(lines)



###############################################################################

def get_ordered_legendEntries(legend, datasetsToIgnore, signalDatasets):

    nDatasets = len(legend.GetListOfPrimitives())

    data_datasets = []
    signal_datasets = []
    background_datasets = []

    # loop over datasets and sort by dataset type
    for index in range(nDatasets):

        legendEntry = legend.GetListOfPrimitives()[index]

        # get relevant info for this dataset
        label = legendEntry.GetLabel()
        object_ = legendEntry.GetObject()
        if object_:
            objectName = object_.GetName()
        else:
            objectName = "NOT FOUND"
    
        # decide whether to ignore this dataset
        ignore = False
        for dataset in datasetsToIgnore:
            if dataset in label or dataset in objectName:
                ignore = True
        if ignore:
            continue

        # check if it's data
        if is_data(label):
            data_datasets.append(legendEntry)
            continue

        # check if it's signal
        isSignal = False
        for dataset in signalDatasets:
            if dataset in label or dataset in objectName:
                isSignal = True
        if isSignal:
            signal_datasets.append(legendEntry)
            continue

        # if it's not data or signal, it's background
        background_datasets.append(legendEntry)
            
    # order them by type for output to a table
    return data_datasets + background_datasets + signal_datasets


###############################################################################

def is_data(label):
    if "data" in label.lower():
        return True
    else:
        return False

###############################################################################

def create_Dataset(legendEntry):

    # get relevant info for this dataset
    label = legendEntry.GetLabel()
    object_ = legendEntry.GetObject()

    if not object_:
        print "No object for legend entry '" + str(label) + "'" + ", skipping it"
        return

    className = object_.ClassName()
    name = object_.GetName()

    data = []
    if "TH1" in className:
        data = extractData_TH1(object_)
    elif "TF1" in className:
        data = extractData_TF1(object_)
    else:
        print
        print "'" + name + "' is of type '" + className + "'  ",
        print "This is not a supported object type, skipping it"
        print
        return

    if data:
        return Dataset(name, label, data)
    else:
        return

###############################################################################

# function to process the input file and extract the legend object
def extract_legend(inputFile):

    # run the input root macro and get the resulting canvas                                                                      
    if ".C" in inputFile:
        ROOT.gROOT.Macro(inputFile)
        canvas = ROOT.gROOT.GetListOfCanvases()[0]
    # get the first canvas from the input file                                                                                             
    elif ".root" in arguments.inputFile:
        inputFile = ROOT.TFile(inputFile)
        objectName = ROOT.gDirectory.GetListOfKeys()[0].GetName()
        canvas = inputFile.Get(objectName)
    else:
        print "invalid input file, quitting..."
        sys.exit(0)

    # see if there's a pad within the canvas                                                                                               
    padName = "NONE"
    for canvasItem in canvas.GetListOfPrimitives():
        name = canvasItem.GetName()
        className = canvasItem.ClassName()
        if "TPad" in canvasItem.ClassName():
            padName = canvasItem.GetName()
            break  # take first canvas we find (the top one)                                                                               
    if padName is not "NONE":
        holder = canvas.GetPrimitive(padName)
    else:
        holder = canvas

    # find legend
    for item in holder.GetListOfPrimitives():
        name = item.GetName()
        className = item.ClassName()
        if "TLegend" in className:
            legend = item
            break

    if legend:
        return legend
    else:
        print "no legend found, quitting..."
        sys.exit(0)        

###############################################################################
