from FriendMake import FriendMake

def FriendLoad(friendLoadArgs):
    '''
    This function loads a single friend.
    
    Inputs:
        friendLoadArgs  - A tuple of (dogName, imgFilePath, g) where:
            dogName         - The name of the dog for this image file.
            imgFilePath     - A string representing the path to the image we found.
            g               - Our global parameters.
    '''

    #Load parameters:
    (dogName, imgFilePath, g)=friendLoadArgs

    with open(imgFilePath, "rb") as imageFileHandle:
        #Load the image file data:
        imgFile=imageFileHandle.read()
    
    #Create a Friend object from it with the dog name connected to it.
    friend=FriendMake(dogName, imgFilePath, imgFile, g)
    
    #Return the resulting friend:
    return friend
