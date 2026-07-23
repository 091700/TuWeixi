package com.warehouse.util;

import java.io.IOException;

import jakarta.servlet.http.HttpServletResponse;

public class ErrorHandler {
    public static void handle(HttpServletResponse resp, Exception e) throws IOException {
        e.printStackTrace();
        resp.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR, 
            "操作失败: " + e.getClass().getSimpleName() + " - " + e.getMessage());
    }
}