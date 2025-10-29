package com.example.quotationfrontendapp.team2;

import android.content.Context;
import android.content.Intent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.quotationfrontendapp.R;
import com.example.quotationfrontendapp.dtos.quotationdtos.QuotePart;

import java.util.List;
import java.util.Locale;

//Adapter for the QuoteParts RecyclerView
public class QuotePartsAdapter extends RecyclerView.Adapter<QuotePartsAdapter.ViewHolder> {
    //Declare the list of quote parts and the context
    private final List<QuotePart> quoteParts;
    private final Context context;
    private final int quoteId;

    //constructor
    public QuotePartsAdapter(Context context, List<QuotePart> quoteParts, int quoteId) {
        this.context = context;
        this.quoteParts = quoteParts;
        this.quoteId = quoteId;
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        //Create the new card item layout using custom layout
        View view = LayoutInflater.from(context).inflate(R.layout.quote_part_card_item, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        QuotePart quotePart = quoteParts.get(position);

        // --- Data Binding to Card Views ---
        //Check if the nested Part object exists
        if (quotePart.getPart() != null) {
            //Holder = contents of the part card
            holder.tvPartDescription.setText(quotePart.getPart().getPartDescription());
            holder.tvMaterialCode.setText(quotePart.getPart().getMaterialCode());
        } else {
            holder.tvPartDescription.setText("Description N/A");
            holder.tvMaterialCode.setText("N/A");
        }
        //Bind the rest of the data
        holder.tvCuttingLength.setText(String.format(Locale.US, "%.1f", quotePart.getCuttingLength()));
        holder.tvQuantity.setText(String.valueOf(quotePart.getQuantity()));
        holder.tvNumPierces.setText(String.valueOf(quotePart.getNumPierces()));

        //Check for null calculated time
        if (quotePart.getCalculatedPartTime() != null) {
            holder.tvPartTime.setText(String.format(Locale.US, "%.1f", quotePart.getCalculatedPartTime()));
        } else {
            holder.tvPartTime.setText("N/A");
        }

        //Set onclicklistener for the edit button
        holder.btnEditPart.setOnClickListener(v -> {
            //Navigate to EditPartActivity
            Intent intent = new Intent(context, EditPartActivity.class);
            //Pass relevant data to next screen for editing
            intent.putExtra("quote_part_id", quotePart.getId());
            intent.putExtra("quote_id", quoteId);
            context.startActivity(intent);
            Toast.makeText(context, "Edit part: " + quotePart.getPart().getPartDescription(), Toast.LENGTH_SHORT).show();
        });
    }

    @Override
    public int getItemCount() {
        //Returns 0 if the list is null to prevent crashes
        return quoteParts != null ? quoteParts.size() : 0;
    }

    //Method to hold the views for a single card item
    public static class ViewHolder extends RecyclerView.ViewHolder {
        //Declare all the views in the card
        TextView tvPartDescription, tvMaterialCode, tvCuttingLength, tvQuantity, tvNumPierces, tvPartTime;
        ImageButton btnEditPart;

        public ViewHolder(@NonNull View itemView) {
            super(itemView);
            //Initialises views
            tvPartDescription = itemView.findViewById(R.id.tvPartDescription);
            tvMaterialCode = itemView.findViewById(R.id.tvMaterialCode);
            tvCuttingLength = itemView.findViewById(R.id.tvCuttingLength);
            tvQuantity = itemView.findViewById(R.id.tvQuantity);
            tvNumPierces = itemView.findViewById(R.id.tvNumPierces);
            tvPartTime = itemView.findViewById(R.id.tvPartTime);
            btnEditPart = itemView.findViewById(R.id.btnEditPart);
        }
    }
}
