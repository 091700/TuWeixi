package com.example.campustaskmanager;

import android.content.Context;
import android.content.SharedPreferences;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.List;

public class SharedPrefsHelper {
    private static final String PREF_NAME = "task_prefs";
    private static final String KEY_TASKS = "tasks";
    private SharedPreferences prefs;
    private Gson gson;

    public SharedPrefsHelper(Context context) {
        prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        gson = new Gson();
    }

    public List<Task> getTasks() {
        String json = prefs.getString(KEY_TASKS, null);
        if (json == null) {
            return new ArrayList<>();
        }
        Type type = new TypeToken<List<Task>>(){}.getType();
        return gson.fromJson(json, type);
    }

    public void saveTask(Task task) {
        List<Task> tasks = getTasks();
        tasks.add(task);
        String json = gson.toJson(tasks);
        prefs.edit().putString(KEY_TASKS, json).apply();
    }

    public void updateTask(Task updatedTask) {
        List<Task> tasks = getTasks();
        for (int i = 0; i < tasks.size(); i++) {
            if (tasks.get(i).getId().equals(updatedTask.getId())) {
                tasks.set(i, updatedTask);
                break;
            }
        }
        String json = gson.toJson(tasks);
        prefs.edit().putString(KEY_TASKS, json).apply();
    }

    public void deleteTask(String taskId) {
        List<Task> tasks = getTasks();
        for (int i = 0; i < tasks.size(); i++) {
            if (tasks.get(i).getId().equals(taskId)) {
                tasks.remove(i);
                break;
            }
        }
        String json = gson.toJson(tasks);
        prefs.edit().putString(KEY_TASKS, json).apply();
    }
}