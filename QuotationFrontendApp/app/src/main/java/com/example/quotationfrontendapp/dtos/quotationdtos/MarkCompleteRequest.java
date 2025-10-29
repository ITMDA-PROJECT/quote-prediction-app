package com.example.quotationfrontendapp.dtos.quotationdtos;

public class MarkCompleteRequest {
    private String quoteNumber;

    public MarkCompleteRequest(String quoteNumber) {
        this.quoteNumber = quoteNumber;
    }

    public String getQuoteNumber() {
        return quoteNumber;
    }
}