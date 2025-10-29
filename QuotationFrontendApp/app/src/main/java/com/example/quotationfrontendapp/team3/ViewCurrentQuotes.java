package com.example.quotationfrontendapp.team3;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.quotationfrontendapp.R;
import com.example.quotationfrontendapp.api.quotationapi.QuotationApiService;
import com.example.quotationfrontendapp.team1.Login;
import com.example.quotationfrontendapp.team2.HomeActivity;
import com.example.quotationfrontendapp.team2.AddQuoteActivity;
import com.example.quotationfrontendapp.team3.adapters.CurrentQuoteAdapter;
import com.example.quotationfrontendapp.api.quotationapi.QuotationApiClient;
import com.example.quotationfrontendapp.dtos.quotationdtos.FilteredQuote;
import com.example.quotationfrontendapp.dtos.quotationdtos.QuoteStatusUpdate;
import com.example.quotationfrontendapp.dtos.quotationdtos.Quotes;

import java.util.ArrayList;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ViewCurrentQuotes extends AppCompatActivity {

    private RecyclerView quotesRecyclerView;
    private CurrentQuoteAdapter quoteAdapter;
    private Button btnAddNewQuote, btnLogout, btnViewCompleted, btnBack;
    private TextView txtEmptyState;
    private List<FilteredQuote> quoteList;
    private QuotationApiService quotationApiService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_view_current_quotes);

        // Initialize Views
        quotesRecyclerView = findViewById(R.id.quotesRecyclerView);
        btnAddNewQuote = findViewById(R.id.btnAddNewQuote);
        btnLogout = findViewById(R.id.btnLogout);
        btnViewCompleted = findViewById(R.id.btnViewCompleted);
        btnBack = findViewById(R.id.btnBack);
        txtEmptyState = findViewById(R.id.txtEmptyState);

        quotationApiService = QuotationApiClient.getService(this);

        // Setup RecyclerView
        quotesRecyclerView.setLayoutManager(new LinearLayoutManager(this));
        quoteList = new ArrayList<>();
        quoteAdapter = new CurrentQuoteAdapter(quoteList);
        quotesRecyclerView.setAdapter(quoteAdapter);

        // Set click listener for marking quotes as complete
        quoteAdapter.setOnQuoteClickListener(this::handleMarkAsComplete);

        // Load quotes
        loadInProgressQuotes();

        // Button Listeners
        btnAddNewQuote.setOnClickListener(v -> {
            Intent intent = new Intent(this, AddQuoteActivity.class);
            startActivity(intent);
        });

        btnViewCompleted.setOnClickListener(v -> {
            Intent intent = new Intent(ViewCurrentQuotes.this, ViewCompletedQuotes.class);
            startActivity(intent);
        });

        btnLogout.setOnClickListener(v -> {
            Toast.makeText(ViewCurrentQuotes.this, "Logging out...", Toast.LENGTH_SHORT).show();
            Intent intent = new Intent(ViewCurrentQuotes.this, Login.class);
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
            startActivity(intent);
            finish();
        });

        btnBack.setOnClickListener(v -> {
            Intent intent = new Intent(ViewCurrentQuotes.this, HomeActivity.class);
            startActivity(intent);
            finish(); // Optional: closes current activity
        });
    }

    private void loadInProgressQuotes() {
        // Show loading state
        txtEmptyState.setText("Loading in-progress quotes...");
        txtEmptyState.setVisibility(View.VISIBLE);
        quotesRecyclerView.setVisibility(View.GONE);

        // Fetch in-progress quotes using correct endpoint
        quotationApiService.getInProgressQuotes().enqueue(new Callback<List<FilteredQuote>>() {
            @Override
            public void onResponse(Call<List<FilteredQuote>> call, Response<List<FilteredQuote>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    quoteList = response.body();

                    // Update UI based on data
                    if (quoteList.isEmpty()) {
                        txtEmptyState.setText("No in-progress quotes yet");
                        txtEmptyState.setVisibility(View.VISIBLE);
                        quotesRecyclerView.setVisibility(View.GONE);
                    } else {
                        txtEmptyState.setVisibility(View.GONE);
                        quotesRecyclerView.setVisibility(View.VISIBLE);
                        quoteAdapter.updateQuotes(quoteList);

                        Toast.makeText(ViewCurrentQuotes.this,
                                "Loaded " + quoteList.size() + " in-progress quotes",
                                Toast.LENGTH_SHORT).show();
                    }
                } else {
                    txtEmptyState.setText("Failed to load quotes");
                    Toast.makeText(ViewCurrentQuotes.this,
                            "Error: " + response.message(),
                            Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<List<FilteredQuote>> call, Throwable t) {
                txtEmptyState.setText("Connection error");
                txtEmptyState.setVisibility(View.VISIBLE);
                quotesRecyclerView.setVisibility(View.GONE);

                Toast.makeText(ViewCurrentQuotes.this,
                        "Error: " + t.getMessage(),
                        Toast.LENGTH_LONG).show();
            }
        });
    }

    private void handleMarkAsComplete(FilteredQuote quote, int position) {
        // Show confirmation dialog
        new AlertDialog.Builder(this)
                .setTitle("Mark as Complete")
                .setMessage("Mark quote " + quote.getQuoteNumber() + " as complete?")
                .setPositiveButton("Yes", (dialog, which) -> markQuoteAsComplete(quote.getQuoteId(), position))
                .setNegativeButton("No", null)
                .show();
    }

    private void markQuoteAsComplete(int quoteId, int position) {
        // Create status update object (true = completed)
        QuoteStatusUpdate statusUpdate = new QuoteStatusUpdate(true);

        // Call API to update quote status
        quotationApiService.updateQuoteStatus(quoteId, statusUpdate).enqueue(new Callback<Quotes>() {
            @Override
            public void onResponse(Call<Quotes> call, Response<Quotes> response) {
                if (response.isSuccessful()) {
                    // Remove from current list
                    quoteAdapter.removeItem(position);

                    Toast.makeText(ViewCurrentQuotes.this,
                            "Quote marked as complete!",
                            Toast.LENGTH_SHORT).show();

                    // Check if list is now empty
                    if (quoteAdapter.getItemCount() == 0) {
                        txtEmptyState.setText("No in-progress quotes yet");
                        txtEmptyState.setVisibility(View.VISIBLE);
                        quotesRecyclerView.setVisibility(View.GONE);
                    }
                } else {
                    Toast.makeText(ViewCurrentQuotes.this,
                            "Failed to update quote status",
                            Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<Quotes> call, Throwable t) {
                Toast.makeText(ViewCurrentQuotes.this,
                        "Error: " + t.getMessage(),
                        Toast.LENGTH_SHORT).show();
            }
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
//        loadInProgressQuotes();
    }
}