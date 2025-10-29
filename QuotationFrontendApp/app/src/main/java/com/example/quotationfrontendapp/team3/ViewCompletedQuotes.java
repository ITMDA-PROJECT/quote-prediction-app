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
import com.example.quotationfrontendapp.team2.AddQuoteActivity;
import com.example.quotationfrontendapp.team2.HomeActivity;
import com.example.quotationfrontendapp.team3.adapters.QuoteAdapter; // YOUR adapter
import com.example.quotationfrontendapp.api.quotationapi.QuotationApiClient;
import com.example.quotationfrontendapp.dtos.quotationdtos.FilteredQuote;

import java.util.ArrayList;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ViewCompletedQuotes extends AppCompatActivity {

    private RecyclerView quotesRecyclerView;
    private QuoteAdapter quoteAdapter; // YOUR adapter name
    private Button btnAddNewQuote, btnLogout, btnViewCurrent, btnBack;
    private TextView txtEmptyState;
    private List<FilteredQuote> quoteList;
    private QuotationApiService quotationApiService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_view_quotes);

        // Initialize Views
        quotesRecyclerView = findViewById(R.id.quotesRecyclerView);
        btnAddNewQuote = findViewById(R.id.btnAddNewQuote);
        btnLogout = findViewById(R.id.btnLogout);
        btnViewCurrent = findViewById(R.id.btnViewCurrent);
        btnBack = findViewById(R.id.btnBack);
        txtEmptyState = findViewById(R.id.txtEmptyState);

        quotationApiService = QuotationApiClient.getService(this);

        // Setup RecyclerView with delete callback
        quotesRecyclerView.setLayoutManager(new LinearLayoutManager(this));
        quoteList = new ArrayList<>();
        quoteAdapter = new QuoteAdapter(quoteList, this::handleDeleteQuote); // YOUR adapter name
        quotesRecyclerView.setAdapter(quoteAdapter);

        // Load quotes
        loadCompletedQuotes();

        // Button Listeners
        btnAddNewQuote.setOnClickListener(v -> {
//            Toast.makeText(ViewCompletedQuotes.this, "Add New Quote - Coming Soon", Toast.LENGTH_SHORT).show();
            Intent intent = new Intent(this, AddQuoteActivity.class);
            startActivity(intent);
        });

        btnViewCurrent.setOnClickListener(v -> {
            Intent intent = new Intent(ViewCompletedQuotes.this, ViewCurrentQuotes.class);
            startActivity(intent);
        });

        btnLogout.setOnClickListener(v -> {
            Toast.makeText(ViewCompletedQuotes.this, "Logging out...", Toast.LENGTH_SHORT).show();
            Intent intent = new Intent(ViewCompletedQuotes.this, Login.class);
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
            startActivity(intent);
            finish();
        });

        btnBack.setOnClickListener(v -> {
            Intent intent = new Intent(ViewCompletedQuotes.this, HomeActivity.class);
            startActivity(intent);
            finish(); // Optional: closes current activity
        });
    }

    private void loadCompletedQuotes() {
        // Show loading state
        txtEmptyState.setText("Loading completed quotes...");
        txtEmptyState.setVisibility(View.VISIBLE);
        quotesRecyclerView.setVisibility(View.GONE);

        // Fetch completed quotes using correct endpoint
        quotationApiService.getCompletedQuotes().enqueue(new Callback<List<FilteredQuote>>() {
            @Override
            public void onResponse(Call<List<FilteredQuote>> call, Response<List<FilteredQuote>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    quoteList = response.body();

                    // Update UI based on data
                    if (quoteList.isEmpty()) {
                        txtEmptyState.setText("No completed quotes yet");
                        txtEmptyState.setVisibility(View.VISIBLE);
                        quotesRecyclerView.setVisibility(View.GONE);
                    } else {
                        txtEmptyState.setVisibility(View.GONE);
                        quotesRecyclerView.setVisibility(View.VISIBLE);
                        quoteAdapter.updateQuotes(quoteList);

                        Toast.makeText(ViewCompletedQuotes.this,
                                "Loaded " + quoteList.size() + " completed quotes",
                                Toast.LENGTH_SHORT).show();
                    }
                } else {
                    txtEmptyState.setText("Failed to load quotes");
                    Toast.makeText(ViewCompletedQuotes.this,
                            "Error: " + response.message(),
                            Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<List<FilteredQuote>> call, Throwable t) {
                txtEmptyState.setText("Connection error");
                txtEmptyState.setVisibility(View.VISIBLE);
                quotesRecyclerView.setVisibility(View.GONE);

                Toast.makeText(ViewCompletedQuotes.this,
                        "Error: " + t.getMessage(),
                        Toast.LENGTH_LONG).show();
            }
        });
    }

    private void handleDeleteQuote(FilteredQuote quote, int position) {
        // Show confirmation dialog
        new AlertDialog.Builder(this)
                .setTitle("Delete Quote")
                .setMessage("Are you sure you want to delete quote " + quote.getQuoteNumber() + "?")
                .setPositiveButton("Delete", (dialog, which) -> deleteQuote(quote.getQuoteId(), position))
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void deleteQuote(int quoteId, int position) {
        quotationApiService.deleteQuote(quoteId).enqueue(new Callback<Void>() {
            @Override
            public void onResponse(Call<Void> call, Response<Void> response) {
                if (response.isSuccessful()) {
                    quoteAdapter.removeItem(position);
                    Toast.makeText(ViewCompletedQuotes.this,
                            "Quote deleted successfully",
                            Toast.LENGTH_SHORT).show();

                    // Check if list is now empty
                    if (quoteAdapter.getItemCount() == 0) {
                        txtEmptyState.setText("No completed quotes yet");
                        txtEmptyState.setVisibility(View.VISIBLE);
                        quotesRecyclerView.setVisibility(View.GONE);
                    }
                } else {
                    Toast.makeText(ViewCompletedQuotes.this,
                            "Failed to delete quote",
                            Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<Void> call, Throwable t) {
                Toast.makeText(ViewCompletedQuotes.this,
                        "Error: " + t.getMessage(),
                        Toast.LENGTH_SHORT).show();
            }
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
//        loadCompletedQuotes();
    }
}