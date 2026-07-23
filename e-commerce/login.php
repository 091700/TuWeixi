<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login in page</title>
    <link rel="stylesheet" href="style.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }

        .container {
            width: 90%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 15px;
        }

        h2 {
            font-size: 2rem;
            margin-bottom: 25px;
            color: #2c3e50;
            text-align: center;
            padding-top: 20px;
        }

        form {
            background: white;
            border-radius: 8px;
            padding: 40px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            width: 350px;
            margin: 0 auto;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }

        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
            margin-bottom: 20px;
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
            width: 100%;
            text-align: center;
        }

        .browse-btn:hover {
            background: #2980b9;
            transform: translateY(-3px);
        }

        .error-message {
            color: red;
            text-align: center;
            margin-top: 10px;
        }

        .new-account-btn {
            display: block;
            text-align: center;
            margin-top: 15px;
            color: #3498db;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <h2>Login in</h2>
    <?php
    session_start();
    require 'database.php';

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $username = $_POST['username'];
        $password = $_POST['password'];

        try {
            $stmt = $pdo->prepare("SELECT * FROM users WHERE username = :username AND password = :password");
            $stmt->bindParam(':username', $username);
            $stmt->bindParam(':password', $password);
            $stmt->execute();

            $user = $stmt->fetch(PDO::FETCH_ASSOC);

            if ($user) {
                $_SESSION['user_logged_in'] = true;
                header('Location: index.php');
                exit;
            } else {
                echo '<p class="error-message">error</p>';
            }
        } catch (PDOException $e) {
            echo '<p class="error-message">error</p>';
        }
    }
    ?>
    <form method="post">
        <label for="username">username:</label>
        <input type="text" id="username" name="username" required><br>
        <label for="password">password:</label>
        <input type="password" id="password" name="password" required><br>
        <button type="submit" class="browse-btn">Login in</button>
    </form>
    <a href="register.php" class="new-account-btn">New Account</a>
</body>
</html>