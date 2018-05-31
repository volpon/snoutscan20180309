from GlobalConstants import g as g_default
from main.api.matches_refine import matches_refine
import numpy as np
import pickle
import base64
import json
import sys
import cv2
import io
import os

#A search of nearest neighbor search implementations brings me to this page:
#https://www.benfrederickson.com/approximate-nearest-neighbours-for-recommender-systems/
#They recommend hnsw from nmslib as the best performant, but it's poorly documented and the 
#bit_hamming search didn't seem to be compatible with any datatypes or formats.

#Faiss is created and used by facebook, and is the second fastest/accurate one available according 
#to that benchmark
import faiss

def image_from_base64(data, g, type = None):
    '''
    This function takes base64 encoded version of the binary contents of an image file, converts
    it to binary, and reads the image file into a numpy array representing the image.
    '''
    return image_from_binary(base64.b64decode(data), g, type)

def image_from_binary(data, g, type = None):
    '''
    This function reads the data from an image file and loads it into a grayscale numpy array
    representing the image.
    '''
    data = np.array(bytearray(data), dtype=np.uint8)
    return cv2.imdecode(data, g.colorNotGrayscale)


class ImageFeatures(object):
    g=None

    def __init__(self, g, features = None):
        if isinstance(features, bytes):
            self.decode(features)
        else:
            self.descriptors = None
            self.keypoints = None
            
        self.g=g


    def _keypoints_package(self, keypoints):
        '''
        This function packages a collection of keypoints into something we can pickle successfully.
        '''
        return [ (
                      k.pt, 
                      k.size,
                      k.angle, 
                      k.response, 
                      k.octave, 
                      k.class_id,
                  ) for k in keypoints ]
    
    def _keypoints_unpackage(self, keypoints_packaged):
        '''
        This function takes a collection of packaged keypoints as made by _keypoints_packaged
        and sets up valid keypoints again from them.
        '''
        
        return [ cv2.KeyPoint(x=k_pack[0][0],
                              y=k_pack[0][1],
                              _size=k_pack[1], 
                              _angle=k_pack[2], 
                              _response=k_pack[3],
                              _octave=k_pack[4],
                              _class_id=k_pack[5]) for k_pack in keypoints_packaged ]
    
    

    def from_image(self, imageFile, g):
        '''
        Creates features with both keypoints and descriptors from the binary data of an image file.
        
        Inputs:
            imageFile     - Either a binary array of the bytes in the image file or a base64 
                            encoded version of this.
        '''
        
        #This is the height we resize all images to:
        imgHeight=int(1000)
      
        #How many features to create, maximum:
        numFeaturesMax=8000
        
        #How much to decimate iamges between levels
        scaleFactor=1.2
        
        #Number of pyramid levels.
        nLevels=8
        
        #The size of the border where the features are not detected.  
        #Should roughly match patchSize.
        edgeThreshold=31
        
        #The definition of cv::ORB::HARRIS_SCORE as of v 3.4.0
        HARRIS_SCORE=0
        
        #The size of the patch to used in each layer to create the ORB descriptor.  This 
        #size on the smaller pyramid layers will cover more of the original image area.
        patchSize=31

        #Decode the image into binary form:
        if (isinstance(imageFile, str)):
            image = image_from_base64(bytes(imageFile, "utf-8"), self.g)
        elif (isinstance(imageFile, bytes)):
            image = image_from_binary(imageFile, self.g)
        else:
            assert False, 'Should have image from one of those cases by now.'
        
        #Get our original dimensions:
        (origHeight,origWidth, *_)=image.shape
        
        #Get the width we need to get the height we want:
        imgWidth=int(round(imgHeight*origWidth/origHeight))                        
        
        #Resize so the height is imgHeight.
        imgResized = cv2.resize(image, (imgWidth,imgHeight),
                                    interpolation = cv2.INTER_CUBIC)
        
        # Initiate ORB extractor
        featureExtractor = cv2.ORB_create(numFeaturesMax, scaleFactor, nLevels,
                                             edgeThreshold, 0, 2,  HARRIS_SCORE, patchSize)
        
        #Detect the keypoints:
        self.keypoints = featureExtractor.detect(imgResized, None)
        
        
        #Create the descriptors around each keypoint:
        self.keypoints, self.descriptors= featureExtractor.compute(imgResized, 
                                                                      self.keypoints)        
        return (self.keypoints, self.descriptors)


    def encode(self):
        '''
        Encodes the keypoints and descriptors.
        '''

        memfile = io.BytesIO()
        
        #Dump the descriptors to the memfile:
        pickle.dump((self._keypoints_package(self.keypoints), 
                     self.descriptors),
                    memfile, protocol=pickle.HIGHEST_PROTOCOL)
        
        #Read the file back:
        memfile.seek(0)
        serialized = memfile.read()

        return serialized

    def decode(self, serialized):
        '''
        Decodes the descriptors only because the keypoints are difficult to pickle.
        '''
        
        memfile = io.BytesIO(serialized)
        
        #Load the file:
        (keypoints_packaged, self.descriptors)=pickle.load(memfile)
        
        #Unpackage our keypoints:
        self.keypoints=self._keypoints_unpackage(keypoints_packaged)

