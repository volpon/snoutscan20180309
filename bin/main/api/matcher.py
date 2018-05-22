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

def image_from_base64(data, type = None):
    return image_from_binary(base64.b64decode(data), type)

def image_from_binary(data, type = None):
    data = np.array(bytearray(data), dtype=np.uint8)
    return cv2.imdecode(data, 0)


class ImageFeatures(object):

    def __init__(self, features = None):
        if isinstance(features, bytes):
            self.decode(features)
        else:
            self.descriptors = None
        pass


    def from_image(self, image):
        '''
        Creates features with both keypoints and descriptors.
        '''
        
        #How many features to create, maximum:
        numFeaturesMax=500
        
        #How much to decimate iamges between levels
        scaleFactor=1.2
        
        #Number of pyramid levels.
        nLevels=8
        
        #The size of the border where the features are not detected.  
        #Should roughly match patchSize.
        edgeThreshold=31
        
        #THe definition of cv::ORB::HARRIS_SCORE as of v 3.4.0
        HARRIS_SCORE=0
        
        #The size of the patch to used in each layer to create the ORB descriptor.  This 
        #size on the smaller pyramid layers will cover more of the original image area.
        patchSize=31

        if (isinstance(image, str)):
            image = image_from_base64(bytes(image, "utf-8"))

        if (isinstance(image, bytes)):
            image = image_from_binary(image)

        # Initiate BRISK detector
        detector = cv2.BRISK_create()

        # Initiate ORB extractor
        descriptorExtractor = cv2.ORB_create(numFeaturesMax, scaleFactor, nLevels,
                                             edgeThreshold, 0, 2,  HARRIS_SCORE, patchSize)
        
        keypoints = detector.detect(image, None)
        keypoints, self.descriptors= descriptorExtractor.compute(image, keypoints)
        
        return (keypoints, self.descriptors)


    def encode(self):
        '''
        Encodes the descriptors only because the keypoints are difficult to pickle.
        '''

        memfile = io.BytesIO()
        pickle.dump(self.descriptors, memfile, protocol=pickle.HIGHEST_PROTOCOL)
        memfile.seek(0)

        serialized = memfile.read()

        return serialized

    def decode(self, serialized):
        '''
        Decodes the descriptors only because the keypoints are difficult to pickle.
        '''
        
        memfile = io.BytesIO(serialized)
        
        self.descriptors=pickle.load(memfile)

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
    
    def __init__(self, friendFeatureDescriptors, index_definition=None):
        '''
        Inputs:
            friendFeatureDescriptors    - The feature descriptors for all the friends, concatenated
                                          together.
            indexDefinition             - A string representing the faiss index setup to use, or ''
                                          or None to represent "use the default"

        Side-effects:
            self.FeatureMatcher is created and the friendFeatureDescriptors are added to it and 
                indexed.                                       
        '''     

        numFriendFeatures,numDimensions=friendFeatureDescriptors.shape
        
        #If it's not specified, provide a default:
        if index_definition is None or index_definition == '':
            index_definition='IVF2048,Flat'
        
        #Initialize the index:
        #self.featureMatcher = faiss.IndexIVFFlat(self.quantizer, numDimensions, nCells, faiss.METRIC_L2)
        self.featureMatcher = faiss.index_factory(numDimensions, index_definition)
        
        #Train our index using the data, so it can do an efficient job at adding it later:
        #(Techically, we just need to train on a set that has a similar distribution as what we'll 
        #be adding later, not the exact same data)
