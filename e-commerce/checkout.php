<?php
session_start();
require 'functions.php';

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

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    unset($_SESSION['cart']);
    header('Location: success.php');
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Checkout | E-commerce Platform</title>
    <link rel="stylesheet" href="style.css">
    <style>
        .checkout-container {
            display: flex;
            gap: 30px;
            margin-top: 30px;
        }
        
        .order-summary {
            flex: 1;
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .payment-form {
            flex: 1;
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .payment-methods {
            display: flex;
            gap: 15px;
            margin: 20px 0;
        }
        
        .payment-method {
            flex: 1;
            text-align: center;
            padding: 15px;
            border: 2px solid #eee;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .payment-method.selected {
            border-color: #3498db;
            background: rgba(52, 152, 219, 0.05);
        }
        
        .payment-method img {
            max-width: 80px;
            height: auto;
            margin-bottom: 10px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }
        
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
        }
        
        .form-row {
            display: flex;
            gap: 15px;
        }
        
        .form-row .form-group {
            flex: 1;
        }
        
        .pay-button {
            background: #27ae60;
            color: white;
            border: none;
            padding: 15px;
            width: 100%;
            border-radius: 6px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .pay-button:hover {
            background: #219653;
        }
        
        .secure-payment {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 20px;
            color: #27ae60;
            font-weight: 500;
            margin-left: auto;
            margin-right: auto;
            width: fit-content;
        }
        
        .order-items {
            max-height: 300px;
            overflow-y: auto;
            margin-bottom: 20px;
            border-bottom: 1px solid #eee;
            padding-bottom: 20px;
        }
        
        .order-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #f5f5f5;
        }
        
        .order-item:last-child {
            border-bottom: none;
        }
        
        .total-row {
            display: flex;
            justify-content: space-between;
            padding: 15px 0;
            font-size: 18px;
            font-weight: bold;
            border-top: 1px solid #eee;
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
                </ul>
            </nav>
            <div class="cart">
                <a href="cart.php">Cart (<?php echo isset($_SESSION['cart']) ? count($_SESSION['cart']) : 0; ?>)</a>
            </div>
        </div>
    </header>

    <main class="container">
        <h2>Checkout</h2>
        
        <?php if (empty($cartItems)): ?>
            <div class="alert alert-info">
                <p>Your cart is empty. Please add some products before checkout.</p>
                <a href="products.php" class="btn">Browse Products</a>
            </div>
        <?php else: ?>
            <div class="checkout-container">
                <div class="order-summary">
                    <h3>Order Summary</h3>
                    
                    <div class="order-items">
                        <?php foreach ($cartItems as $item): ?>
                        <div class="order-item">
                            <div>
                                <strong><?php echo $item['name']; ?></strong>
                                <div><?php echo $item['quantity']; ?> × ¥<?php echo number_format($item['price'], 2); ?></div>
                            </div>
                            <div>¥<?php echo number_format($item['subtotal'], 2); ?></div>
                        </div>
                        <?php endforeach; ?>
                    </div>
                    
                    <div class="total-row">
                        <span>Total:</span>
                        <span>¥<?php echo number_format($total, 2); ?></span>
                    </div>
                    <div style="text-align: center;">
                    <img src="skm.jpg" width="290" height="290">
                    </div>
                    
                    <div class="secure-payment" style="text-align: center;">
                        <span>Secure Payment</span>
                    </div>
                </div>
                
                <div class="payment-form">
                    <h3>Payment Information</h3>
                    
                    <div class="payment-methods">
                        <div class="payment-method selected">
                            <div>Credit Card</div>
                        </div>
                        <div class="payment-method">
                            <div>Alipay</div>
                        </div>
                        <div class="payment-method">
                            <div>WeChat Pay</div>
                        </div>
                    </div>
                    
                    <form method="post">
                        <div class="form-group">
                            <label for="cardNumber">Card Number</label>
                            <input type="text" id="cardNumber" placeholder="1234 5678 9012 3456" required>
                        </div>
                        
                        
                        <button type="submit" class="pay-button">Pay ¥<?php echo number_format($total, 2); ?></button>
                        
                        <div class="secure-payment">
                            <span>Your payment information is encrypted</span>
                        </div>
                    </form>
                </div>
            </div>
        <?php endif; ?>
    </main>


    
    <script>
        document.querySelectorAll('.payment-method').forEach(method => {
            method.addEventListener('click', function() {
                document.querySelectorAll('.payment-method').forEach(m => {
                    m.classList.remove('selected');
                });
                this.classList.add('selected');
            });
        });
        const cardNumberInput = document.getElementById('cardNumber');
        cardNumberInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            let formattedValue = '';
            
            for (let i = 0; i < value.length; i++) {
                if (i > 0 && i % 4 === 0) {
                    formattedValue += ' ';
                }
                formattedValue += value[i];
            }
            
            e.target.value = formattedValue;
        });
        
        const expiryDateInput = document.getElementById('expiryDate');
        expiryDateInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            let formattedValue = '';
            
            if (value.length > 2) {
                formattedValue = value.substring(0, 2) + '/' + value.substring(2, 4);
            } else {
                formattedValue = value;
            }
            
            e.target.value = formattedValue;
        });
    </script>
</body>
</html>