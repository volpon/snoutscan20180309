package com.provisionlab.snoutscan.activities;

import android.Manifest;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.Point;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.design.widget.TextInputEditText;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.util.Base64;
import android.util.Log;
import android.view.Display;
import android.view.Gravity;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.widget.CheckBox;
import android.widget.Toast;

import com.provisionlab.snoutscan.R;
import com.provisionlab.snoutscan.models.Profile;
import com.provisionlab.snoutscan.models.RegisterObject;
import com.provisionlab.snoutscan.server.ApiService;
import com.provisionlab.snoutscan.server.RetrofitApi;
import com.provisionlab.snoutscan.utilities.SharedPrefsUtil;
import com.provisionlab.snoutscan.utilities.Utils;
import com.soundcloud.android.crop.Crop;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Random;

import butterknife.BindView;
import butterknife.ButterKnife;
import butterknife.OnClick;
import io.reactivex.android.schedulers.AndroidSchedulers;
import io.reactivex.disposables.CompositeDisposable;
import io.reactivex.schedulers.Schedulers;

/**
 * Created by superlight on 10/30/2017 AD.
 */

public class SignupActivity extends AppCompatActivity {

    AlertDialog dialog;

    static final int SELECT_FILE = 1;
    static final int REQUEST_CAMERA = 0;

    @BindView(R.id.iv_check_dog_owner)
    CheckBox dogOwnerCheckBox;
    @BindView(R.id.iv_check_direct_call)
    CheckBox phoneCallCheckBox;
    @BindView(R.id.iv_check_app_messaging)
    CheckBox appMessagingCheckBox;
    //    @BindView(R.id.iv_profile)
//    ImageView ivProfile;
    @BindView(R.id.edt_email)
    TextInputEditText edtEmail;
    @BindView(R.id.edt_password)
    TextInputEditText edtPassword;
    @BindView(R.id.edt_phone)
    TextInputEditText edtPhoneNum;

    public static final String PROFILE_ID = "profile_id";
    private static final String TAG = LoginActivity.class.getSimpleName();
    private CompositeDisposable compositeDisposable;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_signup);
        ButterKnife.bind(this);
        getWindow().setSoftInputMode(
                WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN);
        if (ContextCompat.checkSelfPermission(this,
                Manifest.permission.READ_EXTERNAL_STORAGE)
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.READ_EXTERNAL_STORAGE},
                    200);
        }

        compositeDisposable = new CompositeDisposable();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String permissions[], int[] grantResults) {
        switch (requestCode) {
            case 200:
                if (grantResults.length > 0
                        && grantResults[0] == PackageManager.PERMISSION_GRANTED) {


                } else {
                    Toast.makeText(SignupActivity.this, "Photo Library Access permission was denied.", Toast.LENGTH_LONG).show();
                }
                break;
        }
    }

    @OnClick({R.id.btn_back, R.id.btn_signup, /*R.id.photo_view*/})
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.btn_back:
                finish();
                break;
            case R.id.btn_signup:
                signUp();
                break;
            case R.id.photo_view:
                popupActionSheet();
                break;
        }
    }

    public void popupActionSheet() {
        dialog = new AlertDialog.Builder(this, R.style.dialog_style).create();
        dialog.show();
        Window window = dialog.getWindow();
        window.setContentView(R.layout.dialog_photo_action);

        //get display width//
        Display display = getWindowManager().getDefaultDisplay();
        Point size = new Point();
        display.getSize(size);
        int width = size.x;

        window.setWindowAnimations(R.style.AnimBottom);
        window.setGravity(Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL);
        WindowManager.LayoutParams layoutParams = window.getAttributes();
        window.setLayout(width - 80, layoutParams.height);

        window.findViewById(R.id.select_camera).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dialog.dismiss();
                Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
                startActivityForResult(intent, REQUEST_CAMERA);
            }
        });
        window.findViewById(R.id.select_library).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dialog.dismiss();
                Intent intent = new Intent(Intent.ACTION_PICK, android.provider.MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
                intent.setType("image/*");
                startActivityForResult(Intent.createChooser(intent, "Select Image"), SELECT_FILE);
            }
        });
        window.findViewById(R.id.select_cancel).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dialog.dismiss();
            }
        });
    }

    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (resultCode == RESULT_OK) {
            if (requestCode == SELECT_FILE) {
                beginCrop(data.getData());
            } else if (requestCode == REQUEST_CAMERA) {
                Bitmap thumbnail = (Bitmap) data.getExtras().get("data");
                ByteArrayOutputStream bytes = new ByteArrayOutputStream();
                thumbnail.compress(Bitmap.CompressFormat.PNG, 0, bytes);
                File destination = new File(Environment.getExternalStorageDirectory(),
                        System.currentTimeMillis() + ".png");
                FileOutputStream fo;
                try {
                    destination.createNewFile();
                    fo = new FileOutputStream(destination);
                    fo.write(bytes.toByteArray());
                    fo.flush();
                    fo.close();
                } catch (FileNotFoundException e) {
                    e.printStackTrace();
                } catch (IOException e) {
                    e.printStackTrace();
                }
                beginCrop(Uri.fromFile(destination));
            } else if (requestCode == Crop.REQUEST_CROP) {
//                handleCrop(resultCode, data);
            }
        }
    }

    public void beginCrop(Uri source) {
        String child = "";
        int min = 1;
        int max = 1000000;

        Random r = new Random();
        String randomString = String.valueOf(r.nextInt(max - min + 1) + min);
        child = "cropped_" + randomString;

        Uri destination = Uri.fromFile(new File(getCacheDir(), child));
        Crop.of(source, destination).asSquare().start(this);
    }

