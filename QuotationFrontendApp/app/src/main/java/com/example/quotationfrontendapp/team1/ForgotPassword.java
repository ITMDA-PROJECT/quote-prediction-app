package com.example.quotationfrontendapp.team1;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.Toast;

import com.example.quotationfrontendapp.api.userapi.ApiClient;
import com.example.quotationfrontendapp.api.userapi.ApiResponse;
import com.example.quotationfrontendapp.dtos.userdtos.ForgotPasswordRequest;
import com.example.quotationfrontendapp.R;

import org.json.JSONObject;

import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

import android.util.Log;

public class ForgotPassword extends AppCompatActivity
{
    private EditText emailInput;
    private Button sendLinkButton;
    private ImageView backButton;

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_forgot_password);

        emailInput = findViewById(R.id.emailInput);
        backButton = findViewById(R.id.btnBack);
        sendLinkButton = findViewById(R.id.sendLinkButton);

        backButton.setOnClickListener(v -> {
            Intent intent = new Intent(ForgotPassword.this, Login.class);
            startActivity(intent);
            finish();
        });

        sendLinkButton.setOnClickListener(v -> {
            String email = emailInput.getText().toString().trim();
            if (email.isEmpty()) {
                Toast.makeText(ForgotPassword.this, "Please enter your email", Toast.LENGTH_SHORT).show();
            } else {
                sendVerificationLink(email);
            }
        });
    }

    private void sendVerificationLink(String email)
    {
        sendLinkButton.setEnabled(false);
        ForgotPasswordRequest request = new ForgotPasswordRequest(email);

        ApiClient.getInstance().forgotPassword(request).enqueue(new Callback<ApiResponse>() {
            @Override
            public void onResponse(Call<ApiResponse> call, Response<ApiResponse> response) {
                sendLinkButton.setEnabled(true);

                if (response.isSuccessful() && response.body() != null) {
                    ApiResponse apiResponse = response.body();
                    Toast.makeText(ForgotPassword.this, apiResponse.getMessage(), Toast.LENGTH_LONG).show();
                } else {
                    // Try to parse API error message
                    String errorMessage = "Failed to send verification link";
                    try (ResponseBody errorBody = response.errorBody()) {
                        if (errorBody != null) {
                            String errorBodyStr = errorBody.string();
                            JSONObject jObjError = new JSONObject(errorBodyStr);
                            errorMessage = jObjError.getString("detail");
                        }
                    } catch (Exception e) {
                        Log.e("ForgotPassword", "Error parsing response", e);
                    }
                    Toast.makeText(ForgotPassword.this, errorMessage, Toast.LENGTH_LONG).show();
                }
            }

            @Override
            public void onFailure(Call<ApiResponse> call, Throwable t) {
                sendLinkButton.setEnabled(true);
                Toast.makeText(ForgotPassword.this, "Network error: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }
}