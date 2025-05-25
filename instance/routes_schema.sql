-- ────────────────────────────
-- 1) SCHEMA
-- ────────────────────────────

CREATE TABLE routes (
  route_id       VARCHAR(10)  PRIMARY KEY,
  transport_type VARCHAR(10)  NOT NULL,   -- 'bus', 'metro', or 'train'
  start_station  VARCHAR(50)  NOT NULL,
  end_station    VARCHAR(50)  NOT NULL
);

CREATE TABLE route_stations (
  route_id       VARCHAR(10)  REFERENCES routes(route_id),
  station_order  INT          NOT NULL,   -- 1 = first stop
  station_name   VARCHAR(50)  NOT NULL,
  arrival_time   TIME,
  departure_time TIME,
  PRIMARY KEY (route_id, station_order)
);

-- ────────────────────────────
-- 2) DATA: 15 ROUTES
-- ────────────────────────────

-- ---- 6 BUS ROUTES ----
INSERT INTO routes VALUES
  ('B336','bus','Piata Unirii','Pipera'),
  ('B335','bus','Piata Unirii','Aeroport Otopeni'),
  ('B391','bus','Piata Unirii','Drumul Taberei'),
  ('B783','bus','Spital Fundeni','Otopeni'),
  ('B448','bus','Cora Pantelimon','Piata Presei'),
  ('B178','bus','Piata Unirii','Ghencea');

-- B336
INSERT INTO route_stations VALUES
  ('B336',1,'Piata Unirii', NULL,     '06:00'),
  ('B336',2,'Universitate','06:08',   '06:09'),
  ('B336',3,'Aviatorilor','06:17',    '06:18'),
  ('B336',4,'Pipera',      '06:26',   NULL);

-- B335
INSERT INTO route_stations VALUES
  ('B335',1,'Piata Unirii', NULL,     '06:10'),
  ('B335',2,'Gara de Nord','06:18',   '06:19'),
  ('B335',3,'Aviatorilor','06:28',    '06:29'),
  ('B335',4,'Aeroport Otopeni','06:38',NULL);

-- B391
INSERT INTO route_stations VALUES
  ('B391',1,'Piata Unirii', NULL,     '06:20'),
  ('B391',2,'Eroilor','06:28',        '06:29'),
  ('B391',3,'Ghencea','06:37',        '06:38'),
  ('B391',4,'Drumul Taberei','06:46', NULL);

-- B783
INSERT INTO route_stations VALUES
  ('B783',1,'Spital Fundeni',NULL,    '06:30'),
  ('B783',2,'Colentina','06:38',      '06:39'),
  ('B783',3,'Gara de Nord','06:48',   '06:49'),
  ('B783',4,'Otopeni','06:58',        NULL);

-- B448
INSERT INTO route_stations VALUES
  ('B448',1,'Cora Pantelimon',NULL,   '06:40'),
  ('B448',2,'Iancului','06:48',       '06:49'),
  ('B448',3,'Obor','06:57',           '06:58'),
  ('B448',4,'Piata Presei','07:06',   NULL);

-- B178
INSERT INTO route_stations VALUES
  ('B178',1,'Piata Unirii', NULL,     '06:50'),
  ('B178',2,'Eroilor','06:58',        '06:59'),
  ('B178',3,'Cotroceni','07:07',      '07:08'),
  ('B178',4,'Ghencea','07:16',        NULL);

-- ---- 4 METRO ROUTES ----
INSERT INTO routes VALUES
  ('M1','metro','Dristor 2','Pantelimon'),
  ('M2','metro','Pipera','Piata Unirii'),
  ('M3','metro','Preciziei','Anghel Saligny'),
  ('M4','metro','Gara de Nord 2','Străulești');

-- M1
INSERT INTO route_stations VALUES
  ('M1',1,'Dristor 2',     NULL,    '07:00'),
  ('M1',2,'Piata Muncii','07:04',   '07:05'),
  ('M1',3,'Republica','07:09',      '07:10'),
  ('M1',4,'Pantelimon','07:14',     NULL);

-- M2
INSERT INTO route_stations VALUES
  ('M2',1,'Pipera',        NULL,    '07:10'),
  ('M2',2,'Aviatorilor','07:14',   '07:15'),
  ('M2',3,'Universitate','07:19',  '07:20'),
  ('M2',4,'Piata Unirii','07:24',   NULL);

-- M3
INSERT INTO route_stations VALUES
  ('M3',1,'Preciziei',     NULL,    '07:20'),
  ('M3',2,'Grozăvești','07:24',     '07:25'),
  ('M3',3,'Piata Victoriei','07:29', '07:30'),
  ('M3',4,'Anghel Saligny','07:34',  NULL);

-- M4
INSERT INTO route_stations VALUES
  ('M4',1,'Gara de Nord 2', NULL,   '07:30'),
  ('M4',2,'Basarab','07:34',        '07:35'),
  ('M4',3,'Grivița','07:39',        '07:40'),
  ('M4',4,'Străulești','07:44',     NULL);

-- ---- 5 TRAIN ROUTES ----
INSERT INTO routes VALUES
  ('T1','train','Bucharest Nord','Otopeni'),
  ('T2','train','Bucharest Nord','Mogoșoaia'),
  ('T3','train','Bucharest Nord','Ploiești Sud'),
  ('T4','train','Bucharest Nord','Giurgiu'),
  ('T5','train','Bucharest Nord','Videle');

-- T1
INSERT INTO route_stations VALUES
  ('T1',1,'Bucharest Nord',NULL,     '08:00'),
  ('T1',2,'Basarab','08:15',         '08:16'),
  ('T1',3,'Pipera','08:31',          '08:32'),
  ('T1',4,'Otopeni','08:47',         NULL);

-- T2
INSERT INTO route_stations VALUES
  ('T2',1,'Bucharest Nord',NULL,     '08:15'),
  ('T2',2,'Chitila','08:30',         '08:31'),
  ('T2',3,'Mogoșoaia','08:46',       '08:47'),
  ('T2',4,'Buftea','09:01',          NULL);

-- T3
INSERT INTO route_stations VALUES
  ('T3',1,'Bucharest Nord',NULL,     '08:30'),
  ('T3',2,'Buftea','08:45',           '08:46'),
  ('T3',3,'Mogoșoaia','09:01',       '09:02'),
  ('T3',4,'Ploiești Sud','09:17',    NULL);

-- T4
INSERT INTO route_stations VALUES
  ('T4',1,'Bucharest Nord',NULL,     '08:45'),
  ('T4',2,'Băneasa','09:00',         '09:01'),
  ('T4',3,'Letea Veche','09:16',     '09:17'),
  ('T4',4,'Giurgiu','09:32',         NULL);

-- T5
INSERT INTO route_stations VALUES
  ('T5',1,'Bucharest Nord',NULL,     '09:00'),
  ('T5',2,'Bragadiru','09:15',       '09:16'),
  ('T5',3,'Vidra','09:31',           '09:32'),
  ('T5',4,'Videle','09:47',          NULL);
