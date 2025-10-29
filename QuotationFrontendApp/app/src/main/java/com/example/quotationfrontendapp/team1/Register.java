package com.example.quotationfrontendapp.team1;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.quotationfrontendapp.R;
import com.example.quotationfrontendapp.api.userapi.ApiClient;
import com.example.quotationfrontendapp.dtos.userdtos.SignupRequest;
import com.example.quotationfrontendapp.dtos.userdtos.SignupResponse;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class Register extends AppCompatActivity {
    private EditText edtUsername, edtEmail, edtPassword;
    private Button btnRegister, btnLogin;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_register);

        //Inialize Views
        edtUsername = findViewById(R.id.edtUsername);
        edtEmail = findViewById(R.id.edtEmail);
        edtPassword = findViewById(R.id.edtPassword);
        btnRegister = findViewById(R.id.btnRegister);
        btnLogin = findViewById(R.id.btnLogin);

        btnLogin.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(Register.this, Login.class);
                startActivity(intent);
            }
        });

        //Handle button click
        btnRegister.setOnClickListener(v -> {
            String username = edtUsername.getText().toString();
            String email = edtEmail.getText().toString();
            String password = edtPassword.getText().toString();

            //Validation
            if (validateInput(username, email, password)){
                SignupRequest request = new SignupRequest(username, email, password);

                ApiClient.getInstance().signup(request).enqueue(new Callback<SignupResponse>() {

                    @Override
                    public void onResponse(Call<SignupResponse> call, Response<SignupResponse> response) {
                        if (response.isSuccessful() && response.body() != null){
                            Toast.makeText(Register.this, response.body().getMessage(), Toast.LENGTH_LONG).show();
                        } else {
                            Toast.makeText(Register.this, "Registration failed", Toast.LENGTH_SHORT).show();
                        }
                    }

                    @Override
                    public void onFailure(Call<SignupResponse> call, Throwable t) {
                        Toast.makeText(Register.this, "Error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
            }



        });
    }

    private boolean validateInput(String username, String email, String password){
        if (username.isEmpty()){
            edtUsername.setError("Username required");
            edtUsername.requestFocus();
            return false;
        }
        if(email.isEmpty()){
            edtEmail.setError("Email required");
            edtEmail.requestFocus();
            return false;
        }
        if (password.isEmpty()){
            edtPassword.setError("Password required");
            edtPassword.requestFocus();
            return false;
        }
        return true;
    }
}