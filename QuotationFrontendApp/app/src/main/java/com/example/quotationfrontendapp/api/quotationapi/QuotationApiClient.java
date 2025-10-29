package com.example.quotationfrontendapp.api.quotationapi;

import android.content.Context;
import android.content.SharedPreferences;

import com.example.quotationfrontendapp.shared.Globals;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.logging.HttpLoggingInterceptor;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

//Team 2 -- Quotation API Client (with JWT integration)
public class QuotationApiClient {
    //Emulator to local server
    private static final String BASE_URL = "http://10.0.2.2:8002";     //Add / after ??
    //Retrofit instance
    private static Retrofit retrofit;

    public static Retrofit getClient(Context context) {
        //Get token from Globals (automatically injected)
        String jwtToken = Globals.getInstance().getToken(); //Logged in token

//If Globals fails, try to get from shared preferences
//        if (jwtToken == null || jwtToken.isEmpty()) {
//            SharedPreferences prefs = context.getSharedPreferences("MyAppPrefs", Context.MODE_PRIVATE);
//            jwtToken = prefs.getString("jwt_token", "");
//        }

        OkHttpClient.Builder httpClient = new OkHttpClient.Builder();

        //Add JWT token interceptor if token exists (for JWT token injection in header)
        if (jwtToken != null && !jwtToken.isEmpty()) {
            httpClient.addInterceptor(chain -> {
                Request original = chain.request();
                Request.Builder builder = original.newBuilder().header("Authorization", "Bearer " + jwtToken);         //Aligns with quotation service backend
                return chain.proceed(builder.build());
        });
    }

        //Add logging for debugging (remove for production)
        HttpLoggingInterceptor logging = new HttpLoggingInterceptor();
        logging.setLevel(HttpLoggingInterceptor.Level.BODY);
        httpClient.addInterceptor(logging);

        //New retrofit client with JWT token injection
        retrofit = new Retrofit.Builder().baseUrl(BASE_URL).addConverterFactory(GsonConverterFactory.create()).client(httpClient.build()).build();
        return retrofit;
    }

        //Method to get the service
        public static QuotationApiService getService(Context context) {
            return getClient(context).create(QuotationApiService.class);
        }
}

