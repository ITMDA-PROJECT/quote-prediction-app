package com.example.quotationfrontendapp.dtos.quotationdtos;

//Team 3
public class PredictResponse {
    private double prediction;
    private InputData input;

    public double getPrediction() {
        return prediction;
    }

    public InputData getInput() {
        return input;
    }

    public static class InputData {
        private String orderDate;
        private String materialCode;
        private double actualTime;
        private int quantity;

        public String getOrderDate() {
            return orderDate;
        }

        public String getMaterialCode() {
            return materialCode;
        }

        public double getActualTime() {
            return actualTime;
        }

        public int getQuantity() {
            return quantity;
        }
    }
}
