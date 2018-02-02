package com.provisionlab.snoutscan.models;

/**
 * Created by Evgeniy on 15-Jan-18.
 */

public class Image {

    private String data;
    private String type;

    public Image() {
    }

    public String getData() {
        return data;
    }

    public void setData(String data) {
        this.data = data;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    @Override
    public String toString() {
        return "Image{" +
                "data='" + data.substring(50) + '\'' +
                ", type='" + type + '\'' +
                '}';
    }
}
