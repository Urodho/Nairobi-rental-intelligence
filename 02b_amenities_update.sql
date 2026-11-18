-- =====================================================================
-- GenData Project - UPDATE: Security, Schools, Hospitals & Amenities
-- Run this AFTER 02_mysql_database.sql in MySQL Workbench
-- Teacher feedback: add insecurity/security + social amenities
-- =====================================================================
USE nairobi_rentals;

-- Add coordinates to locations (for map)
ALTER TABLE locations ADD COLUMN latitude DECIMAL(9,6);
ALTER TABLE locations ADD COLUMN longitude DECIMAL(9,6);

UPDATE locations SET latitude=-1.2906, longitude=36.7820 WHERE estate_name='Kilimani';
UPDATE locations SET latitude=-1.2635, longitude=36.8080 WHERE estate_name='Westlands';
UPDATE locations SET latitude=-1.2730, longitude=36.7600 WHERE estate_name='Lavington';
UPDATE locations SET latitude=-1.1050, longitude=36.8800 WHERE estate_name='Ruaka';
UPDATE locations SET latitude=-1.1700, longitude=36.9000 WHERE estate_name='Kahawa West';
UPDATE locations SET latitude=-1.2800, longitude=36.8500 WHERE estate_name='Eastleigh';
UPDATE locations SET latitude=-1.3200, longitude=36.8400 WHERE estate_name='South B';
UPDATE locations SET latitude=-1.2715, longitude=36.7730 WHERE estate_name='Kileleshwa';
UPDATE locations SET latitude=-1.2890, longitude=36.8200 WHERE estate_name='Upperhill';
UPDATE locations SET latitude=-1.2400, longitude=36.8900 WHERE estate_name='Ruaraka';
UPDATE locations SET latitude=-1.2200, longitude=36.9000 WHERE estate_name='Kasarani';
UPDATE locations SET latitude=-1.3200, longitude=36.8900 WHERE estate_name='Embakasi';
UPDATE locations SET latitude=-1.3600, longitude=36.9800 WHERE estate_name='Syokimau';
UPDATE locations SET latitude=-1.1800, longitude=36.9500 WHERE estate_name='Thika Road';
UPDATE locations SET latitude=-1.3200, longitude=36.7600 WHERE estate_name='Ngong Road';

-- New table: estate_amenities (1 row per estate, linked to locations)
CREATE TABLE IF NOT EXISTS estate_amenities (
    location_id       INT PRIMARY KEY,
    schools_count     INT DEFAULT 0,
    hospitals_count   INT DEFAULT 0,
    security_rating   INT CHECK (security_rating BETWEEN 1 AND 10),
    transport_score   INT CHECK (transport_score BETWEEN 1 AND 10),
    water_score       INT CHECK (water_score BETWEEN 1 AND 10),
    livability_score  DECIMAL(5,1),  -- calculated below
    CONSTRAINT fk_amenities_location FOREIGN KEY (location_id)
        REFERENCES locations(location_id)
);

INSERT INTO estate_amenities (location_id, schools_count, hospitals_count, security_rating, transport_score, water_score) VALUES
(1, 8,5,8,9,8),   -- Kilimani
(2, 7,4,8,8,8),   -- Kileleshwa
(3,10,6,9,9,9),   -- Westlands
(4, 6,5,9,9,8),   -- Upperhill
(5, 9,4,9,7,9),   -- Lavington
(6, 6,3,6,8,7),   -- South B
(7, 6,3,5,8,6),   -- Eastleigh
(8, 5,2,6,6,6),   -- Ruaka
(9, 4,1,5,5,5),   -- Kahawa West
(10,5,2,6,7,6),   -- Ruaraka
(11,6,2,6,7,6),   -- Kasarani
(12,5,2,5,6,5),   -- Embakasi
(13,4,1,6,5,5),   -- Syokimau
(14,5,2,6,6,6),   -- Thika Road
(15,7,3,7,7,7);   -- Ngong Road

-- Calculate livability score: weighted sum
UPDATE estate_amenities
SET livability_score = ROUND(schools_count*0.8 + hospitals_count*1.2 + security_rating*1.5 + transport_score*1.2 + water_score*1.0, 1);

-- View: safest estates
DROP VIEW IF EXISTS v_safest_estates;
CREATE VIEW v_safest_estates AS
SELECT l.estate_name, a.schools_count, a.hospitals_count, a.security_rating,
       a.transport_score, a.water_score, a.livability_score,
       CASE WHEN a.security_rating>=8 THEN 'Low insecurity'
            WHEN a.security_rating>=6 THEN 'Medium insecurity'
            ELSE 'High insecurity' END AS insecurity_level
FROM locations l JOIN estate_amenities a ON l.location_id=a.location_id
ORDER BY a.livability_score DESC;

-- Q10: Safest & most livable estates
SELECT * FROM v_safest_estates;

-- Q11: Rent vs Livability (best value = low rent + high livability)
SELECT l.estate_name,
       ROUND(AVG(p.price_kes),0) AS avg_rent,
       a.security_rating, a.schools_count, a.hospitals_count, a.livability_score
FROM properties p
JOIN locations l ON p.location_id=l.location_id
JOIN estate_amenities a ON l.location_id=a.location_id
GROUP BY l.estate_name, a.security_rating, a.schools_count, a.hospitals_count, a.livability_score
ORDER BY a.livability_score DESC;

-- Q12: Affordable AND safe (2-bed under 50k, security >= 6)
SELECT p.title, l.estate_name, p.price_kes, a.security_rating, a.livability_score
FROM properties p
JOIN locations l ON p.location_id=l.location_id
JOIN estate_amenities a ON l.location_id=a.location_id
WHERE p.bedrooms=2 AND p.price_kes<50000 AND a.security_rating>=6
ORDER BY p.price_kes ASC;
