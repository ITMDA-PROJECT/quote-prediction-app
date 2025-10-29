package com.example.quotationfrontendapp.dtos.quotationdtos;

//Team 2 -- DtO for returning the quote_part data
public class QuotePartResponse {
    private int id;
    private int quote_id;
    private int part_id;

    private int quantity;
    private float cutting_length;
    private int num_pierces;
    private float calculated_part_time;

    private Part part;

    //Getters and Setters
    public int getId() {
        return id;
    }
    public int getQuote_id() {
        return quote_id;
    }
    public int getPart_id() {
        return part_id;
    }
    public int getQuantity() {
        return quantity;
    }
    public float getCutting_length() {
        return cutting_length;
    }
    public int getNum_pierces() {
        return num_pierces;
    }
    public float getCalculated_part_time() {
        return calculated_part_time;
    }
    public Part getPart() {
        return part;
    }
}
