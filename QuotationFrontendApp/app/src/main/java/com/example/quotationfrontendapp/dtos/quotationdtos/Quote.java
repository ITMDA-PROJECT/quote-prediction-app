package com.example.quotationfrontendapp.dtos.quotationdtos;

//Team 3
public class Quote {
    private String quoteNumber;
    private double predictedTime;
    private String completionDate;

    public Quote(String quoteNumber, double predictedTime, String completionDate) {
        this.quoteNumber = quoteNumber;
        this.predictedTime = predictedTime;
        this.completionDate = completionDate;
    }

    public String getQuoteNumber() {
        return quoteNumber;
    }

    public double getPredictedTime() {
        return predictedTime;
    }

    public String getCompletionDate() {
        return completionDate;
    }
}
