package com.provisionlab.snoutscan.models;

import com.google.gson.annotations.SerializedName;

/**
 * Created by Evgeniy on 15-Jan-18.
 */

public class Profile {

    @SerializedName("profile_id")
    private int profileId;

    private String phone;

    @SerializedName("use_msg")
    private boolean useMessenger;

    @SerializedName("use_phone")
    private boolean usePhone;

    public Profile() {
    }

    public int getProfileId() {
        return profileId;
    }

    public void setProfileId(int profileId) {
        this.profileId = profileId;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public boolean isUseMessenger() {
        return useMessenger;
    }

    public void setUseMessenger(boolean useMessenger) {
        this.useMessenger = useMessenger;
    }

    public boolean isUsePhone() {
        return usePhone;
    }

    public void setUsePhone(boolean usePhone) {
        this.usePhone = usePhone;
    }

    @Override
    public String toString() {
        return "Profile{" +
                "profileId=" + profileId +
                ", phone='" + phone + '\'' +
                ", useMessenger=" + useMessenger +
                ", usePhone=" + usePhone +
                '}';
    }
}
