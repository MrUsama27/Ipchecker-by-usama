-- Run this in your PostgreSQL DB (Render dashboard > DB > Connect > psql)
CREATE TABLE used_ips (
    id SERIAL PRIMARY KEY,
    ip_hash TEXT NOT NULL UNIQUE
);