class ImageMatcher(object):
    '''
    This class is used to match the features from a subject image to features for another friend.
    
    
    '''

    #Anything with a matching distance less than this is considered a candidate for a  "good match".
    matchDistanceThreshold=40
    
    #This is the ratio of the best match distance to second best match distance that also defines
    # what a "good match" is.  Any best matches that have a distance ratio less than this and also
    #have a distance less than matchDistanceThreshold are considered good matches:
    bestToSecondBestDistRatio=.7
    
    def __init__(self, friendFeatureDescriptors, g, index_definition=None,):
        '''
        Inputs:
            friendFeatureDescriptors    - The feature descriptors for all the friends, concatenated
                                          together.
            indexDefinition             - A string representing the faiss index setup to use, or ''
                                          or None to represent "use the default"
                                          
            g                      - Our global constants.


        Side-effects:
            self.FeatureMatcher is created and the friendFeatureDescriptors are added to it and 
                indexed.                                       
        '''     

        numFriendFeatures,numDimensions=friendFeatureDescriptors.shape
        
        #If it's not specified, provide a default:
        if index_definition is None or index_definition == '':
            index_definition='IVF2048,Flat'
        
        #Initialize the index:
        self.featureMatcher = faiss.index_factory(numDimensions, index_definition)
        
        #Train our index using the data, so it can do an efficient job at adding it later:
        #(Techically, we just need to train on a set that has a similar distribution as what we'll 
        #be adding later, not the exact same data)
        self.featureMatcher.train(friendFeatureDescriptors)
        assert self.featureMatcher.is_trained

        #Add our data:
        self.featureMatcher.add(friendFeatureDescriptors)
        with TT('      Total num features in  index: %i' % self.featureMatcher.ntotal):
            pass
                                                        
    def match(self, subjectFeatureDescriptors, excludeFeatureMask, g):
        '''
        This function matches the given subject subjectImg with a given friend subjectImg based on 
        the features in friendFeatureDescriptors.
        
        Inputs:          
            subjectFeatureDescriptors
                                    - A collection of numFeatures feature descriptors for the 
                                      subject subjectImg. 
                                      
            excludeFeatureMask      - A binary mask of the same length as the number of friend 
                                      features that we have saying if each feature should be 
                                      excluded from being considered a match.
                                      
            g                       - Our global constants.

                                      
        Outputs:
            matchedQueryTrainIds    - A numMatches x 2 np array of featureIds, where each row=(a,b)
                                      shows that the a_th feature of the subject image matched the
                                      b_th feature in the array of friend features.
            matchDist               - A np vector of length numMatches specifying the distance 
                                      metric fort each match.
            
        '''
        
        #How many of the best friend features to search for in order to get 2 that are not excluded
        # by excludeFeatureMask:
        numBestFeaturesToFind=40;
        
        #How many subject features we have:
        nSubFeatures=subjectFeatureDescriptors.shape[0]
        
        # For each of the subject image features, find the closest feature descriptor in the 
        #friend image:
        #Arguments: queryDescriptors, k)
        #Return them as a (numSubjectFeatures x k) matrix of distances and ids, 
        # with rows sorted in increasing distance
        distances,ids =self.featureMatcher.search(subjectFeatureDescriptors, numBestFeaturesToFind);
        
        #Convert excludeFeatureMask to a array of Ids to exclude:
        excludeFriendFeatureIds=np.where(excludeFeatureMask)[0]
        
        #The subject feature id and friends feature ids of "good matches"
        matchedQueryTrainIdList=[]
        #Their corresponding distance:
        matchDistList=[]
        
        # Check to make sure that the best match is at least 1/self.bestToSecondBestDistRatio
        # as close as the second best match, and only use those:
        for i in range(nSubFeatures):
            
            #Iterate over our subject matches and find the first one that isn't in 
            # excludeFriendFeatureIds, and call it bestFriendMatchId
            for bestFriendMatchId in range(numBestFeaturesToFind-1):
                subjectFeatureId=ids[i,bestFriendMatchId]
                
                #Break when we have the first one not excluded:
                if subjectFeatureId not in excludeFriendFeatureIds:
                    break
            
            #Search for the second best subject id that isn't in our excludeFeatureFriendsId:
            for secondBestFriendMatchId in range(bestFriendMatchId+1,numBestFeaturesToFind):
                subjectFeatureId=ids[i,secondBestFriendMatchId]
                #Break when we have the first one not excluded:
                if subjectFeatureId not in excludeFriendFeatureIds:
                    break
                
                assert secondBestFriendMatchId != numBestFeaturesToFind-1, \
                    'All matching subject features are excluded. Increase numBestFeaturesToFind.'
            
            #Get what we need from the results:
            bestSubFeatMatchId=ids[i,bestFriendMatchId]
            bestMatchDist=distances[i,bestFriendMatchId]
            secondBestDist=distances[i,secondBestFriendMatchId]

            #Do the ratio test:
            if (    bestMatchDist < self.bestToSecondBestDistRatio*secondBestDist \
                    and bestMatchDist<self.matchDistanceThreshold):
                
                #Then, add the subject feature and friend feature to our "best matches" lists:
                matchedQueryTrainIdList.append((i,bestSubFeatMatchId));
                matchDistList.append(bestMatchDist)
                

        #A special case for when there aren't any matches:
        if len(matchedQueryTrainIdList)==0:
            matchedQueryTrainIds=np.zeros((0,2), dtype='int')
            matchDist=np.zeros((0), dtype='float32')
        else:
            #Just convert the lists to np arrays:
            matchedQueryTrainIds=np.array(matchedQueryTrainIdList)
            matchDist=np.array(matchDistList)
                        
        return (matchedQueryTrainIds, matchDist)

