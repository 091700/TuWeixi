package com.warehouse.controller;

import java.io.IOException;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

import com.warehouse.dao.CustomerDAO;
import com.warehouse.dao.GoodsDAO;
import com.warehouse.dao.OrderDAO;
import com.warehouse.dao.StockDAO;
import com.warehouse.dao.WarehouseDAO;
import com.warehouse.model.Order;
import com.warehouse.util.ErrorHandler;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@WebServlet("/orders")
public class OrderController extends HttpServlet {

    private final OrderDAO orderDAO = new OrderDAO();
    private final CustomerDAO customerDAO = new CustomerDAO();
    private final WarehouseDAO warehouseDAO = new WarehouseDAO();
    private final GoodsDAO goodsDAO = new GoodsDAO();
    private final StockDAO stockDAO = new StockDAO();

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        try {
            List<Order> orders = orderDAO.getAllOrders();
            req.setAttribute("orders", orders);
            req.setAttribute("customers", customerDAO.getAllCustomers());
            req.setAttribute("warehouses", warehouseDAO.getAllWarehouses());
            req.setAttribute("goodsList", goodsDAO.getAllGoods());
            req.getRequestDispatcher("/WEB-INF/views/order-list.jsp").forward(req, resp);
        } catch (Exception e) {
            ErrorHandler.handle(resp, e);
        }
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        try {
            String action = req.getParameter("action");
            if ("confirm".equals(action)) {
                handleConfirmAction(req, resp);
            } else if ("create".equals(action)) {
                handleCreateOrder(req, resp);
            }
        } catch (Exception e) {
            ErrorHandler.handle(resp, e);
        }
    }

    private void handleConfirmAction(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException, SQLException {
        int orderId = Integer.parseInt(req.getParameter("orderId"));
        if (!orderDAO.orderExists(orderId)) {
            resp.setStatus(HttpServletResponse.SC_NOT_FOUND);
            resp.getWriter().write("订单不存在");
            return;
        }
        orderDAO.updateOrderStatus(orderId, "CONFIRMED");

        Order order = orderDAO.getOrderById(orderId);
        int customerId = order.getCustomerId();
        int warehouseId = order.getWarehouseId();
        List<Order.Item> items = order.getItems();

        for (Order.Item item : items) {
            int goodsId = item.getGoodsId();
            int quantity = item.getQuantity();
            stockDAO.stockOut(goodsId, warehouseId, quantity, customerId);
        }
        resp.setStatus(HttpServletResponse.SC_OK);
        resp.getWriter().write("订单确认成功");

    }

    private void handleCreateOrder(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException, SQLException {
        Order order = new Order();
        order.setCustomerId(Integer.parseInt(req.getParameter("customerId")));
        order.setWarehouseId(Integer.parseInt(req.getParameter("warehouseId")));
        List<Order.Item> items = new ArrayList<>();

        String[] goodsIds = req.getParameterValues("goodsId");
        String[] quantities = req.getParameterValues("quantity");
        double totalAmount = 0;
        for (int i = 0; i < goodsIds.length; i++) {
            int goodsId = Integer.parseInt(goodsIds[i]);
            int quantity = Integer.parseInt(quantities[i]);
            if (quantity > 0) {
                double price = goodsDAO.getGoodsById(goodsId).getPrice();
                Order.Item item = new Order.Item();
                item.setGoodsId(goodsId);
                item.setQuantity(quantity);
                item.setUnitPrice(price);
                items.add(item);
                totalAmount += price * quantity;
            }
        }
        order.setTotalAmount(totalAmount);
        order.setItems(items);
        orderDAO.createOrder(order);
        resp.sendRedirect("orders");
    }
}