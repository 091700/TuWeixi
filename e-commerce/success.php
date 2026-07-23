<?php
session_start();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payment Successful | E-commerce Platform</title>
    <link rel="stylesheet" href="style.css">
    <style>
        .success-container {
            text-align: center;
            max-width: 600px;
            margin: 50px auto;
            padding: 40px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .success-icon {
            width: 80px;
            height: 80px;
            background: #27ae60;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
        }
        
        .success-icon svg {
            width: 40px;
            height: 40px;
            stroke: white;
        }
        
        .success-title {
            font-size: 28px;
            color: #27ae60;
            margin-bottom: 20px;
        }
        
        .order-details {
            background: #f9f9f9;
            border-radius: 8px;
            padding: 20px;
            margin: 30px 0;
            text-align: left;
        }
        
        .order-details h4 {
            margin-bottom: 15px;
            color: #2c3e50;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        
        .detail-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        
        .actions {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 30px;
        }
        
        .btn-primary {
            background:#27ae60;
            color: white;
            padding: 12px 25px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            transition: background 0.3s;
        }
        
        .btn-primary:hover {
            background: #2980b9;
        }
    </style>
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
                    <li><a href="admin.php">Admin</a></li>
                </ul>
            </nav>
            <div class="cart">
                <a href="cart.php">Cart (<?php echo isset($_SESSION['cart']) ? count($_SESSION['cart']) : 0; ?>)</a>
            </div>
        </div>
    </header>

    <main class="container">
        <div class="success-container">
            <h2 class="success-title">Payment Successful!</h2>
            <p>Thank you for your purchase. Your order has been successfully paid.</p>
            
            <div class="order-details">
                <h4>Order Information</h4>
                <div class="detail-row">
                    <span>Order Number:</span>
                    <span>#<?php echo rand(100000, 999999); ?></span>
                </div>
                <div class="detail-row">
                    <span>Payment Time:</span>
                    <span><?php echo date('Y-m-d H:i:s'); ?></span>
                </div>
                <div class="detail-row">
                    <span>Payment Amount:</span>
                    <span>¥<?php
                        $total = 0;
                        if (isset($_SESSION['last_order_total'])) {
                            $total = $_SESSION['last_order_total'];
                        }
                        echo number_format($total, 2);
                    ?></span>
                </div>
                <div class="detail-row">
                    <span>Payment Method:</span>
                    <span>Credit Card</span>
                </div>
            </div>
            <div class="actions">
                <a href="index.php" class="btn-primary">Back to Home</a>
                <a href="products.php" class="btn-primary">Continue Shopping</a>
            </div>
        </div>
    </main>

</body>
</html>