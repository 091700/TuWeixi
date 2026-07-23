package com.example.campustaskmanager;

import static com.amap.api.location.AMapLocationClientOption.AMapLocationMode;

import android.Manifest;
import android.app.DatePickerDialog;
import android.app.TimePickerDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.RadioGroup;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.amap.api.location.AMapLocation;
import com.amap.api.location.AMapLocationClient;
import com.amap.api.location.AMapLocationClientOption;
import com.amap.api.location.AMapLocationListener;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.UUID;

public class TaskEditActivity extends AppCompatActivity {
    private static final int REQUEST_CAMERA = 101;
    private static final int REQUEST_LOCATION = 102;
    private EditText etTaskName, etLocation;
    private Spinner spTaskType;
    private Button btnSelectDate, btnSelectTime, btnAssociateLocation, btnTakePhoto, btnSaveTask;
    private RadioGroup rgPriority;
    private TextView tvPhotoCount;
    private String selectedDate = "", selectedTime = "";
    private int photoCount = 0;
    private List<String> imagePaths = new ArrayList<>();
    private SharedPrefsHelper prefsHelper;
    private SharedPreferences themePrefs;
    private static final String PREF_THEME = "pref_theme";
    private static final int THEME_LIGHT = 0;
    private AMapLocationClient locationClient;
    private double latitude = 0.0, longitude = 0.0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        themePrefs = getSharedPreferences("theme_prefs", MODE_PRIVATE);
        int currentTheme = themePrefs.getInt(PREF_THEME, THEME_LIGHT);
        setTheme(currentTheme == THEME_LIGHT ? R.style.AppTheme_Light : R.style.AppTheme_Dark);
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_task_edit);
        prefsHelper = new SharedPrefsHelper(this);
        initViews();
    }

    private void initViews() {
        etTaskName = findViewById(R.id.etTaskName);
        spTaskType = findViewById(R.id.spTaskType);
        btnSelectDate = findViewById(R.id.btnSelectDate);
        btnSelectTime = findViewById(R.id.btnSelectTime);
        etLocation = findViewById(R.id.etLocation);
        btnAssociateLocation = findViewById(R.id.btnAssociateLocation);
        btnTakePhoto = findViewById(R.id.btnTakePhoto);
        tvPhotoCount = findViewById(R.id.tvPhotoCount);
        rgPriority = findViewById(R.id.rgPriority);
        btnSaveTask = findViewById(R.id.btnSaveTask);

        // 恢复日期选择功能
        btnSelectDate.setOnClickListener(v -> {
            Calendar calendar = Calendar.getInstance();
            new DatePickerDialog(this, (view, year, month, dayOfMonth) -> {
                selectedDate = year + "-" + (month + 1) + "-" + dayOfMonth;
                btnSelectDate.setText(selectedDate);
            }, calendar.get(Calendar.YEAR), calendar.get(Calendar.MONTH), calendar.get(Calendar.DAY_OF_MONTH)).show();
        });

        // 恢复时间选择功能
        btnSelectTime.setOnClickListener(v -> {
            Calendar calendar = Calendar.getInstance();
            new TimePickerDialog(this, (view, hourOfDay, minute) -> {
                selectedTime = hourOfDay + ":" + (minute < 10 ? "0" + minute : minute);
                btnSelectTime.setText(selectedTime);
            }, calendar.get(Calendar.HOUR_OF_DAY), calendar.get(Calendar.MINUTE), true).show();
        });

        // 恢复定位功能
        btnAssociateLocation.setOnClickListener(v -> {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.ACCESS_FINE_LOCATION}, REQUEST_LOCATION);
                return;
            }
            startLocation();
        });

        // 恢复拍照功能
        btnTakePhoto.setOnClickListener(v -> {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.CAMERA}, REQUEST_CAMERA);
                return;
            }
            takePhoto();
        });

        // 恢复保存任务功能
        btnSaveTask.setOnClickListener(v -> saveTask());
    }

    // 定位核心逻辑
    private void startLocation() {
        try {
            if (locationClient == null) {
                locationClient = new AMapLocationClient(getApplicationContext());
            }
            AMapLocationClientOption option = new AMapLocationClientOption();
            option.setOnceLocation(true);
            option.setHttpTimeOut(30000);
            option.setLocationMode(AMapLocationMode.Hight_Accuracy);
            option.setLocationCacheEnable(true);
            option.setNeedAddress(true);
            option.setWifiScan(true);
            locationClient.setLocationOption(option);
            locationClient.setLocationListener(location -> {
                if (location != null) {
                    int errorCode = location.getErrorCode();
                    if (errorCode == 0) {
                        latitude = location.getLatitude();
                        longitude = location.getLongitude();
                        String poiName = location.getPoiName() != null ? location.getPoiName() : "未知地点";
                        etLocation.setText(poiName);
                        Toast.makeText(TaskEditActivity.this, getString(R.string.toast_location_success), Toast.LENGTH_SHORT).show();
                    } else {
                        String errorMsg = "定位失败：错误码" + errorCode + "，原因：" + location.getErrorInfo();
                        Toast.makeText(TaskEditActivity.this, errorMsg, Toast.LENGTH_LONG).show();
                    }
                    locationClient.stopLocation();
                } else {
                    Toast.makeText(TaskEditActivity.this, "定位失败：未获取到数据", Toast.LENGTH_SHORT).show();
                }
            });
            locationClient.startLocation();
        } catch (Exception e) {
            e.printStackTrace();
            Toast.makeText(this, "定位初始化失败：" + e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }

    // 拍照核心逻辑
    private void takePhoto() {
        Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        if (intent.resolveActivity(getPackageManager()) != null) {
            startActivityForResult(intent, REQUEST_CAMERA);
        }
    }

    // 保存照片
    private String saveImage(Bitmap bitmap) {
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
        String imageFileName = "JPEG_" + timeStamp + "_";
        File storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);
        if (storageDir == null) return "";
        try {
            File imageFile = File.createTempFile(imageFileName, ".jpg", storageDir);
            FileOutputStream out = new FileOutputStream(imageFile);
            bitmap.compress(Bitmap.CompressFormat.JPEG, 80, out);
            out.flush();
            out.close();
            return imageFile.getAbsolutePath();
        } catch (IOException e) {
            e.printStackTrace();
            return "";
        }
    }

    // 保存任务核心逻辑
    private void saveTask() {
        String name = etTaskName.getText().toString().trim();
        if (name.isEmpty() || selectedDate.isEmpty() || selectedTime.isEmpty()) {
            Toast.makeText(this, "请填写任务名称、截止日期和时间", Toast.LENGTH_SHORT).show();
            return;
        }

        Task task = new Task();
        task.setId(UUID.randomUUID().toString());
        task.setName(name);
        task.setType(spTaskType.getSelectedItem().toString());
        task.setDeadlineDate(selectedDate);
        task.setDeadlineTime(selectedTime);
        task.setLocation(etLocation.getText().toString().trim());

        int priorityId = rgPriority.getCheckedRadioButtonId();
        if (priorityId == R.id.rbHigh) {
            task.setPriority(getString(R.string.rb_high));
        } else if (priorityId == R.id.rbLow) {
            task.setPriority(getString(R.string.rb_low));
        } else {
            task.setPriority(getString(R.string.rb_medium));
        }

        task.setCompleted(false);
        task.setLatitude(latitude);
        task.setLongitude(longitude);
        task.setImagePaths(imagePaths);

        prefsHelper.saveTask(task);
        Toast.makeText(this, getString(R.string.toast_task_saved), Toast.LENGTH_SHORT).show();
        finish();
    }
    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_CAMERA) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                takePhoto();
            } else {
                Toast.makeText(this, "相机权限拒绝，无法拍摄照片", Toast.LENGTH_SHORT).show();
            }
        } else if (requestCode == REQUEST_LOCATION) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                startLocation();
            } else {
                Toast.makeText(this, "定位权限拒绝，无法关联位置", Toast.LENGTH_SHORT).show();
            }
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_CAMERA && resultCode == RESULT_OK) {
            Bundle extras = data.getExtras();
            if (extras != null) {
                Bitmap imageBitmap = (Bitmap) extras.get("data");
                if (imageBitmap != null) {
                    String imagePath = saveImage(imageBitmap);
                    if (!imagePath.isEmpty()) {
                        imagePaths.add(imagePath);
                        photoCount++;
                        tvPhotoCount.setText(getString(R.string.photo_count, photoCount));
                        Toast.makeText(this, getString(R.string.toast_photo_success), Toast.LENGTH_SHORT).show();
                    }
                }
            }
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (locationClient != null) {
            locationClient.onDestroy();
            locationClient = null;
        }
    }
}