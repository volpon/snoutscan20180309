package com.provisionlab.snoutscan.activities;

import android.app.AlertDialog;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Matrix;
import android.graphics.Point;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.design.widget.TabLayout;
import android.support.v7.app.AppCompatActivity;
import android.util.Base64;
import android.util.Log;
import android.view.Display;
import android.view.Gravity;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.RelativeLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.bumptech.glide.Glide;
import com.bumptech.glide.load.engine.DiskCacheStrategy;
import com.google.gson.Gson;
import com.provisionlab.snoutscan.R;
import com.provisionlab.snoutscan.models.DogItem;
import com.provisionlab.snoutscan.models.Error;
import com.provisionlab.snoutscan.models.Image;
import com.provisionlab.snoutscan.models.ImageObject;
import com.provisionlab.snoutscan.models.Profile;
import com.provisionlab.snoutscan.server.ApiService;
import com.provisionlab.snoutscan.server.RetrofitApi;
import com.provisionlab.snoutscan.utilities.AppConstants;
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
import okhttp3.ResponseBody;
import retrofit2.HttpException;
import retrofit2.Response;

import static com.provisionlab.snoutscan.activities.LoginActivity.TOKEN;
import static com.provisionlab.snoutscan.activities.SignupActivity.PROFILE_ID;

/**
 * Created by superlight on 11/2/2017 AD.
 */

public class DogDetailActivity extends AppCompatActivity {

    public static final String DOG_DATA = "dog_data";
    private static final String TAG = DogDetailActivity.class.getSimpleName();
    static final int SELECT_FILE = 1;
    static final int REQUEST_CAMERA = 0;

    AlertDialog dialog;

    //    @BindView(R.id.dog_photo)
//    ViewPager dogImageViewPager;
    //TODO temporary profile photo
    @BindView(R.id.profile_photo)
    ImageView profileImageView;
    @BindView(R.id.dog_status)
    TextView status;
    @BindView(R.id.breed)
    TextView breed;
    @BindView(R.id.sex)
    TextView sex;
    @BindView(R.id.age)
    TextView age;
    @BindView(R.id.location)
    TextView location;
    @BindView(R.id.profile_view)
    RelativeLayout profilePhotoLayout;
    @BindView(R.id.contact_layout)
    LinearLayout contactLayout;
    @BindView(R.id.contact_by_phone)
    RelativeLayout contactByPhoneLayout;
    @BindView(R.id.contact_by_messaging)
    RelativeLayout contactByMessagingLayout;

