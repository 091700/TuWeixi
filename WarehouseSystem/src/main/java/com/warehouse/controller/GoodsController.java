package com.warehouse.controller;

import java.io.IOException;
import java.util.List;

import org.json.JSONObject;

import com.warehouse.dao.GoodsDAO;
import com.warehouse.model.Goods;
import com.warehouse.util.ErrorHandler;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@WebServlet("/goods")
public class GoodsController extends HttpServlet {
    private final GoodsDAO goodsDAO = new GoodsDAO();

    @Override
protected void doGet(HttpServletRequest req, HttpServletResponse resp) 
        throws ServletException, IOException {
    try {
        String action = req.getParameter("action");
        if ("get".equals(action)) {
            handleGetSingleGoods(req, resp);
        } 
        else {
            handleGetAllGoods(req, resp);
        }
        
    } catch (Exception e) {
        ErrorHandler.handle(resp, e);
    }
}


@Override
protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
    try {
        String action = req.getParameter("action");
        if ("delete".equals(action)) {
            handleDelete(req);
        } else {
            handleUpsert(req);
            Goods goods = new Goods();
            goods.setName(req.getParameter("name"));
            goods.setSpecification(req.getParameter("specification"));
            goods.setPrice(Double.parseDouble(req.getParameter("price")));

            if ("update".equals(action)) {
                goods.setGoodsId(Integer.parseInt(req.getParameter("id")));
                goodsDAO.updateGoods(goods);
            } else {
                goodsDAO.insertGoods(goods);
            }
            
            JSONObject json = new JSONObject();
            json.put("status", "success");
            json.put("goodsId", goods.getGoodsId());
            resp.setContentType("application/json");
            resp.getWriter().print(json.toString());
            return;
        }
        JSONObject json = new JSONObject();
        json.put("status", "success");
        resp.setContentType("application/json");
        resp.getWriter().print(json.toString());
    } catch (Exception e) {
        ErrorHandler.handle(resp, e);
    }
}

    private void handleGetSingleGoods(HttpServletRequest req, HttpServletResponse resp) 
        throws Exception {
    String idParam = req.getParameter("id");
    if (idParam == null || idParam.isEmpty()) {
        resp.sendError(HttpServletResponse.SC_BAD_REQUEST, "缺失商品ID参数");
        return;
    }
    
    try {
        int goodsId = Integer.parseInt(idParam);
        Goods goods = goodsDAO.getGoodsById(goodsId);
        
        if (goods == null) {
            resp.sendError(HttpServletResponse.SC_NOT_FOUND, "商品不存在");
            return;
        }
        
        JSONObject json = new JSONObject();
        json.put("goodsId", goods.getGoodsId());
        json.put("name", goods.getName());
        json.put("specification", goods.getSpecification());
        json.put("price", goods.getPrice());
        json.put("stockQuantity", goods.getStockQuantity());
        resp.setContentType("application/json;charset=UTF-8");
        resp.getWriter().print(json.toString());
        
    } catch (NumberFormatException e) {
        resp.sendError(HttpServletResponse.SC_BAD_REQUEST, "无效的商品ID格式");
    }
}
private void handleGetAllGoods(HttpServletRequest req, HttpServletResponse resp)
        throws Exception {
    List<Goods> goodsList = goodsDAO.getAllGoods();
    req.setAttribute("goodsList", goodsList);
    req.getRequestDispatcher("/WEB-INF/views/goods-list.jsp").forward(req, resp);
}
    private void handleDelete(HttpServletRequest req) throws Exception {
        String idParam = req.getParameter("id");
        if (idParam == null || idParam.isEmpty()) {
            throw new IllegalArgumentException("缺少商品ID参数");
        }
        goodsDAO.deleteGoods(Integer.parseInt(idParam));
    }

    private void handleUpsert(HttpServletRequest req) throws Exception {
        Goods goods = new Goods();
        goods.setName(req.getParameter("name"));
        goods.setSpecification(req.getParameter("specification"));
        goods.setPrice(Double.parseDouble(req.getParameter("price")));
        
        System.out.println("收到请求参数：" + req.getParameterMap());

        String idParam = req.getParameter("id");
        if (idParam != null && !idParam.isEmpty()) {
            goods.setGoodsId(Integer.parseInt(idParam));
            goodsDAO.updateGoods(goods);
        } else {
            goodsDAO.insertGoods(goods);
        }
    }
}