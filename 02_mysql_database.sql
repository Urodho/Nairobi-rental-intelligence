-- =====================================================================
-- GenData Project - Nairobi Rental Market Intelligence System
-- FILE 2: Complete MySQL Database (Run this FIRST in MySQL Workbench)
-- =====================================================================
-- HOW TO RUN:
--   1. Open MySQL Workbench
--   2. Click the "SQL" tab / open a query tab
--   3. Open this file (File > Open SQL Script) OR copy-paste all of it
--   4. Click the lightning bolt icon (Execute) at the top
--   5. You should see "Query OK" messages - no red errors
--
-- This file creates: Database, 3 tables, indexes, sample data,
-- a VIEW, a STORED PROCEDURE, a TRIGGER, and 8 analysis queries.
-- =====================================================================

-- ---------------------------------------------------------------------
-- STEP 1: Create and use the database
-- ---------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS nairobi_rentals;
USE nairobi_rentals;

-- ---------------------------------------------------------------------
-- STEP 2: Create tables (Week 2: Schema Design + Normalization)
-- ---------------------------------------------------------------------
-- Table 1: locations - one row per estate (avoids repeating estate names)
CREATE TABLE IF NOT EXISTS locations (
    location_id   INT AUTO_INCREMENT PRIMARY KEY,
    estate_name   VARCHAR(100) NOT NULL UNIQUE,
    county        VARCHAR(50) DEFAULT 'Nairobi',
    latitude      DECIMAL(9,6),
    longitude     DECIMAL(9,6)
);

-- Table 2: agents - one row per agency/landlord
CREATE TABLE IF NOT EXISTS agents (
    agent_id      INT AUTO_INCREMENT PRIMARY KEY,
    agent_name    VARCHAR(100) NOT NULL UNIQUE,
    phone         VARCHAR(20)
);

-- Table 3: properties - the fact table (one row per listing)
CREATE TABLE IF NOT EXISTS properties (
    property_id   INT AUTO_INCREMENT PRIMARY KEY,
    title         VARCHAR(200) NOT NULL,
    location_id   INT NOT NULL,
    agent_id      INT,
    property_type VARCHAR(50) DEFAULT 'Apartment',
    bedrooms      INT NOT NULL,
    bathrooms     INT DEFAULT 1,
    size_sqm      INT,
    price_kes     INT NOT NULL,
    price_per_sqm DECIMAL(10,2),          -- filled by TRIGGER below
    listing_url   VARCHAR(300),
    scraped_date  DATE DEFAULT (CURRENT_DATE),
    CONSTRAINT fk_location FOREIGN KEY (location_id)
        REFERENCES locations(location_id),
    CONSTRAINT fk_agent FOREIGN KEY (agent_id)
        REFERENCES agents(agent_id),
    CONSTRAINT chk_price CHECK (price_kes > 0),
    CONSTRAINT chk_bedrooms CHECK (bedrooms BETWEEN 0 AND 10)
);

-- Indexes for performance (Week 2: Performance Optimization)
CREATE INDEX idx_price ON properties(price_kes);
CREATE INDEX idx_location ON properties(location_id);
CREATE INDEX idx_bedrooms ON properties(bedrooms);

-- ---------------------------------------------------------------------
-- STEP 3: Trigger - auto-calculate price_per_sqm on INSERT
-- ---------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_price_per_sqm;
DELIMITER $$
CREATE TRIGGER trg_price_per_sqm
BEFORE INSERT ON properties
FOR EACH ROW
BEGIN
    IF NEW.size_sqm IS NOT NULL AND NEW.size_sqm > 0 THEN
        SET NEW.price_per_sqm = NEW.price_kes / NEW.size_sqm;
    END IF;
END$$
DELIMITER ;

-- ---------------------------------------------------------------------
-- STEP 4: Sample data (so you can present even if scraper fails)
-- ---------------------------------------------------------------------
INSERT INTO locations (estate_name, county) VALUES
('Kilimani','Nairobi'),('Kileleshwa','Nairobi'),('Westlands','Nairobi'),
('Upperhill','Nairobi'),('Lavington','Nairobi'),('South B','Nairobi'),
('Eastleigh','Nairobi'),('Ruaka','Kiambu'),('Kahawa West','Nairobi'),
('Ruaraka','Nairobi'),('Kasarani','Nairobi'),('Embakasi','Nairobi'),
('Syokimau','Machakos'),('Thika Road','Kiambu'),('Ngong Road','Nairobi');

INSERT INTO agents (agent_name, phone) VALUES
('Pamela Properties','0722000001'),('HassConsult','0722000002'),
('Knight Frank KE','0722000003'),('Private Landlord','0722000004'),
('Rentals.co.ke','0722000005');

