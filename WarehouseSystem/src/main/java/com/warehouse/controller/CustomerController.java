// WarehouseSystem/src/main/java/com/warehouse/controller/CustomerController.java
package com.warehouse.controller;

import java.io.IOException;
import java.sql.SQLException;

import com.warehouse.dao.CustomerDAO;
import com.warehouse.model.Customer;
import com.warehouse.util.ErrorHandler;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@WebServlet("/customers")
public class CustomerController extends HttpServlet {

    private final CustomerDAO customerDAO = new CustomerDAO();

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        try {
            String action = req.getParameter("action");
            if ("create".equals(action)) {
                handleCreateCustomer(req, resp);
            }
        } catch (Exception e) {
            ErrorHandler.handle(resp, e);
        }
    }

    private void handleCreateCustomer(HttpServletRequest req, HttpServletResponse resp) throws SQLException, IOException {
        Customer customer = new Customer();
        customer.setName(req.getParameter("name"));
        customer.setContactPerson(req.getParameter("contactPerson"));
        customer.setAddress(req.getParameter("address"));
        customer.setContactPhone(req.getParameter("contactPhone"));
        customerDAO.insertCustomer(customer);
        resp.sendRedirect(req.getContextPath() + "/xiadan");
    }
}