class MatchResult(object):

    def __init__(self, name, image, match_score):

        self.name = name
        self.image = image
        self.match_score = match_score

    def saveImage(self, path):

        cv2.imwrite(path, self.image)

def find_best_matches(image_data, image_type, friends, max_best_friends, g=None, f_ids_excluded=None,
                      index_definition=None, matcher=None):
    '''
    This function finds the <num_best_friends> best matches for image_data among a collection of 
    friends (excluding the ones indexed by f_ids_excluded ), where each friend represents 
    a photo of a dog, with accompanying metadata.
    
    Inputs:
        image_data      - the subject image data, in numpy format.
        image_type      - Not currently used.
        friends         - A collection of Friend() objects representing the pictures the given image
                          could match to.
        max_best_friends- n in the sentence "Find at most n best matching friends that aren't 
                          excluded"
        g               - Our global constants, or None if we should load the defaults.
        f_ids_excluded  - A collection of the friend ids (indicies into friends) to not match with.
        indexDefinition - A string representing the faiss index setup to use, or ''
                          or None to represent "use the default"
        matcher         - An optional matcher that is already trained that we can use rather than
                          retraining one based on friends.
                              
    Outputs:
        best_indicies   - A list of indicies to the the num_best_friends closest matching friends.
                          Sorted in decending order by quality metric.
        pctSubjectFeaturesMatchedToFriend
                        - The quality metric for each best friend, sorted in descending order.
                          Specifically, it's the percent of the subject features that are matched
                          to each friend image.  A list.
        matcher         - a ImageMatcher that is made on the first query and can be reused if 
                          you want.  If it's given as an input, then it's output unchanged.
    '''
    
    #Take care of the default:
    if f_ids_excluded is None:
        f_ids_excluded=[]
    
    if image_data is None:
        return None, None
    
    #If we don't have a g.  Load the defualts from our best optimization run so far:
    if g is None:
        g=g_default

    assert len(friends) >=1, 'Must have at least one friend to match with.'

    subjectFeatures=ImageFeatures(g)
    
    #Make our features and keypoints.
    subjectFeatureKeypoints, subjectFeatureDescriptorsBytes=subjectFeatures.from_image(image_data,g)
    
    #Extract our subject feature coordinates from the keypoints:
    subjectKPPos=np.array([ (kp.pt[0], kp.pt[1]) for kp in subjectFeatureKeypoints])
    
    #Unpack the bytes now that we're about to use them:
    subjectFeatureDescriptors=np.unpackbits(subjectFeatureDescriptorsBytes,axis=1).astype('float32')
    
    numSubjectFeatures=subjectFeatureDescriptors.shape[0]
    
    #For each feature, this is the friend id it came from (index to friends):
    friendIdsList=[]
    
    #The descriptors for this feature:
    friendDescriptorsList=[]
    
    #This array holds the keypoint positions of the friends (x,y):
    friendKPPosList=[]
        
    #####
    ##Loop through all of our friends and combine the feature data:
    #####
    for index in range(len(friends)):
        
        #Get this friend:
        friend=friends[index]
        
        fPhoto=friend.photo

        #If our friend doesn't have featureDescriptors yet, then decode them:
        if fPhoto.featureDescriptors is None:
            
            #Decode our features:
            fPhoto.set_binary(fPhoto.data, fPhoto.type)

        if fPhoto.featureDescriptors is None:
            with TT('Warning:  Found a friend without featureDescriptors!'):
                pass
                    
        #Get our features
        friendFeatureKeypoints=friend.photo.featureKeypoints
        friendFeatureDescriptors=friend.photo.featureDescriptors
        
        numFeatures=len(friendFeatureDescriptors)
        
        assert numFeatures == len(friendFeatureKeypoints), \
            'The number of keypoints and descriptors should be equal.'
        
        #Add our indices to the list:
        friendIdsList.append(np.full(numFeatures,index))
        
        #Add our descriptors to the list:
        friendDescriptorsList.append(friendFeatureDescriptors)
        
        friendKPPosList.append([(kp.pt[0], kp.pt[1]) for kp in friendFeatureKeypoints])
                
    #Combine the lists together to make one array for the whole list of friends:
    friendIds=np.concatenate(friendIdsList)
    friendDescriptorsBytes=np.concatenate(friendDescriptorsList)
    friendKPPos=np.vstack(friendKPPosList)
    
    #Convert f_ids_excluded to featureIdsExcluded:
    
    #Initialize a binary mask saying if we should exclude this feature:
    excludeFeatureMask=np.zeros((len(friendIds)), dtype=bool)
    
    for i in f_ids_excluded:
        #Add any to the mask that have value in friendIds equal to i:
        excludeFeatureMask=np.bitwise_or(excludeFeatureMask, friendIds==i)
            
    #Convert the byte representation to an array of bits:      
    friendDescriptors=np.unpackbits(friendDescriptorsBytes, axis=1).astype('float32')
    
    assert len(friendIds) == len(friendDescriptors) \
            and len(friendDescriptors) == friendKPPos.shape[0] \
            and len(friendIds) == friendDescriptors.shape[0], 'These should be the same.'
    

    #If we don't already have a matcher, make one from the friendDescriptors:
    if matcher==None:    
        #Make a matcher object using our friend image features:
        matcher = ImageMatcher(friendDescriptors, g, index_definition)    

    #Using our subject-image based matcher, calculate how well it matches with this specific 
    # subject image.
    (matchedQueryTrainIds, matchDist) = matcher.match(subjectFeatureDescriptors, 
                                                      excludeFeatureMask,g)
    
    with TT('Found %i matches based on ratio test.' % len(matchDist)): pass
    
    #Further filter these matches using our geometric constraints:
    (matchedQueryTrainIds, matchDist)=matches_refine( subjectKPPos,
                                                      friendKPPos, 
                                                      friendIds,
                                                      matchedQueryTrainIds, 
                                                      matchDist, g)  

    with TT('Filtered to %i matches using RANSAC.' % len(matchDist)): pass
    
    #These are the friendIds of the best-matched feature of each subject feature:
    friendIdsOfBestMatch=friendIds[matchedQueryTrainIds[:,1]]
    
    #This is the unique set of friendIds represented in this set, and the number of features 
    #matches that correspond to that friend:
    [friendIdsMatched, numMatches]=np.unique(friendIdsOfBestMatch, return_counts=True)
    
    #Return a list of indicies saying how we would sort numMatches in descending order:
    howToSort=np.flip(np.argsort(numMatches),0)
    
    ##TODO:  This would be a good place to display some info about what's matching and what isn't
    # but we would need the friend names and maybe file names for that to make sense.
    
    #Make sure we return at least one as "best", even if it's a sucky one with 0 confidence:    
    if len(howToSort) == 0:
        friendIdsSorted=np.array([0])
        numMatchesSorted=np.array([0])
    else:
        #Sort them in descending order by numMatches:
        friendIdsSorted=friendIdsMatched[howToSort]
        numMatchesSorted=numMatches[howToSort]
        
    #Convert to a percent:
    pctSubjectFeaturesMatchedToFriend=numMatchesSorted/numSubjectFeatures
    
    #Make sure we only return at most max_best_friends results:
    friendIdsSorted=friendIdsSorted[:max_best_friends].tolist()
    pctSubjectFeaturesMatchedToFriend=pctSubjectFeaturesMatchedToFriend[:max_best_friends].tolist()
    
    #Convert to database ids:
    bestFriendDbIdsSorted=[ friends[friendId].id for friendId in friendIdsSorted ]
    
    #Return our list of best indicies to friends[] and their corresponding best scores:
    return bestFriendDbIdsSorted, pctSubjectFeaturesMatchedToFriend, friendIdsSorted, matcher
    
    
def find_best_match(image_data, image_type, friends, g=None, index_definition=None, f_ids_excluded=None, 
                    matcher=None):
    '''
    This function finds the best match for image_data among a collection of friends, where
    each friend represents a photo of a dog, with accompanying metadata.
    
    See find_best_matches for a definition of the inputs and outputs.
    '''
    
    #Take care of the default:
    if f_ids_excluded is None:
        f_ids_excluded=[]

    #Find our best match:
    best_db_ids_sorted, percentMatched, friend_ids, matcher=\
        find_best_matches(image_data, image_type, friends, 1, g, f_ids_excluded, index_definition, 
                          matcher)

    #Get our info for the bet matching friend:
    best_db_id=best_db_ids_sorted[0]
    percentOfSubjectFeaturesMatched=percentMatched[0]
    friend_id=friend_ids[0]
    
    return best_db_id, percentOfSubjectFeaturesMatched, friend_id, matcher