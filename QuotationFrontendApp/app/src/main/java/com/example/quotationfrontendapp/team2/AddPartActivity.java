package com.example.quotationfrontendapp.team2;

import android.content.Intent;
import android.os.Bundle;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.quotationfrontendapp.R;
import com.example.quotationfrontendapp.api.quotationapi.QuotationApiClient;
import com.example.quotationfrontendapp.api.quotationapi.QuotationApiService;
import com.example.quotationfrontendapp.dtos.quotationdtos.Material;
import com.example.quotationfrontendapp.dtos.quotationdtos.QuotePart;
import com.example.quotationfrontendapp.dtos.quotationdtos.QuotePartAdd;

import java.util.ArrayList;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class AddPartActivity extends AppCompatActivity {
    private EditText etPartDescription, etCuttingLength, etQuantity, etNumPierces;
    private Spinner spMaterialCode;
    private Button btnAddPart, btnViewQuote;
    private TextView tvQuoteNumber;

    private QuotationApiService quotationApiService;
    //List of material codes
    private List<String> materialcodes = new ArrayList<>();
    private String quoteNumber;
    private int quoteId;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_add_part);

        //Initialise views
        etPartDescription = findViewById(R.id.etPartDescription);
        etCuttingLength = findViewById(R.id.etCuttingLength);
        etQuantity = findViewById(R.id.etQuantity);
        etNumPierces = findViewById(R.id.etNumPierces);
        spMaterialCode = findViewById(R.id.spMaterialCode);
        btnAddPart = findViewById(R.id.btnAddPart);
        btnViewQuote = findViewById(R.id.btnViewQuote);
        tvQuoteNumber = findViewById(R.id.tvQuoteNumber);

        //Get quoteId and quote number from intent
        quoteId = getIntent().getIntExtra("quote_id", -1);
        quoteNumber = getIntent().getStringExtra("quote_number");
        tvQuoteNumber.setText("Quote Number: " + quoteNumber);

        //Initialise service
        quotationApiService = QuotationApiClient.getService(this);

        //Populate material code drop down
        loadMaterialCodes();

        //Set button click listeners
        //Add part button click listener
        btnAddPart.setOnClickListener(v ->
            //Method to add part
            addPart()
        );

        //View quote button click listener
        btnViewQuote.setOnClickListener(v -> {
            Intent viewIntent = new Intent(AddPartActivity.this, ViewQuoteActivity.class);
            viewIntent.putExtra("quote_id", quoteId);
            startActivity(viewIntent);
        });
    }

    //Method to use endpoint to populate drop down with list of materialcodes
    private void loadMaterialCodes() {
        quotationApiService.getAllMaterials().enqueue(new Callback<List<Material>>() {
            @Override
            public void onResponse(Call<List<Material>> call, Response<List<Material>> response) {
                //If resultset is returned
                if (response.isSuccessful() && response.body() != null) {
                    //Iterate through each material
                    for (Material material : response.body()) {
                        //Add material code ONLY to list
                        materialcodes.add(material.getMaterial_code());
                    }

                    //Notify adapter
                    ArrayAdapter<String> adapter = new ArrayAdapter<>(AddPartActivity.this, android.R.layout.simple_spinner_item, materialcodes);
                    adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
                    spMaterialCode.setAdapter(adapter);
                } else {
                    //Notify error
                    Toast.makeText(AddPartActivity.this, "Failed to load materials", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<List<Material>> call, Throwable t) {
                //Notify error
                Toast.makeText(AddPartActivity.this, "Failed to load materials", Toast.LENGTH_SHORT).show();
            }

        });
    }
    //Method to take in input and send via endpoint to add part to quote
    public void addPart() {
        //Field variables
        String partDescription = etPartDescription.getText().toString().trim();
        String materialCode = spMaterialCode.getSelectedItem() != null ? spMaterialCode.getSelectedItem().toString() : "";
        String cuttingLengthString = etCuttingLength.getText().toString().trim();
        String quantityString = etQuantity.getText().toString().trim();
        String numPiercesString = etNumPierces.getText().toString().trim();

        //Input validation
        if (partDescription.isEmpty() || materialCode.isEmpty() || cuttingLengthString.isEmpty() || quantityString.isEmpty() || numPiercesString.isEmpty()) {
            Toast.makeText(this, "Please fill in all fields", Toast.LENGTH_SHORT).show();
            return;
        }

        //Transform input into correct datatype
        double cuttingLength = Double.parseDouble(cuttingLengthString);
        int quantity = Integer.parseInt(quantityString);
        int numPierces = Integer.parseInt(numPiercesString);

        //DTO
        QuotePartAdd partAdd = new QuotePartAdd(partDescription, materialCode, cuttingLength, quantity, numPierces);

        //Use endpoint
        quotationApiService.addPartToQuote(quoteId, partAdd).enqueue(new Callback<QuotePart>() {
            @Override
            public void onResponse(Call<QuotePart> call, Response<QuotePart> response) {
                if (response.isSuccessful()) {
                    Toast.makeText(AddPartActivity.this, "Part added successfully", Toast.LENGTH_SHORT).show();
                    clearFields();
                } else {
                    Toast.makeText(AddPartActivity.this, "Failed to add part", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<QuotePart> call, Throwable t) {
                Toast.makeText(AddPartActivity.this, "Error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    //Method to clear fields
    private void clearFields(){
        etPartDescription.setText("");
        etCuttingLength.setText("");
        etQuantity.setText("");
        etNumPierces.setText("");
        spMaterialCode.setSelection(0);
    }
}
