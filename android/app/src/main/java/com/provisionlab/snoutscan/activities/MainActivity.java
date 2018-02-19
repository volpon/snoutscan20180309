package com.provisionlab.snoutscan.activities;

import android.Manifest;
import android.app.Fragment;
import android.content.Intent;
import android.os.Bundle;
import android.support.design.widget.BottomNavigationView;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;

import com.karumi.dexter.Dexter;
import com.karumi.dexter.PermissionToken;
import com.karumi.dexter.listener.PermissionDeniedResponse;
import com.karumi.dexter.listener.PermissionGrantedResponse;
import com.karumi.dexter.listener.PermissionRequest;
import com.karumi.dexter.listener.single.PermissionListener;
import com.provisionlab.snoutscan.R;
import com.provisionlab.snoutscan.fragments.AlertFragment;
import com.provisionlab.snoutscan.fragments.HealthFragment;
import com.provisionlab.snoutscan.fragments.ProfileFragment;
import com.provisionlab.snoutscan.fragments.SettingsFragment;
import com.provisionlab.snoutscan.utilities.BottomNavigationViewHelper;

import butterknife.BindView;
import butterknife.ButterKnife;


/**
 * Created by superlight on 10/31/2017 AD.
 */

public class MainActivity extends AppCompatActivity {

    private static final String TAG = MainActivity.class.getSimpleName();

    @BindView(R.id.navigation)
    BottomNavigationView navigation;
    private BottomNavigationView.OnNavigationItemSelectedListener mOnNavigationItemSelectedListener
            = item -> {
        switch (item.getItemId()) {
            case R.id.navigation_alert:
                changeFragment(fragments.ALERT);
                return true;
            case R.id.navigation_profile:
                changeFragment(fragments.PROFILE);
                return true;
            case R.id.navigation_camera:
                goScanActivity();
                return true;
            case R.id.navigation_health:
                changeFragment(fragments.HEALTH);
                return true;
            case R.id.navigation_settings:
                changeFragment(fragments.SETTINGS);
                return true;
        }
        return false;
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        ButterKnife.bind(this);

        navigation.setOnNavigationItemSelectedListener(mOnNavigationItemSelectedListener);
        BottomNavigationViewHelper.removeShiftMode(navigation);
        navigation.getMenu().getItem(0).setChecked(true);
        //For first time setup
        changeFragment(fragments.ALERT);

        Dexter.withActivity(this)
                .withPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE)
                .withListener(new PermissionListener() {
                                  @Override
                                  public void onPermissionGranted(PermissionGrantedResponse response) {
                                      Log.d(TAG, "Write external storage permission granted");
                                  }

                                  @Override
                                  public void onPermissionDenied(PermissionDeniedResponse response) {
                                      Log.d(TAG, "Write external storage permission denied!");
                                  }

                                  @Override
                                  public void onPermissionRationaleShouldBeShown(PermissionRequest permission, PermissionToken token) {
                                      token.continuePermissionRequest();
                                  }
                              }
                ).check();
    }


    private void changeFragment(fragments selectedFragment) {

        Fragment newFragment = null;

        if (selectedFragment == fragments.ALERT) {
            newFragment = new AlertFragment();
        } else if (selectedFragment == fragments.PROFILE) {
            newFragment = new ProfileFragment();
        } else if (selectedFragment == fragments.HEALTH) {
            newFragment = new HealthFragment();
        } else if (selectedFragment == fragments.SETTINGS) {
            newFragment = new SettingsFragment();
        }

        getFragmentManager().beginTransaction().replace(
                R.id.fragmentContainer, newFragment)
                .commit();
    }

    public void goScanActivity() {
        startActivity(new Intent(this, ScanActivity.class));
    }

    private enum fragments {
        ALERT,
        PROFILE,
        HEALTH,
        SETTINGS
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
    }

    @Override
    public void onBackPressed() {
    }
}
