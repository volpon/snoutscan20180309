import argparse
import os
from LeafDirsInTreeFind import LeafDirsInTreeFind

def ArgsParse():
    '''Parse arguments and provide help text if something is wrong.'''
    
    #The directory with this file in it:
    thisDir=os.path.dirname(os.path.realpath(__file__))
    
    progDescription='''This is a command line interface for the matcher API.  It takes a set of
                        directories named after dogs with individual image files in them as the 
                        argument.  The dog names are used as labels for the images.'''
        
    parser = argparse.ArgumentParser(description=progDescription,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('dauDataTreeRoot', action='store', nargs='+',
                        help='''This specifies the root directory of one or more directory trees
                                whose leaf nodes are directories named after the individual dogs
                                with image files for that dog in that directory.
                                ''')
    
    #Get our arguments:
    args=parser.parse_args()
    
    #The list of directories with friend images in them:
    args.friendDirectories=LeafDirsInTreeFind(args.dauDataTreeRoot)
    
    assert len(args.friendDirectories) >1, 'Not enough leaf directories found in dauDataTreeRoot.'
        
    return args