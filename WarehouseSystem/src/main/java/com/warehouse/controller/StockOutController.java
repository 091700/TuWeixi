package com.warehouse.controller;

import java.io.IOException;
import java.util.List;

import com.warehouse.dao.CustomerDAO;
import com.warehouse.dao.StockDAO;
import com.warehouse.dao.WarehouseDAO;
import com.warehouse.model.Customer;
import com.warehouse.model.Warehouse;
import com.warehouse.util.ErrorHandler;

import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@WebServlet("/stock-out")
public class StockOutController extends HttpServlet {
    private final StockDAO stockDAO = new StockDAO();
    private final WarehouseDAO warehouseDAO = new WarehouseDAO();
    private final CustomerDAO customerDAO = new CustomerDAO();

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        try {
            int goodsId = Integer.parseInt(req.getParameter("goods_id"));
            req.setAttribute("goods_id", goodsId);
            List<Customer> customers = new CustomerDAO().getAllCustomers();
            req.setAttribute("customers", customers);
            List<Warehouse> warehouses = new WarehouseDAO().getAllWarehouses();
            req.setAttribute("warehouses", warehouses);
            req.getRequestDispatcher("/WEB-INF/views/stock-out.jsp").forward(req, resp);
        } catch (Exception e) {
            ErrorHandler.handle(resp, e);
        }
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        try {
            int warehouseId = Integer.parseInt(req.getParameter("warehouse_id"));
            int goodsId = Integer.parseInt(req.getParameter("goods_id"));
            int quantity = Integer.parseInt(req.getParameter("quantity"));
            int customerId = Integer.parseInt(req.getParameter("customer_id"));
            
            stockDAO.stockOut(warehouseId, goodsId, quantity, customerId);
            resp.sendRedirect(req.getContextPath() + "/goods");
        } catch (Exception e) {
            ErrorHandler.handle(resp, e);
        }
    }
}