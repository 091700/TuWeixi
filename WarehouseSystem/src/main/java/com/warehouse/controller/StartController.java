package com.warehouse.controller;

import java.io.IOException;
import java.sql.SQLException;

import com.warehouse.dao.UserDAO;
import com.warehouse.util.ErrorHandler;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@WebServlet("/login")
public class StartController extends HttpServlet {
    private final UserDAO userDAO = new UserDAO();

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        try {
            req.getRequestDispatcher("/WEB-INF/views/login.jsp").forward(req, resp);
        } catch (Exception e) {
            ErrorHandler.handle(resp, e);
        }
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        String username = req.getParameter("username");
        String password = req.getParameter("password");
        String role = req.getParameter("role");

        try {
            String validRole = userDAO.validateUser(username, password);
            if (validRole != null && validRole.equals(role)) {
                if (role.equals("customer")) {
                    resp.sendRedirect(req.getContextPath() + "/xiadan");
                } else if (role.equals("admin")) {
                    resp.sendRedirect(req.getContextPath() + "/goods");
                }
            } else {
                req.setAttribute("error", "用户名或密码错误");
                req.getRequestDispatcher("/WEB-INF/views/login.jsp").forward(req, resp);
            }
        } catch (SQLException e) {
            ErrorHandler.handle(resp, e);
        }
    }
}