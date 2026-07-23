package com.example.intelligentbookplatform.controller;

import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

import com.example.intelligentbookplatform.model.Order;
import com.example.intelligentbookplatform.model.User;
import com.example.intelligentbookplatform.service.OrderService;

@Controller
@RequestMapping("/orders")
public class OrderController {
    
    @Autowired
    private OrderService orderService;
    
    // 创建订单（POST请求，通过表单提交）
    @PostMapping
    public String createOrder(@RequestParam Long bookId,
                            @RequestParam Integer quantity,
                            @AuthenticationPrincipal User user) {
        List<OrderService.CartItem> cartItems = new ArrayList<>();
        cartItems.add(new OrderService.CartItem(bookId, quantity));
        
        orderService.createOrder(user, cartItems);
        return "redirect:/orders/my"; // 创建后跳转到订单列表
    }
    
    // 查看我的订单（GET请求，支持浏览器直接访问）
    @GetMapping("/my")
    public String myOrders(@AuthenticationPrincipal User user, Model model) {
        List<Order> orders = orderService.getOrdersByUser(user);
        model.addAttribute("orders", orders); // 传递订单数据到页面
        return "orders";
    }
    
    // 更新订单状态（POST请求，管理员用）
    @PostMapping("/{orderId}/status")
    public String updateOrderStatus(@PathVariable Long orderId,
                                  @RequestParam Order.Status status) {
        orderService.updateOrderStatus(orderId, status);
        return "redirect:/admin/orders"; // 跳转到管理员订单页
    }
}