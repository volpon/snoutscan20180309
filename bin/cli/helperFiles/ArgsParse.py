import argparse
import os
from LeafDirsInTreeFind import LeafDirsInTreeFind

def ArgsParse():
    '''Parse arguments and provide help text if something is wrong.'''
    
    #The directory with this file in it:
    thisDir=os.path.dirname(os.path.realpath(__file__))
    
    progDescription='''This is a command line interface for the matcher API.  It takes a set of
                        directories named after dogs with individual image files in them as the 
                        argument.  The dog names are used as labels for the images.
                        
                        It matches each image shown with all of the other images (not including 
                        itself), and calculates the best match for each one.  It then outputs 
                        a confusion matrix on stdout specifying how many images of each dog name
                        were matched with images of every other dog name.'''
        
    parser = argparse.ArgumentParser(description=progDescription,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('dauDataTreeRoot', action='store', nargs='+',
                        help='''This specifies the root directory of one or more directory trees
                                whose leaf nodes are directories named after the individual dogs
                                with image files for that dog in that directory.
                                ''')
    
    parser.add_argument('-i','--indexDefinition', action='store', metavar='indexDefinition',
                      default='',
                      help='''A string representing the faiss index defintion. 
                      If specified, it overrides the default (for benchmarking 
                      different indicies).''')

    parser.add_argument('-o','--optimizeHyperparameters', action='store_true',                 
                        help='''This mode runs the benchmark repeatedly with different selections 
                                of hyperparameters and optimizes an objective function to find the
                                best combination of accuracy and speed.
                                ''')
    
    #Get our arguments:
    args=parser.parse_args()
    
    #The list of directories with friend images in them:
    args.friendDirectories=LeafDirsInTreeFind(args.dauDataTreeRoot)
    
    assert len(args.friendDirectories) >1, 'Not enough leaf directories found in dauDataTreeRoot.'
        
    return args