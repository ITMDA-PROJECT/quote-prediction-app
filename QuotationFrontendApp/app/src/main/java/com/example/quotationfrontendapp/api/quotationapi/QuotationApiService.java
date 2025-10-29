package com.example.quotationfrontendapp.api.quotationapi;

import com.example.quotationfrontendapp.dtos.quotationdtos.FilteredQuote;
import com.example.quotationfrontendapp.dtos.quotationdtos.MLPredictionResponse;
import com.example.quotationfrontendapp.dtos.quotationdtos.Material;
import com.example.quotationfrontendapp.dtos.quotationdtos.Part;
import com.example.quotationfrontendapp.dtos.quotationdtos.QuotePart;
import com.example.quotationfrontendapp.dtos.quotationdtos.QuotePartAdd;
import com.example.quotationfrontendapp.dtos.quotationdtos.QuotePartUpdate;
import com.example.quotationfrontendapp.dtos.quotationdtos.QuoteStatusUpdate;
import com.example.quotationfrontendapp.dtos.quotationdtos.Quotes;

import java.util.List;
import java.util.Map;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.DELETE;
import retrofit2.http.GET;
import retrofit2.http.POST;
import retrofit2.http.PUT;
import retrofit2.http.Path;

//Team 2 -- Quotation API Service
public interface QuotationApiService {

    //TEST API
    @GET("/")
    Call<Map<String, String>> healthCheck();
    //----------------------------------------------------------------------------------------------------------------


    //MATERIALS
    //Get all materials and associated data
    @GET("materials")
    Call<List<Material>> getAllMaterials();

    //Get single material info by code
    @GET("materials/{material_code}")
    Call<Material> getMaterial(@Path("material_code") String materialCode);
    //----------------------------------------------------------------------------------------------------------------


    //QUOTES
    //Create Quote
    @POST("quotes")
    Call<Quotes> createQuote(@Body Quotes quotes);

    //Get quote by id
    @GET("quotes/{quote_id}")
    Call<Quotes> getQuote(@Path("quote_id") int quoteId);

    //Get quote details by id
    @GET("quotes/{quote_id}/details")
    Call<Quotes> getQuoteDetails(@Path("quote_id") int quoteId);

    //Update quote status
    @PUT("quotes/{quote_id}/status")
    Call<Quotes> updateQuoteStatus(@Path("quote_id") int quoteId, @Body QuoteStatusUpdate statusUpdate);


    //----------------------------------------------------------------------------------------------------------------


    //PARTS
    //Get all parts
    @GET("parts")
    Call<List<Part>> getAllParts();

    //Create a part
    @POST("parts")
    Call<Part> createPart(@Body Part part);

    //Get a part
    @GET("parts/{part_id}")
    Call<Part> getPart(@Path("part_id") int partId);
    //----------------------------------------------------------------------------------------------------------------



    //QUOTE_PARTS
    //Adding parts to a quote
    @POST("quotes/{quote_id}/add-part")
    Call<QuotePart> addPartToQuote(@Path("quote_id") int quoteId, @Body QuotePartAdd quotePartAdd);

    //Updating part of a quote
    @PUT("quote-parts/{quote_part_id}")
    Call<QuotePart> updateQuotePart(@Path("quote_part_id") int quotePartId, @Body QuotePartUpdate updateData);

    //Deleting a quote's part
    @DELETE("quote-parts/{quote_part_id}")
    Call<Void> deleteQuotePart(@Path("quote_part_id") int quotePartId);
    //----------------------------------------------------------------------------------------------------------------


    //ML PREDICTION
    @POST("quotes/{quote_id}/predict")
    Call<MLPredictionResponse> predictQuoteTime(@Path("quote_id") int quoteId);         //Verify Response and not Request DTO
    //----------------------------------------------------------------------------------------------------------------


    //CALLING COMPLETED & IN-PROGRESS QUOTES

    @GET("quotes/in-progress-filtered")
    Call<List<FilteredQuote>> getInProgressQuotes();

    @GET("quotes/completed-filtered")
    Call<List<FilteredQuote>> getCompletedQuotes();

    // Delete quote
    @DELETE("quotes/{quote_id}")
    Call<Void> deleteQuote(@Path("quote_id") int quoteId);
}

