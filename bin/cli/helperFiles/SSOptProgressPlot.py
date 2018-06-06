#This allows us to make plots without an xwindows connection:
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

import os
import numpy as np
from matplotlib.patches import Rectangle
from shared import snoutScanDir

def SSOptProgressPlot(compositeCosts, costsFromAccuracy, costsFromTime):
    '''
    This function plots our progress through SSOptimize.
    
    Inputs:
        compositeCosts                  
        costsFromAccuracy 
        costsFromTime                   - Lists of data to plot vs iteration number.
    '''
    
    try:
        #Check to see if we've made a figure yet.  If we haven't, make one.
        if not hasattr(SSOptProgressPlot, 'figure'):
            SSOptProgressPlot.figure=plt.figure()

        #Make sure the right figure is activated:
        fig=plt.figure(SSOptProgressPlot.figure.number)
        
        costsFromAccuracyColor='yellow'
        costsFromTimeColor='green'

        sp=plt.stackplot(range(len(compositeCosts)), costsFromAccuracy, costsFromTime,
                        colors=[costsFromAccuracyColor, costsFromTimeColor])
        plt.title('Costs vs iteration.')
        
        #This is a work-around to get the legend to work:
        # https://stackoverflow.com/questions/14534130/legend-not-showing-up-in-matplotlib-stacked-area-plot
        legendProxies = []
        for poly in sp:
            legendProxies.append(plt.Rectangle((0, 0), 1, 1, fc=poly.get_facecolor()[0]))

        #Make a legend:
        plt.legend(legendProxies, ['costsFromAccuracy', 'costsFromTime'])

        #Set the yaxis to ignore the outliers so one big spike doesn't make the rest of the graph tiny.
        #plt.axis(ymax=np.percentile(compositeCosts, 95), ymin=0)

        #Get the file name to save to:
        progressPlotFile=os.path.join(snoutScanDir, 'progress.png')
    
        #Save the figure rather than displaying it:
        plt.savefig(progressPlotFile, dpi=150)
        
        ##Display the figure (If we're not using the AGG backend)
        #plt.show(block=False)
        #plt.pause(.1)
    except:
        pass