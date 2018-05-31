#This file holds variables that are shared in many places, but do not varry.

import os
from os.path import expanduser

homeDir = expanduser("~")
snoutScanDir=homeDir + '/.snoutScan'

try:
    #Make sure the directory exists:
    os.mkdir(snoutScanDir)
except FileExistsError:
    #Don't worry if it already exists -that's fine.
    pass

#This file holds the last set of parameters we used (for repeatability):
savedParametersFile=snoutScanDir + '/lastParameters.pickle'
