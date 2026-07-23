package com.warehouse.controller;

import java.io.IOException;
import java.sql.SQLException;

import com.warehouse.dao.CustomerDAO;
import com.warehouse.dao.GoodsDAO;
import com.warehouse.dao.WarehouseDAO;
import com.warehouse.util.ErrorHandler;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@WebServlet("/xiadan")
public class XiadanController extends HttpServlet {

    private final CustomerDAO customerDAO = new CustomerDAO();
    private final WarehouseDAO warehouseDAO = new WarehouseDAO();
    private final GoodsDAO goodsDAO = new GoodsDAO();

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        try {
            req.setAttribute("customers", customerDAO.getAllCustomers());
            req.setAttribute("warehouses", warehouseDAO.getAllWarehouses());
            req.setAttribute("goodsList", goodsDAO.getAllGoods());
            req.getRequestDispatcher("/WEB-INF/views/xiadan.jsp").forward(req, resp);
        } catch (SQLException e) {
            ErrorHandler.handle(resp, e);
        }
    }
}