//    private void handleCrop(int resultCode, Intent result) {
//        if (resultCode == RESULT_OK) {
//            Glide.with(ivProfile.getContext())
//                    .load(Crop.getOutput(result))
//                    .dontAnimate()
//                    .into(ivProfile);
//            ivProfile.buildDrawingCache();
//            Bitmap bmap = ivProfile.getDrawingCache();
//            String encodedImageData = getEncoded64ImageStringFromBitmap(bmap);
//        } else if (resultCode == Crop.RESULT_ERROR) {
//            Toast.makeText(this, Crop.getError(result).getMessage(), Toast.LENGTH_SHORT).show();
//        }
//    }

    public String getEncoded64ImageStringFromBitmap(Bitmap bitmap) {
        ByteArrayOutputStream stream = new ByteArrayOutputStream();
        bitmap.compress(Bitmap.CompressFormat.JPEG, 90, stream);
        byte[] byteFormat = stream.toByteArray();
        //get the base 64 String
        String imgString = Base64.encodeToString(byteFormat, Base64.NO_WRAP);
        return imgString;
    }

    private void signUp() {
        if (Utils.isConnectedToNetwork(this)) {
            ApiService apiService = RetrofitApi.getInstance().getApiService();

            String email = edtEmail.getText().toString();
            String password = edtPassword.getText().toString();
            String phone = edtPhoneNum.getText().toString();
            boolean usePhone = phoneCallCheckBox.isChecked();
            boolean useMessaging = appMessagingCheckBox.isChecked();

            if (email.equals("")) {
                Toast.makeText(this, R.string.email_error_message, Toast.LENGTH_SHORT).show();
            } else if (password.equals("")) {
                Toast.makeText(this, R.string.pass_error_message, Toast.LENGTH_SHORT).show();
            } else {

                if (Utils.isConnectedToNetwork(this)) {
                    findViewById(R.id.progress_layout).setVisibility(View.VISIBLE);

                    RegisterObject registerObject = new RegisterObject(email, password, phone, useMessaging, usePhone);
                    Log.d(TAG, "RegisterObject " + registerObject);

                    compositeDisposable.add(apiService.signUp(registerObject)
                            .observeOn(AndroidSchedulers.mainThread())
                            .subscribeOn(Schedulers.io())
                            .subscribe(this::handleResponse, this::handleError));
                } else {
                    Toast.makeText(this, getString(R.string.no_internet), Toast.LENGTH_LONG).show();
                }
            }
        }
    }

    private void handleResponse(Profile result) {
        findViewById(R.id.progress_layout).setVisibility(View.GONE);
        Log.d(TAG, "SignUpObject " + result);
        SharedPrefsUtil.putIntData(this, PROFILE_ID, result.getProfileId());
        finish();
    }

    private void handleError(Throwable t) {
        findViewById(R.id.progress_layout).setVisibility(View.GONE);
        Toast.makeText(this, "Error " + t.getMessage(), Toast.LENGTH_LONG).show();
        Log.d(TAG, "Error " + t.getMessage());
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        compositeDisposable.clear();
    }
}
