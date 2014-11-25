#!/usr/bin/env python

###############################################################################
###############################################################################
###############################################################################

# DEFINE POINT CLASS

###############################################################################

class Point(object):

    def __init__(self, xValue, yValue):
        # for TH1, xValue filled with bin center
        self.xValue = xValue
        self.yValue = yValue

    def __repr__(self):
        return 'x: %s, y: %s\n' % (self.xValue,
                                   self.yValue)

###############################################################################

# END DATUM CLASS

###############################################################################
###############################################################################
###############################################################################

# DEFINE DATUM CLASS

###############################################################################

class Datum(object):

    def __init__(self, xValue, yValue, errorDown, errorUp, errorLeft, errorRight):
        # for TH1, xValue filled with bin center
        self.xValue = xValue
        self.yValue = yValue
        # used similarly for both TH1 and TGraph objects
        self.errorDown = errorDown
        self.errorUp = errorUp
        # used to find bin edges in TH1, or as x-error in TGraph
        self.errorLeft = errorLeft
        self.errorRight = errorRight

    def __repr__(self):
        return 'x: %s + %s - %s  y: %s + %s - %s\n' % (self.xValue,
                                                       self.errorRight,
                                                       self.errorLeft,
                                                       self.yValue,
                                                       self.errorUp,
                                                       self.errorDown)

###############################################################################

# END DATUM CLASS

###############################################################################
###############################################################################
###############################################################################

# DEFINE DATASET CLASS

###############################################################################

class Dataset(object):

    def __init__(self, name, legendEntry, data):
        self.name = name
        self.legendEntry = legendEntry
        self.data = data  # will contain dict of Datum or Point objects (key = binNum)

    def __repr__(self):
        return ('\n%s: "%s"' % (self.name,
                                self.legendEntry)
                )

###############################################################################

# END DATASET CLASS

###############################################################################
###############################################################################
###############################################################################

# DEFINE FIGURE CLASS

###############################################################################


class Figure(object):
    def __init__(self, inputFile, xAxisLabel, yAxisLabel, datasetSeries):
        self.inputFile = inputFile
        self.xAxisLabel = xAxisLabel
        self.yAxisLabel = yAxisLabel
        self.datasetSeries = datasetSeries  # will contain a vector of Dataset objects

    def __repr__(self):
        return '\n%s' % (self.datasetSeries)

###############################################################################

# END FIGURE CLASS

###############################################################################
###############################################################################
###############################################################################

# DEFINE PAPER CLASS

###############################################################################


class Paper(object):
    def __init__(self, figureSeries):
        self.figureSeries = figureSeries  # will contain a vector of Figure objects

    def __repr__(self):
        return '\n%s' % (self.figureSeries)

###############################################################################

# END PAPER CLASS

###############################################################################
###############################################################################
###############################################################################
