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


from HEPData.ExtractionTools.hepDataClasses import *
from HEPData.ExtractionTools.hepDataUtilities import *

import ROOT

ROOT.gROOT.SetBatch()

# parse the command-line options
parser = OptionParser()
parser.add_option("-i", "--inputFile",
                  dest="inputFile",
                  help="Specifies the input root macro to use")
parser.add_option("-t", "--test",
                  action="store_true",
                  dest="runTest",
                  default=False,
                  help=("Returns a list of the datasets "
                        "included in a figure ")
                  )
parser.add_option("-x", "--ignore",
                  dest="datasetsToIgnore",
                  action="append",
                  help=("Ignores dataset by legend entry. "
                        "Syntax for multiples is "
                        "'-x dataset1 -x dataset2' etc.")
                  )
parser.add_option("-l", "--legendEntry",
                  dest="legendEntries",
                  action="append",
                  help=("Specifies order of datasets in legend. "
                        "Options are 'signal','obs','exp','1sigma','2sigma'. "
                        "Syntax for multiples is "
                        "'-l dataset1 -l dataset2' etc.")
                  )
parser.add_option("-s", "--swapAxes", action="store_true", dest="swapAxes", default=False,
                  help="signifies a plot in which the x value is the dependent variable")

(arguments, args) = parser.parse_args()

if not arguments.inputFile:
    print "\nPlease specify input file"
    print "\nExiting..."
    sys.exit(0)
if not arguments.legendEntries and not arguments.runTest:
    print "\nPlease specify legend order"
    print "\nExiting..."
    sys.exit(0)

# initialize this so we can always look at it
if not arguments.datasetsToIgnore:
    arguments.datasetsToIgnore = []


###############################################################################
#
# BEGIN MAIN PROGRAM
#
###############################################################################

# get the legend out of the input file
legend = extract_legend(arguments.inputFile)

#legend_order = ["signal","obs","exp","1sigma","2sigma"]
legend_order = arguments.legendEntries

# run test and exit if "-t" option included
if arguments.runTest:
    print_dataset_table(legend,arguments.datasetsToIgnore)
    sys.exit(0)

datasets = {}

nDatasets = len(legend.GetListOfPrimitives())
for index in range(nDatasets):

    name = legend_order[index]

    legendEntry = legend.GetListOfPrimitives()[index]
    label = legendEntry.GetLabel()

    object_ = legendEntry.GetObject()
    className = object_.ClassName()

    data = []
    if "TGraphAsymmErrors" in className:
        data = extractData_TGraphAsymmErrors(object_)
    elif "TGraph" in className:
        data = extractData_TGraph(object_)
    elif "TPolyLine" in className:
        data = extractData_TGraph(object_)
    elif "TF1" in className:
        data = extractData_TF1(object_)
    else:
        print "'" + name + "' is of type '" + className + "'  ",
        print "This is not a supported object type, skipping it"
        print
        continue


    if not data:
        continue

    # swap the x and y values
    if arguments.swapAxes:
        swapped_data = []
        for datum in data:
            if hasattr(datum, 'errorLeft'):
                swapped_data.append(Datum(datum.yValue,
                                          datum.xValue,
                                          datum.errorLeft,
                                          datum.errorRight,
                                          datum.errorDown,
                                          datum.errorUp))
            else:
                swapped_data.append(Point(datum.yValue,
                                          datum.xValue))

        data = swapped_data

    # situation is normal, just write the dataset
    if data[0].xValue != data[-1].xValue:
        datasets[name] = Dataset(name, label, data)

    # if we have a loop for the shaded bands, split them into + & -
    else:
        firstHalf = []
        secondHalf = []
        for index in range(len(data)):
            if index < len(data)/2:
                firstHalf.append(data[index])
            else:
                secondHalf.append(data[index])                

        secondHalf.reverse()

        # add the plus and minus datasets separately
        if firstHalf[0].yValue < secondHalf[0].yValue:
            datasets["minus"+name] = Dataset("minus"+name, label, firstHalf)
            datasets["plus"+name] = Dataset("plus"+name, label, secondHalf)
        else:
            datasets["plus"+name] = Dataset("plus"+name, label, firstHalf)
            datasets["minus"+name] = Dataset("minus"+name, label, secondHalf)


        



for dataset in datasets:
    print datasets[dataset].name
    print datasets[dataset].data

if datasets:
    write_limit_table(datasets)