#        assert not self.featureMatcher.is_trained
        self.featureMatcher.train(friendFeatureDescriptors)
        assert self.featureMatcher.is_trained

        #Add our data:
        self.featureMatcher.add(friendFeatureDescriptors)
        print('      Total num features in  index: ', self.featureMatcher.ntotal, file=sys.stderr)
                                                        
    def match(self, subjectFeatureDescriptors, excludeFeatureMask):
        '''
        This function matches the given subject subjectImg with a given friend subjectImg based on 
        the features in friendFeatureDescriptors.
        
        Inputs:
            subjectFeatureDescriptors
                                    - The feature descriptors for the subject subjectImg. 
            excludeFeatureMask      - A binary mask of the same length as the number of friend 
                                      features that we have saying if each feature should be 
                                      excluded from being considered a match.

        @return percent
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
            
        print('      Found %i good_matches w/ subjectFeatureIds:\n      ' % len(matchDistList), 
              matchedQueryTrainIds[:,0], file=sys.stderr);
            
        return (matchedQueryTrainIds, matchDist)

class MatchResult(object):

    def __init__(self, name, image, match_score):

        self.name = name
        self.image = image
        self.match_score = match_score


    def saveImage(self, path):

        cv2.imwrite(path, self.image)


def find_best_matches(image_data, image_type, friends,  num_best_friends, f_ids_excluded,
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
        num_best_friends- n in the sentence "Find the n best matching friends that aren't excluded"
        f_ids_excluded  - A collection of the friend ids (indicies into friends) to not match with.
        indexDefinition - A string representing the faiss index setup to use, or ''
                          or None to represent "use the default"
        matcher         - An optional matcher that is already trained that we can use rather than
                          retraining one based on friends.
                              
    Outputs:
        best_indicies   - A list of indicies to the the num_best_friends closest matching friends.
                          Sorted in decending order by quality metric.
        match_scores    - The quality metric for each best friend, sorted in descending order.
        matcher         - a ImageMatcher that is made on the first query and can be reused if 
                          you want.  If it's given as an input, then it's output unchanged.
    '''
    
    #Take care of the default:
    if f_ids_excluded==None:
        f_ids_excluded=[]
    
    if image_data is None:
        return None, None

    subjectFeatures=ImageFeatures()
    
    #Make our features and keypoints.
    subjectFeatureKeypoints, subjectFeatureDescriptorsBytes=subjectFeatures.from_image(image_data)
    
    #Unpack the bytes now that we're about to use them:
    subjectFeatureDescriptors=np.unpackbits(subjectFeatureDescriptorsBytes,axis=1).astype('float32')
    
    #For each feature, this is the friend id it came from (index to friends):
    friendIdsList=[]
    
    #The descriptors for this feature:
    friendDescriptorsList=[]
        
    #####
    ##Loop through all of our friends and combine the feature data:
    #####
    for index in range(len(friends)):
        
        #Get this friend:
        friend=friends[index]

        #Make sure our friend photo has features:
        if friend.photo.featureDescriptors is None:
            print('Warning: Skipping a friend without features, %s.' % friend.name, 
                  file=sys.stderr);
            continue
        
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
                
    #Combine the lists together to make one array for the whole list of friends:
    friendIds=np.concatenate(friendIdsList)
    friendDescriptorsBytes=np.concatenate(friendDescriptorsList)
    #Convert f_ids_excluded to featureIdsExcluded:
    
    #Initialize a binary mask saying if we should exclude this feature:
    excludeFeatureMask=np.zeros((len(friendIds)), dtype=bool)
    
    for i in f_ids_excluded:
        #Add any to the mask that have value in friendIds equal to i:
        excludeFeatureMask=np.bitwise_or(excludeFeatureMask, friendIds==i)
            
    #Convert the byte representation to an array of bits:      
    friendDescriptors=np.unpackbits(friendDescriptorsBytes, axis=1).astype('float32')
    
    assert len(friendIds) == len(friendDescriptors) \
           and len(friendIds) == friendDescriptors.shape[0], 'These should be the same.'
    

    #If we don't already have a matcher, make one from the friendDescriptors:
    if matcher==None:    
        #Make a matcher object using our friend image features:
        matcher = ImageMatcher(friendDescriptors, index_definition)    

    #Using our subject-image based matcher, calculate how well it matches with this specific 
    # friend image.
    (matchedQueryTrainIds, matchDist) = matcher.match(subjectFeatureDescriptors, excludeFeatureMask)
    
    ##TODO:  convert matchedQueryTrainIds to which friends actually matched and how good the 
    #match was, best_indices, best_scores, sorted by score.
    
    #These are the friendIds of the best match feature of each subject feature:
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
        friendIdsSorted=[0]
        numMatchesSorted=[0]
    else:
        #Sort them in descending order by numMatches:
        friendIdsSorted=friendIdsMatched[howToSort]
        numMatchesSorted=numMatches[howToSort]
    
    #Return our list of best indicies to friends[] and their corresponding best scores:
    return friendIdsSorted, numMatchesSorted, matcher
    
    
def find_best_match(image_data, image_type, friends, index_definition=None, f_ids_excluded=None, matcher=None):
    '''
    This function finds the best match for image_data among a collection of friends, where
    each friend represents a photo of a dog, with accompanying metadata.
    
    See find_best_matches for a definition of the inputs and outputs.
    '''
    
    #Take care of the default:
    if f_ids_excluded is None:
        f_ids_excluded=[]

    #Find our best match:
    best_indices, match_scores, matcher=find_best_matches(image_data, image_type, friends, 
                                                          1, f_ids_excluded, 
                                                          index_definition, matcher)

    #Get our info for the bet matching friend:
    best_index=best_indices[0]
    best_score=match_scores[0]
    best_db_id=friends[best_index].id
    
    return best_db_id, best_score, best_index, matcher