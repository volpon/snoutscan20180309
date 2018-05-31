import cv2

def ImgDisplay(windowTitle, image):
    '''
    This function displays an image using opencv, but allows you to close it like normal with the X.
    
    Inputs:
        windowTitle         - The name we want to give the window.  Re-using the name re-uses the 
                               window.  This is displayed in the title bar too.
        image               - the numpy array representing the image.
    '''
    
    #Display the image:
    cv2.imshow(windowTitle, image)
    
    #ImgWaitToClose(
    
    #Wait them to click close:
    while cv2.getWindowProperty(windowTitle, 0) >= 0:
        
        keyCode = cv2.waitKey(50)
        
        #If they pressed a key, then break:
        if keyCode != -1:
            break;

    #Do one more wait to let the windows close and not look like it's frozen:
    keyCode = cv2.waitKey(50)
