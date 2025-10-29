package com.example.quotationfrontendapp.team1;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.example.quotationfrontendapp.R;
import com.example.quotationfrontendapp.api.userapi.ApiClient;
import com.example.quotationfrontendapp.api.userapi.ApiResponse;
import com.example.quotationfrontendapp.dtos.userdtos.LoginRequest;
import com.example.quotationfrontendapp.shared.Globals;
import com.example.quotationfrontendapp.team2.HomeActivity;


import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

import org.json.JSONObject;
import android.util.Log;

public class Login extends AppCompatActivity
{
    private EditText edtUsernameOrEmail, edtPassword;
    private Button btnLogin, btnRegister;
    private TextView tvForgotPassword;

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        // Link Java objects to XML elements
        edtUsernameOrEmail = findViewById(R.id.edtUsernameOrEmail);
        edtPassword = findViewById(R.id.edtPassword);
        btnLogin = findViewById(R.id.btnLogin);
        btnRegister = findViewById(R.id.btnRegister);
        tvForgotPassword = findViewById(R.id.tvForgotPassword);

        // Handle login button click
        btnLogin.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String userInput = edtUsernameOrEmail.getText().toString().trim();
                String password = edtPassword.getText().toString().trim();

                if (userInput.isEmpty() || password.isEmpty()) {
                    Toast.makeText(Login.this, "Please fill in all fields", Toast.LENGTH_SHORT).show();
                } else {
                    loginUser(userInput, password);
                }
            }
        });

        // Handle register button click (redirect to register page)
        btnRegister.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(Login.this, Register.class);
                startActivity(intent);
            }
        });

        tvForgotPassword.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(Login.this, ForgotPassword.class);
                startActivity(intent);
            }
        });
    }

    // Login function -- API call
    private void loginUser(String usernameOrEmail, String password)
    {
        btnLogin.setEnabled(false);
        // Call API Login
        LoginRequest request = new LoginRequest(usernameOrEmail, password);
        ApiClient.getInstance().login(request).enqueue(new Callback<ApiResponse>() {
            @Override
            public void onResponse(Call<ApiResponse> call, Response<ApiResponse> response) {
                btnLogin.setEnabled(true);
                if (response.isSuccessful() && response.body() != null){
                    ApiResponse apiResponse = response.body();
                    //Gets token and user id from response (admin_id // associated with admin_id)
                    String token = apiResponse.getToken();
                    int userId = apiResponse.getUserId();
                    String username = apiResponse.getUsername();


                    if (token != null && !token.isEmpty()) {
                        Globals globals = Globals.getInstance();
                        globals.setUsersId(userId);
                        globals.setUserName(username);
                        globals.setToken(token);

//                        //Save token persistently if Globals is not used
//                        saveToken(token);         //Call method at bottom to save to sharepref
//                        //SharedPreferences sharedPref = getSharedPreferences("MyAppPrefs", MODE_PRIVATE);
//                        //sharedPref.edit().putString("jwt_token", token).apply();

                        //Login Success --- Go to next screen
                        Intent intent = new Intent(Login.this, HomeActivity.class);
                        startActivity(intent);
                        finish();
                    }
                } else {
                    String errorMessage = "Login failed"; // fallback
                    try (ResponseBody errorBody = response.errorBody()) {
                        if (errorBody != null) {
                            String errorBodyStr = errorBody.string();
                            JSONObject jObjError = new JSONObject(errorBodyStr);
                            errorMessage = jObjError.getString("detail");
                        }
                    } catch (Exception e) {
                        Log.e("LoginError", "Failed to parse error body", e);
                    }

                    Toast.makeText(Login.this, errorMessage, Toast.LENGTH_LONG).show();
                }
            }

            @Override
            public void onFailure(Call<ApiResponse> call, Throwable t) {
                btnLogin.setEnabled(true);
                Toast.makeText(Login.this, "Error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    //Save token function
//    private void saveToken(String token)
//    {
//        SharedPreferences sharedPref = getSharedPreferences("MyAppPrefs", MODE_PRIVATE);
//        sharedPref.edit().putString("jwt_token", token).putString("username", usernameOrEmail).apply();
//    }
}

