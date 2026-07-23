<?php
session_start();
require 'functions.php';

$products = getProducts();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>All Products | E-commerce Platform</title>
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
        <h2>All Products</h2>
        
        <div class="products-grid">
            <?php foreach ($products as $product): ?>
            <div class="product-card">
                <h3><?php echo $product['name']; ?></h3>
                <p class="price">¥<?php echo number_format($product['price'], 2); ?></p>
                <p><?php echo substr($product['description'], 0, 50); ?>...</p>
                <form method="post" action="add_to_cart.php">
                    <input type="hidden" name="product_id" value="<?php echo $product['id']; ?>">
                    <button type="submit" class="btn">Add to Cart</button>
                </form>
            </div>
            <?php endforeach; ?>
        </div>
    </main>
</body>
</html>