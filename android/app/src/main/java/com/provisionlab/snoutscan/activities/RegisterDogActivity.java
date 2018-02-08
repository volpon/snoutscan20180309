package com.provisionlab.snoutscan.activities;

import android.app.Activity;
import android.os.Bundle;
import android.support.design.widget.TextInputEditText;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.widget.CheckBox;
import android.widget.ImageView;
import android.widget.Toast;

import com.google.gson.Gson;
import com.provisionlab.snoutscan.R;
import com.provisionlab.snoutscan.models.DogItem;
import com.provisionlab.snoutscan.models.Error;
import com.provisionlab.snoutscan.server.ApiService;
import com.provisionlab.snoutscan.server.RetrofitApi;
import com.provisionlab.snoutscan.utilities.CustomEditText;
import com.provisionlab.snoutscan.utilities.SharedPrefsUtil;
import com.provisionlab.snoutscan.utilities.Utils;

import java.io.IOException;

import butterknife.BindView;
import butterknife.ButterKnife;
import butterknife.OnClick;
import io.reactivex.android.schedulers.AndroidSchedulers;
import io.reactivex.disposables.CompositeDisposable;
import io.reactivex.schedulers.Schedulers;
import okhttp3.ResponseBody;
import retrofit2.HttpException;

import static com.provisionlab.snoutscan.activities.LoginActivity.TOKEN;
import static com.provisionlab.snoutscan.activities.SignupActivity.PROFILE_ID;
import static com.provisionlab.snoutscan.utilities.AppConstants.JWT;

/**
 * Created by superlight on 11/2/2017 AD.
 */

public class RegisterDogActivity extends AppCompatActivity {

    private static final String TAG = RegisterDogActivity.class.getSimpleName();
    private boolean usedMyLocation = true;
    private boolean checkedMale = true;
    private boolean isSnoutSelected = true;
    private CompositeDisposable compositeDisposable;

    @BindView(R.id.edt_dogname)
    TextInputEditText nameEditText;
    @BindView(R.id.edt_breed)
    TextInputEditText breedEditText;
    @BindView(R.id.edt_year)
    CustomEditText yearEditText;
    @BindView(R.id.edt_month)
    CustomEditText monthEditText;
    @BindView(R.id.iv_check_male)
    ImageView ivCheckMale;
    @BindView(R.id.iv_check_female)
    ImageView ivCheckFemale;
    @BindView(R.id.use_dog_location)
    CheckBox useLocationCheckBox;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_register_dog);
        ButterKnife.bind(this);
        getWindow().setSoftInputMode(
                WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN);

        compositeDisposable = new CompositeDisposable();
    }

    private void initUI(DogItem dog) {
        useLocationCheckBox.setOnCheckedChangeListener((buttonView, isChecked) -> {
            if (isChecked) {
                Log.d(TAG, "Checked");
            } else {
                Log.d(TAG, "Unchecked");
            }
        });
    }

    @OnClick({R.id.btn_back, R.id.iv_check_male, R.id.iv_check_female,/*R.id.profile_view,*/ R.id.btn_register})
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.btn_back:
                finish();
                break;
            case R.id.btn_register:
                registerDog();
                break;
            case R.id.iv_check_male:
                checkedMale = true;
                updateCheckGenderState();
                break;
            case R.id.iv_check_female:
                checkedMale = false;
                updateCheckGenderState();
                break;
        }
    }

    public void updateCheckGenderState() {
        ivCheckMale.setImageResource((checkedMale) ? R.drawable.img_checked : R.drawable.img_unchecked);
        ivCheckFemale.setImageResource((checkedMale) ? R.drawable.img_unchecked : R.drawable.img_checked);
    }

    private void registerDog() {
        if (Utils.isConnectedToNetwork(this)) {
            ApiService apiService = RetrofitApi.getInstance().getApiService();

            DogItem dogItem = new DogItem();
            dogItem.setName(nameEditText.getText().toString());
            dogItem.setBreed(breedEditText.getText().toString());

            if (checkedMale) {
                dogItem.setSex("Male");
            } else {
                dogItem.setSex("Female");
            }

            String age = yearEditText.getText().toString() + " " + monthEditText.getText().toString();
            dogItem.setAge(age);
            dogItem.setLocation("default location");
            dogItem.setStatus("");

            Log.d(TAG, "Dog " + dogItem);

            if (dogItem.getName().isEmpty()) {
                Toast.makeText(this, "Name could not be empty", Toast.LENGTH_SHORT).show();
            } else if (dogItem.getAge().isEmpty()) {
                Toast.makeText(this, "Age could not be empty", Toast.LENGTH_SHORT).show();
            } else if (dogItem.getSex().isEmpty()) {
                Toast.makeText(this, "Sex could not be empty", Toast.LENGTH_SHORT).show();
            } else {
                findViewById(R.id.progress_layout).setVisibility(View.VISIBLE);
                compositeDisposable.add(apiService.addNewDog(
                        JWT + " " + SharedPrefsUtil.getStringData(this, TOKEN),
                        SharedPrefsUtil.getIntData(this, PROFILE_ID), dogItem)
                        .observeOn(AndroidSchedulers.mainThread())
                        .subscribeOn(Schedulers.io())
                        .subscribe(this::handleRegisterResponse, this::handleRegisterError));
            }
        } else {
            Toast.makeText(this, getString(R.string.no_internet), Toast.LENGTH_LONG).show();
        }
    }

    private void handleRegisterResponse(DogItem result) throws IOException {
        findViewById(R.id.progress_layout).setVisibility(View.GONE);
        Log.d(TAG, "Dog id " + result.getDogId());
        setResult(Activity.RESULT_OK);
        finish();
    }

    private void handleRegisterError(Throwable t) throws IOException {
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
        compositeDisposable.clear();
    }
}
