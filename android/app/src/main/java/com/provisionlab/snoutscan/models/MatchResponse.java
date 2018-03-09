package com.provisionlab.snoutscan.models;

/**
 * Created by evgeniyosetrov on 2/19/18.
 */

public class MatchResponse {

    private String status;
    private int profile;
    private double percent;

    public MatchResponse() {
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public int getProfile() {
        return profile;
    }

    public void setProfile(int profile) {
        this.profile = profile;
    }

    public double getPercent() {
        return percent;
    }

    public void setPercent(double percent) {
        this.percent = percent;
    }

    @Override
    public String toString() {
        return "MatchResponse{" +
                "status='" + status + '\'' +
                ", profile=" + profile +
                ", percent=" + percent +
                '}';
    }
}
