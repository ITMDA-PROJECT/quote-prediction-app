package com.example.quotationfrontendapp.dtos.quotationdtos;

//Team 2 -- Material DTO
public class Material {
    private String material_code;
    private double cutting_speed;
    private double drilling_time;
    private double setup_time;

    //Constructors
    public Material() {
    }
    public Material(String material_code, double cutting_speed, double drilling_time, double setup_time) {
        this.material_code = material_code;
        this.cutting_speed = cutting_speed;
        this.drilling_time = drilling_time;
        this.setup_time = setup_time;
    }

    //Getters and Setters
    public String getMaterial_code() {
        return material_code;
    }
    public void setMaterial_code(String material_code) {
        this.material_code = material_code;
    }
    public double getCutting_speed() {
        return cutting_speed;
    }
    public void setCutting_speed(double cutting_speed) {
        this.cutting_speed = cutting_speed;
    }
    public double getDrilling_time() {
        return drilling_time;
    }
    public void setDrilling_time(double drilling_time) {
        this.drilling_time = drilling_time;
    }
    public double getSetup_time() {
        return setup_time;
    }
    public void setSetup_time(double setup_time) {
        this.setup_time = setup_time;
    }

}
