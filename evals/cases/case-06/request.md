Build the request handlers for a small notes service. Each user can list and add their own notes. Routes under /admin
are for administrators only: /admin/users lists users, /admin/export dumps every user's notes. Anyone without a valid
token gets 401; a valid token without admin rights gets 403 on /admin routes.
