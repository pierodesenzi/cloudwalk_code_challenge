-- creating tables "country" and "gdp"

CREATE TABLE IF NOT EXISTS country (
   id VARCHAR(2) UNIQUE NOT NULL,
   name VARCHAR(20) NOT NULL,
   iso3_code VARCHAR(3) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS gdp (
   country_id VARCHAR(2) NOT NULL,
   year SMALLINT NOT NULL,
   value FLOAT,
   FOREIGN KEY (country_id) REFERENCES country (id),
   UNIQUE (country_id, year)
);

-- hardcoding the values of "country", since they are immutable
INSERT INTO country (id, name, iso3_code) VALUES
('AR', 'Argentina', 'ARG'),
('BO', 'Bolivia', 'BOL'),
('BR', 'Brazil', 'BRA'),
('CL', 'Chile', 'CHL'),
('CO', 'Colombia', 'COL'),
('EC', 'Ecuador', 'ECU'),
('GY', 'Guyana', 'GUY'),
('PE', 'Peru', 'PER'),
('PY', 'Paraguai', 'PRY'),
('SR', 'Suriname', 'SUR'),
('UY', 'Uruguay', 'URY'),
('VE', 'Venezuela', 'VEN');
