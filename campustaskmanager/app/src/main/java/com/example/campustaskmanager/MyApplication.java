package com.example.campustaskmanager;

import android.app.Application;
import com.amap.api.maps.MapsInitializer;
import com.amap.api.location.AMapLocationClient;

public class MyApplication extends Application {
    @Override
    public void onCreate() {
        super.onCreate();
        try {

            MapsInitializer.updatePrivacyShow(this, true, true);
            MapsInitializer.updatePrivacyAgree(this, true);

            AMapLocationClient.updatePrivacyShow(this, true, true);
            AMapLocationClient.updatePrivacyAgree(this, true);

            MapsInitializer.initialize(getApplicationContext());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}