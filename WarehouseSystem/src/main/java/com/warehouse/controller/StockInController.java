package com.warehouse.controller;

import java.io.IOException;

import com.warehouse.dao.GoodsDAO;
import com.warehouse.dao.StockDAO;
import com.warehouse.dao.SupplierDAO;
import com.warehouse.dao.WarehouseDAO;
import com.warehouse.model.Goods;
import com.warehouse.model.Warehouse;
import com.warehouse.util.ErrorHandler;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@WebServlet("/stock-in")
public class StockInController extends HttpServlet {
    private final StockDAO stockDAO = new StockDAO();
    private final WarehouseDAO warehouseDAO = new WarehouseDAO();
    private final GoodsDAO goodsDAO = new GoodsDAO();
    private final SupplierDAO supplierDAO = new SupplierDAO();

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        try {
            int goodsId = Integer.parseInt(req.getParameter("goods_id"));
            req.setAttribute("goods_id", goodsId);
            req.setAttribute("warehouses", warehouseDAO.getAllWarehouses());
            req.setAttribute("suppliers", supplierDAO.getAllSuppliers());
            req.setAttribute("goodsList", goodsDAO.getAllGoods());
            req.getRequestDispatcher("/WEB-INF/views/stock-in.jsp").forward(req, resp);
        } catch (Exception e) {
            ErrorHandler.handle(resp, e);
        }
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        try {
            int warehouseId = Integer.parseInt(req.getParameter("warehouse_id"));
            int goodsId = Integer.parseInt(req.getParameter("goods_id"));
            int quantity = Integer.parseInt(req.getParameter("quantity"));
            int supplierId = Integer.parseInt(req.getParameter("supplier_id"));

            Goods goods = new GoodsDAO().getGoodsById(goodsId);
            if (goods == null) {
                throw new IllegalArgumentException("商品不存在");
            }
            Warehouse warehouse = new WarehouseDAO().getWarehouseById(warehouseId);
            if (warehouse == null) {
                throw new IllegalArgumentException("仓库不存在");
            }
            new StockDAO().stockIn(goodsId, warehouseId, quantity, supplierId);
            resp.sendRedirect(req.getContextPath() + "/goods");
        } catch (Exception e) {
            ErrorHandler.handle(resp, e);
        }
    }
}