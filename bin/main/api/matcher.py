import numpy as np
import pickle
import base64
import json
import sys
import cv2
import io
import os

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

        if (isinstance(image, str)):
            image = image_from_base64(bytes(image, "utf-8"))

        if (isinstance(image, bytes)):
            image = image_from_binary(image)

        # Initiate BRISK detector
        detector = cv2.BRISK_create()

        # Initiate BRIEF extractor
        descriptorExtractor = cv2.ORB_create()

        keypoints = detector.detect(image, None)
        keypoints, self.descriptors = descriptorExtractor.compute(image, keypoints)
              
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
    
    def __init__(self, friendFeatureDescriptors):
        '''
        Inputs:
            friendFeatureDescriptors    - The feature descriptors for all the friends, concatenated
                                          together.

        Side-effects:
            self.FeatureMatcher is created and the friendFeatureDescriptors are added to it and 
                indexed.                                       
        '''
      
        # FLANN parameters:
        #A constant that means to use the Locally sensitive hashing distance metric:
        FLANN_INDEX_LSH = 6
        indexParams= dict(algorithm = FLANN_INDEX_LSH,
                           table_number = 6, # 12
                           key_size = 12,     # 20
                           multi_probe_level = 1) #2
        searchParams = dict(checks=50)   # or pass empty dictionary

        #index_params,search_params
        self.featureMatcher = cv2.FlannBasedMatcher(indexParams,searchParams)
        
        self.featureMatcher.clear()
        
        #Add the stuff we want to index:
        self.featureMatcher.add(friendFeatureDescriptors)
        
        import pdb; pdb.set_trace()
        
        #Train the tree:
        self.featureMatcher.train()
                
    def match(self, subjectFeatureDescriptors):
        '''
        This function matches the given subject subjectImg with a given friend subjectImg based on 
        the features in friendFeatureDescriptors.
        
        Inputs:
            subjectFeatureDescriptors
                                    - The feature descriptors for the subject subjectImg.        
        @return percent
        '''
        
        # For each of the subject image features, find the closest feature descriptor in the 
        #friend image:
        #Arguments: queryDescriptors, k)
        #Find the top two matches in the whole training dataset for each descriptor in 
        #subjectFeatureDescriptors, and return them as rows of a list of lists:
        matches = self.featureMatcher.knnMatch( subjectFeatureDescriptors, k=2 );
        
        good_matches=[]
        # Check to make sure that the best match is at least 1/.7 as close as the second best
        # match, and only use those:
        
        for matchPair in matches:
            
            if len(matchPair) ==2:
                #Divvy them out:
                (bestMatch,secondBestMatch) =matchPair
            elif len(matchPair) ==1:
                #Then we only had one match - assume it's good.
                good_matches.append(matchPair[0]);
                continue
            elif len(matchPair)==0:
                continue
            else:
                assert 0, 'Should not be getting this number of matches back: %i' % len(matchPair) 
            
            #Do the ratio test:
            if (    bestMatch.distance < self.bestToSecondBestDistRatio*secondBestMatch.distance \
                    and bestMatch.distance<self.matchDistanceThreshold):
                good_matches.append(bestMatch);
                
        print('      Found %i good_matches' % len(good_matches), file=sys.stderr);

        ######
        #Convert to a list of matching indicies so that what calls this doesn't need to know about 
        # the DMatch  datatype.
        
        matchedQueryTrainIds=np.array([ (m.queryIdx, m.trainIdx) for m in good_matches])
        
        #The distance metric for each match:
        matchDist=np.array([ m.distance for m in good_matches])
              
        return (matchedQueryTrainIds, matchDist)

class MatchResult(object):

    def __init__(self, name, image, percent):

        self.name = name
        self.image = image
        self.percent = percent


    def saveImage(self, path):

        cv2.imwrite(path, self.image)


def find_best_matches(image_data, image_type, friends, num_best_friends):
    '''
    This function finds the <num_best_friends> best matches for image_data among a collection of 
    friends, where each friend represents a photo of a dog, with accompanying metadata.
    
    Inputs:
        image_data      - the subject image data, in numpy format.
        image_type      - Not currently used.
        friends         - A collection of Friend() objects representing the pictures the given image
                          could match to.
        num_best_friends- n in the sentence "Find the n best matching friends"   
                              
    Outputs:
        best_indicies   - A list of indicies to the the num_best_friends closest matching friends.
                          Sorted in decending order by quality matric.
        match_scores    - The quality metric for each best friend, sorted in descending order.
    '''
    
    if image_data is None:
        return None, None

    subjectFeatures=ImageFeatures()
    
    #Make our features and keypoints.
    subjectFeatureKeypoints, subjectFeatureDescriptors=subjectFeatures.from_image(image_data)
    
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
        
        break
        
    #Combine the lists together to make one array for the whole list of friends:
    friendIds=np.concatenate(friendIdsList)
    friendDescriptors=np.concatenate(friendDescriptorsList)
        
    #Make a matcher object using our subject image features:
    matcher = ImageMatcher(friendDescriptors)    

    #Using our subject-image based matcher, calculate how well it matches with this specific 
    # friend image.
    (matchedQueryTrainIds, matchDist) = matcher.match(subjectFeatureDescriptors)
    
    ##TODO:  convert matchedQueryTrainIds to which friends actually matched and how good the 
    #match was
        
    #Return our list of best indicies to friends[] and their corresponding best scores:
    return best_indices, best_scores
    
    
def find_best_match(image_data, image_type, friends):
    '''
    This function finds the best match for image_data among a collection of friends, where
    each friend represents a photo of a dog, with accompanying metadata.
    
    See find_best_matches for a definition of the inputs and outputs.
    '''

    #Find our best match:
    best_indices, match_scores=find_best_matches(image_data, image_type, friends, 1)

    #Get our info for the bet matching friend:
    best_index=best_indices[0]
    best_score=best_scores[0]
    best_db_id=friends[best_index].id
    
    return best_db_id, best_score, best_index