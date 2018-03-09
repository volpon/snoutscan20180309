package com.provisionlab.snoutscan.models;

import android.os.Parcel;
import android.os.Parcelable;

import com.google.gson.annotations.SerializedName;

/**
 * Created by superlight on 10/31/2017 AD.
 */

public class DogItem implements Parcelable {

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

    protected DogItem(Parcel in) {
        dogId = in.readInt();
        name = in.readString();
        breed = in.readString();
        sex = in.readString();
        age = in.readString();
        location = in.readString();
        status = in.readString();
    }

    public static final Creator<DogItem> CREATOR = new Creator<DogItem>() {
        @Override
        public DogItem createFromParcel(Parcel in) {
            return new DogItem(in);
        }

        @Override
        public DogItem[] newArray(int size) {
            return new DogItem[size];
        }
    };

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

    @Override
    public int describeContents() {
        return 0;
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeInt(dogId);
        dest.writeString(name);
        dest.writeString(breed);
        dest.writeString(sex);
        dest.writeString(age);
        dest.writeString(location);
        dest.writeString(status);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof DogItem)) return false;

        DogItem dogItem = (DogItem) o;

        if (getDogId() != dogItem.getDogId()) return false;
        if (getName() != null ? !getName().equals(dogItem.getName()) : dogItem.getName() != null)
            return false;
        if (getBreed() != null ? !getBreed().equals(dogItem.getBreed()) : dogItem.getBreed() != null)
            return false;
        if (getSex() != null ? !getSex().equals(dogItem.getSex()) : dogItem.getSex() != null)
            return false;
        if (getAge() != null ? !getAge().equals(dogItem.getAge()) : dogItem.getAge() != null)
            return false;
        if (getLocation() != null ? !getLocation().equals(dogItem.getLocation()) : dogItem.getLocation() != null)
            return false;
        return getStatus() != null ? getStatus().equals(dogItem.getStatus()) : dogItem.getStatus() == null;
    }

    @Override
    public int hashCode() {
        int result = getDogId();
        result = 31 * result + (getName() != null ? getName().hashCode() : 0);
        result = 31 * result + (getBreed() != null ? getBreed().hashCode() : 0);
        result = 31 * result + (getSex() != null ? getSex().hashCode() : 0);
        result = 31 * result + (getAge() != null ? getAge().hashCode() : 0);
        result = 31 * result + (getLocation() != null ? getLocation().hashCode() : 0);
        result = 31 * result + (getStatus() != null ? getStatus().hashCode() : 0);
        return result;
    }
}
