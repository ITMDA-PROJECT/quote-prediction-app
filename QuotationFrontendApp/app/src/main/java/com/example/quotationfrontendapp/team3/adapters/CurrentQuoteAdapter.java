package com.example.quotationfrontendapp.team3.adapters;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.quotationfrontendapp.R;
import com.example.quotationfrontendapp.dtos.quotationdtos.FilteredQuote;

import java.util.List;

public class CurrentQuoteAdapter extends RecyclerView.Adapter<CurrentQuoteAdapter.QuoteViewHolder> {

    private List<FilteredQuote> quoteList;
    private OnQuoteClickListener clickListener;

    // Interface for click handling
    public interface OnQuoteClickListener {
        void onQuoteClick(FilteredQuote quote, int position);
    }

    public CurrentQuoteAdapter(List<FilteredQuote> quoteList) {
        this.quoteList = quoteList;
    }

    public void setOnQuoteClickListener(OnQuoteClickListener listener) {
        this.clickListener = listener;
    }

    @NonNull
    @Override
    public QuoteViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_current_quote, parent, false);
        return new QuoteViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull QuoteViewHolder holder, int position) {
        FilteredQuote quote = quoteList.get(position);
        holder.bind(quote, position);
    }

    @Override
    public int getItemCount() {
        return quoteList.size();
    }

    public void updateQuotes(List<FilteredQuote> newQuotes) {
        this.quoteList = newQuotes;
        notifyDataSetChanged();
    }

    public void removeItem(int position) {
        quoteList.remove(position);
        notifyItemRemoved(position);
        notifyItemRangeChanged(position, quoteList.size());
    }

    class QuoteViewHolder extends RecyclerView.ViewHolder {
        TextView txtQuoteNumber;
        TextView txtPredictedTime;

        public QuoteViewHolder(@NonNull View itemView) {
            super(itemView);
            txtQuoteNumber = itemView.findViewById(R.id.txtQuoteNumber);
            txtPredictedTime = itemView.findViewById(R.id.txtPredictedTime);
        }

        public void bind(FilteredQuote quote, int position) {
            txtQuoteNumber.setText(quote.getQuoteNumber());
            txtPredictedTime.setText(quote.getFormattedTime());

            // Add click listener to the entire item
            itemView.setOnClickListener(v -> {
                if (clickListener != null) {
                    clickListener.onQuoteClick(quote, position);
                }
            });
        }
    }
}