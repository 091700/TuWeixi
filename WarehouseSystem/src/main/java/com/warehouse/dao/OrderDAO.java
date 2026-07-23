package com.warehouse.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

import com.warehouse.config.DBConfig;
import com.warehouse.model.Order;

public class OrderDAO {

    public List<Order> getAllOrders() throws SQLException {
        List<Order> orders = new ArrayList<>();
        String sql = "SELECT o.*, " +
                "c.customer_name, " +
                "w.warehouse_name " +
                "FROM `order` o " +
                "JOIN customer c ON o.customer_id = c.customer_id " +
                "JOIN warehouse w ON o.warehouse_id = w.warehouse_id";

        try (Connection conn = DBConfig.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {

            while (rs.next()) {
                Order order = mapOrderFromResultSet(rs);
                order.setItems(getOrderItems(order.getOrderId(), conn));
                orders.add(order);
            }
        }
        return orders;
    }
    public Order getOrderById(int orderId) throws SQLException {
        Order order = null;
        String sql = "SELECT o.*, " +
                "c.customer_name, " +
                "w.warehouse_name " +
                "FROM `order` o " +
                "JOIN customer c ON o.customer_id = c.customer_id " +
                "JOIN warehouse w ON o.warehouse_id = w.warehouse_id " +
                "WHERE o.order_id = ?";

        try (Connection conn = DBConfig.getConnection();
            PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, orderId);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    order = mapOrderFromResultSet(rs);
                    order.setItems(getOrderItems(order.getOrderId(), conn));
                }
            }
        }
        return order;
    }
    private Order mapOrderFromResultSet(ResultSet rs) throws SQLException {
        Order order = new Order();
        order.setOrderId(rs.getInt("order_id"));
        order.setCustomerId(rs.getInt("customer_id"));
        order.setCustomerName(rs.getString("customer_name"));
        order.setWarehouseId(rs.getInt("warehouse_id"));
        order.setWarehouseName(rs.getString("warehouse_name"));
        order.setTotalAmount(rs.getDouble("total_amount"));
        order.setStatus(rs.getString("status"));
        order.setCreatedAt(rs.getTimestamp("created_at"));
        return order;
    }

    private List<Order.Item> getOrderItems(int orderId, Connection conn) throws SQLException {
        List<Order.Item> items = new ArrayList<>();
        String sql = "SELECT oi.goods_id, " +
                "g.name AS goods_name, " +
                "oi.quantity, " +
                "oi.unit_price " +
                "FROM order_item oi " +
                "JOIN goods g ON oi.goods_id = g.goods_id " +
                "WHERE oi.order_id = ?";

        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, orderId);
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    Order.Item item = new Order.Item();
                    item.setGoodsId(rs.getInt("goods_id"));
                    item.setGoodsName(rs.getString("goods_name"));
                    item.setQuantity(rs.getInt("quantity"));
                    item.setUnitPrice(rs.getDouble("unit_price"));
                    items.add(item);
                }
            }
        }
        return items;
    }

    public void createOrder(Order order) throws SQLException {
        try (Connection conn = DBConfig.getConnection()) {
            conn.setAutoCommit(false);

            try {
                String orderSql = "INSERT INTO `order` (customer_id, warehouse_id, total_amount, status) " +
                        "VALUES (?, ?, ?, ?)";

                try (PreparedStatement orderStmt = conn.prepareStatement(orderSql, Statement.RETURN_GENERATED_KEYS)) {
                    orderStmt.setInt(1, order.getCustomerId());
                    orderStmt.setInt(2, order.getWarehouseId());
                    orderStmt.setDouble(3, order.getTotalAmount());
                    orderStmt.setString(4, "PENDING");

                    int affectedRows = orderStmt.executeUpdate();
                    System.out.println("插入订单主表，影响行数: " + affectedRows);

                    if (affectedRows == 0) {
                        throw new SQLException("创建订单失败，未插入任何记录");
                    }

                    try (ResultSet rs = orderStmt.getGeneratedKeys()) {
                        if (rs.next()) {
                            int orderId = rs.getInt(1);
                            System.out.println("新订单ID: " + orderId);

                            insertOrderItems(conn, orderId, order.getItems());
                        } else {
                            throw new SQLException("创建订单失败，未获取到订单ID");
                        }
                    }
                }

                conn.commit();
                System.out.println("订单创建成功");
            } catch (SQLException e) {
                conn.rollback();
                System.err.println("创建订单失败，事务已回滚: " + e.getMessage());
                throw e;
            } finally {
                conn.setAutoCommit(true);
            }
        }
    }

    private void insertOrderItems(Connection conn, int orderId, List<Order.Item> items) throws SQLException {
        String itemSql = "INSERT INTO order_item (order_id, goods_id, quantity, unit_price) " +
                "VALUES (?, ?, ?, ?)";

        try (PreparedStatement itemStmt = conn.prepareStatement(itemSql)) {
            for (Order.Item item : items) {
                itemStmt.setInt(1, orderId);
                itemStmt.setInt(2, item.getGoodsId());
                itemStmt.setInt(3, item.getQuantity());
                itemStmt.setDouble(4, item.getUnitPrice());
                itemStmt.addBatch();
            }

            int[] batchResults = itemStmt.executeBatch();
            System.out.println("插入订单明细，影响行数: " + batchResults.length);
        }
    }

    public void updateOrderStatus(int orderId, String status) throws SQLException {
        System.out.println("更新订单状态: orderId=" + orderId + ", status=" + status);

        try (Connection conn = DBConfig.getConnection()) {
            conn.setAutoCommit(false);

            try {
                String sql = "UPDATE `order` SET status = ? WHERE order_id = ?";

                try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
                    pstmt.setString(1, status);
                    pstmt.setInt(2, orderId);

                    int rowsUpdated = pstmt.executeUpdate();
                    System.out.println("更新状态影响行数: " + rowsUpdated);

                    if (rowsUpdated == 0) {
                        throw new SQLException("未更新任何行，订单ID可能不存在: " + orderId);
                    }
                }

                conn.commit();
                System.out.println("订单状态更新成功");
            } catch (SQLException e) {
                conn.rollback();
                System.err.println("更新订单状态失败，事务已回滚: " + e.getMessage());
                throw e;
            } finally {
                conn.setAutoCommit(true);
            }
        }
    }

    public boolean orderExists(int orderId) throws SQLException {
        String sql = "SELECT COUNT(*) FROM `order` WHERE order_id = ?";

        try (Connection conn = DBConfig.getConnection();
            PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, orderId);

            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    return rs.getInt(1) > 0;
                }
            }
        }
        return false;
    }
}