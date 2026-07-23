package com.warehouse.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

import com.warehouse.config.DBConfig;
import com.warehouse.model.Customer;

public class CustomerDAO {
    public List<Customer> getAllCustomers() throws SQLException {
        List<Customer> list = new ArrayList<>();
        String sql = "SELECT "
            + "customer_id, "
            + "customer_name, "
            + "contact_person, "
            + "customer_address, "
            + "contact_phone "
            + "FROM customer";
        try (Connection conn = DBConfig.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
            
            while (rs.next()) {
                Customer customer = new Customer();
                customer.setId(rs.getInt("customer_id"));
                customer.setName(rs.getString("customer_name"));
                customer.setContactPerson(rs.getString("contact_person"));
                customer.setAddress(rs.getString("customer_address"));
                customer.setContactPhone(rs.getString("contact_phone"));
                list.add(customer);
            }
        }
        return list;
    }
    public void insertCustomer(Customer customer) throws SQLException {
        String sql = "INSERT INTO customer (customer_name, customer_address, contact_person, contact_phone) VALUES (?, ?, ?, ?)";
        try (Connection conn = DBConfig.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, customer.getName());
            pstmt.setString(2, customer.getAddress());
            pstmt.setString(3, customer.getContactPerson());
            pstmt.setString(4, customer.getContactPhone());
            pstmt.executeUpdate();
        }
    }
}