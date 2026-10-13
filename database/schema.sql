SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS tbl_transactions;
DROP TABLE IF EXISTS tbl_records;
DROP TABLE IF EXISTS tbl_categories;
DROP TABLE IF EXISTS tbl_claims;
DROP TABLE IF EXISTS tbl_matches;
DROP TABLE IF EXISTS tbl_audit_log;
DROP TABLE IF EXISTS tbl_reports;
DROP TABLE IF EXISTS tbl_users;
DROP TABLE IF EXISTS tbl_roles;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE tbl_roles (
    role_id TINYINT PRIMARY KEY,
    role_name VARCHAR(30) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE tbl_users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    role_id TINYINT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    contact_no VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(64) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_users_role FOREIGN KEY (role_id) REFERENCES tbl_roles(role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE tbl_reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    report_type VARCHAR(10) NOT NULL,
    pet_name VARCHAR(80),
    species VARCHAR(50) NOT NULL,
    breed VARCHAR(80),
    gender VARCHAR(20),
    primary_color VARCHAR(40),
    secondary_color VARCHAR(40),
    distinguishing_marks TEXT,
    incident_date DATETIME NOT NULL,
    location VARCHAR(255) NOT NULL,
    photo_path VARCHAR(255),
    status VARCHAR(30) NOT NULL DEFAULT 'Active',
    is_deleted TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reports_user FOREIGN KEY (user_id) REFERENCES tbl_users(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE tbl_matches (
    match_id INT AUTO_INCREMENT PRIMARY KEY,
    lost_report_id INT NOT NULL,
    found_report_id INT NOT NULL,
    match_score DECIMAL(5,2) NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'Pending Admin Verification',
    admin_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_match_lost FOREIGN KEY (lost_report_id) REFERENCES tbl_reports(report_id),
    CONSTRAINT fk_match_found FOREIGN KEY (found_report_id) REFERENCES tbl_reports(report_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE tbl_claims (
    claim_id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL,
    user_id INT NOT NULL,
    claim_type VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Submitted',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_claim_match FOREIGN KEY (match_id) REFERENCES tbl_matches(match_id),
    CONSTRAINT fk_claim_user FOREIGN KEY (user_id) REFERENCES tbl_users(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE tbl_audit_log (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    action VARCHAR(100) NOT NULL,
    table_affected VARCHAR(50) NOT NULL DEFAULT 'system',
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES tbl_users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;