    private DogItem dog;
    private String mimeType;
    private String base64Image;
    private CompositeDisposable compositeDisposable;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_dog_detail);
        ButterKnife.bind(this);

        initUI();

        compositeDisposable = new CompositeDisposable();

        getProfileData();
    }

    private void initUI() {

        TabLayout tabLayout = findViewById(R.id.tab_layout);
//        tabLayout.setupWithViewPager(dogImageViewPager, true);
//
//        dogImageViewPager.addOnPageChangeListener(new ViewPager.OnPageChangeListener() {
//
//            @Override
//            public void onPageScrolled(int position, float positionOffset, int positionOffsetPixels) {
//            }
//
//            @Override
//            public void onPageSelected(int position) {
//            }
//
//            @Override
//            public void onPageScrollStateChanged(int state) {
//            }
//        });

        if (getIntent() != null && getIntent().getExtras() != null) {
            dog = (DogItem) getIntent().getSerializableExtra(DOG_DATA);
            Log.d(TAG, "Dog detail " + dog);

            status.setText(dog.getName());
            breed.setText(dog.getBreed());
            sex.setText(dog.getSex());
            age.setText(Utils.getAge(dog));
            location.setText(dog.getLocation());

            Glide.with(this)
                    .load(Utils.getUrl(dog))
                    .skipMemoryCache(true)
                    .diskCacheStrategy(DiskCacheStrategy.NONE)
                    .into(profileImageView);
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

        window.findViewById(R.id.select_camera).setOnClickListener(v -> {
            dialog.dismiss();
            Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
            startActivityForResult(intent, REQUEST_CAMERA);
        });

        window.findViewById(R.id.select_library).setOnClickListener(v -> {
            dialog.dismiss();
            Intent intent = new Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
            intent.setType("image/*");
            startActivityForResult(Intent.createChooser(intent, "Select Image"), SELECT_FILE);
        });

        window.findViewById(R.id.select_cancel).setOnClickListener(v -> dialog.dismiss());
    }

    private void getProfileData() {
        if (Utils.isConnectedToNetwork(this)) {
            findViewById(R.id.progress_layout).setVisibility(View.VISIBLE);
            ApiService apiService = RetrofitApi.getInstance().getApiService();

            compositeDisposable.add(apiService.fetchProfileData(
                    SharedPrefsUtil.getIntData(this, PROFILE_ID))
                    .observeOn(AndroidSchedulers.mainThread())
                    .subscribeOn(Schedulers.io())
                    .subscribe(this::handleProfileResponse, this::handleProfileError));
        } else {
            Toast.makeText(this, getString(R.string.no_internet), Toast.LENGTH_LONG).show();
        }
    }

    private void uploadPhoto() {
        if (Utils.isConnectedToNetwork(this)) {
            findViewById(R.id.progress_layout).setVisibility(View.VISIBLE);
            ApiService apiService = RetrofitApi.getInstance().getApiService();

            Image image = new Image();
            image.setData(base64Image);
            image.setType(mimeType);
            ImageObject imageObject = new ImageObject(image);

            Log.d(TAG, "Image " + image);

            compositeDisposable.add(apiService.uploadPhoto(
                    AppConstants.JWT + " " + SharedPrefsUtil.getStringData(this, TOKEN),
                    dog.getDogId(),
                    imageObject)
                    .observeOn(AndroidSchedulers.mainThread())
                    .subscribeOn(Schedulers.io())
                    .subscribe(this::handleUploadResponse, this::handleUploadError));
        } else {
            Toast.makeText(this, getString(R.string.no_internet), Toast.LENGTH_LONG).show();
        }
    }

    private void handleUploadResponse(Response<Void> result) {
        findViewById(R.id.progress_layout).setVisibility(View.GONE);
        Log.d(TAG, "Upload photo " + result);
        if (result.code() == 204) {
            Glide.with(this)
                    .load(Utils.getUrl(dog))
                    .into(profileImageView);
        }
    }

    private void handleUploadError(Throwable t) throws IOException {
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

    private void handleProfileResponse(Profile profile) {
        findViewById(R.id.progress_layout).setVisibility(View.GONE);
        Log.d(TAG, "Profile data " + profile);

        if (profile.isUseMessenger() && profile.isUsePhone()) {
            contactLayout.setVisibility(View.VISIBLE);
            contactByMessagingLayout.setVisibility(View.VISIBLE);
            contactByPhoneLayout.setVisibility(View.VISIBLE);
        } else if (profile.isUseMessenger()) {
            contactLayout.setVisibility(View.VISIBLE);
            contactByMessagingLayout.setVisibility(View.VISIBLE);
        } else if (profile.isUsePhone()) {
            contactLayout.setVisibility(View.VISIBLE);
            contactByPhoneLayout.setVisibility(View.VISIBLE);
        }
    }

    private void handleProfileError(Throwable t) throws IOException {
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
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (resultCode == RESULT_OK) {
            if (requestCode == SELECT_FILE) {
                beginCrop(data.getData());
            } else if (requestCode == REQUEST_CAMERA) {
                mimeType = getContentResolver().getType(data.getData());
                Bitmap thumbnail = (Bitmap) data.getExtras().get("data");
                ByteArrayOutputStream bytes = new ByteArrayOutputStream();
                thumbnail.compress(Bitmap.CompressFormat.PNG, 100, bytes);
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
                handleCrop(data);
            }
        } else if (resultCode == Crop.RESULT_ERROR) {
            Toast.makeText(this, Crop.getError(data).getMessage(), Toast.LENGTH_SHORT).show();
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

    private void handleCrop(Intent result) {
        Uri imageUri = Crop.getOutput(result);

        try {
            Bitmap bitmap = MediaStore.Images.Media.getBitmap(this.getContentResolver(), imageUri);
            findViewById(R.id.progress_layout).setVisibility(View.VISIBLE);
            new ConvertImageToBase64Task().execute(bitmap);
        } catch (IOException e) {
            Log.e(TAG, e.getMessage());
        }
    }

    public Bitmap getResizedBitmap(Bitmap bm, int newWidth, int newHeight) {
        int width = bm.getWidth();
        int height = bm.getHeight();
        float scaleWidth = ((float) newWidth) / width;
        float scaleHeight = ((float) newHeight) / height;

        Matrix matrix = new Matrix();
        matrix.postScale(scaleWidth, scaleHeight);

        Bitmap resizedBitmap = Bitmap.createBitmap(
                bm, 0, 0, width, height, matrix, false);
        bm.recycle();
        return resizedBitmap;
    }

    private class ConvertImageToBase64Task extends AsyncTask<Bitmap, Void, Bitmap> {

        @Override
        protected Bitmap doInBackground(Bitmap[] params) {
            Bitmap resizedBitmap = getResizedBitmap(params[0], 320, 240);
            ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
            resizedBitmap.compress(Bitmap.CompressFormat.PNG, 100, byteArrayOutputStream);
            byte[] byteArray = byteArrayOutputStream.toByteArray();
            base64Image = Base64.encodeToString(byteArray, Base64.DEFAULT);
            return resizedBitmap;
        }

        @Override
        protected void onPostExecute(Bitmap resizedBitmap) {
            super.onPostExecute(resizedBitmap);
            findViewById(R.id.progress_layout).setVisibility(View.GONE);
            uploadPhoto();
        }
    }

    @OnClick({R.id.back, R.id.close, R.id.profile_view})
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.back:
            case R.id.close:
                finish();
                break;
            case R.id.profile_view:
                popupActionSheet();
                break;
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        compositeDisposable.clear();
    }
}
