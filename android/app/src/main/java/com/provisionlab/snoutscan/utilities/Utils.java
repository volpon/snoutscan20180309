package com.provisionlab.snoutscan.utilities;

import android.app.ActivityManager;
import android.content.Context;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.util.Log;

import com.provisionlab.snoutscan.models.DogItem;

/**
 * Created by Evgeniy on 07.03.2017.
 */

public class Utils {

    private static final String TAG = Utils.class.getSimpleName();

    /**
     * Check internet connection
     *
     * @param context
     * @return
     */
    public static boolean isConnectedToNetwork(Context context) {

        ConnectivityManager cm = (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo activeNetwork = cm.getActiveNetworkInfo();
        if (activeNetwork != null) {
            if (activeNetwork.getType() == ConnectivityManager.TYPE_WIFI) {
                return true;
            } else if (activeNetwork.getType() == ConnectivityManager.TYPE_MOBILE) {
                return true;
            }
        } else {
            return false;
        }

        return false;
    }

    public static boolean isServiceRunning(Class<?> serviceClass, Context context) {
        ActivityManager manager = (ActivityManager) context.getSystemService(Context.ACTIVITY_SERVICE);
        for (ActivityManager.RunningServiceInfo service : manager.getRunningServices(Integer.MAX_VALUE)) {
            if (serviceClass.getName().equals(service.service.getClassName())) {
                return true;
            }
        }
        return false;
    }

    public static String getAge(DogItem dogItem) {
        if (dogItem.getAge() != null && dogItem.getAge().length() > 0) {
            String[] ageArray = dogItem.getAge().split(" ");
            return ageArray[0] + " years, " + ageArray[1] + " months.";
        } else {
            return dogItem.getAge();
        }
    }

    public static String getUrl(DogItem dogItem) {
        String url = "https://" + AppConstants.SERVER_URL + "/profile/" + dogItem.getDogId() + "/photo";
        Log.d(TAG, "Photo " + url);
        return url;
    }
}
