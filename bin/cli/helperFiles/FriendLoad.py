from FriendMake import FriendMake

def FriendLoad(dogName, imgFilePath, g, tt):
    '''
    This function loads a single friend.
    
    Inputs:
        dogName         - The name of the dog for this image file.
        imgFilePath     - A string representing the path to the image we found.
        g               - Our global parameters.
        tt              - a TicToc() instance to use for output.
    '''
    TT=tt.TT

    with TT('Computing features for %s: %s' % (dogName, imgFilePath)):
        
        with open(imgFilePath, "rb") as imageFileHandle:
            #Load the image file data:
            imgFile=imageFileHandle.read()
        
        #Create a Friend object from it with the dog name connected to it.
        friend=FriendMake(dogName, imgFilePath, imgFile, g)
        
    #Return the resulting friend:
    return friend
