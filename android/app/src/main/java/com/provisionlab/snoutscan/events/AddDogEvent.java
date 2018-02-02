package com.provisionlab.snoutscan.events;

import com.provisionlab.snoutscan.models.DogItem;

/**
 * Created by superlight on 10/31/2017 AD.
 */

public class AddDogEvent {

    private DogItem dogItem;

    public AddDogEvent(DogItem dogItem) {
        this.dogItem = dogItem;
    }
}
