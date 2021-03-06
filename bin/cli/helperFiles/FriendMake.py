from main.api.model import Profile, Friend, Photo
from sqlalchemy.orm.session import make_transient
from CachePersistent import CachePersistent

#TODO:  Update these:
friendMakingDependencies=['/.condaUser/app/main/api/model.py']


#@CachePersistent('/.snoutScanPersist/friendCache', friendMakingDependencies)
def FriendMake(friendName, imgFilePath, image, g):
    '''
    This function makes a Friend() given just a friendName, imageName, and an image.
    
    Inputs:
        friendName          - the name of the friend, an identifier.
        imgFilePath         - the full path to the file image, just so we can record it.
        image               - the image data itself.
        g                   - Our global constants.

    '''
    
    #Make the Photo:
    photo=Photo(g)
    
    #Make it so we don't save this in the database.
    make_transient(photo)
    
    #Add the image data and compute descriptors:
    photo.set_binary(image,'myType')
    
    #Make a profile:
    profile=Profile('andy@email.com', 'password', {'phone': '555-555-5555', 
                                                   'use_phone': False,
                                                   'use_msg': False})
    #Make it so we don't save this in the database.
    make_transient(profile)
    
    friend=Friend(profile, {'name'      : friendName,
                            'breed'     : imgFilePath,
                            'sex'       : 'Male',
                            'location'  : 'Minneapolis',
                            'staus'     : 'alive'
                                }, g)
    
    make_transient(friend)
    
    #Update our photo:
    friend.photo=photo
    
    return friend
