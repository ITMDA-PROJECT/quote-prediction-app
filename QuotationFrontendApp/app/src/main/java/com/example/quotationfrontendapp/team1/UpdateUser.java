package com.example.quotationfrontendapp.team1;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import com.example.quotationfrontendapp.api.userapi.ApiClient;
import com.example.quotationfrontendapp.R;
import com.example.quotationfrontendapp.api.userapi.ApiResponse;
import com.example.quotationfrontendapp.dtos.userdtos.AccountDetailsResponse;
import com.example.quotationfrontendapp.dtos.userdtos.UpdateUserRequest;
import com.example.quotationfrontendapp.dtos.userdtos.UpdateUserResponse;
import com.example.quotationfrontendapp.shared.Globals;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class UpdateUser extends AppCompatActivity {
    private EditText edtUsernameEdit, edtEmailEdit, edtPasswordEdit;
    private Button btnUpdateUser, btnDeleteUser;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_edit_user);

        edtUsernameEdit = findViewById(R.id.edtUsernameEdit);
        edtEmailEdit = findViewById(R.id.edtEmailEdit);
        edtPasswordEdit = findViewById(R.id.edtPasswordEdit);
        btnUpdateUser = findViewById(R.id.btnUpdateUser);
        btnDeleteUser = findViewById(R.id.btnDeleteUser);

        loadUserDetails();

        btnUpdateUser.setOnClickListener(v -> updateUser());
        btnDeleteUser.setOnClickListener(v -> deleteUser());
    }

    private void loadUserDetails() {
        ApiClient.getInstance().getAccountDetails("Bearer " + Globals.getInstance().getToken())
                .enqueue(new Callback<AccountDetailsResponse>() {
                    @Override
                    public void onResponse(Call<AccountDetailsResponse> call, Response<AccountDetailsResponse> response) {
                        if (response.isSuccessful() && response.body() != null) {
                            edtUsernameEdit.setText(response.body().getUsername());
                            edtEmailEdit.setText(response.body().getEmail());
                        } else {
                            Toast.makeText(UpdateUser.this, "Failed to load user details", Toast.LENGTH_SHORT).show();
                        }
                    }

                    @Override
                    public void onFailure(Call<AccountDetailsResponse> call, Throwable t) {
                        Toast.makeText(UpdateUser.this, "Error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
    }

    private void updateUser() {
        String username = edtUsernameEdit.getText().toString().trim();
        String email = edtEmailEdit.getText().toString().trim();
        String password = edtPasswordEdit.getText().toString().trim();

        btnUpdateUser.setEnabled(false);
        btnDeleteUser.setEnabled(false);

        UpdateUserRequest request = new UpdateUserRequest(username, email, password.isEmpty() ? null : password);

        ApiClient.getInstance().updateUser("Bearer " + Globals.getInstance().getToken(), request)
                .enqueue(new Callback<UpdateUserResponse>() {
                    @Override
                    public void onResponse(Call<UpdateUserResponse> call, Response<UpdateUserResponse> response) {

                        btnUpdateUser.setEnabled(true);
                        btnDeleteUser.setEnabled(true);

                        if (response.isSuccessful() && response.body() != null) {
                            Toast.makeText(UpdateUser.this, response.body().getMessage(), Toast.LENGTH_LONG).show();

                            // Update globals
                            Globals.getInstance().setUserName(response.body().getUpdated_data().getUsername());
                            Globals.getInstance().setEmail(response.body().getUpdated_data().getEmail());

                            //Clear password field
                            edtPasswordEdit.setText("");

                        } else {
                            Toast.makeText(UpdateUser.this, "Update failed", Toast.LENGTH_SHORT).show();
                        }
                    }

                    @Override
                    public void onFailure(Call<UpdateUserResponse> call, Throwable t) {
                        btnUpdateUser.setEnabled(true);
                        btnDeleteUser.setEnabled(true);

                        Toast.makeText(UpdateUser.this, "Error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
    }

    private void deleteUser() {
        btnUpdateUser.setEnabled(false);
        btnDeleteUser.setEnabled(false);

        ApiClient.getInstance().deleteUser("Bearer " + Globals.getInstance().getToken())
                .enqueue(new Callback<ApiResponse>() {
                    @Override
                    public void onResponse(Call<ApiResponse> call, Response<ApiResponse> response) {
                        btnUpdateUser.setEnabled(true);
                        btnDeleteUser.setEnabled(true);

                        if (response.isSuccessful() && response.body() != null) {
                            Toast.makeText(UpdateUser.this, response.body().getMessage(), Toast.LENGTH_LONG).show();

                            // Clear globals and go to login
                            Globals.getInstance().clearData();

                            Intent intent = new Intent(UpdateUser.this, Login.class);
                            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
                            startActivity(intent);
                            finish();
                        } else {
                            Toast.makeText(UpdateUser.this, "Failed to delete account", Toast.LENGTH_SHORT).show();
                        }
                    }

                    @Override
                    public void onFailure(Call<ApiResponse> call, Throwable t) {
                        btnUpdateUser.setEnabled(true);
                        btnDeleteUser.setEnabled(true);

                        Toast.makeText(UpdateUser.this, "Error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
    }
}
