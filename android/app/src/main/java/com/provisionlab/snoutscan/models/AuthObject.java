package com.provisionlab.snoutscan.models;

import com.google.gson.annotations.SerializedName;

/**
 * Created by Evgeniy on 15-Jan-18.
 */

public class AuthObject {

    @SerializedName("access_token")
    private String accessToken;
    private int profile;

    public AuthObject() {
    }

    public String getAccessToken() {
        return accessToken;
    }

    public void setAccessToken(String accessToken) {
        this.accessToken = accessToken;
    }

    public int getProfile() {
        return profile;
    }

    public void setProfile(int profile) {
        this.profile = profile;
    }

    @Override
    public String toString() {
        return "AuthObject{" +
                "accessToken='" + accessToken + '\'' +
                ", profile=" + profile +
                '}';
    }
}
