package com.example.quotationfrontendapp.shared;

import com.example.quotationfrontendapp.team2.HomeActivity;

//Team 1
public class Globals {
    private static Globals instance;

    private int usersId;    //admin set from login response from user service
    private String userName;
    private String email;
    private String token;   //token set from login response from user service


    private Globals() {}

    public static synchronized Globals getInstance() { //synchronized' for thread safety
        if (instance == null) {
            instance = new Globals();
        }
        return instance;
    }

    //Team 2 added to clear Globals file (Logout from data layer)
    public void clearData() {
        //Reset data in instance
        this.usersId = 0;
        this.userName = null;
        this.email = null;
        this.token = null;
    }

    public int getUsersId() {
        return usersId;
    }

    public void setUsersId(int usersId) {
        this.usersId = usersId;
    }

    public String getUserName() {
        return userName;
    }

    public void setUserName(String userName) {
        this.userName = userName;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getToken() {
        return token;
    }

    public void setToken(String token) {
        this.token = token;
    }
}
