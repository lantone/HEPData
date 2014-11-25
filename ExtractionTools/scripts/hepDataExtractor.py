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
from datetime import datetime

from hepDataClasses import *
from hepDataUtilities import *

import ROOT
#from ROOT import gROOT

ROOT.gROOT.SetBatch()

# command-line options

# -x "ignore": ignore a dataset
# -m mode [limit,histogram]
# -t test: returns a list of datasets in the figure (and a txt file)
# -i input file (output will have same file name with .txt extension)
# -d specify text file with input datasets to consider


# parse the command-line options
parser = OptionParser()
parser.add_option("-t", "--test",
                  action="store_true",
                  dest="runTest",
                  default=False,
                  help=("Returns a list of the datasets "
                        "included in a figure "
                        "and saves to '$inputFile_datasets.txt'")
                  )
parser.add_option("-i", "--inputFile",
                  dest="inputFile",
                  help="Specifies the input root macro or root file to use")
parser.add_option("-x", "--ignore",
                  dest="datasetsToIgnore",
                  action="append",
                  help=("Ignores dataset by legend entry. "
                        "Syntax for multiples is "
                        "'-x dataset1 -x dataset2' etc.")
                  )
parser.add_option("-s", "--signalDatasets",
                  dest="signalDatasets",
                  action="append",
                  help=("Tags dataset as signal by legend entry.. "
                        "Syntax for multiples is "
                        "'-s dataset1 -s dataset2' etc.")
                  )


(arguments, args) = parser.parse_args()

# initialize this so we can always look at it
if not arguments.datasetsToIgnore:
    arguments.datasetsToIgnore = []

# initialize this so we can always look at it
if not arguments.signalDatasets:
    arguments.signalDatasets = []

if not arguments.inputFile:
    print "\nPlease specify input file"
    print "\nExiting..."
    sys.exit(0)

NSIGFIGS = 2


###############################################################################
#
# BEGIN MAIN PROGRAM
#
###############################################################################

print str(datetime.now()),"starting"

# get the legend out of the input file
legend = extract_legend(arguments.inputFile)

# run test and exit if "-t" option included
if arguments.runTest:
    print_dataset_table(legend,arguments.datasetsToIgnore)
    sys.exit(0)

# create an ordered list (by dataset type) of all the datasets to include
ordered_datasets = get_ordered_legendEntries(legend,
                                             arguments.datasetsToIgnore,
                                             arguments.signalDatasets)


# for each dataset,
# extract the contents and create a "Dataset" object
datasets = []
for legendEntry in ordered_datasets:

    dataset = create_Dataset(legendEntry)
    if dataset:
        datasets.append(dataset)

write_histogram_table(datasets)


print str(datetime.now()), "finished running"


