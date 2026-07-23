package com.example.campustaskmanager;

import java.util.ArrayList;
import java.util.List;

// 1. 彻底删除 implements Serializable！
public class Task {
    // 2. 初始化所有字段（避免任何 null）
    private String id = "";
    private String name = "";
    private String type = "";
    private String priority = "中";
    private String deadlineDate = "";
    private String deadlineTime = "";
    private String location = "";
    private boolean isCompleted = false;
    private double latitude = 0.0;
    private double longitude = 0.0;
    private List<String> imagePaths = new ArrayList<>();

    // 3. 必须有 无参构造方法
    public Task() {}

    // 4. 所有字段的 getter/setter 必须完整（复制粘贴，一个都不能少）
    public String getId() { return id; }
    public void setId(String id) { this.id = id != null ? id : ""; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name != null ? name : ""; }
    public String getType() { return type; }
    public void setType(String type) { this.type = type != null ? type : ""; }
    public String getPriority() { return priority; }
    public void setPriority(String priority) { this.priority = priority != null ? priority : "中"; }
    public String getDeadlineDate() { return deadlineDate; }
    public void setDeadlineDate(String deadlineDate) { this.deadlineDate = deadlineDate != null ? deadlineDate : ""; }
    public String getDeadlineTime() { return deadlineTime; }
    public void setDeadlineTime(String deadlineTime) { this.deadlineTime = deadlineTime != null ? deadlineTime : ""; }
    public String getLocation() { return location; }
    public void setLocation(String location) { this.location = location != null ? location : ""; }
    public boolean isCompleted() { return isCompleted; }
    public void setCompleted(boolean completed) { isCompleted = completed; }
    public double getLatitude() { return latitude; }
    public void setLatitude(double latitude) { this.latitude = latitude; }
    public double getLongitude() { return longitude; }
    public void setLongitude(double longitude) { this.longitude = longitude; }
    public List<String> getImagePaths() { return imagePaths; }
    public void setImagePaths(List<String> imagePaths) { this.imagePaths = imagePaths != null ? imagePaths : new ArrayList<>(); }
}