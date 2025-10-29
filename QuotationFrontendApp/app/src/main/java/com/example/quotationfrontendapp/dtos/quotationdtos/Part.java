package com.example.quotationfrontendapp.dtos.quotationdtos;

import com.google.gson.annotations.SerializedName;

//Team 2 -- DTO for returning part data (+ material data associated with material_code attached to part)
public class Part {
    @SerializedName("id")
    private int id;                         //For Read in pydantic schema
    @SerializedName("part_description")
    private String partDescription;
    @SerializedName("material_code")
    private String materialCode;
    @SerializedName("material")
    private Material material;              //Nested Material object optional for Read in pydantic schema backend

    //Constructors
    public Part() {
    }
    public Part(int id, String partDescription, String materialCode) {
        this.id = id;
        this.partDescription = partDescription;
        this.materialCode = materialCode;
    }

    //Getters and Setters
    public int getId() {
        return id;
    }
    public void setId(int id) {
        this.id = id;
    }
    public String getPartDescription() {
        return partDescription;
    }
    public void setPartDescription(String partDescription) {
        this.partDescription = partDescription;
    }
    public String getMaterialCode() {
        return materialCode;
    }
    public void setMaterialCode(String materialCode) {
        this.materialCode = materialCode;
    }
    public Material getMaterial() {
        return material;
    }
    public void setMaterial(Material material) {
        this.material = material;
    }
}
