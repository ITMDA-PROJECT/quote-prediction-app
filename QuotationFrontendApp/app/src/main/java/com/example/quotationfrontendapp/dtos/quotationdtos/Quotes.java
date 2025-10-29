package com.example.quotationfrontendapp.dtos.quotationdtos;

import com.google.gson.annotations.SerializedName;

import java.util.List;

//Team 2 -- Quote DTO (Serialised to match pydantic)
public class Quotes {
    @SerializedName("id")
    private int id;
    @SerializedName("quote_number")
    private String quoteNumber;                        //Auto-generated upon quote creation
    @SerializedName("calculated_total_time")
    private Double calculatedTotalTime;
    @SerializedName("predicted_total_time")
    private Double predictedTotalTime;
    @SerializedName("turn_around_days")
    private double turnAroundDays;
    @SerializedName("admin_id")
    private Integer adminId;                           //Optional, but retrieved from Global
    @SerializedName("order_date")
    private String orderDate;                         //Auto-generated upon quote creation
    @SerializedName("quote_status")
    private boolean quoteStatus;                      //Auto-initialised to False (In Progress) upon quote creation
    @SerializedName("quote_parts")
    private List<QuotePart> quoteParts;

    //Constructors
    public Quotes() {
    }
    public Quotes(double turnAroundDays) {
        this.turnAroundDays = turnAroundDays;
    }

    //Getters and Setters (updated to match new field names)
    public int getId() {
        return id;
    }
    public void setId(int id) {
        this.id = id;
    }
    public double getTurnAroundDays() {
        return turnAroundDays;
    }
    public void setTurnAroundDays(double turnAroundDays) {
        this.turnAroundDays = turnAroundDays;
    }
    public Integer getAdminId() {
        return adminId;
    }
    public void setAdminId(Integer adminId) {
        this.adminId = adminId;
    }
    public String getQuoteNumber() {
        return quoteNumber;
    }
    public void setQuoteNumber(String quoteNumber) {
        this.quoteNumber = quoteNumber;
    }
    public Double getCalculatedTotalTime() {
        return calculatedTotalTime;
    }
    public void setCalculatedTotalTime(Double calculatedTotalTime) {
        this.calculatedTotalTime = calculatedTotalTime;
    }
    public Double getPredictedTotalTime() {
        return predictedTotalTime;
    }
    public void setPredictedTotalTime(Double predictedTotalTime) {
        this.predictedTotalTime = predictedTotalTime;
    }
    public String getOrderDate() {
        return orderDate;
    }
    public void setOrderDate(String orderDate) {
        this.orderDate = orderDate;
    }
    public boolean isQuoteStatus() {
        return quoteStatus;
    }
    public void setQuoteStatus(boolean quoteStatus) {
        this.quoteStatus = quoteStatus;
    }
    public List<QuotePart> getQuoteParts() {
        return quoteParts;
    }
    public void setQuoteParts(List<QuotePart> quoteParts) {
        this.quoteParts = quoteParts;
    }
}
