package com.provisionlab.snoutscan.activities;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.design.widget.TextInputEditText;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.Toast;

import com.google.gson.Gson;
import com.provisionlab.snoutscan.R;
import com.provisionlab.snoutscan.models.AuthObject;
import com.provisionlab.snoutscan.models.Error;
import com.provisionlab.snoutscan.models.LoginObject;
import com.provisionlab.snoutscan.server.ApiService;
import com.provisionlab.snoutscan.server.RetrofitApi;
import com.provisionlab.snoutscan.utilities.SharedPrefsUtil;
import com.provisionlab.snoutscan.utilities.Utils;

import java.io.IOException;

import butterknife.BindView;
import butterknife.ButterKnife;
import butterknife.OnClick;
import io.reactivex.android.schedulers.AndroidSchedulers;
import io.reactivex.disposables.Disposable;
import io.reactivex.schedulers.Schedulers;
import okhttp3.ResponseBody;
import retrofit2.HttpException;

import static com.provisionlab.snoutscan.activities.SignupActivity.PROFILE_ID;
import static com.provisionlab.snoutscan.activities.TutorialActivity.FIRST_RUN;


/**
 * Created by superlight on 10/30/2017 AD.
 */

public class LoginActivity extends AppCompatActivity {

    @BindView(R.id.edt_email)
    TextInputEditText edtEmail;
    @BindView(R.id.edt_password)
    TextInputEditText edtPassword;

    public static final String TOKEN = "token";
    private static final String TAG = LoginActivity.class.getSimpleName();
    private Disposable disposable;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);
        ButterKnife.bind(this);

        if (SharedPrefsUtil.getBooleanData(this, FIRST_RUN)) {
            if (ContextCompat.checkSelfPermission(this,
                    Manifest.permission.CAMERA)
                    != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this,
                        new String[]{Manifest.permission.CAMERA},
                        200);
            }
        } else {
            finish();
            startActivity(new Intent(this, TutorialActivity.class));
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String permissions[], @NonNull int[] grantResults) {
        switch (requestCode) {
            case 200:
                // If request is cancelled, the result arrays are empty.
                if (grantResults.length > 0
                        && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    Toast.makeText(this, "Camera Access permission granted.", Toast.LENGTH_LONG).show();
                } else {
                    Toast.makeText(this, "Camera Access permission was denied.", Toast.LENGTH_LONG).show();
                    // permission denied, boo! Disable the
                    // functionality that depends on this permission.
                }
                break;
            // other 'case' lines to check for other
            // permissions this app might request
        }
    }

    @OnClick({R.id.btn_login, R.id.btn_facebook, R.id.signup_layout, R.id.btn_scan})
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.btn_login:
                login();
                break;
            case R.id.btn_facebook:
                break;
            case R.id.signup_layout:
                startActivity(new Intent(this, SignupActivity.class));
                break;
            case R.id.btn_scan:
                startActivity(new Intent(this, ScanActivity.class));
                break;
        }
    }

    private void login() {
        if (Utils.isConnectedToNetwork(this)) {
            ApiService apiService = RetrofitApi.getInstance().getApiService();

            String email = edtEmail.getText().toString();
            String password = edtPassword.getText().toString();

            if (email.equals("")) {
                Toast.makeText(this, R.string.email_error_message, Toast.LENGTH_SHORT).show();
            } else if (password.equals("")) {
                Toast.makeText(this, R.string.pass_error_message, Toast.LENGTH_SHORT).show();
            } else {

                findViewById(R.id.progress_layout).setVisibility(View.VISIBLE);

                LoginObject loginObject = new LoginObject(email, password);
                Log.d(TAG, "LoginObject " + loginObject);

                disposable = apiService.signIn(loginObject)
                        .observeOn(AndroidSchedulers.mainThread())
                        .subscribeOn(Schedulers.io())
                        .subscribe(this::handleResponse, this::handleError);
            }
        } else {
            Toast.makeText(this, getString(R.string.no_internet), Toast.LENGTH_LONG).show();
        }
    }

    private void handleResponse(AuthObject result) {
        findViewById(R.id.progress_layout).setVisibility(View.GONE);
        Log.d(TAG, "AuthObject " + result);
        SharedPrefsUtil.putStringData(this, TOKEN, result.getAccessToken());
        SharedPrefsUtil.putIntData(this, PROFILE_ID, result.getProfile());
        startActivity(new Intent(this, MainActivity.class));
        finish();
    }

    private void handleError(Throwable t) throws IOException {
        findViewById(R.id.progress_layout).setVisibility(View.GONE);

        if (t != null) {
            if (t instanceof HttpException) {
                ResponseBody responseBody = ((HttpException) t).response().errorBody();

                Toast.makeText(this, "Error: " +
                        (responseBody != null ? new Gson().fromJson(responseBody.string(), Error.class).getError().getMessage() : null), Toast.LENGTH_LONG).show();
            } else {
                Log.d(TAG, "Error " + t.getMessage());
            }
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (disposable != null) {
            disposable.dispose();
        }
    }
}
