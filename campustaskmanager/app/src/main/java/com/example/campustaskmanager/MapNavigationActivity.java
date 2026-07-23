package com.example.campustaskmanager;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.amap.api.maps.AMap;
import com.amap.api.maps.MapView;
import com.amap.api.maps.CameraUpdateFactory;
import com.amap.api.maps.model.LatLng;
import com.amap.api.maps.model.MarkerOptions;

public class MapNavigationActivity extends AppCompatActivity {
    private MapView mapView;
    private AMap aMap;
    private TextView tvDestination;
    private Button btnNavBack;
    private String locationName;
    private double latitude, longitude;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_map_navigation);

        tvDestination = findViewById(R.id.tvDestination);
        btnNavBack = findViewById(R.id.btnNavBack);
        mapView = findViewById(R.id.mapView);
        mapView.onCreate(savedInstanceState);

        locationName = getIntent().getStringExtra("location");
        latitude = getIntent().getDoubleExtra("latitude", 0.0);
        longitude = getIntent().getDoubleExtra("longitude", 0.0);

        btnNavBack.setOnClickListener(v -> finish());

        initMap();
    }

    private void initMap() {
        if (aMap == null) {
            aMap = mapView.getMap();
        }

        tvDestination.setText(getString(R.string.destination_prefix) + (locationName.isEmpty() ? getString(R.string.location_unknown) : locationName));

        if (latitude != 0.0 && longitude != 0.0) {
            LatLng targetLatLng = new LatLng(latitude, longitude);
            aMap.moveCamera(CameraUpdateFactory.newLatLngZoom(targetLatLng, 18));
            aMap.addMarker(new MarkerOptions()
                    .position(targetLatLng)
                    .title(locationName)
                    .snippet("导航目的地"));
        } else {
            Toast.makeText(this, getString(R.string.navigation_invalid), Toast.LENGTH_SHORT).show();
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        mapView.onResume();
    }

    @Override
    protected void onPause() {
        super.onPause();
        mapView.onPause();
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        mapView.onSaveInstanceState(outState);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        mapView.onDestroy();
    }
}