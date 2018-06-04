from hyperopt import hp
from GCExtract import GCExtract
import cv2

#This file keeps global constants that we might want to optimize over in a hyperparamter search.


# Documentation for hyperopt and the distributions can be found here:
#  https://github.com/hyperopt/hyperopt/wiki/FMin

#This is a list of global constants.  We'll convert them to g later.
#Each global constant is a tuple of:
# (parameterName, distributionFn, distributionFnArgsExceptForLabel, fixedValue, varry=1)
gc=[]

###########
#Defining the global constants:

#Some examples:
#gc.append(('pastTimeBinsIncrementSec', hp.uniform, (1*60*60, 30*24*60*60), 60*60*24, 1))
#gc.append(('pastTimeNumBinsMax', hp.quniform, (1, 10*365, 1), 5*365, 0))
#gc.append(('variablesMakeStationary', hp.randint, (1,),  0, 0))
#gc.append(('spacyLanguageModel', hp.choice, (('en',),), 'en', 1))


#This flag defines if we load (and thus process) our images as color iamges or grayscale images:
gc.append(('colorNotGrayscale', hp.choice, ((cv2.IMREAD_GRAYSCALE, cv2.IMREAD_COLOR),), 
           cv2.IMREAD_GRAYSCALE, 1))

#The height that we convert all of the snout images to before we start the rest of the process:
#We keep the aspect ratio the same.
gc.append(('imgHeight', hp.quniform, (500,4096,1), 1000, 1))

#How many features to create for each image, maximum:
gc.append(('numFeaturesMax', hp.quniform, (500,20000,1), 8000, 1))



#The type of keypoint detector we use:
gc.append(('keypointType', hp.choice, (('ORB', 'AGAST', 'AKAZE', 'BRISK', 'FAST', 'MSER' ),),
           'MSER', 1))
               
#The type of descriptor extractor we use:
gc.append(('descriptorType', hp.choice, (('ORB', 'AKAZE', 'BRISK' ),), 'BRISK', 1))

########
#Options for the ORB keypoint detector / descriptor extractor:
#https://docs.opencv.org/3.4.1/db/d95/classcv_1_1ORB.html
###

#The pyramid decimation ratio. >=1.
gc.append(('orbScaleFactor', hp.uniform, (1.01, 2), 1.2, 1))

#The number of pyramid levels
gc.append(('orbNLevels', hp.quniform, (1, 16, 1), 8, 1))

#The size of the patch to used in each layer to create the ORB descriptor.  This 
#size on the smaller pyramid layers will cover more of the original image area.
#Also used for the edgeThreshold:
gc.append(('orbPatchSize', hp.quniform, (5, 64, 1), 31, 1))

########
#Options for the agast keypoint detector/descriptor extractor:
#https://docs.opencv.org/3.4.1/d7/d19/classcv_1_1AgastFeatureDetector.html#details
###

#Some threshold.  Unkown:
gc.append(('agastThreshold', hp.uniform, (5,30), 10, 1))

#Boolean turning on nonmaxSuppression:
gc.append(('agastNonmaxSuppression', hp.choice, ((True, False,),), True, 1))

gc.append(('agastType', hp.choice, ((cv2.AgastFeatureDetector_AGAST_5_8,
                                     cv2.AgastFeatureDetector_AGAST_7_12d,
                                     cv2.AgastFeatureDetector_AGAST_7_12s,
                                     cv2.AgastFeatureDetector_NONMAX_SUPPRESSION,
                                     cv2.AgastFeatureDetector_OAST_9_16,
                                     cv2.AgastFeatureDetector_THRESHOLD),), 
            cv2.AgastFeatureDetector_OAST_9_16, 1))
                        
                         
