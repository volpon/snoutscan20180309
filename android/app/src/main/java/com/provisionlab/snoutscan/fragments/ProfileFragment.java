package com.provisionlab.snoutscan.fragments;

import android.app.Fragment;
import android.content.Intent;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.RelativeLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.google.gson.Gson;
import com.provisionlab.snoutscan.R;
import com.provisionlab.snoutscan.activities.DogDetailActivity;
import com.provisionlab.snoutscan.activities.RegisterDogActivity;
import com.provisionlab.snoutscan.adapters.ProfileDogListAdapter;
import com.provisionlab.snoutscan.models.DogItem;
import com.provisionlab.snoutscan.models.Error;
import com.provisionlab.snoutscan.models.Profile;
import com.provisionlab.snoutscan.server.ApiService;
import com.provisionlab.snoutscan.server.RetrofitApi;
import com.provisionlab.snoutscan.utilities.AppConstants;
import com.provisionlab.snoutscan.utilities.SharedPrefsUtil;
import com.provisionlab.snoutscan.utilities.Utils;

import java.io.IOException;
import java.util.List;

import butterknife.BindView;
import butterknife.ButterKnife;
import butterknife.OnClick;
import io.reactivex.android.schedulers.AndroidSchedulers;
import io.reactivex.disposables.CompositeDisposable;
import io.reactivex.schedulers.Schedulers;
import okhttp3.ResponseBody;
import retrofit2.HttpException;

import static android.app.Activity.RESULT_OK;
import static com.provisionlab.snoutscan.activities.DogDetailActivity.DOG_ID;
import static com.provisionlab.snoutscan.activities.LoginActivity.TOKEN;
import static com.provisionlab.snoutscan.activities.SignupActivity.PROFILE_ID;

/**
 * Created by superlight on 10/31/2017 AD.
 */

public class ProfileFragment extends Fragment implements ProfileDogListAdapter.OnDogClickListener {

    private static final String TAG = ProfileFragment.class.getSimpleName();
    private static final int REQUEST_CODE = 1002;
    public static final int DELETE_RESULT_CODE = 1003;

    private ProfileDogListAdapter adapter;
    private CompositeDisposable compositeDisposable;

