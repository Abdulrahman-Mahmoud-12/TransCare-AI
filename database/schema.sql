-- ===========================================================
-- RetailIQ Database Schema
-- Author: Abdelrahman Mahmoud
-- Database: retailiq
-- ===========================================================

DROP DATABASE IF EXISTS retailiq;
CREATE DATABASE retailiq;
USE retailiq;

-- ===========================================================
-- USERS
-- ===========================================================

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('customer', 'admin') NOT NULL DEFAULT 'customer',
    admin_id VARCHAR(50) UNIQUE DEFAULT NULL,

    -- Populated with your Python enum matching options, made nullable for admins
    customer_category ENUM('New', 'Regular', 'VIP', 'Churn Risk') DEFAULT NULL,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL DEFAULT NULL
);

-- ===========================================================
-- CATEGORIES
-- ===========================================================

CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    image_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===========================================================
-- PRODUCTS
-- ===========================================================

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    barcode VARCHAR(50) UNIQUE,
    name VARCHAR(150) NOT NULL,
    brand VARCHAR(100),
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2),
    stock_quantity INT NOT NULL DEFAULT 0,
    minimum_stock INT DEFAULT 10,
    shelf_location VARCHAR(50),
    image_url VARCHAR(255),

    status ENUM(
        'active',
        'out_of_stock',
        'hidden'
    ) DEFAULT 'active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE CASCADE
);

-- ===========================================================
-- OFFERS
-- ===========================================================

CREATE TABLE offers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    discount_percentage DECIMAL(5,2),
    description TEXT,
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE
);

-- ===========================================================
-- ORDERS
-- ===========================================================

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    total_discount DECIMAL(12,2) DEFAULT 0,
    payment_method ENUM(
        'cash',
        'credit_card',
        'wallet'
    ) NOT NULL,

    status ENUM(
        'pending',
        'completed',
        'cancelled',
        'refunded'
    ) DEFAULT 'pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (customer_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- ===========================================================
-- ORDER ITEMS
-- ===========================================================

CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount DECIMAL(10,2) DEFAULT 0,
    subtotal DECIMAL(12,2) NOT NULL,

    FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE CASCADE,

    FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE
);

-- ===========================================================
-- INVENTORY HISTORY
-- ===========================================================

CREATE TABLE inventory_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    change_type ENUM(
        'restock',
        'sale',
        'return',
        'damage',
        'manual_update'
    ) NOT NULL,

    quantity INT NOT NULL,
    previous_stock INT,
    new_stock INT,
    changed_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE,

    FOREIGN KEY (changed_by)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- ===========================================================
-- SHELF DETECTIONS
-- ===========================================================

CREATE TABLE shelf_detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uploaded_by INT,
    image_path VARCHAR(255) NOT NULL,
    processed_image_path VARCHAR(255),
    total_products INT DEFAULT 0,
    empty_spaces INT DEFAULT 0,
    occupancy_percentage DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (uploaded_by)
        REFERENCES users(id)
        ON DELETE SET NULL
);

-- ===========================================================
-- CUSTOMER ANALYTICS
-- ===========================================================

CREATE TABLE customer_analytics (
    customer_id INT PRIMARY KEY,
    total_orders INT DEFAULT 0,
    total_spent DECIMAL(12,2) DEFAULT 0,
    favorite_category INT,
    favorite_product INT,
    segment VARCHAR(50),
    return_probability DECIMAL(5,2),
    last_purchase TIMESTAMP NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (customer_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (favorite_category)
        REFERENCES categories(id),

    FOREIGN KEY (favorite_product)
        REFERENCES products(id)
);

-- ===========================================================
-- REPORTS
-- ===========================================================

CREATE TABLE reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    generated_by INT,
    report_type ENUM(
        'daily',
        'weekly',
        'monthly',
        'custom'
    ),
    file_path VARCHAR(255),
    summary TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (generated_by)
        REFERENCES users(id)
);

-- ===========================================================
-- INDEXES
-- ===========================================================

CREATE INDEX idx_products_name
ON products(name);

CREATE INDEX idx_products_category
ON products(category_id);

CREATE INDEX idx_orders_customer
ON orders(customer_id);

CREATE INDEX idx_orders_date
ON orders(created_at);

CREATE INDEX idx_offers_product
ON offers(product_id);

CREATE INDEX idx_inventory_product
ON inventory_history(product_id);

CREATE INDEX idx_shelf_date
ON shelf_detections(created_at);

CREATE INDEX idx_reports_date
ON reports(generated_at);