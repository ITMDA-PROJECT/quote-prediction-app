package com.example.quotationfrontendapp.dtos.quotationdtos;

//Team 3
public class TrainRequest {
    private String file_path;

    public TrainRequest() {
        // Empty constructor for optional file_path (uses default data)
    }

    public TrainRequest(String file_path) {
        this.file_path = file_path;
    }
}
