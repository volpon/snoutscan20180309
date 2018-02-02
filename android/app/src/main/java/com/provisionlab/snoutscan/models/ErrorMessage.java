package com.provisionlab.snoutscan.models;

/**
 * Created by Evgeniy on 15-Jan-18.
 */

public class ErrorMessage {

    private String message;

    public ErrorMessage() {
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    @Override
    public String toString() {
        return "ErrorMessage{" +
                "message='" + message + '\'' +
                '}';
    }
}
