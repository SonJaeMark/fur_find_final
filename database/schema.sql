-- Disable foreign key checks during initialization
SET FOREIGN_KEY_CHECKS = 0;

-- Drop tables if they already exist
DROP TABLE IF EXISTS tbl_transactions;
DROP TABLE IF EXISTS tbl_audit_log;
DROP TABLE IF EXISTS tbl_records;
DROP TABLE IF EXISTS tbl_users;
DROP TABLE IF EXISTS tbl_categories;
DROP TABLE IF EXISTS tbl_roles;

SET FOREIGN_KEY_CHECKS = 1;

-- 1. Roles Table
CREATE TABLE tbl_roles (
    role_id TINYINT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(30) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Categories Table (e.g., Dog, Cat, Bird)
CREATE TABLE tbl_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Users Table
CREATE TABLE tbl_users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    role_id TINYINT NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    is_active TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_users_role FOREIGN KEY (role_id) 
        REFERENCES tbl_roles(role_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Pet Records / Reports Table
CREATE TABLE tbl_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    record_name VARCHAR(100) NOT NULL,
    description TEXT,
    quantity INT DEFAULT 1,
    unit_price DECIMAL(10,2) DEFAULT 0.00,
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_records_user FOREIGN KEY (user_id) 
        REFERENCES tbl_users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_records_category FOREIGN KEY (category_id) 
        REFERENCES tbl_categories(category_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Audit Log Table
CREATE TABLE tbl_audit_log (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    action VARCHAR(100) NOT NULL,
    table_affected VARCHAR(50) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) 
        REFERENCES tbl_users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Transactions Table
CREATE TABLE tbl_transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    record_id INT NOT NULL,
    user_id INT NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    quantity_changed INT NOT NULL,
    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    remarks VARCHAR(255),
    CONSTRAINT fk_trans_record FOREIGN KEY (record_id) 
        REFERENCES tbl_records(record_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_trans_user FOREIGN KEY (user_id) 
        REFERENCES tbl_users(user_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;