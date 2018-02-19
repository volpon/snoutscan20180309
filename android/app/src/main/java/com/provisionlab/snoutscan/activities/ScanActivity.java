package com.provisionlab.snoutscan.activities;

import android.app.ProgressDialog;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.hardware.Camera;
import android.media.MediaPlayer;
import android.media.MediaScannerConnection;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Environment;
import android.support.v7.app.AppCompatActivity;
import android.util.Base64;
import android.util.Log;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import com.google.gson.Gson;
import com.provisionlab.snoutscan.R;
import com.provisionlab.snoutscan.models.Error;
import com.provisionlab.snoutscan.models.Image;
import com.provisionlab.snoutscan.models.ImageObject;
import com.provisionlab.snoutscan.server.ApiService;
import com.provisionlab.snoutscan.server.RetrofitApi;
import com.provisionlab.snoutscan.utilities.Utils;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Calendar;

import butterknife.BindView;
import butterknife.ButterKnife;
import butterknife.OnClick;
import io.reactivex.android.schedulers.AndroidSchedulers;
import io.reactivex.disposables.Disposable;
import io.reactivex.schedulers.Schedulers;
import okhttp3.ResponseBody;
import retrofit2.HttpException;
import retrofit2.Response;

/**
 * Created by superlight on 10/31/2017 AD.
 */

public class ScanActivity extends AppCompatActivity {

    private static final String TAG = ScanActivity.class.getSimpleName();
    private SurfaceHolder previewHolder = null;
    private Camera camera = null;
    private boolean inPreview = false;
    Bitmap bmp;
    static Bitmap mutableBitmap;
    File imageFileName = null;
    File imageFileFolder = null;
    private MediaScannerConnection msConn;
    ProgressDialog dialog;
    private boolean isClicked = false;
    private MediaPlayer player;
    private String mimeType;
    private String base64Image;
    private Disposable disposable;

