package com.example.quotationfrontendapp.dtos.quotationdtos;

import java.util.List;

public class QuotesListResponse {
    private List<QuoteData> quotes;
    private String message;

    public List<QuoteData> getQuotes() {
        return quotes;
    }

    public String getMessage() {
        return message;
    }

    public static class QuoteData {
        private String quoteNumber;
        private double predictedTime;
        private String completionDate;

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
}