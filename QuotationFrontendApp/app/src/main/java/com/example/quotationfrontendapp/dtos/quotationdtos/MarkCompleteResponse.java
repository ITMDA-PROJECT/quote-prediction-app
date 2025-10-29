package com.example.quotationfrontendapp.dtos.quotationdtos;

public class MarkCompleteResponse {
    private boolean success;
    private String message;
    private String quoteNumber;

    public boolean isSuccess() {
        return success;
    }

    public String getMessage() {
        return message;
    }

    public String getQuoteNumber() {
        return quoteNumber;
    }
}