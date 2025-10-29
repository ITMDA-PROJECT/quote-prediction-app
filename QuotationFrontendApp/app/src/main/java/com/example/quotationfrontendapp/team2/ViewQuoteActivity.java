package com.example.quotationfrontendapp.team2;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.quotationfrontendapp.R;
import com.example.quotationfrontendapp.api.quotationapi.QuotationApiClient;
import com.example.quotationfrontendapp.api.quotationapi.QuotationApiService;
import com.example.quotationfrontendapp.dtos.quotationdtos.MLPredictionResponse;
import com.example.quotationfrontendapp.dtos.quotationdtos.Quotes;
import com.example.quotationfrontendapp.team3.ViewCurrentQuotes;

import java.util.Locale;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ViewQuoteActivity extends AppCompatActivity {
    //Declare
    private TextView tvQuoteNumber, tvTurnaroundDays;
    private RecyclerView rvQuoteParts;
    private Button btnGetTurnaround, btnViewAllQuotes;

    //instance of service
    private QuotationApiService apiService;
    private int quoteId;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_view_quote);

        //Initialise Views
        tvQuoteNumber = findViewById(R.id.tvQuoteNumber);
        tvTurnaroundDays = findViewById(R.id.tvTurnaroundDays);
        rvQuoteParts = findViewById(R.id.rvQuoteParts);
        btnGetTurnaround = findViewById(R.id.btnGetTurnaround);
        btnViewAllQuotes = findViewById(R.id.btnViewAllQuotes);

        //Initialise RecyclerView
        rvQuoteParts.setLayoutManager(new LinearLayoutManager(this));

        //Get quote ID from Intent
        quoteId = getIntent().getIntExtra("quote_id", -1);
        //Verify quote ID is valid
        if (quoteId == -1) {
            Toast.makeText(this, "Error: Quote ID not found.", Toast.LENGTH_LONG).show();
            finish();
            return;
        }

        //Initialize Retrofit Service
        apiService = QuotationApiClient.getService(this);

        //Call method to load quote details
        fetchQuoteDetails();

        //Onclick button listeners
        btnGetTurnaround.setOnClickListener(v -> getTurnaroundPrediction());    //call endpoint for turnaround prediction

        //Redirects to view all quotes page
        btnViewAllQuotes.setOnClickListener(v -> {
            Intent intent = new Intent(ViewQuoteActivity.this, ViewCurrentQuotes.class);
            startActivity(intent);
        });
    }

    //Method to get quote details via endpoint using quoteId
    private void fetchQuoteDetails() {
        apiService.getQuoteDetails(quoteId).enqueue(new Callback<Quotes>() {
            @Override
            public void onResponse(Call<Quotes> call, Response<Quotes> response) {
                if (response.isSuccessful() && response.body() != null) {
                    Quotes quote = response.body();
                    //Set quote number
                    tvQuoteNumber.setText("Quote Number: " + quote.getQuoteNumber());

                    //Notify adapter of quote parts
                    QuotePartsAdapter adapter = new QuotePartsAdapter(ViewQuoteActivity.this, quote.getQuoteParts(), quoteId);
                    rvQuoteParts.setAdapter(adapter);
                } else {
                    Toast.makeText(ViewQuoteActivity.this, "Failed to load quote details.", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<Quotes> call, Throwable t) {
                Toast.makeText(ViewQuoteActivity.this, "Fetch Quote details error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    //Method to get turnaround prediction via endpoint using quoteId
    private void getTurnaroundPrediction() {
        apiService.predictQuoteTime(quoteId).enqueue(new Callback<MLPredictionResponse>() {
            @Override
            public void onResponse(Call<MLPredictionResponse> call, Response<MLPredictionResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    MLPredictionResponse prediction = response.body();
                    //Set turnaround days
                    tvTurnaroundDays.setText(String.format(Locale.US, "%.2f", prediction.getPredicted_total_time()));
                    //Notify admin that prediction was successful
                    Toast.makeText(ViewQuoteActivity.this, "Prediction Successful", Toast.LENGTH_LONG).show();
                } else {
                    //Notify admin that prediction failed
                    Toast.makeText(ViewQuoteActivity.this, "Failed to get prediction.", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<MLPredictionResponse> call, Throwable t) {
                Toast.makeText(ViewQuoteActivity.this, "Fetch Prediction Error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }
}
