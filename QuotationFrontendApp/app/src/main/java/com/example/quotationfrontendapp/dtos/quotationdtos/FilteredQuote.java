package com.example.quotationfrontendapp.dtos.quotationdtos;

import com.google.gson.annotations.SerializedName;

public class FilteredQuote {
    @SerializedName("quote_number")
    private String quoteNumber;

    @SerializedName("predicted_total_time")
    private Double predictedTotalTime;

    @SerializedName("id")
    private int quoteId;

    // Constructors
    public FilteredQuote() {}

    public FilteredQuote(String quoteNumber, Double predictedTotalTime, int quoteId) {
        this.quoteId = quoteId;
        this.quoteNumber = quoteNumber;
        this.predictedTotalTime = predictedTotalTime;
    }

    // Getters and Setters
    public String getQuoteNumber() {
        // Ensure quote number always has WXQ prefix
//        if (quoteNumber != null && !quoteNumber.startsWith("WXQ")) {
//            return "WXQ" + quoteNumber;
//        }
        return quoteNumber != null ? quoteNumber : "N/A";
    }

    public void setQuoteNumber(String quoteNumber) {
        this.quoteNumber = quoteNumber;
    }

    public Double getPredictedTotalTime() {
        return predictedTotalTime;
    }

    public void setPredictedTotalTime(Double predictedTotalTime) {
        this.predictedTotalTime = predictedTotalTime;
    }

    public int getQuoteId() {
        return quoteId;
    }

    public void setQuoteId(int quoteId) {
        this.quoteId = quoteId;
    }

    // Helper method to format time for display
    public String getFormattedTime() {
        if (predictedTotalTime == null) {
            return "N/A";
        }
        return String.format("%.1f days", predictedTotalTime);
    }
}
