package com.warehouse.dao;

import java.sql.CallableStatement;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

import com.warehouse.config.DBConfig;

public class StockDAO {
    public void stockIn(int goodsId, int warehouseId, int quantity, int supplierId) throws SQLException {
        try (Connection conn = DBConfig.getConnection();
            CallableStatement cstmt = conn.prepareCall("{call insert_stock_in_record(?, ?, ?, ?, ?)}")) {
            cstmt.setInt(1, goodsId);
            cstmt.setInt(2, warehouseId);
            cstmt.setInt(3, quantity);
            cstmt.setInt(4, supplierId);
            cstmt.setString(5, "system");
            cstmt.executeUpdate();
        }
    }


    public void stockOut(int goodsId, int warehouseId, int quantity, int customerId) throws SQLException {
        try (Connection conn = DBConfig.getConnection()) {
            String checkSql = "SELECT stock_quantity FROM goods WHERE goods_id = ? FOR UPDATE";
            try (PreparedStatement p1 = conn.prepareStatement(checkSql)) {
                p1.setInt(1, goodsId);
                ResultSet rs = p1.executeQuery();
                if (rs.next() && rs.getInt(1) < quantity) {
                    throw new SQLException("库存不足");
                }
            }
            try (CallableStatement cstmt = conn.prepareCall("{call insert_stock_out_record(?, ?, ?, ?, ?)}")) {
                cstmt.setInt(1, goodsId);
            cstmt.setInt(2, warehouseId);
            cstmt.setInt(3, quantity);
            cstmt.setInt(4, customerId);
            cstmt.setString(5, "system");
            cstmt.executeUpdate();

            }
        }
    }}