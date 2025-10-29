package com.example.quotationfrontendapp.dtos.quotationdtos;

//Team 2 -- Quote Part Add DTO (Request schema)
public class QuotePartAdd {
    //Existing: Just need part_id
    private Integer part_id;
    //Custom: Need part_description, material_code
    private String part_description;
    private String material_code;
    //Mandatory for quote linkage
    private int quantity;
    private double cutting_length;
    private int num_pierces;

    //Constructors
    public QuotePartAdd() {
    }
    //For existing part (Not used -- with catalogue idea)
//    public QuotePartAdd(int part_id, int quantity, double cutting_length, int num_pierces) {
//        this.part_id = part_id;
//        this.quantity = quantity;
//        this.cutting_length = cutting_length;
//        this.num_pierces = num_pierces;
//    }
    //For custom part
    public QuotePartAdd(String part_description, String material_code, double cutting_length, int quantity, int num_pierces) {
        //part_id created automatically on backend
        this.part_description = part_description;
        this.material_code = material_code;
        this.quantity = quantity;
        this.cutting_length = cutting_length;
        this.num_pierces = num_pierces;
    }

    //Getters and Setters
    public Integer getPart_id() {
        return part_id;
    }
    public void setPart_id(Integer part_id) {
        this.part_id = part_id;
    }
    public String getPart_description() {
        return part_description;
    }
    public void setPart_description(String part_description) {
        this.part_description = part_description;
    }
    public String getMaterial_code() {
        return material_code;
    }
    public void setMaterial_code(String material_code) {
        this.material_code = material_code;
    }
    public int getQuantity() {
        return quantity;
    }
    public void setQuantity(int quantity) {
        this.quantity = quantity;
    }
    public double getCutting_length() {
        return cutting_length;
    }
    public void setCutting_length(double cutting_length) {
        this.cutting_length = cutting_length;
    }
    public int getNum_pierces() {
        return num_pierces;
    }
    public void setNum_pierces(int num_pierces) {
        this.num_pierces = num_pierces;
    }
}
