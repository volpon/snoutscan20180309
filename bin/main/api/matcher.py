import cv2
import numpy as np
import base64
import json
import io
import sys
import pickle

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
        descriptorExtractor = cv2.xfeatures2d.BriefDescriptorExtractor_create()

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

        # Create BFMatcher object
        self.featureMatcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    def match(self, friendFeatureKeypoints, friendFeatureDescriptors, friendImage=None):
        '''
        This function matches the given subject subjectImg with a given friend subjectImg based on 
        the features in friendFeatureDescriptors.
        
        Inputs:
            friendFeatureKeypoints      - The feature keypoints for this friend.            
            friendFeatureDescriptors    - The feature descriptors for this friend.
            friendImage                 - The numpy array representing the subjectImg, for display 
                                          if displayImages=True
        
        @return percent
        '''

        if friendFeatureDescriptors is None:
            return None

        # Match subjectFeatureDescriptors descriptors
        #Note: This is calling BFMatcher.match, not ImageMatcher.match:
        matches = self.featureMatcher.match(self.subjectFeatureDescriptors, 
                                            friendFeatureDescriptors,
                                            );
        if len(matches) == 0:
            return 0
        
        #Display our matches:
        if self.displayImages:
            outImg = cv2.drawMatches(self.subjectImg, self.subjectFeatureKeypoints, friendImage, 
                                     friendFeatureKeypoints, matches, None )
        
        # quick calculation of the max and min distances between keypoints

        max_dist = 0;
        min_dist = 100;

        for m in matches:
            if m.distance < min_dist:
                min_dist = m.distance
            if m.distance > max_dist:
                max_dist = m.distance

        # calculate good matches

        good_matches = []
        for m in matches:
            if m.distance <= 3 * min_dist:
                good_matches.append(m)

        # show user percentage of match
        percent = (100 * len(good_matches)) / len(matches);

        return percent;


class MatchResult(object):

    def __init__(self, name, image, percent):

        self.name = name
        self.image = image
        self.percent = percent


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
            print('Warning: Skipping a friend without features, %s.' % friend.name, file=sys.stderr);
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
