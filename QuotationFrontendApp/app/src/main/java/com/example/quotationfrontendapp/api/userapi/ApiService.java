package com.example.quotationfrontendapp.api.userapi;

import com.example.quotationfrontendapp.dtos.quotationdtos.*;
import com.example.quotationfrontendapp.dtos.userdtos.*;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.DELETE;
import retrofit2.http.GET;
import retrofit2.http.Header;
import retrofit2.http.POST;
import retrofit2.http.PUT;

public interface ApiService
{
    @POST("/login")
    Call<ApiResponse> login(@Body LoginRequest request);

    @POST("/forgot-password")
    Call<ApiResponse> forgotPassword(@Body ForgotPasswordRequest request);

    @POST("/reset-password")
    Call<ApiResponse> resetPassword(@Body ResetPasswordRequest request);

    @POST("/signup")
    Call<SignupResponse> signup(@Body SignupRequest request);

    @GET("/account_details")
    Call<AccountDetailsResponse> getAccountDetails(@Header("Authorization") String token);

    @PUT("/update")
    Call<UpdateUserResponse> updateUser(@Header("Authorization") String token, @Body UpdateUserRequest request);

    @DELETE("/delete")
    Call<ApiResponse> deleteUser(@Header("Authorization") String token);
}
