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
        patchSize=63

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
    
    def __init__(self, subjectFeatureKeypoints, subjectFeatureDescriptors, 
                 displayImages=False, subjectImg=None):
        '''
        Inputs:
            subjectFeatureKeypoints
                                    - The feature keypoints for the subject subjectImg.
            subjectFeatureDescriptors
                                    - The feature descriptors for the subject subjectImg.
            displayImages           - Says if we should display subjectImgs for debugging purposes.
            subjectImg              - If displayImages==True, then this is the subjectImg from which
                                      subjectFeatureDescriptors was created.
        '''

        assert not displayImages or subjectImg is not None,\
            'Need to specify an subjectImg if dispalyImages=True.'

        self.subjectFeatureDescriptors = subjectFeatureDescriptors
        self.subjectFeatureKeypoints = subjectFeatureKeypoints
        self.displayImages = displayImages
        self.subjectImg=subjectImg

        # FLANN parameters
        
        #A constant that means to use the Locally sensitive hashing distance metric:
        FLANN_INDEX_LSH = 6
        indexParams= dict(algorithm = FLANN_INDEX_LSH,
                           table_number = 6, # 12
                           key_size = 12,     # 20
                           multi_probe_level = 1) #2
        searchParams = dict(checks=50)   # or pass empty dictionary

        #index_params,search_params
        self.featureMatcher = cv2.FlannBasedMatcher(indexParams,searchParams)

    def match(self, friendFeatureKeypoints, friendFeatureDescriptors, friendImage=None):
        '''
        This function matches the given subject subjectImg with a given friend subjectImg based on 
        the features in friendFeatureDescriptors.
        
        Inputs:
            friendFeatureKeypoints      - The feature keypoints for this friend.            
            friendFeatureDescriptors    - The feature descriptors for this friend.
            friendImage                 - The numpy array representing the subjectImg, for display 
                                          if displayImages=True
        
        @return match_score
        '''

        if friendFeatureDescriptors is None:
            return None
        

        # For each of the subject image features, find the closest feature descriptor in the 
        #friend image:
        matches = self.featureMatcher.knnMatch(self.subjectFeatureDescriptors, 
                                            friendFeatureDescriptors,k=2
                                            );
                                    
        if len(matches) == 0:
            return 0
        
        good_matches=[]
        # Check to make sure that the best match is at least 1/.7 as close as the second best
        # match, and only use those:
        
        for matchPair in matches:
            
            if len(matchPair) ==2:
                #Divvy them out:
                (bestMatch,secondBestMatch) =matchPair
            elif len(matchPair) ==1:
                #Then we only had one match - assume it's good.
                (bestMatch,)=matchPair
                good_matches.append(bestMatch);
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


        # show user the number of good matches that there are:
        match_score = len(good_matches)
        
        #Display our good_matches:
        if self.displayImages:
            outImg = cv2.drawMatches(self.subjectImg, self.subjectFeatureKeypoints, friendImage, 
                                     friendFeatureKeypoints, good_matches, None )
            
            #Write to disk in case we need to communicate with someone else:
            cv2.imwrite(os.path.expanduser('/tmp/good_matches.png'), outImg)
            
            cv2.imshow('good_matches', outImg)
            
            #Press any key to exit.
            cv2.waitKey(0)
            cv2.destroyAllWindows()   

        return match_score;


class MatchResult(object):

    def __init__(self, name, image, match_score):

        self.name = name
        self.image = image
        self.match_score = match_score


    def saveImage(self, path):

        cv2.imwrite(path, self.image)


def find_best_match(image_data, image_type, friends, displayImages=False):
    '''
    This function finds the best match for image_data among a collection of friends, where
    each friend represents a photo of a dog, with accompanying metadata.
    
    Inputs:
        image_data      - the subject image data, in numpy format.
        image_type      - Not currently used.
        friends         - A collection of Friend() objects representing the pictures the given image
                          could match to.
        displayImages   - Says if we should display images for debugging purposes.
    '''

    if image_data is None:
        return None, None

    subjectFeatures=ImageFeatures()
    
    #Make our features and keypoints.
    subjectFeatureKeypoints, subjectFeatureDescriptors=subjectFeatures.from_image(image_data)
    
    #Make a matcher object using our subject image features:
    matcher = ImageMatcher(subjectFeatureKeypoints, subjectFeatureDescriptors, displayImages, 
                           image_data)

    best_match_score = -float('Inf')
    
    #The databse id of our best match:
    best_db_id = 0
    
    #The list index of our best friend:
    best_index=None

    #####
    ##Loop through all of our friends and find the one that has the highest matcher.match score:
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
        
        #Get our friend image:
        friendImgBinary,friendImgType=friend.photo.get_binary()

        #Using our subject-image based matcher, calculate how well it matches with this specific 
        # friend image.
        match_score = matcher.match(friendFeatureKeypoints, friendFeatureDescriptors,
                                    friendImgBinary)

        #Find the largest per in the group.
        if match_score and match_score > best_match_score:
            best_match_score = match_score
            best_db_id = friend.id
            best_index = index

    ##Only return a result if we have at least a match score of 50:
    #if best_match_score > 50:
    return best_db_id, best_match_score, best_index

    #return None, None
