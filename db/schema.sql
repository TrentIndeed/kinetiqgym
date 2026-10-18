-- D1 tables for the two site forms (src/worker.js). Apply with:
--   npx wrangler d1 execute kinetiqgym --remote --file db/schema.sql
-- Workers KV allows 1,000 writes a day on the free plan, and a signup took about four; D1 allows 100,000.

-- the build list: one row per email; a second call with the same email only adds the interest answer
CREATE TABLE IF NOT EXISTS signups (
  email    TEXT PRIMARY KEY,
  interest TEXT,
  source   TEXT,
  country  TEXT,
  created  TEXT NOT NULL,
  updated  TEXT NOT NULL
);

-- "Discuss a project" messages; id is "<created>:<8 hex>"
CREATE TABLE IF NOT EXISTS enquiries (
  id      TEXT PRIMARY KEY,
  created TEXT NOT NULL,
  name    TEXT,
  email   TEXT,
  company TEXT,
  message TEXT,
  country TEXT
);

-- per-address request counters for the forms: a hash of path and address, never the address itself; rows go after a few hours
CREATE TABLE IF NOT EXISTS rate (
  key  TEXT PRIMARY KEY,
  hour TEXT NOT NULL,
  n    INTEGER NOT NULL
);
