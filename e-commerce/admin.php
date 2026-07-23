<?php
session_start();
require 'functions.php';

if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header('Location: index.php');
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = $_POST['name'];
    $price = $_POST['price'];
    $description = $_POST['description'];
    
    if (isset($_POST['add_product'])) {
        addProduct($name, $price, $description);
    } elseif (isset($_POST['delete_product'])) {
        $productId = $_POST['product_id'];
        deleteProduct($productId);
    }
}

$products = getProducts();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin | E-commerce Platform</title>
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
                    <li><a href="admin.php">Admin</a></li>
                </ul>
            </nav>
            <div class="cart">
                <a href="cart.php">Cart (<?php echo isset($_SESSION['cart']) ? count($_SESSION['cart']) : 0; ?>)</a>
            </div>
        </div>
    </header>

    <main class="container">
        <h2>Product Management</h2>
        
        <div class="admin-section">
            <h3>Add New Product</h3>
            <form method="post">
                <div>
                    <label>Product Name:</label>
                    <input type="text" name="name" required>
                </div>
                <div>
                    <label>Price:</label>
                    <input type="number" name="price" step="0.01" required>
                </div>
                <div>
                    <label>Description:</label>
                    <textarea name="description" required></textarea>
                </div>
                <button type="submit" name="add_product" class="btn">Add Product</button>
            </form>
        </div>
        
        <div class="admin-section">
            <h3>Product List</h3>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Price</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($products as $product): ?>
                    <tr>
                        <td><?php echo $product['id']; ?></td>
                        <td><?php echo $product['name']; ?></td>
                        <td>¥<?php echo number_format($product['price'], 2); ?></td>
                        <td>
                            <form method="post">
                                <input type="hidden" name="product_id" value="<?php echo $product['id']; ?>">
                                <button type="submit" name="delete_product" class="btn">Delete</button>
                            </form>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </main>
</body>
</html>