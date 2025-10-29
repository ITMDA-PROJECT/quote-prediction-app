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
import com.example.quotationfrontendapp.dtos.quotationdtos.QuotePart;
import com.example.quotationfrontendapp.dtos.quotationdtos.QuotePartUpdate;
import com.example.quotationfrontendapp.dtos.quotationdtos.Quotes;

import java.util.Locale;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class EditPartActivity extends AppCompatActivity {
    //Declare fields
    private EditText etPartDescription, etCuttingLength, etQuantity, etNumPierces;
    private Spinner spMaterialCode;
    private Button btnSaveEdits;
    private TextView tvQuoteNumber;

    private QuotationApiService apiService;
    private int quotePartId;
    private int quoteId;                //Passing back to ViewQuoteActivity

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_edit_part);

        //Initialise Views
        etPartDescription = findViewById(R.id.etPartDescription);
        etCuttingLength = findViewById(R.id.etCuttingLength);
        etQuantity = findViewById(R.id.etQuantity);
        etNumPierces = findViewById(R.id.etNumPierces);
        spMaterialCode = findViewById(R.id.spMaterialCode);
        btnSaveEdits = findViewById(R.id.btnSaveEdits);
        tvQuoteNumber = findViewById(R.id.tvQuoteNumber);

        //The Part Description and Material Code are not editable in this flow
        etPartDescription.setEnabled(false);
        spMaterialCode.setEnabled(false);

        //Get quote_part_id from the intent
        quotePartId = getIntent().getIntExtra("quote_part_id", -1);
        if (quotePartId == -1) {
            //If quote_part_id is not found, show an error message and finish the activity
            Toast.makeText(this, "Error: Quote Part ID not found.", Toast.LENGTH_LONG).show();
            finish();
            return;
        }

        //Initialise Retrofit Service
        apiService = QuotationApiClient.getService(this);

        //Method to load the existing part data
        loadPartDetails();

        //Set onclick listener for the save button
        btnSaveEdits.setOnClickListener(v -> savePartEdits());
    }

    //method to get the part details by fetching entire quote
    private void loadPartDetails() {
        //Fetch the entire quote to get quote_part info (The backend API doesn't have a GET /quote-parts/{id} endpoint)
        quoteId = getIntent().getIntExtra("quote_id", -1);
        //Set the quote number in the TextView
        tvQuoteNumber.setText("Quote: " + quoteId);

        //If quote_id is not found, show an error message and finish the activity
        if (quoteId != -1) {
            apiService.getQuoteDetails(quoteId).enqueue(new Callback<Quotes>() {
                @Override
                public void onResponse(Call<Quotes> call, Response<Quotes> response) {
                    if (response.isSuccessful() && response.body() != null) {
                        //Iterate through response
                        for (QuotePart part : response.body().getQuoteParts()) {
                            //Get particular quote_part
                            if (part.getId() == quotePartId) {
                                //Set fields to retrieved quote_part data
                                populateFields(part);
                                break;
                            }
                        }
                    } else {
                        Toast.makeText(EditPartActivity.this, "Failed to load part details.", Toast.LENGTH_SHORT).show();
                    }
                }

                @Override
                public void onFailure(Call<com.example.quotationfrontendapp.dtos.quotationdtos.Quotes> call, Throwable t) {
                    Toast.makeText(EditPartActivity.this, "Response Error for getQuoteDetails (Editing Part): " + t.getMessage(), Toast.LENGTH_SHORT).show();
                }
            });
        }
    }

    //Method to populate the fields with the retrieved data
    private void populateFields(QuotePart part) {
        etPartDescription.setText(part.getPart().getPartDescription());
        etCuttingLength.setText(String.format(Locale.US, "%.1f", part.getCuttingLength()));
        etQuantity.setText(String.valueOf(part.getQuantity()));
        etNumPierces.setText(String.valueOf(part.getNumPierces()));

        //Adapter for the disabled spinner to show the material code
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, new String[]{part.getPart().getMaterialCode()});
        spMaterialCode.setAdapter(adapter);
    }

    //Method to save the edited part
    private void savePartEdits() {
        //editable Field variables
        String cuttingLengthString = etCuttingLength.getText().toString().trim();
        String quantityString = etQuantity.getText().toString().trim();
        String numPiercesString = etNumPierces.getText().toString().trim();

        //Input validation
        if (cuttingLengthString.isEmpty() || quantityString.isEmpty() || numPiercesString.isEmpty()) {
            Toast.makeText(this, "Please ensure all fields are filled.", Toast.LENGTH_SHORT).show();
            return;
        }

        //Transform input into correct datatype
        double cuttingLength = Double.parseDouble(cuttingLengthString);
        int quantity = Integer.parseInt(quantityString);
        int numPierces = Integer.parseInt(numPiercesString);

        //Create the DTO for the update request
        QuotePartUpdate updateDto = new QuotePartUpdate(quantity, cuttingLength, numPierces);

        //Call the update quote_part endpoint
        apiService.updateQuotePart(quotePartId, updateDto).enqueue(new Callback<QuotePart>() {
            @Override
            public void onResponse(Call<QuotePart> call, Response<QuotePart> response) {
                if (response.isSuccessful()) {
                    //Notify admin of successful update
                    Toast.makeText(EditPartActivity.this, "Part updated successfully!", Toast.LENGTH_SHORT).show();

                    //Navigate back to the ViewQuoteActivity and refresh it
                    Intent intent = new Intent(EditPartActivity.this, ViewQuoteActivity.class);
                    intent.putExtra("quote_id", quoteId);   //Needed for viewing

                    //Flags to clear the back stack and create a new instance of the activity
                    intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
                    startActivity(intent);
                    finish();                       //Close the EditPartActivity
                } else {
                    //Alert admin of failed update
                    Toast.makeText(EditPartActivity.this, "Failed to update part.", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<QuotePart> call, Throwable t) {
                Toast.makeText(EditPartActivity.this, "Response Error for updateQuotePart (Saving edits): " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }
}

