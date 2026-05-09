-- ============================================================
--  MindWhile ERP — Book Sales Module
--  Database: books
--  MySQL Workbench Script
--  Run this entire file to set up the database from scratch.
-- ============================================================

-- 1. Create & select database
CREATE DATABASE IF NOT EXISTS books
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE books;

-- ============================================================
-- 2. vendors
-- ============================================================
CREATE TABLE IF NOT EXISTS vendors (
    id              INT          NOT NULL AUTO_INCREMENT,
    name            VARCHAR(100) NOT NULL,
    vendor_type     VARCHAR(50)  DEFAULT NULL,   -- Wholesaler, Publisher, Distributor, Retailer
    contact         VARCHAR(20)  DEFAULT NULL,   -- Phone
    address         VARCHAR(255) DEFAULT NULL,
    payment_method  VARCHAR(50)  DEFAULT NULL,
    books_supplied  INT          DEFAULT 0,
    total_amount    DOUBLE       DEFAULT 0.0,
    status          VARCHAR(20)  DEFAULT 'Active',
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 3. books  (inventory)
-- ============================================================
CREATE TABLE IF NOT EXISTS books (
    id              INT          NOT NULL AUTO_INCREMENT,
    name            VARCHAR(150) NOT NULL,
    book_class      VARCHAR(30)  DEFAULT NULL,   -- e.g. Class 1 … Class 10
    book_type       VARCHAR(20)  DEFAULT 'Set',  -- Set / Single
    total_qty       INT          DEFAULT 0,
    sets_qty        INT          DEFAULT 0,
    singles_qty     INT          DEFAULT 0,
    cost_price      DOUBLE       DEFAULT 0.0,
    selling_price   DOUBLE       DEFAULT 0.0,
    stock_available INT          DEFAULT 0,
    vendor_id       INT          DEFAULT NULL,
    vendor_name     VARCHAR(150) DEFAULT NULL,
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    CONSTRAINT books_vendor_fk
        FOREIGN KEY (vendor_id) REFERENCES vendors (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 4. stock  (stock-in entries)
-- ============================================================
CREATE TABLE IF NOT EXISTS stock (
    id       INT      NOT NULL AUTO_INCREMENT,
    book_id  INT      DEFAULT NULL,
    quantity INT      NOT NULL,
    date     DATETIME DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    CONSTRAINT stock_book_fk
        FOREIGN KEY (book_id) REFERENCES books (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 5. sales
-- ============================================================
CREATE TABLE IF NOT EXISTS sales (
    id              INT          NOT NULL AUTO_INCREMENT,
    book_id         INT          DEFAULT NULL,
    student_name    VARCHAR(100) NOT NULL,
    `class`         VARCHAR(20)  DEFAULT NULL,
    book_name       VARCHAR(100) DEFAULT NULL,
    book_type       VARCHAR(20)  DEFAULT 'Set',
    qty             INT          DEFAULT 1,
    unit_price      DOUBLE       DEFAULT 0.0,
    total_amount    DOUBLE       NOT NULL,
    payment_method  VARCHAR(50)  DEFAULT 'Cash',
    date            DATETIME     DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    CONSTRAINT sales_book_fk
        FOREIGN KEY (book_id) REFERENCES books (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 6. returns
-- ============================================================
CREATE TABLE IF NOT EXISTS `returns` (
    id       INT      NOT NULL AUTO_INCREMENT,
    sale_id  INT      DEFAULT NULL,
    amount   DOUBLE   NOT NULL,
    date     DATETIME DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    CONSTRAINT returns_sale_fk
        FOREIGN KEY (sale_id) REFERENCES sales (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- Done!  Verify tables:
-- ============================================================
SHOW TABLES;
