package com.provisionlab.snoutscan.server;

import com.provisionlab.snoutscan.models.AuthObject;
import com.provisionlab.snoutscan.models.DogItem;
import com.provisionlab.snoutscan.models.Image;
import com.provisionlab.snoutscan.models.ImageObject;
import com.provisionlab.snoutscan.models.LoginObject;
import com.provisionlab.snoutscan.models.MatchResponse;
import com.provisionlab.snoutscan.models.Profile;
import com.provisionlab.snoutscan.models.RegisterObject;

import java.util.List;

import io.reactivex.Observable;
import retrofit2.Response;
import retrofit2.http.Body;
import retrofit2.http.DELETE;
import retrofit2.http.GET;
import retrofit2.http.Header;
import retrofit2.http.Headers;
import retrofit2.http.POST;
import retrofit2.http.PUT;
import retrofit2.http.Path;

/**
 * Created by Evgeniy on 07.03.2017.
 */

public interface ApiService {

    @Headers("Content-Type: application/json")
    @POST("api/profile/signup")
    Observable<Profile> signUp(@Body RegisterObject registerObject);

    @Headers("Content-Type: application/json")
    @POST("api/auth")
    Observable<AuthObject> signIn(@Body LoginObject loginObject);

    @Headers("Content-Type: application/json")
    @PUT("api/profile/{id}")
    Observable<Response<Void>> updateProfile(@Header("Authorization") String token,
                                             @Path("id") int id,
                                             @Body DogItem dogItem);

    @Headers("Content-Type: application/json")
    @GET("api/profile/{id}")
    Observable<Profile> fetchProfileData(@Path("id") int id);

    @Headers("Content-Type: application/json")
    @POST("api/profile/{id}/friends/new")
    Observable<DogItem> addNewDog(@Header("Authorization") String token,
                                  @Path("id") int id,
                                  @Body DogItem dogItem);

    @Headers("Content-Type: application/json")
    @GET("api/profile/{id}/friends")
    Observable<List<DogItem>> getDogs(@Header("Authorization") String token,
                                      @Path("id") int id);

    @Headers("Content-Type: application/json")
    @GET("api/friend/{id}")
    Observable<DogItem> getDogInfo(@Path("id") int id);

    @Headers("Content-Type: application/json")
    @DELETE("api/friend/{id}")
    Observable<Response<Void>> deleteDog(@Header("Authorization") String token,
                                          @Path("id") int id);

    @Headers("Content-Type: application/json")
    @PUT("api/friend/{id}/photo")
    Observable<Response<Void>> uploadPhoto(@Header("Authorization") String token,
                                           @Path("id") int id,
                                           @Body ImageObject image);

    @Headers("Content-Type: application/json")
    @GET("api/profile/{id}/photo")
    Observable<Image> downloadPhoto(@Path("id") int id);

    @Headers("Content-Type: application/json")
    @POST("api/query_match")
    Observable<MatchResponse> matchPhoto(@Body ImageObject image);
}