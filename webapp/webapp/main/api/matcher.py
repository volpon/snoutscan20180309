import cv2
import numpy as np
import base64
from main.api.model import Profile, Photo

def image_from_base64(data, type):
    return image_from_binary(base64.b64decode(data), type)

def image_from_binary(data, type):
    data = np.array(bytearray(data), dtype=np.uint8)
    return cv2.imdecode(data, 0)

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

    def compare(self, image1, image2):

        # Initiate BRISK detector
        detector = cv2.BRISK_create()
        #detector = cv2.FeatureDetector_create("BRISK")

        # Initiate BRIEF extractor
        descriptorExtractor = cv2.xfeatures2d.BriefDescriptorExtractor_create()
        #descriptorExtractor = cv2.DescriptorExtractor_create("BRIEF")

        # Create BFMatcher object
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        # first image
        keypoints1 = detector.detect(image1, None)
        keypoints1, descriptors1 = descriptorExtractor.compute(image1, keypoints1)
        #keypoints1, descriptors1 = detector.detectAndCompute(image1, None)

        # second image
        keypoints2 = detector.detect(image2, None)
        keypoints2, descriptors2 = descriptorExtractor.compute(image2, keypoints2)
        #keypoints2, descriptors2 = detector.detectAndCompute(image2, None)

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
        descriptorExtractor = cv2.xfeatures2d.BriefDescriptorExtractor_create()
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


def find_best_match(image_data, image_type):

    image1 = image_from_base64(image_data, image_type)

    if image1 is None:
        return None, None

    match = MatchFragment()

    profiles = Profile.query.all()

    best_per = 0
    best_id = 0

    for profile in profiles:

        photo = profile.photo

        data2, type2 = photo.get_binary()

        if data2 is None:
            continue

        image2 = image_from_binary(data2, type2)

        if image2 is None:
            continue

        per = match.compare(image1, image2)

        if per > best_per:
            best_per = per
            best_id = profile.id

    if best_per > 50:
        return best_id, best_per

    return None, None
