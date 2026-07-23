package com.example.studentmanage.util;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.lang.reflect.Field;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.List;

import javax.servlet.http.HttpServletResponse;

import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.CellType;
import org.apache.poi.ss.usermodel.DateUtil;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.ss.usermodel.Workbook;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.web.multipart.MultipartFile;

public class ExcelUtil {
    public static <T> List<T> importExcel(MultipartFile file, Class<T> clazz) throws Exception {
        List<T> list = new ArrayList<>();
        InputStream inputStream = file.getInputStream();
        Workbook workbook = new XSSFWorkbook(inputStream);
        Sheet sheet = workbook.getSheetAt(0);  // 读取第一个工作表

        // 读取表头（跳过第1行，假设第1行是标题）
        int rowStart = 1;
        int rowEnd = sheet.getLastRowNum();

        for (int i = rowStart; i <= rowEnd; i++) {
            Row row = sheet.getRow(i);
            if (row == null) continue;

            // 反射创建实体类对象
            T obj = clazz.getDeclaredConstructor().newInstance();
            Field[] fields = clazz.getDeclaredFields();  // 获取实体类所有字段

            // 逐个单元格赋值（假设Excel列顺序与实体类字段顺序一致）
            for (int j = 0; j < fields.length; j++) {
                Field field = fields[j];
                field.setAccessible(true);  // 允许访问私有字段
                Cell cell = row.getCell(j);
                if (cell == null) continue;

                // 根据字段类型设置值
                if (field.getType() == String.class) {
                    field.set(obj, getCellValue(cell));
                } else if (field.getType() == Integer.class) {
                    field.set(obj, Integer.parseInt(getCellValue(cell)));
                } else if (field.getType() == Double.class) {
                    field.set(obj, Double.parseDouble(getCellValue(cell)));
                }
            }
            list.add(obj);
        }

        workbook.close();
        inputStream.close();
        return list;
    }

    // 2. Excel导出（List<实体类> -> 响应下载）
    public static <T> void exportExcel(HttpServletResponse response, String fileName, String sheetName, List<T> data, Class<T> clazz) throws IOException {
        Workbook workbook = new XSSFWorkbook();
        Sheet sheet = workbook.createSheet(sheetName);

        // 1. 创建表头（字段名）
        Row headerRow = sheet.createRow(0);
        Field[] fields = clazz.getDeclaredFields();
        for (int i = 0; i < fields.length; i++) {
            Cell cell = headerRow.createCell(i);
            cell.setCellValue(fields[i].getName());  // 表头为字段名
        }

        // 2. 填充数据
        for (int i = 0; i < data.size(); i++) {
            Row dataRow = sheet.createRow(i + 1);
            T obj = data.get(i);
            for (int j = 0; j < fields.length; j++) {
                Field field = fields[j];
                field.setAccessible(true);
                try {
                    Object value = field.get(obj);
                    Cell cell = dataRow.createCell(j);
                    cell.setCellValue(value != null ? value.toString() : "");
                } catch (IllegalAccessException e) {
                    e.printStackTrace();
                }
            }
        }

        // 3. 响应配置（下载）
        response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
        response.setHeader("Content-Disposition", "attachment;filename=" + URLEncoder.encode(fileName, "UTF-8"));
        OutputStream outputStream = response.getOutputStream();
        workbook.write(outputStream);

        // 4. 关闭资源
        outputStream.close();
        workbook.close();
    }
    private static String getCellValue(Cell cell) {
        if (cell == null) return "";
        CellType cellType = cell.getCellType();
        switch (cellType) {
            case STRING:
                return cell.getStringCellValue().trim();
            case NUMERIC:
                if (DateUtil.isCellDateFormatted(cell)) {
                    return cell.getDateCellValue().toString();
                }
                double num = cell.getNumericCellValue();
                if (num == (long) num) {
                    return String.valueOf((long) num);
                } else {
                    return String.valueOf(num);
                }
            case BOOLEAN:
                return String.valueOf(cell.getBooleanCellValue());
            case FORMULA:
                try {
                    return cell.getStringCellValue();
                } catch (Exception e) {
                    return String.valueOf(cell.getNumericCellValue());
                }
            default:
                return "";
        }
    }
}