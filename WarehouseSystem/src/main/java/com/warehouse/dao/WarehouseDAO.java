package com.warehouse.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

import com.warehouse.config.DBConfig;
import com.warehouse.model.Warehouse;

public class WarehouseDAO {
    public List<Warehouse> getAllWarehouses() throws SQLException {
        List<Warehouse> warehouses = new ArrayList<>();
        String sql = "SELECT * FROM warehouse";
        
        try (Connection conn = DBConfig.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            while (rs.next()) {
                Warehouse warehouse = new Warehouse();
                warehouse.setId(rs.getInt("warehouse_id"));
                warehouse.setName(rs.getString("warehouse_name"));
                warehouse.setAddress(rs.getString("warehouse_address"));
                warehouse.setArea(rs.getDouble("warehouse_area"));
                warehouses.add(warehouse);
            }
        }
        return warehouses;
    }

    public Warehouse getWarehouseById(int id) throws SQLException {
        String sql = "SELECT * FROM warehouse WHERE warehouse_id = ?";
        try (Connection conn = DBConfig.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    Warehouse warehouse = new Warehouse();
                    warehouse.setId(rs.getInt("warehouse_id"));
                    warehouse.setName(rs.getString("warehouse_name"));
                    warehouse.setAddress(rs.getString("warehouse_address"));
                    warehouse.setArea(rs.getDouble("warehouse_area"));
                    return warehouse;
                }
            }
        }
        return null;
    }

    public void insertWarehouse(Warehouse warehouse) throws SQLException {
        String sql = "INSERT INTO warehouse (warehouse_name, warehouse_address, warehouse_area) VALUES (?, ?, ?)";
        try (Connection conn = DBConfig.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, warehouse.getName());
            pstmt.setString(2, warehouse.getAddress());
            pstmt.setDouble(3, warehouse.getArea());
            pstmt.executeUpdate();
        }
    }

    public void updateWarehouse(Warehouse warehouse) throws SQLException {
        String sql = "UPDATE warehouse SET warehouse_name = ?, warehouse_address = ?, warehouse_area = ? WHERE warehouse_id = ?";
        try (Connection conn = DBConfig.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, warehouse.getName());
            pstmt.setString(2, warehouse.getAddress());
            pstmt.setDouble(3, warehouse.getArea());
            pstmt.setInt(4, warehouse.getId());
            pstmt.executeUpdate();
        }
    }

    public void deleteWarehouse(int id) throws SQLException {
        String sql = "DELETE FROM warehouse WHERE warehouse_id = ?";
        try (Connection conn = DBConfig.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            pstmt.executeUpdate();
        }
    }
}