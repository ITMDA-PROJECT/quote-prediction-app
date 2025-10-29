package com.example.quotationfrontendapp.team2;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import com.example.quotationfrontendapp.R;
import com.example.quotationfrontendapp.shared.Globals;
import com.example.quotationfrontendapp.team1.Login;
import com.example.quotationfrontendapp.team1.UpdateUser;
import com.example.quotationfrontendapp.team3.ViewCurrentQuotes;

public class HomeActivity extends AppCompatActivity {
    private TextView tvWelcome;
    private LinearLayout btnAddQuotation, btnViewQuotations, btnEditUser;
    private Button btnLogout;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_home);
        //Instance of Globals
        Globals globals = Globals.getInstance();

        //Retrieve JWT token and username for displaying welcome message (Globals/SharedPref/Intents)
        String adminUsername = globals.getUserName();
        String jwtToken = globals.getToken();
        int adminId = globals.getUsersId();

        //Initialise views
        tvWelcome = findViewById(R.id.tvWelcome);
        btnAddQuotation = findViewById(R.id.btnAddQuotation);
        btnViewQuotations = findViewById(R.id.btnViewQuotations);
        btnLogout = findViewById(R.id.btnLogout);
        btnEditUser = findViewById(R.id.btnEditUser);

        //Personalised greeting
        if (adminUsername != null && !adminUsername.isEmpty()) {
            tvWelcome.setText("Welcome, " + adminUsername + "!");
        }

        //Set click listeners
        btnAddQuotation.setOnClickListener(v -> {
            //Redirect to Add Quote screen
            Intent addIntent = new Intent(HomeActivity.this, AddQuoteActivity.class);
            //Pass JWT token and username to AddQuoteActivity
            addIntent.putExtra("jwt_token", jwtToken);
            addIntent.putExtra("username", adminUsername);
            addIntent.putExtra("admin_id", adminId);
            startActivity(addIntent);
        });

        btnViewQuotations.setOnClickListener(v -> {
            //Todo (Team 3 adjustments if needed)
            //Redirect to View Quotes screen (Team 3)
            Intent viewIntent = new Intent(HomeActivity.this, ViewCurrentQuotes.class);
            viewIntent.putExtra("jwt_token", jwtToken);
            startActivity(viewIntent);
        });

        btnEditUser.setOnClickListener(v -> {
            Intent editUserIntent = new Intent(HomeActivity.this, UpdateUser.class);
            startActivity(editUserIntent);
        });

        btnLogout.setOnClickListener(v -> {
            //Clear globals file when return to login screen
            globals.clearData();

            //Redirect to login screen
            Intent loginIntent = new Intent(HomeActivity.this, Login.class);
            //Flags clear the activity stack so can't go back to HomeActivity screen
            loginIntent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
            startActivity(loginIntent);
            finish();                   //Close the HomeActivity
        });
    }
}
