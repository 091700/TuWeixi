package com.warehouse.controller;

import java.io.IOException;

import com.google.gson.Gson;
import com.warehouse.dao.WarehouseDAO;
import com.warehouse.model.Warehouse;
import com.warehouse.util.ErrorHandler;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@WebServlet("/warehouses")
public class WarehouseController extends HttpServlet {
    private final WarehouseDAO warehouseDAO = new WarehouseDAO();
    private final Gson gson = new Gson(); // 添加Gson实例

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) 
            throws ServletException, IOException {
        try {
            String action = req.getParameter("action");
            
            if ("edit".equals(action)) {
                int id = Integer.parseInt(req.getParameter("id"));
                Warehouse warehouse = warehouseDAO.getWarehouseById(id);
                req.setAttribute("warehouse", warehouse);
            } else if ("get".equals(action)) { // 新增：处理获取单个仓库数据
                int id = Integer.parseInt(req.getParameter("id"));
                Warehouse warehouse = warehouseDAO.getWarehouseById(id);
                resp.setContentType("application/json");
                gson.toJson(warehouse, resp.getWriter()); // 返回JSON
                return;
            }
            
            req.setAttribute("warehouses", warehouseDAO.getAllWarehouses());
            req.getRequestDispatcher("/WEB-INF/views/warehouse-list.jsp").forward(req, resp);
            
        } catch (Exception e) {
            ErrorHandler.handle(resp, e);
        }
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) 
            throws ServletException, IOException {
        try {
            String action = req.getParameter("action");
            
            if ("delete".equals(action)) {
                // 添加参数非空校验
                String idParam = req.getParameter("id");
                if (idParam == null || idParam.isEmpty()) {
                    throw new IllegalArgumentException("删除仓库时ID不能为空");
                }
                int id = Integer.parseInt(idParam);
                warehouseDAO.deleteWarehouse(id);
                
            } else {
                Warehouse warehouse = new Warehouse();
                warehouse.setName(req.getParameter("name"));
                warehouse.setAddress(req.getParameter("address"));
                warehouse.setArea(Double.parseDouble(req.getParameter("area")));

                if ("update".equals(action)) {
                    // 添加参数非空校验
                    String idParam = req.getParameter("id");
                    if (idParam == null || idParam.isEmpty()) {
                        throw new IllegalArgumentException("更新仓库时ID不能为空");
                    }
                    warehouse.setId(Integer.parseInt(idParam));
                    warehouseDAO.updateWarehouse(warehouse);
                } else {
                    warehouseDAO.insertWarehouse(warehouse);
                }
            }
            resp.sendRedirect("warehouses?r=" + System.currentTimeMillis());
            
        } catch (Exception e) {
            ErrorHandler.handle(resp, e);
        }
    }
}