    @BindView(R.id.surface)
    SurfaceView preview;
    @BindView(R.id.txt_alert)
    TextView txtAlert;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_scan);

        ButterKnife.bind(this);

        player = MediaPlayer.create(this, R.raw.dogsounds);

        previewHolder = preview.getHolder();
        previewHolder.addCallback(surfaceCallback);
        previewHolder.setType(SurfaceHolder.SURFACE_TYPE_PUSH_BUFFERS);

        previewHolder.setFixedSize(getWindow().getWindowManager()
                .getDefaultDisplay().getWidth(), getWindow().getWindowManager()
                .getDefaultDisplay().getHeight());
    }


    @Override
    public void onResume() {
        super.onResume();
        camera = Camera.open();
    }

    @Override
    public void onPause() {
        if (inPreview) {
            camera.stopPreview();
        }

        camera.release();
        camera = null;
        inPreview = false;
        super.onPause();
    }

    private Camera.Size getBestPreviewSize(int width, int height, Camera.Parameters parameters) {
        Camera.Size result = null;
        for (Camera.Size size : parameters.getSupportedPreviewSizes()) {
            if (size.width <= width && size.height <= height) {
                if (result == null) {
                    result = size;
                } else {
                    int resultArea = result.width * result.height;
                    int newArea = size.width * size.height;
                    if (newArea > resultArea) {
                        result = size;
                    }
                }
            }
        }
        return (result);
    }

    SurfaceHolder.Callback surfaceCallback = new SurfaceHolder.Callback() {
        public void surfaceCreated(SurfaceHolder holder) {
            try {
                camera.setPreviewDisplay(previewHolder);
            } catch (Throwable t) {
                Log.e("PreviewDemo",
                        "Exception in setPreviewDisplay()", t);
                Toast.makeText(ScanActivity.this, t.getMessage(), Toast.LENGTH_LONG)
                        .show();
            }
        }

        public void surfaceChanged(SurfaceHolder holder,
                                   int format, int width,
                                   int height) {
            Camera.Parameters parameters = camera.getParameters();
            Camera.Size size = getBestPreviewSize(width, height,
                    parameters);

            if (size != null) {
                parameters.setPreviewSize(size.width, size.height);
                camera.setParameters(parameters);
                camera.setDisplayOrientation(90);
                camera.startPreview();
                inPreview = true;
            }
        }

        public void surfaceDestroyed(SurfaceHolder holder) {
            // no-op
        }
    };


    Camera.PictureCallback photoCallback = new Camera.PictureCallback() {
        public void onPictureTaken(final byte[] data, final Camera camera) {
            dialog = ProgressDialog.show(ScanActivity.this, "", "Saving Photo");
            new Thread() {
                public void run() {
                    try {
                        Thread.sleep(1000);
                    } catch (Exception ex) {

                    }
                    onPictureTake(data);
                }
            }.start();
        }
    };


    public void onPictureTake(byte[] data) {
        new SavePhotoTask().execute(data);
    }

    class SavePhotoTask extends AsyncTask<byte[], String, String> {
        @Override
        protected String doInBackground(byte[]... data) {
            bmp = BitmapFactory.decodeByteArray(data[0], 0, data[0].length);
            mutableBitmap = bmp.copy(Bitmap.Config.ARGB_8888, true);

            ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
            mutableBitmap.compress(Bitmap.CompressFormat.PNG, 100, byteArrayOutputStream);
            byte[] byteArray = byteArrayOutputStream.toByteArray();
            base64Image = Base64.encodeToString(byteArray, Base64.DEFAULT);

            savePhoto(mutableBitmap);
            return null;
        }

        @Override
        protected void onPostExecute(String s) {
            super.onPostExecute(s);
            matchPhoto();
        }
    }

    public void savePhoto(Bitmap bmp) {
        imageFileFolder = new File(Environment.getExternalStorageDirectory().toString() + File.separator + "Snoutscan/");
        imageFileFolder.mkdir();
        FileOutputStream out;
        Calendar c = Calendar.getInstance();
        String date = fromInt(c.get(Calendar.MONTH)) + fromInt(c.get(Calendar.DAY_OF_MONTH)) + fromInt(c.get(Calendar.YEAR)) +
                fromInt(c.get(Calendar.HOUR_OF_DAY)) + fromInt(c.get(Calendar.MINUTE)) + fromInt(c.get(Calendar.SECOND));
        imageFileName = new File(imageFileFolder, date.toString() + ".jpg");
        Uri uri = Uri.parse(imageFileName.toString());
        Log.d(TAG, "Uri " + uri);
        mimeType = getContentResolver().getType(uri);

        try {
            out = new FileOutputStream(imageFileName);
            bmp.compress(Bitmap.CompressFormat.JPEG, 100, out);
            out.flush();
            out.close();
            scanPhoto(imageFileName.toString());
        } catch (Exception e) {
            Log.e(TAG, "Error " + e.getMessage());
        }
    }

    public String fromInt(int val) {
        return String.valueOf(val);
    }

    public void scanPhoto(final String imageFileName) {
        msConn = new MediaScannerConnection(ScanActivity.this, new MediaScannerConnection.MediaScannerConnectionClient() {
            public void onMediaScannerConnected() {
                msConn.scanFile(imageFileName, null);
                Log.d(TAG, "connection established");
            }

            public void onScanCompleted(String path, Uri uri) {
                msConn.disconnect();
                dialog.dismiss();
                Log.d(TAG, "scan completed");
            }
        });
        msConn.connect();
    }

    @OnClick({R.id.btn_shatter, R.id.btn_back, R.id.btn_sound})
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.btn_shatter:
                onBack();
                break;
            case R.id.btn_back:
                finish();
                break;
            case R.id.btn_sound:
                if (!isClicked) {
                    player = MediaPlayer.create(this, R.raw.dogsounds);
                    player.start();
                    isClicked = true;
                    Log.d(TAG, "Start " + isClicked);
                } else {
                    player.stop();
                    isClicked = false;
                    Log.d(TAG, "Stop " + isClicked);
                }
                break;
        }
    }

//    @Override
//    public boolean onKeyDown(int keyCode, KeyEvent event) {
//        if (keyCode == KeyEvent.KEYCODE_MENU && event.getRepeatCount() == 0) {
//            onBack();
//        }
//        return super.onKeyDown(keyCode, event);
//    }

    public void onBack() {
        Log.d(TAG, "onBack: yes");
        camera.takePicture(null, null, photoCallback);
        inPreview = false;
    }

    private void matchPhoto() {
        if (Utils.isConnectedToNetwork(this)) {
            findViewById(R.id.progress_layout).setVisibility(View.VISIBLE);
            ApiService apiService = RetrofitApi.getInstance().getApiService();

            Image image = new Image();
            image.setData(base64Image);
            image.setType(mimeType);
            ImageObject imageObject = new ImageObject(image);

            Log.d(TAG, "Image " + image);

            disposable = apiService.matchPhoto(
                    imageObject)
                    .observeOn(AndroidSchedulers.mainThread())
                    .subscribeOn(Schedulers.io())
                    .subscribe(this::handleUploadResponse, this::handleUploadError);
        } else {
            Toast.makeText(this, getString(R.string.no_internet), Toast.LENGTH_LONG).show();
        }
    }

    private void handleUploadResponse(Response<Void> result) {
        findViewById(R.id.progress_layout).setVisibility(View.GONE);
        Log.d(TAG, "Upload photo " + result);
        if (result.code() == 200) {
            Log.d(TAG, "Upload result response " + result.body().toString());
        } else {
            Log.d(TAG, "Error result response " + result.body().toString());
        }
        finish();
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

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (player != null) {
            player.stop();
            player.release();
        }

        if (disposable != null) {
            disposable.dispose();
        }
    }
}
