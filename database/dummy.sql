-- Seed Roles
INSERT INTO tbl_roles (role_id, role_name) VALUES
(1, 'Super Admin'),
(2, 'Admin'),
(3, 'Pet Owner');

-- Seed Categories
INSERT INTO tbl_categories (category_id, category_name) VALUES
(1, 'Dog'),
(2, 'Cat'),
(3, 'Bird'),
(4, 'Other');

-- Seed Users (Default password: password123)
INSERT INTO tbl_users (user_id, role_id, username, password_hash, full_name, is_active) VALUES
(1, 1, 'superadmin', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'System Super Admin', 1),
(2, 2, 'admin1', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'FurFind Admin', 1),
(3, 3, 'john_doe', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'John Doe', 1);

-- Seed Sample Pet Records
INSERT INTO tbl_records (record_id, user_id, category_id, record_name, description, quantity, unit_price, status) VALUES
(1, 3, 1, 'Golden Retriever (Lost)', 'Golden coat, wearing a red collar, missing near Central Park', 1, 0.00, 'Lost'),
(2, 3, 2, 'Siamese Cat (Found)', 'Found near Main St., blue eyes, very friendly', 1, 0.00, 'Found');

-- Seed Initial Audit Logs
INSERT INTO tbl_audit_log (user_id, action, table_affected) VALUES
(1, 'SYSTEM_INIT', 'tbl_roles'),
(1, 'SEED_DATA_INSERTED', 'tbl_users');

-- Seed Initial Transactions
INSERT INTO tbl_transactions (record_id, user_id, transaction_type, quantity_changed, remarks) VALUES
(1, 3, 'REPORT_CREATED', 1, 'Initial lost report filed'),
(2, 3, 'REPORT_CREATED', 1, 'Initial found report filed');