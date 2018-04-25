import cv2
import numpy as np
import base64
import json
import io
import sys

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

    @classmethod
    def from_image(cls, image):

        if (isinstance(image, str)):
            image = image_from_base64(bytes(image, "utf-8"))

        if (isinstance(image, bytes)):
            image = image_from_binary(image)

        # Initiate BRISK detector
        detector = cv2.BRISK_create()

        # Initiate BRIEF extractor
        descriptorExtractor = cv2.xthisFriendFeaturesd.BriefDescriptorExtractor_create()

        keypoints = detector.detect(image, None)
        keypoints, descriptors = descriptorExtractor.compute(image, keypoints)

        x = cls()
        x.descriptors = descriptors
        return x

    def encode(self):

        memfile = io.BytesIO()
        np.save(memfile, self.descriptors)
        memfile.seek(0)

        serialized = memfile.read()

        return serialized

    def decode(self, serialized):

        memfile = io.BytesIO(serialized)
        self.descriptors = np.load(memfile)


class ImageMatcher(object):

    def __init__(self, image: ImageFeatures):

        self.image = image

        # Create BFMatcher object
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        pass

    def match(self, thisFriendFeatures: ImageFeatures):
        """
        @return percent
        """

        if thisFriendFeatures is None or thisFriendFeatures.descriptors is None:
            return None

        # Match image descriptors
        matches = self.matcher.match(self.image.descriptors, thisFriendFeatures.descriptors);
        if len(matches) == 0:
            return 0
        
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


class MatchFragment(object):
    
    def __init__(self):
        pass

    def compare(self, image1, thisFriendFeatures):

        # Initiate BRISK detector
        detector = cv2.BRISK_create()
        #detector = cv2.FeatureDetector_create("BRISK")

        # Initiate BRIEF extractor
        descriptorExtractor = cv2.xthisFriendFeaturesd.BriefDescriptorExtractor_create()
        #descriptorExtractor = cv2.DescriptorExtractor_create("BRIEF")

        # Create BFMatcher object
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        # first image
        keypoints1 = detector.detect(image1, None)
        keypoints1, descriptors1 = descriptorExtractor.compute(image1, keypoints1)
        #keypoints1, descriptors1 = detector.detectAndCompute(image1, None)

        # second image
        keypoints2 = detector.detect(thisFriendFeatures, None)
        keypoints2, descriptors2 = descriptorExtractor.compute(thisFriendFeatures, keypoints2)
        #keypoints2, descriptors2 = detector.detectAndCompute(thisFriendFeatures, None)

        # Match image descriptors
        matches = matcher.match(descriptors1, descriptors2);
        
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

    def compareTwoImages(self, name: str, path1: str, path2: str):

        # Initiate BRISK detector
        detector = cv2.BRISK_create()
        #detector = cv2.FeatureDetector_create("BRISK")

        # Initiate BRIEF extractor
        descriptorExtractor = cv2.xthisFriendFeaturesd.BriefDescriptorExtractor_create()
        #descriptorExtractor = cv2.DescriptorExtractor_create("BRIEF")

        # Create BFMatcher object
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        # first image
        img1 = cv2.imread(path1,0)

        keypoints1 = detector.detect(img1, None)
        keypoints1, descriptors1 = descriptorExtractor.compute(img1, keypoints1)
        #keypoints1, descriptors1 = detector.detectAndCompute(img1, None)

        # second image
        img2 = cv2.imread(path2,0)

        keypoints2 = detector.detect(img2, None)
        keypoints2, descriptors2 = descriptorExtractor.compute(img2, keypoints2)
        #keypoints2, descriptors2 = detector.detectAndCompute(img2, None)

        # Match image descriptors
        matches = matcher.match(descriptors1, descriptors2);
        if len(matches) == 0:
            return None
        
        # Feature and connection colors
        RED = (255, 0, 0)
        GREEN = (0, 255, 0)

        # the output and drawing functions are primarily for testing purposes.

        # draw the matches --
        #
        # helps to visualize what connections the matcher is making while I
        # improve the algorithm. this will not necessarily be included in a
        # consumer-facing release.

        outputImg = cv2.drawMatches(img1, keypoints1, img2, keypoints2, matches, None, GREEN, RED, None, cv2.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS)

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

        return MatchResult(name, outputImg, percent);

def find_best_match(image_data, image_type, friends):
    '''
    This function finds the best match for image_data among a collection of friends, where
    each friend represents a photo of a dog, with accompanying metadata.
    
    Inputs:
        image_data  - the subject image data, either as an array of bytes or as a base64 encoded 
                      string.
        image_type  - Not currently used.
        friends     - A collection of Friend() objects representing the pictures the given image
                      could match to.
    '''

    if image_data is None:
        return None, None

    #Make a matcher object using our subject image features:
    matcher = ImageMatcher(ImageFeatures.from_image(image_data))

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

        #Get the friend's photo:
        photo = friend.photo

        if photo.features is None:
            print('Warning: Skipping a friend without features, %s.' % friend.name, file=sys.stderr);
            continue
        
        #Get our features
        thisFriendFeatures = ImageFeatures(photo.features)

        #Using our subject-image based matcher, calculate how well it matches with this specific 
        # friend image.
        match_score = matcher.match(thisFriendFeatures)

        #Find the largest per in the group.
        if match_score and match_score > best_match_score:
            best_match_score = match_score
            best_db_id = friend.id
            best_index = index

    ##Only return a result if we have at least a match score of 50:
    #if best_match_score > 50:
    return best_db_id, best_match_score, best_index

    #return None, None