########
#Options for the agast keypoint detector/descriptor extractor:
#https://docs.opencv.org/3.4.1/d8/d30/classcv_1_1AKAZE.html#details
###
gc.append(('akazeDescriptorType', hp.choice, ((cv2.AKAZE_DESCRIPTOR_KAZE_UPRIGHT,
                                     cv2.AKAZE_DESCRIPTOR_MLDB_UPRIGHT,
                                     cv2.AKAZE_DESCRIPTOR_KAZE,
                                     cv2.AKAZE_DESCRIPTOR_MLDB,
                                     ),), 
            cv2.AKAZE_DESCRIPTOR_MLDB, 1))

#The proportion of bits to use per channel.  Each channel has 162 possible bits.
gc.append(('akazeDescriptorSizeRelative', hp.uniform, (0.2,1.0), 0.526749, 1))

#The number of descriptor channels to use, 1-3:
gc.append(('akazeNumChan', hp.choice, ((1,2,3),), 3 ,1))

#Detector response threshold to accept a point:
gc.append(('akazeThreshold', hp.uniform, (0.0001, 0.001), 0.001, 1))

#the number of actaves to use:
gc.append(('akazeNOctaves', hp.quniform, (2,8,1), 4, 1))

#Number of sublevels per scale level:
gc.append(('akazeNOctaveLayers', hp.quniform, (2,8,1), 4, 1))

#Diffusivity type:
gc.append(('akazeDiffusivityType', hp.choice, ((cv2.KAZE_DIFF_PM_G1,
                                                cv2.KAZE_DIFF_PM_G2,
                                                cv2.KAZE_DIFF_WEICKERT,
                                                cv2.KAZE_DIFF_CHARBONNIER),), 
            cv2.KAZE_DIFF_PM_G2, 1))

########
#Options for the BRISK keypoint detector/descriptor extractor:
#https://docs.opencv.org/3.4.1/de/dbf/classcv_1_1BRISK.html
###

#Detection threshold score:
gc.append(('briskThreshold', hp.quniform, (10,60,1), 30, 1))

#The number of octaves to use: 0 is a single scale.
gc.append(('briskOctaves', hp.quniform, (0,8,1), 3, 1))

########
#Options for the FAST keypoint detector:
#https://docs.opencv.org/3.4.1/df/d74/classcv_1_1FastFeatureDetector.html#details
###

gc.append(('fastThreshold', hp.quniform, (3, 30, 1), 10, 1))

gc.append(('fastNonmaxSuppression', hp.choice, ((True, False,),), True, 1))

gc.append(('fastType', hp.choice, ((cv2.FAST_FEATURE_DETECTOR_FAST_N,
                                    cv2.FAST_FEATURE_DETECTOR_NONMAX_SUPPRESSION,
                                    cv2.FAST_FEATURE_DETECTOR_THRESHOLD,
                                    cv2.FAST_FEATURE_DETECTOR_TYPE_5_8,
                                    cv2.FAST_FEATURE_DETECTOR_TYPE_7_12,
                                    cv2.FAST_FEATURE_DETECTOR_TYPE_9_16),), 
            cv2.FAST_FEATURE_DETECTOR_TYPE_9_16, 1))

########
#Options for the Maximally Stable Extremal Region keypoint detector:
#https://docs.opencv.org/3.4.1/d3/d28/classcv_1_1MSER.html#details
###

gc.append(('mserDelta', hp.quniform, (3, 30, 1), 5, 1))

gc.append(('mserMinArea', hp.quniform, (20, 120, 1), 60, 1))

gc.append(('mserMaxArea', hp.quniform, (3000, 30000, 1), 14400, 1))

gc.append(('mserMaxVariation', hp.uniform, (0.01, 1), 0.25, 1))

gc.append(('mserMinDiversity', hp.uniform, (0.01, 1), 0.25, 1))

gc.append(('mserMaxEvolution', hp.quniform, (50, 800, 1), 200, 1))

gc.append(('mserMinMargin', hp.uniform, (0.0001, 0.02), 0.003, 1))

gc.append(('mserEdgeBlurSize', hp.quniform, (1, 13, 1), 5, 1))

#
#######################

#Produce g and searchSpace and other variables we will be importing from other files:
(g, searchVarNamesInOrder, fixedParamDict, searchSpace)=GCExtract(gc)
