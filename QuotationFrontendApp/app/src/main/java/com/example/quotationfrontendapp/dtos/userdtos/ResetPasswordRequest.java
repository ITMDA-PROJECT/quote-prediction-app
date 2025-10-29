package com.example.quotationfrontendapp.dtos.userdtos;

public class ResetPasswordRequest
{
    private String token;
    private String new_password;

    public ResetPasswordRequest(String token, String new_password)
    {
        this.token = token;
        this.new_password = new_password;
    }

    public String getToken()
    {
        return token;
    }
    public String getNew_password()
    {
        return new_password;
    }
}
