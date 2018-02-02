package com.provisionlab.snoutscan.server;

import com.provisionlab.snoutscan.utilities.AppConstants;

import java.util.concurrent.TimeUnit;

import okhttp3.OkHttpClient;
import retrofit2.Retrofit;
import retrofit2.adapter.rxjava2.RxJava2CallAdapterFactory;
import retrofit2.converter.gson.GsonConverterFactory;

/**
 * Created by Evgeniy on 24.02.2017.
 */

public class RetrofitApi {

    private static RetrofitApi instance;
    private ApiService apiService;

    public static RetrofitApi getInstance() {
        if (instance == null) {
            instance = new RetrofitApi();
        }

        return instance;
    }

    private RetrofitApi() {
        apiService = buildRetrofit(AppConstants.SERVER_URL);
    }

    private static ApiService buildRetrofit(String url) {

        OkHttpClient client = new OkHttpClient.Builder()
                .connectTimeout(10, TimeUnit.SECONDS)
                .readTimeout(60, TimeUnit.SECONDS).build();

        Retrofit retrofit = new Retrofit.Builder()
                .baseUrl("https://" + url + "/")
                .addConverterFactory(GsonConverterFactory.create())
                .addCallAdapterFactory(RxJava2CallAdapterFactory.create())
                .client(client)
                .build();

        return retrofit.create(ApiService.class);
    }

    public ApiService getApiService() {
        return apiService;
    }
}
