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
            self.keypoints = None
        pass


    @classmethod
    def from_image(cls, image):

        if (isinstance(image, str)):
            image = image_from_base64(bytes(image, "utf-8"))

        if (isinstance(image, bytes)):
            image = image_from_binary(image)

        # Initiate BRISK detector
        detector = cv2.BRISK_create()

        # Initiate BRIEF extractor
        descriptorExtractor = cv2.xfeatures2d.BriefDescriptorExtractor_create()

        keypoints = detector.detect(image, None)
        keypoints, descriptors = descriptorExtractor.compute(image, keypoints)

        x = cls()
        x.descriptors = descriptors
        x.keypoints = keypoints
        
        return x


    def encode(self):

        memfile = io.BytesIO()
        pickle.dump((self.descriptors, self.keypoints), memfile, protocol=pickle.HIGHEST_PROTOCOL)
        memfile.seek(0)

        serialized = memfile.read()

        return serialized

    def decode(self, serialized):
        
        memfile = io.BytesIO(serialized)
        
        (self.descriptors, self.keypoints)=pickle.load(memfile)

class ImageMatcher(object):
    '''
    This class is used to match the features from a subject image to features for another friend.
    
    
    '''

    def __init__(self, subjectImgFeatures: ImageFeatures, displayImages=False, subjectImg=None):
        '''
        Inputs:
            subjectImgFeatures      - The features for the subject subjectImg.
            displayImages           - Says if we should display subjectImgs for debugging purposes.
            subjectImg              - If displayImages==True, then this is the subjectImg from which
                                      subjectImgFeatures was created.
        '''

        assert not displayImages or subjectImg is not None,\
            'Need to specify an subjectImg if dispalyImages=True.'

        self.subjectImgFeatures = subjectImgFeatures
        self.displayImages = displayImages
        self.subjectImg=subjectImg

        # Create BFMatcher object
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    def match(self, friendFeatures: ImageFeatures, friendImage=None):
        '''
        This function matches the given subject subjectImg with a given friend subjectImg based on 
        the features in friendFeatures.
        
        Inputs:
            friendFeatures      - The features for this friend.
            friendImage         - The numpy array representing the subjectImg, for display if 
                                  displayImages=True
        
        @return percent
        '''

        if friendFeatures is None \
                or friendFeatures.descriptors is None \
                or friendFeatures.keypoints is None:
            return None

        # Match subjectImgFeatures descriptors
        #Note: This is calling BFMatcher.match, not ImageMatcher.match:
        matches = self.matcher.match(self.subjectImgFeatures.descriptors, friendFeatures.descriptors,
                                     );
        if len(matches) == 0:
            return 0
        
        #Display our matches:
        if self.displayImages:
            outImg = cv2.drawMatches(self.subjectImg, self.subjectImgFeatures.keypoints, friendImage, 
                            friendFeatures.keypoints, matches, None )
        
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

    #Make a matcher object using our subject image features:
    matcher = ImageMatcher(ImageFeatures.from_image(image_data), displayImages, image_data)

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
        if friend.photo.features is None:
            print('Warning: Skipping a friend without features, %s.' % friend.name, file=sys.stderr);
            continue
        
        #Get our features
        friendFeatures = ImageFeatures(friend.photo.features)
        
        #Get our friend image:
        friendImgBinary,friendImgType=friend.photo.get_binary()

        #Using our subject-image based matcher, calculate how well it matches with this specific 
        # friend image.
        match_score = matcher.match(friendFeatures, friendImgBinary)

        #Find the largest per in the group.
        if match_score and match_score > best_match_score:
            best_match_score = match_score
            best_db_id = friend.id
            best_index = index

    ##Only return a result if we have at least a match score of 50:
    #if best_match_score > 50:
    return best_db_id, best_match_score, best_index

    #return None, None