-- 40 realistic listings (location_id matches order above: 1=Kilimani ... 15=Ngong Road)
INSERT INTO properties (title, location_id, agent_id, property_type, bedrooms, bathrooms, size_sqm, price_kes, listing_url, scraped_date) VALUES
('2 Bed Apartment in Kilimani',1,1,'Apartment',2,2,95,85000,'https://property24.co.ke/1','2026-10-20'),
('3 Bed Apartment in Kilimani',1,2,'Apartment',3,3,130,120000,'https://property24.co.ke/2','2026-10-22'),
('1 Bed Flat in Kilimani',1,4,'Flat',1,1,55,45000,'https://property24.co.ke/3','2026-11-01'),
('2 Bed Apartment in Kileleshwa',2,3,'Apartment',2,2,100,95000,'https://property24.co.ke/4','2026-10-25'),
('3 Bed Townhouse in Kileleshwa',2,1,'Townhouse',3,3,150,150000,'https://property24.co.ke/5','2026-11-02'),
('2 Bed Apartment in Westlands',3,2,'Apartment',2,2,90,90000,'https://property24.co.ke/6','2026-10-18'),
('1 Bed Apartment in Westlands',3,5,'Apartment',1,1,50,55000,'https://property24.co.ke/7','2026-11-05'),
('2 Bed Apartment in Upperhill',4,3,'Apartment',2,2,85,75000,'https://property24.co.ke/8','2026-10-28'),
('3 Bed Apartment in Lavington',5,1,'Apartment',3,3,140,160000,'https://property24.co.ke/9','2026-11-03'),
('2 Bed Apartment in South B',6,4,'Apartment',2,2,80,48000,'https://property24.co.ke/10','2026-10-15'),
('1 Bed Flat in South B',6,5,'Flat',1,1,45,32000,'https://property24.co.ke/11','2026-11-08'),
('2 Bed Apartment in Eastleigh',7,4,'Apartment',2,2,75,38000,'https://property24.co.ke/12','2026-10-30'),
('1 Bed Flat in Eastleigh',7,4,'Flat',1,1,40,25000,'https://property24.co.ke/13','2026-11-10'),
('2 Bed Apartment in Ruaka',8,1,'Apartment',2,2,85,38000,'https://property24.co.ke/14','2026-10-12'),
('3 Bed Townhouse in Ruaka',8,2,'Townhouse',3,3,120,55000,'https://property24.co.ke/15','2026-11-01'),
('1 Bed Flat in Ruaka',8,5,'Flat',1,1,50,22000,'https://property24.co.ke/16','2026-11-12'),
('2 Bed Apartment in Kahawa West',9,4,'Apartment',2,2,80,35000,'https://property24.co.ke/17','2026-10-20'),
('1 Bed Flat in Kahawa West',9,4,'Flat',1,1,45,20000,'https://property24.co.ke/18','2026-11-06'),
('2 Bed Apartment in Ruaraka',10,1,'Apartment',2,2,85,42000,'https://property24.co.ke/19','2026-10-24'),
('3 Bed Apartment in Kasarani',11,2,'Apartment',3,3,110,58000,'https://property24.co.ke/20','2026-11-02'),
('2 Bed Apartment in Embakasi',12,3,'Apartment',2,2,80,36000,'https://property24.co.ke/21','2026-10-27'),
('2 Bed Apartment in Syokimau',13,5,'Apartment',2,2,90,34000,'https://property24.co.ke/22','2026-11-04'),
('3 Bed Bungalow in Syokimau',13,1,'Bungalow',3,3,140,65000,'https://property24.co.ke/23','2026-10-19'),
('2 Bed Apartment in Thika Road',14,2,'Apartment',2,2,85,40000,'https://property24.co.ke/24','2026-11-07'),
('2 Bed Apartment in Ngong Road',15,3,'Apartment',2,2,90,52000,'https://property24.co.ke/25','2026-10-31'),
('1 Bed Studio in Kilimani',1,5,'Studio',1,1,35,38000,'https://property24.co.ke/26','2026-11-09'),
('4 Bed Townhouse in Lavington',5,2,'Townhouse',4,4,200,220000,'https://property24.co.ke/27','2026-10-16'),
('2 Bed Apartment in Westlands',3,1,'Apartment',2,2,95,88000,'https://property24.co.ke/28','2026-11-11'),
('3 Bed Apartment in Upperhill',4,5,'Apartment',3,3,125,110000,'https://property24.co.ke/29','2026-11-13'),
('2 Bed Apartment in Ruaka',8,4,'Apartment',2,2,82,36500,'https://property24.co.ke/30','2026-11-14'),
('1 Bed Flat in Kasarani',11,4,'Flat',1,1,48,24000,'https://property24.co.ke/31','2026-11-15'),
('2 Bed Apartment in Kahawa West',9,2,'Apartment',2,2,78,33000,'https://property24.co.ke/32','2026-11-15'),
('3 Bed Apartment in Kilimani',1,3,'Apartment',3,2,120,115000,'https://property24.co.ke/33','2026-11-14'),
('2 Bed Apartment in South B',6,1,'Apartment',2,2,82,50000,'https://property24.co.ke/34','2026-11-13'),
('2 Bed Apartment in Eastleigh',7,5,'Apartment',2,2,72,36000,'https://property24.co.ke/35','2026-11-12'),
('3 Bed Townhouse in Ruaka',8,3,'Townhouse',3,3,115,52000,'https://property24.co.ke/36','2026-11-10'),
('1 Bed Flat in Embakasi',12,4,'Flat',1,1,42,21000,'https://property24.co.ke/37','2026-11-08'),
('2 Bed Apartment in Thika Road',14,1,'Apartment',2,2,88,43000,'https://property24.co.ke/38','2026-11-06'),
('2 Bed Apartment in Ngong Road',15,2,'Apartment',2,2,92,55000,'https://property24.co.ke/39','2026-11-03'),
('3 Bed Apartment in Kileleshwa',2,5,'Apartment',3,3,135,140000,'https://property24.co.ke/40','2026-11-01');

