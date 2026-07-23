<?php
session_start();
require 'functions.php';

if (!isset($_SESSION['user_logged_in']) || $_SESSION['user_logged_in'] !== true) {
    header('Location: login.php');
    exit;
}

$products = getProducts();
$featuredProducts = array_slice($products, 0, 4);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-commerce Platform</title>
    <link rel="stylesheet" href="style.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
        }
        
        body {
            background-color: #f8f9fa;
            color: #333;
            line-height: 1.6;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        header {
            background: #2c3e50;
            padding: 15px 0;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .nav-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: 700;
            color: white;
            text-decoration: none;
        }
        
        .nav-links {
            display: flex;
            list-style: none;
        }
        
        .nav-links li {
            margin: 0 15px;
        }
        
        .nav-links a {
            color: rgba(255, 255, 255, 0.85);
            text-decoration: none;
            font-weight: 500;
            padding: 8px 0;
            position: relative;
            transition: color 0.3s;
        }
        
        .nav-links a:hover,
        .nav-links a.active {
            color: white;
        }
        
        .nav-links a::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 0;
            height: 2px;
            background: white;
            transition: width 0.3s;
        }
        
        .nav-links a:hover::after,
        .nav-links a.active::after {
            width: 100%;
        }
        
        .cart-btn {
            background: #e74c3c;
            color: white;
            padding: 8px 15px;
            border-radius: 4px;
            text-decoration: none;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: background 0.3s;
        }
        
        .cart-btn:hover {
            background: #c0392b;
        }
        
        .cart-count {
            background: white;
            color: #e74c3c;
            width: 22px;
            height: 22px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.85rem;
            font-weight: bold;
        }
        
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .welcome-section {
            background: linear-gradient(rgba(44, 62, 80, 0.9), rgba(44, 62, 80, 0.9));
            color: white;
            padding: 80px 20px;
            text-align: center;
        }
        
        .welcome-container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .welcome-title {
            font-size: 2.5rem;
            margin-bottom: 20px;
            font-weight: 700;
        }
        
        .welcome-subtitle {
            font-size: 1.2rem;
            margin-bottom: 30px;
            opacity: 0.9;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .browse-btn {
            background: #3498db;
            color: white;
            padding: 12px 30px;
            border-radius: 4px;
            text-decoration: none;
            font-weight: 500;
            display: inline-block;
            transition: background 0.3s, transform 0.3s;
        }
        
        .browse-btn:hover {
            background: #2980b9;
            transform: translateY(-3px);
        }

        .featured-section {
            padding: 60px 20px;
            background: white;
        }
        
        .section-header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .section-title {
            font-size: 2rem;
            color: #2c3e50;
            margin-bottom: 15px;
            position: relative;
            display: inline-block;
        }
        
        .section-title::after {
            content: '';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 3px;
            background: #3498db;
        }
        
        .section-subtitle {
            color: #777;
            font-size: 1.1rem;
            margin-top: 15px;
        }
        
        .products-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .product-card {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s;
        }
        
        .product-card:hover {
            transform: translateY(-10px);
        }
        
        .product-image {
            height: 180px;
            background: linear-gradient(45deg, #f5f7fa, #e4e7eb);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #3498db;
            font-size: 3.5rem;
        }
        
        .product-info {
            padding: 20px;
        }
        
        .product-name {
            font-size: 1.2rem;
            margin-bottom: 10px;
            color: #2c3e50;
        }
        
        .product-price {
            font-weight: 700;
            font-size: 1.3rem;
            color: #e74c3c;
            margin-bottom: 15px;
        }
        
        .add-to-cart-form {
            display: flex;
        }
        
        .add-to-cart-btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            flex: 1;
            transition: background 0.3s;
        }
        
        .add-to-cart-btn:hover {
            background: #2980b9;
        }
        
        .features-section {
            padding: 60px 20px;
            background: #f8f9fa;
        }
        
        .features-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .feature-card {
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
            text-align: center;
        }
        
        .feature-icon {
            width: 60px;
            height: 60px;
            background: rgba(52, 152, 219, 0.1);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            color: #3498db;
            font-size: 1.5rem;
        }
        
        .feature-title {
            font-size: 1.3rem;
            margin-bottom: 15px;
            color: #2c3e50;
        }
        
        .feature-desc {
            color: #777;
            line-height: 1.6;
        }

        footer {
            background: #2c3e50;
            color: white;
            padding: 40px 20px 20px;
            margin-top: auto;
        }
        
        .footer-container {
            max-width: 1200px;
            margin: 0 auto;
            text-align: center;
        }
        
        .footer-links {
            display: flex;
            justify-content: center;
            list-style: none;
            margin-bottom: 30px;
        }
        
        .footer-links li {
            margin: 0 15px;
        }
        
        .footer-links a {
            color: rgba(255, 255, 255, 0.8);
            text-decoration: none;
            transition: color 0.3s;
        }
        
        .footer-links a:hover {
            color: white;
        }
        
        .copyright {
            color: rgba(255, 255, 255, 0.6);
            font-size: 0.9rem;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        @media (max-width: 768px) {
            .nav-container {
                flex-direction: column;
                gap: 15px;
            }
            
            .nav-links {
                margin-top: 10px;
            }
            
            .welcome-title {
                font-size: 2rem;
            }
            
            .section-title {
                font-size: 1.8rem;
            }
            
            .products-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    <script>
        function checkAdminPassword() {
            var password = prompt("password:");
            if (password) {
                fetch('verify_password.php', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: 'password=' + encodeURIComponent(password),
                })
               .then(response => response.text())
               .then(data => {
                    console.log('Result:', data);
                    if (data.trim() === 'success') {
                        window.location.href = 'admin.php';
                    } else {
                        alert('Incorrect password, please try again!');
                    }
                })
               .catch(error => {
                    console.error('Request error:', error);
                    alert('An error occurred, please try again later');
                });
            }
            return false;
        }
    </script>
</head>
<body>
    <header>
        <div class="nav-container">
            <a href="index.php" class="logo">E-commerce Platform</a>
            
            <ul class="nav-links">
                <li><a href="index.php" class="active">Home</a></li>
                <li><a href="products.php">All Products</a></li>
                <li><a href="cart.php">Cart</a></li>
                <li><a href="#" onclick="checkAdminPassword()">Admin</a></li>
                <li><a href="logout.php">Logout</a></li>
            </ul>
            
            <a href="cart.php" class="cart-btn">
                <span>Cart</span>
                <div class="cart-count"><?php echo isset($_SESSION['cart']) ? count($_SESSION['cart']) : 0; ?></div>
            </a>
        </div>
    </header>

    <div class="main-content">
        <section class="welcome-section">
            <div class="welcome-container">
                <h1 class="welcome-title">Welcome to E-commerce Platform</h1>
                <p class="welcome-subtitle">We offer a wide range of wonderful products</p>
                <a href="products.php" class="browse-btn">Browse All Products</a>
            </div>
        </section>
        <section class="featured-section">
            <div class="section-header">
                <h2 class="section-title">Featured Products</h2>
                <p class="section-subtitle">Discover our most popular products</p>
            </div>
            
            <div class="products-grid">
            <?php
            $limitedProducts = array_slice($featuredProducts, 0, 2);
            foreach ($limitedProducts as $product):
            ?>
                <div class="product-card">
                    <div class="product-image">O_o</div>
                    <div class="product-info">
                        <h3 class="product-name"><?php echo $product['name']; ?></h3>
                        <div class="product-price">$<?php echo number_format($product['price'], 2); ?></div>

                        <form method="post" action="add_to_cart.php" class="add-to-cart-form">
                            <input type="hidden" name="product_id" value="<?php echo $product['id']; ?>">
                            <button type="submit" class="add-to-cart-btn">Add to Cart</button>
                        </form>
                    </div>
                </div>
                <?php endforeach; ?>
            </div>
        </section>
    </div>
</body>
</html>