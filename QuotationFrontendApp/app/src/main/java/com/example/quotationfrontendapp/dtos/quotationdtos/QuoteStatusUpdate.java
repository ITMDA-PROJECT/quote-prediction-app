package com.example.quotationfrontendapp.dtos.quotationdtos;

//Team 2 -- DTO for updating quote status (marking an In progress quote as complete)
public class QuoteStatusUpdate {
    private boolean new_quote_status;

    //Constructor
    public QuoteStatusUpdate(boolean new_quote_status) {
        this.new_quote_status = new_quote_status;
    }

    //Getters and Setters
    public boolean isNew_quote_status() {
        return new_quote_status;
    }
    public void setNew_quote_status(boolean new_quote_status) {
        this.new_quote_status = new_quote_status;
    }
}
