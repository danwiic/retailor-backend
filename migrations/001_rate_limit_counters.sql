CREATE TABLE IF NOT EXISTS rate_limit_counters (
    key_hash TEXT NOT NULL,
    action TEXT NOT NULL,
    window_date DATE NOT NULL,
    count INTEGER NOT NULL CHECK (count >= 0),
    PRIMARY KEY (key_hash, action, window_date)
);
