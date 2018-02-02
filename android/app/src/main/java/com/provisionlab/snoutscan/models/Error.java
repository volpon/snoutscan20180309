package com.provisionlab.snoutscan.models;

/**
 * Created by Evgeniy on 15-Jan-18.
 */

public class Error {

    private ErrorMessage error;

    public Error() {
    }

    public ErrorMessage getError() {
        return error;
    }

    public void setError(ErrorMessage error) {
        this.error = error;
    }

    @Override
    public String toString() {
        return "Error{" +
                "error=" + error +
                '}';
    }
}