-- ---------------------------------------------------------------------
-- STEP 5: View (Week 2: Database Objects)
-- ---------------------------------------------------------------------
DROP VIEW IF EXISTS v_cheap_2bed;
CREATE VIEW v_cheap_2bed AS
SELECT p.title, l.estate_name, p.price_kes, p.bedrooms, p.size_sqm
FROM properties p
JOIN locations l ON p.location_id = l.location_id
WHERE p.bedrooms = 2 AND p.price_kes < 50000
ORDER BY p.price_kes ASC;

-- ---------------------------------------------------------------------
-- STEP 6: Stored Procedure (Week 2: Database Objects)
-- ---------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_avg_rent_by_bedrooms;
DELIMITER $$
CREATE PROCEDURE sp_avg_rent_by_bedrooms(IN p_bedrooms INT)
BEGIN
    SELECT l.estate_name,
           COUNT(*) AS listings,
           ROUND(AVG(p.price_kes),0) AS avg_rent,
           MIN(p.price_kes) AS min_rent,
           MAX(p.price_kes) AS max_rent
    FROM properties p
    JOIN locations l ON p.location_id = l.location_id
    WHERE p.bedrooms = p_bedrooms
    GROUP BY l.estate_name
    ORDER BY avg_rent ASC;
END$$
DELIMITER ;

-- =====================================================================
-- ANALYSIS QUERIES - Run these one by one for your presentation
-- =====================================================================

-- Q1: Fundamentals - Find 2-bed under 50k, cheapest first
SELECT p.title, l.estate_name, p.price_kes, p.bedrooms
FROM properties p
JOIN locations l ON p.location_id = l.location_id
WHERE p.bedrooms = 2 AND p.price_kes < 50000
ORDER BY p.price_kes ASC;

-- Q2: Aggregation + GROUP BY + CASE (Affordable / Mid-range / Premium)
SELECT l.estate_name,
       COUNT(*) AS listings,
       ROUND(AVG(p.price_kes),0) AS avg_rent,
       CASE WHEN AVG(p.price_kes) < 40000 THEN 'Affordable'
            WHEN AVG(p.price_kes) < 70000 THEN 'Mid-range'
            ELSE 'Premium' END AS category
FROM properties p
JOIN locations l ON p.location_id = l.location_id
GROUP BY l.estate_name
ORDER BY avg_rent ASC;

-- Q3: JOIN + Subquery - Estates cheaper than overall average
SELECT l.estate_name, ROUND(AVG(p.price_kes),0) AS avg_rent
FROM properties p
JOIN locations l ON p.location_id = l.location_id
WHERE p.price_kes < (SELECT AVG(price_kes) FROM properties)
GROUP BY l.estate_name
ORDER BY avg_rent ASC;

-- Q4: CTE + Window Function - Top 3 cheapest 2-beds per estate
WITH ranked AS (
    SELECT p.*, l.estate_name,
           ROW_NUMBER() OVER (PARTITION BY p.location_id ORDER BY p.price_kes ASC) AS rn
    FROM properties p
    JOIN locations l ON p.location_id = l.location_id
    WHERE p.bedrooms = 2
)
SELECT estate_name, title, price_kes, rn FROM ranked WHERE rn <= 3
ORDER BY estate_name, rn;

-- Q5: Window Function - Price per sqm ranking (best value per m2)
SELECT l.estate_name, p.title, p.price_kes, p.size_sqm,
       ROUND(p.price_per_sqm,0) AS price_per_sqm,
       RANK() OVER (ORDER BY p.price_per_sqm ASC) AS value_rank
FROM properties p
JOIN locations l ON p.location_id = l.location_id
ORDER BY p.price_per_sqm ASC
LIMIT 15;

-- Q6: Use the View
SELECT * FROM v_cheap_2bed;

-- Q7: Use the Stored Procedure (change the number to 1, 2, or 3)
CALL sp_avg_rent_by_bedrooms(2);

-- Q8: CRUD demo - Update a price, then check it
-- UPDATE properties SET price_kes = 40000 WHERE property_id = 1;
-- SELECT * FROM properties WHERE property_id = 1;

-- Q9: Summary stats for your slides
SELECT COUNT(*) AS total_listings,
       ROUND(AVG(price_kes),0) AS avg_rent,
       MIN(price_kes) AS cheapest,
       MAX(price_kes) AS most_expensive
FROM properties;
