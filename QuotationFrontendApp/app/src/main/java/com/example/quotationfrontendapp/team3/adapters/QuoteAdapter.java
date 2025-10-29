package com.example.quotationfrontendapp.team3.adapters;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.quotationfrontendapp.dtos.quotationdtos.FilteredQuote; // Changed from Quote
import com.example.quotationfrontendapp.R;

import java.util.List;

public class QuoteAdapter extends RecyclerView.Adapter<QuoteAdapter.QuoteViewHolder> {

    private List<FilteredQuote> quoteList; // Changed from Quote
    private OnDeleteClickListener deleteListener; // Added

    // Interface for delete callback
    public interface OnDeleteClickListener {
        void onDeleteClick(FilteredQuote quote, int position);
    }

    public QuoteAdapter(List<FilteredQuote> quoteList, OnDeleteClickListener deleteListener) { // Updated constructor
        this.quoteList = quoteList;
        this.deleteListener = deleteListener;
    }

    @NonNull
    @Override
    public QuoteViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_quote_completed, parent, false); // Make sure this is the right layout
        return new QuoteViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull QuoteViewHolder holder, int position) {
        FilteredQuote quote = quoteList.get(position); // Changed from Quote
        holder.txtQuoteNumber.setText(quote.getQuoteNumber());
        holder.txtPredictedTime.setText(quote.getFormattedTime()); // Use helper method

        // Set delete button click listener
        holder.btnDelete.setOnClickListener(v -> {
            if (deleteListener != null) {
                deleteListener.onDeleteClick(quote, position);
            }
        });
    }

    @Override
    public int getItemCount() {
        return quoteList.size();
    }

    public void updateQuotes(List<FilteredQuote> newQuotes) { // Changed from Quote
        this.quoteList = newQuotes;
        notifyDataSetChanged();
    }

    public void removeItem(int position) { // Added for delete functionality
        quoteList.remove(position);
        notifyItemRemoved(position);
        notifyItemRangeChanged(position, quoteList.size());
    }

    static class QuoteViewHolder extends RecyclerView.ViewHolder {
        TextView txtQuoteNumber;
        TextView txtPredictedTime;
        Button btnDelete; // Changed from txtCompletionDate

        public QuoteViewHolder(@NonNull View itemView) {
            super(itemView);
            txtQuoteNumber = itemView.findViewById(R.id.txtQuoteNumber);
            txtPredictedTime = itemView.findViewById(R.id.txtPredictedTime);
            btnDelete = itemView.findViewById(R.id.btnDeleteQuote); // Changed from txtCompletionDate
        }
    }
}