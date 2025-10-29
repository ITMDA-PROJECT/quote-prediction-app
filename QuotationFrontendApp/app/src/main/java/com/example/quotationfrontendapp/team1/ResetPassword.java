package com.example.quotationfrontendapp.team1;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.Toast;

import com.example.quotationfrontendapp.R;
import com.example.quotationfrontendapp.api.userapi.ApiClient;
import com.example.quotationfrontendapp.api.userapi.ApiResponse;
import com.example.quotationfrontendapp.dtos.userdtos.ResetPasswordRequest;

import org.json.JSONObject;

import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import android.util.Log;

public class ResetPassword extends AppCompatActivity
{
    private EditText newPasswordInput, confirmPasswordInput;
    private Button resetButton;
    private String token;
    private ImageView backButton;

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_reset_password);

        newPasswordInput = findViewById(R.id.newPasswordInput);
        confirmPasswordInput = findViewById(R.id.confirmPasswordInput);
        resetButton = findViewById(R.id.resetButton);
        backButton = findViewById(R.id.btnBack);

        // Get token from intent/deep link
        Intent intent = getIntent();
        Uri data = intent.getData();
        if (data != null && data.getQueryParameter("token") != null) {
            token = data.getQueryParameter("token");
        } else {
            Toast.makeText(this, "Invalid or missing token.", Toast.LENGTH_LONG).show();
            finish();
            return;
        }

        backButton.setOnClickListener(v -> {
            Intent intent1 = new Intent(ResetPassword.this, Login.class);
            startActivity(intent1);
            finish();
        });

        resetButton.setOnClickListener(v -> {
            String newPassword = newPasswordInput.getText().toString().trim();
            String confirmPassword = confirmPasswordInput.getText().toString().trim();

            if (newPassword.isEmpty() || confirmPassword.isEmpty()) {
                Toast.makeText(this, "Please fill in all fields", Toast.LENGTH_SHORT).show();
            } else if (!newPassword.equals(confirmPassword)) {
                Toast.makeText(this, "Passwords do not match", Toast.LENGTH_SHORT).show();
            } else {
                resetPassword(token, newPassword);
            }
        });
    }

    private void resetPassword(String token, String newPassword) {
        resetButton.setEnabled(false);

        ResetPasswordRequest request = new ResetPasswordRequest(token, newPassword);

        ApiClient.getInstance().resetPassword(request).enqueue(new Callback<ApiResponse>() {
            @Override
            public void onResponse(Call<ApiResponse> call, Response<ApiResponse> response) {
                resetButton.setEnabled(true);

                if (response.isSuccessful() && response.body() != null) {
                    ApiResponse apiResponse = response.body();
                    Toast.makeText(ResetPassword.this, apiResponse.getMessage(), Toast.LENGTH_LONG).show();

                    // Go back to login screen
                    Intent intent = new Intent(ResetPassword.this, Login.class);
                    startActivity(intent);
                    finish();
                } else {
                    String errorMessage = "Password reset failed";
                    try (ResponseBody errorBody = response.errorBody()) {
                        if (errorBody != null) {
                            String errorBodyStr = errorBody.string();
                            JSONObject jObjError = new JSONObject(errorBodyStr);
                            errorMessage = jObjError.getString("detail");
                        }
                    } catch (Exception e) {
                        Log.e("ResetPassword", "Error parsing response", e);
                    }
                    Toast.makeText(ResetPassword.this, errorMessage, Toast.LENGTH_LONG).show();
                }
            }

            @Override
            public void onFailure(Call<ApiResponse> call, Throwable t) {
                resetButton.setEnabled(true);
                Toast.makeText(ResetPassword.this, "Network error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }
}