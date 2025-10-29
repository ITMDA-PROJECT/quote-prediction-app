package com.example.quotationfrontendapp.dtos.quotationdtos;

import com.google.gson.annotations.SerializedName;

//Team 2 -- Updating a quote part DTO
public class QuotePartUpdate {
    @SerializedName("quantity")
    private int quantity;
    @SerializedName("cutting_length")
    private double cuttingLength;
    @SerializedName("num_pierces")
    private int numPierces;

    public QuotePartUpdate(int quantity, double cuttingLength, int numPierces) {
        this.quantity = quantity;
        this.cuttingLength = cuttingLength;
        this.numPierces = numPierces;
    }
}
