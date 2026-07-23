package com.warehouse.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

import com.warehouse.config.DBConfig;
import com.warehouse.model.Goods;

public class GoodsDAO {
    public List<Goods> getAllGoods() throws SQLException {
        List<Goods> goodsList = new ArrayList<>();
        String sql = "SELECT * FROM goods";
        
        try (Connection conn = DBConfig.getConnection();
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery(sql)) {
            
            while (rs.next()) {
                Goods goods = new Goods();
                goods.setGoodsId(rs.getInt("goods_id"));
                goods.setName(rs.getString("name"));
                goods.setSpecification(rs.getString("specification"));
                goods.setPrice(rs.getDouble("price"));
                goods.setStockQuantity(rs.getInt("stock_quantity"));
                goodsList.add(goods);
            }
        }
        return goodsList;
    }

    public Goods getGoodsById(int id) throws SQLException {
        String sql = "SELECT goods_id, name, specification, price, stock_quantity AS stockQuantity, min_stock AS minStock FROM goods WHERE goods_id = ?";
        System.out.println("[SQL] 执行查询: " + sql);
    System.out.println("[SQL] 参数: goods_id=" + id);
        try (Connection conn = DBConfig.getConnection();
            PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    Goods goods = new Goods();
                    goods.setGoodsId(rs.getInt("goods_id"));
                    goods.setName(rs.getString("name"));
                    goods.setSpecification(rs.getString("specification"));
                    goods.setPrice(rs.getDouble("price"));
                    goods.setStockQuantity(rs.getInt("stockQuantity"));
                    return goods;
                }
            }
        }
        return null;
    }

    public void insertGoods(Goods goods) throws SQLException {
        String sql = "INSERT INTO goods (name, specification, price) VALUES (?, ?, ?)";
        try (Connection conn = DBConfig.getConnection();
            PreparedStatement pstmt = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            
            pstmt.setString(1, goods.getName());
            pstmt.setString(2, goods.getSpecification());
            pstmt.setDouble(3, goods.getPrice());
            
            int affectedRows = pstmt.executeUpdate();
            if (affectedRows == 0) {
                throw new SQLException("新增商品失败，无行受影响");
            }
            
            try (ResultSet rs = pstmt.getGeneratedKeys()) {
                if (rs.next()) {
                    goods.setGoodsId(rs.getInt(1));
                }
            }
        }
    }


    public void updateGoods(Goods goods) throws SQLException {
        String sql = "UPDATE goods SET name=?, specification=?, price=? WHERE goods_id=?";
        try (Connection conn = DBConfig.getConnection();
            PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, goods.getName());
            pstmt.setString(2, goods.getSpecification());
            pstmt.setDouble(3, goods.getPrice());
            pstmt.setInt(4, goods.getGoodsId());
            pstmt.executeUpdate();
        }
    }

    public void deleteGoods(int goodsId) throws SQLException {
        try (Connection conn = DBConfig.getConnection()) {
            conn.setAutoCommit(false);
            String[] deleteSQLs = {
                "DELETE FROM stock_in_record WHERE goods_id = ?",
                "DELETE FROM stock_out_record WHERE goods_id = ?",
                "DELETE FROM order_item WHERE goods_id = ?",
                "DELETE FROM goods WHERE goods_id = ?"
            };
            
            try {
                for (String sql : deleteSQLs) {
                    try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
                        pstmt.setInt(1, goodsId);
                        System.out.println("执行SQL：" + pstmt.toString());
                        int affected = pstmt.executeUpdate();
                        System.out.println("影响行数：" + affected);
                    }
                }
                conn.commit();
            } catch (SQLException e) {
                conn.rollback();
                throw new SQLException("删除失败：" + e.getMessage());
            }
        }
    }}

