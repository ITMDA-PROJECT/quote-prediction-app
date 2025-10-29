package com.example.quotationfrontendapp.dtos.userdtos;

public class UpdateUserRequest {
    private String username;
    private String email;
    private String password;

    public UpdateUserRequest(String username, String email, String password) {
        this.username = username;
        this.email = email;
        this.password = password;
    }
}
