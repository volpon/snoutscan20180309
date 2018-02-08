package com.provisionlab.snoutscan.models;

import com.google.gson.annotations.SerializedName;

/**
 * Created by Evgeniy on 27-Jan-18.
 */

public class RegisterObject {

    private String email;
    private String password;
    private String phone;
    @SerializedName("use_msg")
    private boolean useMessaging;
    @SerializedName("use_phone")
    private boolean usePhone;

    public RegisterObject() {
    }

    public RegisterObject(String email, String password, String phone, boolean useMessaging, boolean usePhone) {
        this.email = email;
        this.password = password;
        this.phone = phone;
        this.useMessaging = useMessaging;
        this.usePhone = usePhone;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public boolean isUseMessaging() {
        return useMessaging;
    }

    public void setUseMessaging(boolean useMessaging) {
        this.useMessaging = useMessaging;
    }

    public boolean isUsePhone() {
        return usePhone;
    }

    public void setUsePhone(boolean usePhone) {
        this.usePhone = usePhone;
    }

    @Override
    public String toString() {
        return "RegisterObject{" +
                "email='" + email + '\'' +
                ", password='" + password + '\'' +
                ", phone='" + phone + '\'' +
                ", useMessaging=" + useMessaging +
                ", usePhone=" + usePhone +
                '}';
    }
}
