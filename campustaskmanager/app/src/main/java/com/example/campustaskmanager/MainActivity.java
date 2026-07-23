package com.example.campustaskmanager;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import java.util.ArrayList;
import java.util.List;
import android.app.AlertDialog;
import com.google.gson.Gson;

public class MainActivity extends AppCompatActivity {
    private ListView lvTasks;
    private Button btnAddTask, btnAll, btnPending, btnCompleted, btnToggleTheme;
    private SharedPrefsHelper prefsHelper;
    private List<Task> allTasks;
    private TaskAdapter adapter;
    private SharedPreferences themePrefs;
    private static final String PREF_THEME = "pref_theme";
    private static final int THEME_LIGHT = 0;
    private static final int THEME_DARK = 1;
    private int currentTheme = THEME_LIGHT;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        themePrefs = getSharedPreferences("theme_prefs", MODE_PRIVATE);
        currentTheme = themePrefs.getInt(PREF_THEME, THEME_LIGHT);
        setTheme(currentTheme == THEME_LIGHT ? R.style.AppTheme_Light : R.style.AppTheme_Dark);
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        initViews();
        prefsHelper = new SharedPrefsHelper(this);
        allTasks = prefsHelper.getTasks();
        adapter = new TaskAdapter(allTasks);
        lvTasks.setAdapter(adapter);

        btnAddTask.setOnClickListener(v -> {
            startActivity(new Intent(MainActivity.this, TaskEditActivity.class));
        });

        btnAll.setOnClickListener(v -> adapter.updateData(allTasks));
        btnPending.setOnClickListener(v -> {
            List<Task> pending = new ArrayList<>();
            for (Task task : allTasks) {
                if (!task.isCompleted()) pending.add(task);
            }
            adapter.updateData(pending);
        });
        btnCompleted.setOnClickListener(v -> {
            List<Task> completed = new ArrayList<>();
            for (Task task : allTasks) {
                if (task.isCompleted()) completed.add(task);
            }
            adapter.updateData(completed);
        });

        btnToggleTheme.setOnClickListener(v -> {
            currentTheme = (currentTheme == THEME_LIGHT) ? THEME_DARK : THEME_LIGHT;
            themePrefs.edit().putInt(PREF_THEME, currentTheme).apply();
            recreate();
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        allTasks = prefsHelper.getTasks();
        adapter.updateData(allTasks);
    }

    private void initViews() {
        lvTasks = findViewById(R.id.lvTasks);
        btnAddTask = findViewById(R.id.btnAddTask);
        btnAll = findViewById(R.id.btnAll);
        btnPending = findViewById(R.id.btnPending);
        btnCompleted = findViewById(R.id.btnCompleted);
        btnToggleTheme = findViewById(R.id.btnToggleTheme);
    }

    private class TaskAdapter extends ArrayAdapter<Task> {
        private List<Task> data;

        public TaskAdapter(List<Task> data) {
            super(MainActivity.this, 0, data);
            this.data = data;
        }

        public void updateData(List<Task> newData) {
            if (newData == null) newData = new ArrayList<>();
            data.clear();
            data.addAll(newData);
            notifyDataSetChanged();
        }

        @Override
        public View getView(int position, View convertView, ViewGroup parent) {
            ViewHolder holder;
            if (convertView == null) {
                convertView = getLayoutInflater().inflate(R.layout.item_task, parent, false);
                holder = new ViewHolder();
                holder.tvName = convertView.findViewById(R.id.tvTaskName);
                holder.tvDeadline = convertView.findViewById(R.id.tvDeadline);
                holder.tvType = convertView.findViewById(R.id.tvTaskType);
                holder.tvPriority = convertView.findViewById(R.id.tvPriority);
                convertView.setTag(holder);
            } else {
                holder = (ViewHolder) convertView.getTag();
            }

            Task task = data.get(position);
            holder.tvName.setText(task.getName() != null ? task.getName() : "未命名任务");
            String deadlinePrefix = getString(R.string.deadline_prefix);
            String deadline = deadlinePrefix + (task.getDeadlineDate() != null ? task.getDeadlineDate() : "")
                    + " " + (task.getDeadlineTime() != null ? task.getDeadlineTime() : "");
            holder.tvDeadline.setText(deadline);
            holder.tvType.setText(task.getType() != null ? task.getType() : "无类型");

            String priority = task.getPriority() != null ? task.getPriority() : "中";
            holder.tvPriority.setText(priority);
            if (priority.equals("高")) {
                holder.tvPriority.setBackgroundResource(R.drawable.tag_bg_red);
                holder.tvPriority.setTextColor(getResources().getColor(R.color.white));
            } else if (priority.equals("低")) {
                holder.tvPriority.setBackgroundResource(R.drawable.tag_bg_yellow);
                holder.tvPriority.setTextColor(getResources().getColor(R.color.gray_900));
            } else {
                holder.tvPriority.setBackgroundResource(R.drawable.tag_bg_yellow);
                holder.tvPriority.setTextColor(getResources().getColor(R.color.gray_900));
            }

            TextView tvItemCompleteStatus = convertView.findViewById(R.id.tvItemCompleteStatus);
            if (task.isCompleted()) {
                tvItemCompleteStatus.setText("已完成");
                tvItemCompleteStatus.setBackgroundResource(R.drawable.tag_bg_green);
                tvItemCompleteStatus.setTextColor(getResources().getColor(R.color.white));
            } else {
                tvItemCompleteStatus.setText("未完成");
                tvItemCompleteStatus.setBackgroundResource(R.drawable.tag_bg_yellow);
                tvItemCompleteStatus.setTextColor(getResources().getColor(R.color.gray_900));
            }

            convertView.setOnLongClickListener(v -> {
                new AlertDialog.Builder(MainActivity.this)
                        .setTitle(getString(R.string.dialog_task_operation))
                        .setItems(new String[]{
                                getString(R.string.dialog_mark_complete),
                                getString(R.string.dialog_delete_task)
                        }, (dialog, which) -> {
                            if (which == 0) {
                                task.setCompleted(!task.isCompleted());
                                prefsHelper.updateTask(task);
                            } else if (which == 1) {
                                prefsHelper.deleteTask(task.getId());
                            }
                            allTasks = prefsHelper.getTasks();
                            adapter.updateData(allTasks);
                        })
                        .show();
                return true;
            });

            convertView.setOnClickListener(v -> {
                Intent intent = new Intent(MainActivity.this, TaskDetailActivity.class);
                Gson gson = new Gson();
                String taskStr = gson.toJson(task);
                intent.putExtra("taskStr", taskStr);
                startActivity(intent);
            });

            return convertView;
        }

        private class ViewHolder {
            TextView tvName, tvDeadline, tvType, tvPriority;
        }
    }
}