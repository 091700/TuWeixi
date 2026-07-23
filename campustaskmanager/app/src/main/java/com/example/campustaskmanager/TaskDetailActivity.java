package com.example.campustaskmanager;

import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.google.gson.Gson;
import java.io.File;
import java.util.List;

public class TaskDetailActivity extends AppCompatActivity {
    private TextView tvDetailName, tvCompleteStatus, tvDetailInfo;
    private Button btnBack, btnNavigate;
    private LinearLayout llPhotos;
    private Task task;
    private SharedPreferences themePrefs;
    private static final String PREF_THEME = "pref_theme";
    private static final int THEME_LIGHT = 0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        themePrefs = getSharedPreferences("theme_prefs", MODE_PRIVATE);
        int currentTheme = themePrefs.getInt(PREF_THEME, THEME_LIGHT);
        setTheme(currentTheme == THEME_LIGHT ? R.style.AppTheme_Light : R.style.AppTheme_Dark);
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_task_detail);
        initViews();
        String taskStr = getIntent().getStringExtra("taskStr");
        task = new Gson().fromJson(taskStr, Task.class);
        setTaskData();
        loadPhotos();
    }
    private void initViews() {
        tvDetailName = findViewById(R.id.tvDetailName);
        tvCompleteStatus = findViewById(R.id.tvCompleteStatus);
        tvDetailInfo = findViewById(R.id.tvDetailInfo);
        llPhotos = findViewById(R.id.llPhotos);
        btnBack = findViewById(R.id.btnBack);
        btnNavigate = findViewById(R.id.btnNavigate);
        btnBack.setOnClickListener(v -> finish());
        btnNavigate.setOnClickListener(v -> {
            Intent intent = new Intent(this, MapNavigationActivity.class);
            intent.putExtra("location", task.getLocation());
            intent.putExtra("latitude", task.getLatitude());
            intent.putExtra("longitude", task.getLongitude());
            startActivity(intent);
        });
    }

    private void setTaskData() {
        tvDetailName.setText(task.getName().isEmpty() ? "未命名任务" : task.getName());
        boolean isCompleted = task.isCompleted();
        tvCompleteStatus.setText(isCompleted ? getString(R.string.task_complete) : getString(R.string.task_pending));
        tvCompleteStatus.setBackgroundResource(isCompleted ? R.drawable.tag_bg_green : R.drawable.tag_bg_yellow);

        String type = task.getType().isEmpty() ? getString(R.string.task_no_type) : task.getType();
        String priority = task.getPriority();
        String deadlineDate = task.getDeadlineDate().isEmpty() ? getString(R.string.deadline_none) : task.getDeadlineDate();
        String deadlineTime = task.getDeadlineTime().isEmpty() ? "" : task.getDeadlineTime();
        String location = task.getLocation().isEmpty() ? getString(R.string.task_location_none) : task.getLocation();
        String status = isCompleted ? getString(R.string.task_status_completed) : getString(R.string.task_status_pending);

        tvDetailInfo.setText(String.format(getString(R.string.task_detail_info),
                type, priority, deadlineDate, deadlineTime, location, status));
    }

    private void loadPhotos() {
        List<String> imagePaths = task.getImagePaths();
        if (imagePaths == null || imagePaths.isEmpty()) {
            Toast.makeText(this, getString(R.string.toast_no_photo), Toast.LENGTH_SHORT).show();
            return;
        }
        llPhotos.removeAllViews();

        for (String path : imagePaths) {
            File imageFile = new File(path);
            if (!imageFile.exists()) continue;

            ImageView ivPhoto = new ImageView(this);
            LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                    150, 150);
            params.setMargins(8, 0, 8, 0);
            ivPhoto.setLayoutParams(params);
            ivPhoto.setScaleType(ImageView.ScaleType.CENTER_CROP);
            ivPhoto.setBackgroundResource(R.color.gray_300);
            Bitmap bitmap = BitmapFactory.decodeFile(path);
            ivPhoto.setImageBitmap(bitmap);
            llPhotos.addView(ivPhoto);
        }
    }
}