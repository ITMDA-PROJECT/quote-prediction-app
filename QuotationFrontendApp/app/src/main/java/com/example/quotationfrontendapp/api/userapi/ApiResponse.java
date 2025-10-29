package com.example.quotationfrontendapp.api.userapi;

public class ApiResponse
{
    private String message;
    private String token;
    private int userId;
    private String username;


    public String getMessage() {
        return message;
    }

    public String getToken() {
        return token;
    }
    public int getUserId() { return userId; }
    public String getUsername() {return username;}
}
