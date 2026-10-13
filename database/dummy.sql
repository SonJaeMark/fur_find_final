INSERT INTO tbl_roles (role_id, role_name) VALUES (1, 'Pet Owner'), (2, 'Admin'), (3, 'Super Admin');

INSERT INTO tbl_users (user_id, role_id, full_name, email, contact_no, status, password_hash, salt) VALUES
(1, 3, 'System Super Admin', 'superadmin@furfind.com', '09170000001', 'Active', '053577392f3abde43d21621f7cb3b2a355fbd93c72807885aa0e911fc9509029', 'a1b2c3d4e5f60718293a4b5c6d7e8f90'),
(2, 2, 'FurFind Admin', 'admin@furfind.com', '09170000002', 'Active', '053577392f3abde43d21621f7cb3b2a355fbd93c72807885aa0e911fc9509029', 'a1b2c3d4e5f60718293a4b5c6d7e8f90'),
(3, 1, 'John Doe', 'john@furfind.com', '09170000003', 'Active', '053577392f3abde43d21621f7cb3b2a355fbd93c72807885aa0e911fc9509029', 'a1b2c3d4e5f60718293a4b5c6d7e8f90'),
(4, 1, 'Jane Finder', 'jane@furfind.com', '09170000004', 'Active', '053577392f3abde43d21621f7cb3b2a355fbd93c72807885aa0e911fc9509029', 'a1b2c3d4e5f60718293a4b5c6d7e8f90');

INSERT INTO tbl_reports (report_id, user_id, report_type, pet_name, species, breed, gender, primary_color, secondary_color, distinguishing_marks, incident_date, location, photo_path, status) VALUES
(1, 3, 'Lost', 'Buddy', 'Dog', 'Golden Retriever', 'Male', 'Golden', 'White', 'Red collar', '2026-10-08 09:00:00', 'Quezon City', 'uploads/sample.jpg', 'Active'),
(2, 4, 'Found', 'Unknown', 'Dog', 'Golden Retriever', 'Male', 'Golden', '', 'Wearing a red collar', '2026-10-09 17:30:00', 'Quezon City', 'uploads/sample.jpg', 'Active');

INSERT INTO tbl_matches (match_id, lost_report_id, found_report_id, match_score, status) VALUES
(1, 1, 2, 92.00, 'Pending Admin Verification');

INSERT INTO tbl_audit_log (user_id, action, table_affected, details) VALUES
(1, 'SYSTEM_INIT', 'tbl_roles', 'Database seeded.');