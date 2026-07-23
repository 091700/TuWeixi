<?php
require 'database.php';

function getProducts() {
    global $pdo;
    try {
        $stmt = $pdo->query("SELECT * FROM products");
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    } catch (PDOException $e) {
        return [];
    }
}

function getProductById($id) {
    global $pdo;
    try {
        $stmt = $pdo->prepare("SELECT * FROM products WHERE id = ?");
        $stmt->execute([$id]);
        return $stmt->fetch(PDO::FETCH_ASSOC);
    } catch (PDOException $e) {
        return null;
    }
}

function addProduct($name, $price, $description) {
    global $pdo;
    try {
        $stmt = $pdo->prepare("INSERT INTO products (name, price, description) VALUES (?, ?, ?)");
        $stmt->execute([$name, $price, $description]);
        return $pdo->lastInsertId();
    } catch (PDOException $e) {
        return false;
    }
}

// 删除产品
function deleteProduct($id) {
    global $pdo;
    try {
        $stmt = $pdo->prepare("DELETE FROM products WHERE id = ?");
        return $stmt->execute([$id]);
    } catch (PDOException $e) {
        return false;
    }
}

if (basename($_SERVER['SCRIPT_NAME']) == 'add_to_cart.php') {
    session_start();
    
    if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['product_id'])) {
        $productId = $_POST['product_id'];

        if (getProductById($productId)) {
            if (!isset($_SESSION['cart'])) {
                $_SESSION['cart'] = [];
            }
            
            if (isset($_SESSION['cart'][$productId])) {
                $_SESSION['cart'][$productId]++;
            } else {
                $_SESSION['cart'][$productId] = 1;
            }
        }
        
        header('Location: ' . $_SERVER['HTTP_REFERER']);
        exit;
    }
}
?>