package com.example.intelligentbookplatform.service;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.example.intelligentbookplatform.model.Book;
import com.example.intelligentbookplatform.model.Order;
import com.example.intelligentbookplatform.model.OrderItem;
import com.example.intelligentbookplatform.model.User;
import com.example.intelligentbookplatform.repository.BookRepository;
import com.example.intelligentbookplatform.repository.OrderRepository;

@Service
@Transactional
public class OrderService {
    
    @Autowired
    private OrderRepository orderRepository;
    
    @Autowired
    private BookRepository bookRepository;
    
    // 创建订单
    public Order createOrder(User buyer, List<CartItem> cartItems) {
        Order order = new Order();
        order.setBuyer(buyer);
        BigDecimal totalPrice = BigDecimal.ZERO;
        
        List<OrderItem> orderItems = new ArrayList<>();
        
        for (CartItem item : cartItems) {
            Book book = bookRepository.findById(item.getBookId())
                    .orElseThrow(() -> new RuntimeException("图书不存在: " + item.getBookId()));
            
            if (book.getStock() < item.getQuantity()) {
                throw new RuntimeException("库存不足: " + book.getTitle());
            }
            
            OrderItem orderItem = new OrderItem();
            orderItem.setBook(book);
            orderItem.setQuantity(item.getQuantity());
            orderItem.setPrice(book.getPrice());
            orderItem.setOrder(order);
            orderItems.add(orderItem);
            
            // 计算总价
            totalPrice = totalPrice.add(book.getPrice().multiply(BigDecimal.valueOf(item.getQuantity())));
            
            // 更新库存和销量
            book.setStock(book.getStock() - item.getQuantity());
            book.setPurchaseCount(book.getPurchaseCount() + item.getQuantity());
            bookRepository.save(book);
        }
        
        order.setTotalPrice(totalPrice);
        order.setOrderItems(orderItems);
        return orderRepository.save(order);
    }
    
    // 获取用户的所有订单
    public List<Order> getOrdersByUser(User user) {
        return orderRepository.findByBuyerOrderByCreatedAtDesc(user);
    }
    
    // 根据ID查询订单
    public Order findOrderById(Long id) {
        return orderRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("订单不存在"));
    }
    
    // 更新订单状态
    public Order updateOrderStatus(Long orderId, Order.Status status) {
        Order order = findOrderById(orderId);
        order.setStatus(status);
        return orderRepository.save(order);
    }
    
    // 购物车项内部类
    public static class CartItem {
        private Long bookId;
        private Integer quantity;
        
        public CartItem() {}
        
        public CartItem(Long bookId, Integer quantity) {
            this.bookId = bookId;
            this.quantity = quantity;
        }
        
        // Getter和Setter
        public Long getBookId() { return bookId; }
        public void setBookId(Long bookId) { this.bookId = bookId; }
        
        public Integer getQuantity() { return quantity; }
        public void setQuantity(Integer quantity) { this.quantity = quantity; }
    }
}