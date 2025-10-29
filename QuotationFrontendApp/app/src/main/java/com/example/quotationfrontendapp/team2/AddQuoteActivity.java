package com.example.quotationfrontendapp.team2;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.quotationfrontendapp.R;
import com.example.quotationfrontendapp.api.quotationapi.QuotationApiClient;
import com.example.quotationfrontendapp.api.quotationapi.QuotationApiService;
import com.example.quotationfrontendapp.dtos.quotationdtos.Quotes;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;


public class AddQuoteActivity extends AppCompatActivity {
    private EditText etTurnaroundDays;
    private Button btnCreateQuote;
    //Instance of service
    private QuotationApiService quotationApiService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_add_quote);

        //Initialise views
        etTurnaroundDays = findViewById(R.id.etTurnaroundDays);
        btnCreateQuote = findViewById(R.id.btnCreateQuote);

        //Initialise service
        quotationApiService = QuotationApiClient.getService(this);

        //Set click listeners
        btnCreateQuote.setOnClickListener(v -> {
            String turnaroundDaysString = etTurnaroundDays.getText().toString().trim();

            //Input Validation
            if (turnaroundDaysString.isEmpty()) {
                Toast.makeText(this, "Please enter turnaround days!", Toast.LENGTH_SHORT).show();
            }
            double turnaroundDays;
            try {
                //Change to double
                turnaroundDays = Double.parseDouble(turnaroundDaysString);
            } catch (NumberFormatException e) {
                Toast.makeText(this, "Turnaround days must be a valid number!", Toast.LENGTH_SHORT).show();
                return;
            }

            //Create quote
            Quotes newQuote = new Quotes(turnaroundDays);

            //Send request to Quotation Service backend
            Call<Quotes> call = quotationApiService.createQuote(newQuote);
            call.enqueue(new Callback<Quotes>(){
                @Override
                public void onResponse(Call<Quotes> call, Response<Quotes> response) {
                    if (response.isSuccessful() && response.body() != null) {
                        Quotes createdQuote = response.body();
                        //Send confirmation message
                        Toast.makeText(AddQuoteActivity.this, "Quote created successfully!", Toast.LENGTH_SHORT).show();

                        //Redirect to AddPartActivity screen
                        Intent newIntent = new Intent(AddQuoteActivity.this, AddPartActivity.class);
                        //Send quote id to AddPartActivity
                        newIntent.putExtra("quote_id", createdQuote.getId());
                        newIntent.putExtra("quote_number", createdQuote.getQuoteNumber());
                        startActivity(newIntent);
                        finish();
                    }
                    else {
                        //Upon failure, alert admin
                        Toast.makeText(AddQuoteActivity.this, "Error creating quote!", Toast.LENGTH_SHORT).show();
                    }
                }

                @Override
                public void onFailure(Call<Quotes> call, Throwable t) {
                    //Upon failure, alert admin (indates failure with backend)
                    Toast.makeText(AddQuoteActivity.this, "Error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                }
            });
        });
    }
}
