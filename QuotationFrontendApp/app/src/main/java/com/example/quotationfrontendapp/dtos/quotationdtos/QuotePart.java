package com.example.quotationfrontendapp.dtos.quotationdtos;

import com.google.gson.annotations.SerializedName;

//Team 2 -- Quote Part DTO
public class QuotePart {
    @SerializedName("id")
    private int id;
    @SerializedName("quote_id")
    private int quoteId;             //FK in Pydantic
    @SerializedName("part_id")
    private int partId;                //FK in Pydantic
    @SerializedName("quantity")
    private int quantity;
    @SerializedName("cutting_length")
    private double cuttingLength;
    @SerializedName("num_pierces")
    private int numPierces;
    @SerializedName("calculated_part_time")
    private Double calculatedPartTime;        //Optional in pydantic basemodel
    @SerializedName("part")
    private Part part;                  //Optional nested Part object exists per quote part row

    //Constructors
    public QuotePart() {
    }
    public QuotePart(int quantity, double cuttingLength, int numPierces, int quoteId, int partId) {
        this.quantity = quantity;
        this.cuttingLength = cuttingLength;
        this.numPierces = numPierces;
        this.quoteId = quoteId;
        this.partId = partId;
    }

    //Getters and Setters
    public int getId() {
        return id;
    }
    public void setId(int id) {
        this.id = id;
    }
    public int getQuantity() {
        return quantity;
    }
    public void setQuantity(int quantity) {
        this.quantity = quantity;
    }
    public double getCuttingLength() {
        return cuttingLength;
    }
    public void setCuttingLength(double cuttingLength) {
        this.cuttingLength = cuttingLength;
    }
    public int getNumPierces() {
        return numPierces;
    }
    public void setNumPierces(int numPierces) {
        this.numPierces = numPierces;
    }
    public Double getCalculatedPartTime() {
        return calculatedPartTime;
    }
    public void setCalculatedPartTime(Double calculatedPartTime) {
        this.calculatedPartTime = calculatedPartTime;
    }
    public int getQuoteId() {
        return quoteId;
    }
    public void setQuoteId(int quoteId) {
        this.quoteId = quoteId;
    }
    public int getPartId() {
        return partId;
    }
    public void setPartId(int partId) {
        this.partId = partId;
    }
    public Part getPart() {
        return part;
    }
    public void setPart(Part part) {
        this.part = part;
    }
}
