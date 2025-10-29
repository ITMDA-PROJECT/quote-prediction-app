package com.example.quotationfrontendapp.dtos.quotationdtos;

//Team 3
public class PredictRequest {
    private String orderDate;      // Format: YYYY-MM-DD
    private String materialCode;
    private double actualTime;
    private int quantity;

    public PredictRequest(String orderDate, String materialCode, double actualTime, int quantity) {
        this.orderDate = orderDate;
        this.materialCode = materialCode;
        this.actualTime = actualTime;
        this.quantity = quantity;
    }
}