    @BindView(R.id.iv_profile)
    ImageView profileImageView;
    @BindView(R.id.txt_user_name)
    TextView usernameTextView;
    @BindView(R.id.txt_user_type)
    TextView userTypeTextView;
    @BindView(R.id.contact_layout)
    LinearLayout contactLayout;
    @BindView(R.id.contact_by_phone)
    RelativeLayout contactByPhoneLayout;
    @BindView(R.id.contact_by_messaging)
    RelativeLayout contactByMessagingLayout;
    @BindView(R.id.txt_user_location)
    TextView locationTextView;
    @BindView(R.id.dog_list)
    RecyclerView mRecyclerView;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_profile, container, false);
        ButterKnife.bind(this, view);
        return view;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        compositeDisposable = new CompositeDisposable();
        getProfileData();
        adapter = new ProfileDogListAdapter(getActivity());
        LinearLayoutManager linearLayoutManager = new LinearLayoutManager(getActivity());
        mRecyclerView.setLayoutManager(linearLayoutManager);
        mRecyclerView.setAdapter(adapter);
        adapter.setListener(this);
        getDogs();
    }

    @OnClick({R.id.btn_add, R.id.profile_view})
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.btn_add:
                startActivityForResult(new Intent(getActivity(), RegisterDogActivity.class), REQUEST_CODE);
                break;
            case R.id.profile_view:

                break;
        }
    }

    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (resultCode == RESULT_OK) {
            switch (requestCode) {
                case REQUEST_CODE:
                    getDogs();
                    break;
                case DELETE_RESULT_CODE:
                    Log.d(TAG, "Delete");
                    getDogs();
                    break;
            }
        }
    }

    private void getProfileData() {
        if (Utils.isConnectedToNetwork(getActivity())) {
            getActivity().findViewById(R.id.progress_layout).setVisibility(View.VISIBLE);
            ApiService apiService = RetrofitApi.getInstance().getApiService();

            compositeDisposable.add(apiService.fetchProfileData(
                    SharedPrefsUtil.getIntData(getActivity(), PROFILE_ID))
                    .observeOn(AndroidSchedulers.mainThread())
                    .subscribeOn(Schedulers.io())
                    .subscribe(this::handleProfileResponse, this::handleProfileError));
        } else {
            Toast.makeText(getActivity(), getString(R.string.no_internet), Toast.LENGTH_LONG).show();
        }
    }

    private void getDogs() {
        if (Utils.isConnectedToNetwork(getActivity())) {
            getActivity().findViewById(R.id.progress_layout).setVisibility(View.VISIBLE);
            ApiService apiService = RetrofitApi.getInstance().getApiService();

            compositeDisposable.add(apiService.getDogs(
                    AppConstants.JWT + " " + SharedPrefsUtil.getStringData(getActivity(), TOKEN),
                    SharedPrefsUtil.getIntData(getActivity(), PROFILE_ID))
                    .observeOn(AndroidSchedulers.mainThread())
                    .subscribeOn(Schedulers.io())
                    .subscribe(this::handleDogsResponse, this::handleDogsError));
        } else {
            Toast.makeText(getActivity(), getString(R.string.no_internet), Toast.LENGTH_LONG).show();
        }
    }

    private void handleProfileResponse(Profile result) {
        getActivity().findViewById(R.id.progress_layout).setVisibility(View.GONE);
        Log.d(TAG, "Profile " + result);

        if (result.isUseMessenger() && result.isUsePhone()) {
            contactLayout.setVisibility(View.VISIBLE);
            contactByMessagingLayout.setVisibility(View.VISIBLE);
            contactByPhoneLayout.setVisibility(View.VISIBLE);
        } else if (result.isUseMessenger()) {
            contactLayout.setVisibility(View.VISIBLE);
            contactByMessagingLayout.setVisibility(View.VISIBLE);
        } else if (result.isUsePhone()) {
            contactLayout.setVisibility(View.VISIBLE);
            contactByPhoneLayout.setVisibility(View.VISIBLE);
        }
    }

    private void handleProfileError(Throwable t) throws IOException {
        getActivity().findViewById(R.id.progress_layout).setVisibility(View.GONE);

        if (t != null) {
            if (t instanceof HttpException) {
                ResponseBody responseBody = ((HttpException) t).response().errorBody();

                Toast.makeText(getActivity(), "Error: " +
                        (responseBody != null ? new Gson().fromJson(responseBody.string(), Error.class).getError().getMessage() : null), Toast.LENGTH_LONG).show();
            } else {
                Log.d(TAG, "Error " + t.getMessage());
            }
        }
    }

    private void handleDogsResponse(List<DogItem> dogs) {
        getActivity().findViewById(R.id.progress_layout).setVisibility(View.GONE);
        Log.d(TAG, "Dogs " + dogs);

        if (dogs != null && dogs.size() > 0) {
            adapter.setItems(dogs);
        }
    }

    private void handleDogsError(Throwable t) throws IOException {
        getActivity().findViewById(R.id.progress_layout).setVisibility(View.GONE);

        if (t != null) {
            if (t instanceof HttpException) {
                ResponseBody responseBody = ((HttpException) t).response().errorBody();

                Toast.makeText(getActivity(), "Error: " +
                        (responseBody != null ? new Gson().fromJson(responseBody.string(), Error.class).getError().getMessage() : null), Toast.LENGTH_LONG).show();
            } else {
                Log.d(TAG, "Error " + t.getMessage());
            }
        }
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();

        compositeDisposable.clear();
    }

    @Override
    public void onClick(DogItem dogItem) {
        Intent intent = new Intent(getActivity(), DogDetailActivity.class);
        intent.putExtra(DOG_ID, dogItem.getDogId());
        startActivityForResult(intent, DELETE_RESULT_CODE);
    }
}
