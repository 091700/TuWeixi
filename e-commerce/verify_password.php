<?php
session_start();
require 'database.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $inputPassword = $_POST['password'];

    try {
        $stmt = $pdo->query("SELECT password FROM password");
        $passwords = $stmt->fetchAll(PDO::FETCH_ASSOC);
        $isValid = false;

        foreach ($passwords as $row) {
            if ($row['password'] === $inputPassword) {
                $isValid = true;
                break;
            }
        }

        if ($isValid) {
            $_SESSION['admin_logged_in'] = true;
            echo 'success';
        } else {
            echo 'error';
        }
    } catch (PDOException $e) {
        error_log("database error: " . $e->getMessage());
        echo 'error';
    }
}
?>