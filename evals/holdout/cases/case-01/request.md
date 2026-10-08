Build the request handlers for the Pedalo ops API. A rider can list their own trips. Everything under /staff is for staff only:
/staff/trips.json and /staff/trips.csv dump every rider's trips, with names and emails. No token gives 401; a rider token on a /staff route gives 403.
