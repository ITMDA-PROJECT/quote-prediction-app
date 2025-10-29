package com.example.quotationfrontendapp.dtos.userdtos;

public class LoginRequest
{
    private String username_or_email;
    private String password;

    public LoginRequest(String username_or_email, String password) {
        this.username_or_email = username_or_email;
        this.password = password;
    }

}
