import argparse
import os

def ArgsParse():
    '''Parse arguments and provide help text if something is wrong.'''
    
    #The directory with this file in it:
    thisDir=os.path.dirname(os.path.realpath(__file__))
    
    progDescription='''This program...'''
        
    parser = argparse.ArgumentParser(description=progDescription,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    #parser.add_argument('-t','--train', action='store_true',
                        #help='''Use the program in training mode.''')
    
    #parser.add_argument('-j','--numJobs', action='store', type=int, metavar='numJobs',
                      #default='-1',
                      #help='''How many compuation jobs to start in parallel.''')
    
    #parser.add_argument('dauDataTreeRootOrDir', action='store', nargs='+',
                        #help='''This specifies a set of dauCapture-created directories to process.
                                #Each of the specified directories is searched recursively for 
                                #subdirectories and each leaf directory is interpreted as a data 
                                #directory.  Each data directory represents a single card and has 
                                #a sequence of numerically-numbered images in it starting at 00.png, 
                                #and (if in training mode) a graded.csv file in it with exactally 
                                #two lines (a header line, and a data line) specifying the opinion 
                                #of the card appraiser for this card.''')
    
    #Get our arguments:
    args=parser.parse_args()
    
    return args