# Tuning sqlite-vec for notes search  (post, 2026-09-08)

Page size, batch inserts and quantizing vectors to int8: three changes that took a 50,000-note index from 480 ms to 70 ms per query. The post gives the
SQL, the settings and a timing table for each change on the same machine.
