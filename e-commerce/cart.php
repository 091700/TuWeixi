<?php
session_start();
require 'functions.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['remove_item'])) {
        $productId = $_POST['product_id'];
        if (isset($_SESSION['cart'][$productId])) {
            unset($_SESSION['cart'][$productId]);
        }
    } elseif (isset($_POST['clear_cart'])) {
        unset($_SESSION['cart']);
    }
}

$cartItems = [];
$total = 0;

if (isset($_SESSION['cart']) && !empty($_SESSION['cart'])) {
    foreach ($_SESSION['cart'] as $productId => $quantity) {
        $product = getProductById($productId);
        if ($product) {
            $product['quantity'] = $quantity;
            $product['subtotal'] = $product['price'] * $quantity;
            $total += $product['subtotal'];
            $cartItems[] = $product;
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shopping Cart | E-commerce Platform</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <div class="container">
            <h1><a href="index.php">E-commerce Platform</a></h1>
            <nav>
                <ul>
                    <li><a href="index.php">Home</a></li>
                    <li><a href="products.php">All Products</a></li>
                    <li><a href="cart.php">Cart</a></li>
                </ul>
            </nav>
            <div class="cart">
                <a href="cart.php">Cart (<?php echo isset($_SESSION['cart']) ? count($_SESSION['cart']) : 0; ?>)</a>
            </div>
        </div>
    </header>

    <main class="container">
        <h2>Shopping Cart</h2>
        
        <?php if (empty($cartItems)): ?>
            <p>Your cart is empty. <a href="products.php">Browse Products</a></p>
        <?php else: ?>
            <table>
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>Unit Price</th>
                        <th>Quantity</th>
                        <th>Subtotal</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($cartItems as $item): ?>
                    <tr>
                        <td><?php echo $item['name']; ?></td>
                        <td>¥<?php echo number_format($item['price'], 2); ?></td>
                        <td><?php echo $item['quantity']; ?></td>
                        <td>¥<?php echo number_format($item['subtotal'], 2); ?></td>
                        <td>
                            <form method="post">
                                <input type="hidden" name="product_id" value="<?php echo $item['id']; ?>">
                                <button type="submit" name="remove_item" class="btn">Remove</button>
                            </form>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
            
            <div class="cart-summary">
                <h3>Order Total: ¥<?php echo number_format($total, 2); ?></h3>
                
                <div class="cart-actions">
                    <form method="post">
                        <button type="submit" name="clear_cart">Clear Cart</button>
                    </form>
                    <a href="checkout.php" class="btn">Checkout</a>
                </div>
            </div>
        <?php endif; ?>
    </main>
</body>
</html>