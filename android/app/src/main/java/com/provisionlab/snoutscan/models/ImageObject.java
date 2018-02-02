package com.provisionlab.snoutscan.models;

/**
 * Created by Evgeniy on 16-Jan-18.
 */

public class ImageObject {

    private Image image;

    public ImageObject() {
    }

    public ImageObject(Image image) {
        this.image = image;
    }

    public Image getImage() {
        return image;
    }

    public void setImage(Image image) {
        this.image = image;
    }

    @Override
    public String toString() {
        return "ImageObject{" +
                "image=" + image +
                '}';
    }
}
