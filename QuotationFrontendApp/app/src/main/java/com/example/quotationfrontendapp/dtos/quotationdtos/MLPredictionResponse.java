package com.example.quotationfrontendapp.dtos.quotationdtos;

import java.util.Map;

//Team 2 -- ML Response DTO
public class MLPredictionResponse {
    public Double predicted_total_time;     //Optional for no value returned (in terms of days)
    public Map<String, Object> input;
    public String message;                  //Optional

    //Getters and setters
    public Double getPredicted_total_time() {
        return predicted_total_time;
    }
    public void setPredicted_total_time(Double predicted_total_time) {
        this.predicted_total_time = predicted_total_time;
    }
}

