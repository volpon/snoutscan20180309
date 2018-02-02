package com.provisionlab.snoutscan.models;

import com.google.gson.annotations.SerializedName;

import java.io.Serializable;

/**
 * Created by superlight on 10/31/2017 AD.
 */

public class DogItem implements Serializable {

    @SerializedName("friend_id")
    private int dogId;
    private String name;
    private String breed;
    private String sex;
    private String age;
    private String location;
    private String status;

    public DogItem() {
    }

    public DogItem(int dogId, String name, String breed, String sex, String age, String location, String status) {
        this.dogId = dogId;
        this.name = name;
        this.breed = breed;
        this.sex = sex;
        this.age = age;
        this.location = location;
        this.status = status;
    }

    public int getDogId() {
        return dogId;
    }

    public void setDogId(int dogId) {
        this.dogId = dogId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getBreed() {
        return breed;
    }

    public void setBreed(String breed) {
        this.breed = breed;
    }

    public String getSex() {
        return sex;
    }

    public void setSex(String sex) {
        this.sex = sex;
    }

    public String getAge() {
        return age;
    }

    public void setAge(String age) {
        this.age = age;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    @Override
    public String toString() {
        return "DogItem{" +
                "dogId=" + dogId +
                ", name='" + name + '\'' +
                ", breed='" + breed + '\'' +
                ", sex='" + sex + '\'' +
                ", age='" + age + '\'' +
                ", location='" + location + '\'' +
                ", status='" + status + '\'' +
                '}';
    }
}
