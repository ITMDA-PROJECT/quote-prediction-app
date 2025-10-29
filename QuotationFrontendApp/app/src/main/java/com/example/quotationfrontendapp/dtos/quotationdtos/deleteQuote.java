package com.example.quotationfrontendapp.dtos.quotationdtos;

import com.google.gson.annotations.SerializedName;

public class deleteQuote {
    @SerializedName("id")
    private int id;

    public deleteQuote(int id) {
        this.id = id;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }
}


