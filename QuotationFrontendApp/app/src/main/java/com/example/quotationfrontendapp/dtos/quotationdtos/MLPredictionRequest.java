package com.example.quotationfrontendapp.dtos.quotationdtos;

//Team 2 -- DTO for requesting a estimate from ML model
public class MLPredictionRequest {
    public String order_date;
    public String material_code;
    public double calculated_total_time;
    public int quantity;

    public String getOrder_date() {
        return order_date;
    }
    public void setOrder_date(String order_date) {
        this.order_date = order_date;
    }
    public String getMaterial_code() {
        return material_code;
    }
    public void setMaterial_code(String material_code) {
        this.material_code = material_code;
    }
    public double getCalculated_total_time() {
        return calculated_total_time;
    }
    public void setCalculated_total_time(double calculated_total_time) {
        this.calculated_total_time = calculated_total_time;
    }
    public int getQuantity() {
        return quantity;
    }
    public void setQuantity(int quantity) {
        this.quantity = quantity;
    }
}
