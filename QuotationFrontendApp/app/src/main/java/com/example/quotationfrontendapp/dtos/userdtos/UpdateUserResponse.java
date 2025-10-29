package com.example.quotationfrontendapp.dtos.userdtos;

public class UpdateUserResponse {
    private String message;
    private UpdatedData updated_data;

    public String getMessage() {
        return message;
    }

    public UpdatedData getUpdated_data() {
        return updated_data;
    }

    public static class UpdatedData {
        private String username;
        private String email;

        public String getUsername() {
            return username;
        }

        public String getEmail() {
            return email;
        }
    }
}
