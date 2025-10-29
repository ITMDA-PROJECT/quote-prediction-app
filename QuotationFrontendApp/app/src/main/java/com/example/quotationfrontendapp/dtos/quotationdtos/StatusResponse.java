package com.example.quotationfrontendapp.dtos.quotationdtos;

//Team 3
public class StatusResponse {
    private String status;
    private boolean model_loaded;
    private boolean encoder_loaded;
    private String message;

    public String getStatus() {
        return status;
    }

    public boolean isModelLoaded() {
        return model_loaded;
    }

    public boolean isEncoderLoaded() {
        return encoder_loaded;
    }

    public String getMessage() {
        return message;
    }

    public boolean isReady() {
        return "ready".equals(status);
    }
}
