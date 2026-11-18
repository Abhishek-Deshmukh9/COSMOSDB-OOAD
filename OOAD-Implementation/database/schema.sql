CREATE DATABASE IF NOT EXISTS CosmosDB;
USE CosmosDB;

CREATE TABLE IF NOT EXISTS Constellation (
    constellation_id INT AUTO_INCREMENT PRIMARY KEY,
    constellation_name VARCHAR(255) NOT NULL,
    min_ra DOUBLE NOT NULL CHECK (min_ra BETWEEN 0 AND 360),
    max_ra DOUBLE NOT NULL CHECK (max_ra BETWEEN 0 AND 360),
    min_dec DOUBLE NOT NULL CHECK (min_dec BETWEEN -90 AND 90),
    max_dec DOUBLE NOT NULL CHECK (max_dec BETWEEN -90 AND 90),
    description TEXT NOT NULL,
    pop_rank INT NOT NULL CHECK (pop_rank BETWEEN 1 AND 88),
    INDEX idx_constellation_name (constellation_name)
);

CREATE TABLE IF NOT EXISTS StarSystem (
    system_id INT AUTO_INCREMENT PRIMARY KEY,
    system_name VARCHAR(255) UNIQUE NOT NULL,
    ra DOUBLE CHECK (ra BETWEEN 0 AND 360 OR ra IS NULL),
    `dec` DOUBLE CHECK (`dec` BETWEEN -90 AND 90 OR `dec` IS NULL),
    num_stars INT NOT NULL DEFAULT 1 CHECK (num_stars > 0),
    num_planets INT NOT NULL DEFAULT 0 CHECK (num_planets >= 0),
    num_moons INT NOT NULL DEFAULT 0 CHECK (num_moons >= 0),
    distance_ly DOUBLE CHECK (distance_ly > 0 OR distance_ly IS NULL),
    constellation_id INT,
    CONSTRAINT fk_constellation FOREIGN KEY (constellation_id)
        REFERENCES Constellation(constellation_id) ON DELETE SET NULL,
    INDEX idx_system_name (system_name),
    INDEX idx_system_constellation (constellation_id)
);

CREATE TABLE IF NOT EXISTS Discovery (
    discovery_id INT AUTO_INCREMENT PRIMARY KEY,
    discovery_year INT CHECK (discovery_year BETWEEN 1992 AND 2026 OR discovery_year IS NULL),
    discovery_method VARCHAR(255),
    discovery_locale VARCHAR(255),
    discovery_facility VARCHAR(255),
    discovery_telescope VARCHAR(255),
    discovery_instrument VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS Star (
    star_id INT AUTO_INCREMENT PRIMARY KEY,
    star_name VARCHAR(255) NOT NULL UNIQUE,
    system_id INT NOT NULL,
    spectral_type VARCHAR(20),
    star_temp DOUBLE CHECK (star_temp BETWEEN 415 AND 57000 OR star_temp IS NULL),
    star_radius DOUBLE CHECK (star_radius BETWEEN 0.0115 AND 88.475 OR star_radius IS NULL),
    star_mass DOUBLE CHECK (star_mass BETWEEN 0.0094 AND 10.94 OR star_mass IS NULL),
    star_metallicity DOUBLE CHECK (star_metallicity BETWEEN -1 AND 0.79 OR star_metallicity IS NULL),
    star_luminosity DOUBLE CHECK (star_luminosity BETWEEN -6.09 AND 3.8 OR star_luminosity IS NULL),
    star_gravity DOUBLE CHECK (star_gravity BETWEEN 0.541 AND 8.07 OR star_gravity IS NULL),
    star_age DOUBLE CHECK (star_age BETWEEN 0 AND 16.1 OR star_age IS NULL),
    star_brightness DOUBLE CHECK (star_brightness BETWEEN 2.36431 AND 20.1861 OR star_brightness IS NULL),
    CONSTRAINT fk_star_system FOREIGN KEY (system_id)
        REFERENCES StarSystem(system_id) ON DELETE CASCADE,
    INDEX idx_star_system (system_id)
);

CREATE TABLE IF NOT EXISTS Planet (
    planet_id INT AUTO_INCREMENT PRIMARY KEY,
    planet_name VARCHAR(255) NOT NULL UNIQUE,
    system_id INT NOT NULL,
    discovery_id INT,
    is_circumbinary BOOLEAN NOT NULL DEFAULT FALSE,
    orbital_period DOUBLE CHECK (orbital_period BETWEEN 0.090706293 AND 402000000 OR orbital_period IS NULL),
    orbit_radius DOUBLE CHECK (orbit_radius BETWEEN 0.0044 AND 19000 OR orbit_radius IS NULL),
    radius_earth DOUBLE CHECK (radius_earth BETWEEN 0.3098 AND 87.20586985 OR radius_earth IS NULL),
    mass_earth DOUBLE CHECK (mass_earth BETWEEN 0.02 AND 9534.85221 OR mass_earth IS NULL),
    planet_density DOUBLE CHECK (planet_density BETWEEN 0.0051 AND 2000 OR planet_density IS NULL),
    eccentricity DOUBLE CHECK (eccentricity BETWEEN 0 AND 0.95 OR eccentricity IS NULL),
    insolation_flux DOUBLE CHECK (insolation_flux BETWEEN 0.0003 AND 44900 OR insolation_flux IS NULL),
    planet_temp DOUBLE CHECK (planet_temp BETWEEN 34 AND 4050 OR planet_temp IS NULL),
    ttv_obs BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_planet_system FOREIGN KEY (system_id)
        REFERENCES StarSystem(system_id) ON DELETE CASCADE,
    CONSTRAINT fk_planet_discovery FOREIGN KEY (discovery_id)
        REFERENCES Discovery(discovery_id) ON DELETE SET NULL,
    INDEX idx_planet_system (system_id),
    INDEX idx_planet_discovery (discovery_id)
);
