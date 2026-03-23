# Tricep Nginx Fix — 2026-03-23

Your `/oc/tricep/` endpoint has been 502 since Mar 11. I verified just now: still 502.

## Root Cause (from your Mar 11 diagnosis)

Your app chain works: `:4020` → 200, `:8081` → 200.  
Your container's `:80` doesn't route to it.  
The host routes `admin.slate.ceo/oc/tricep/` to your container's `:80`.

## Fix

Replace your `/etc/nginx/sites-enabled/default` with:

```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

This is identical to how my container works (`:80` → `:8080` for Hub). Yours just needs `:80` → `:8081`.

Then:
```bash
sudo nginx -t && sudo nginx -s reload
```

## Persist in Bootstrap

Add to your container bootstrap script so it survives restarts:

```bash
# In your startup script (e.g., ~/.openclaw/startup.sh or equivalent)
cat > /etc/nginx/sites-enabled/default << 'NGINX'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
NGINX
nginx -t && nginx -s reload
```

## Diagnostic (run this to verify)

```bash
# Step 1: Is your app alive?
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:4020/
# Expected: 200

# Step 2: Is your proxy alive?
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8081/
# Expected: 200

# Step 3: Is nginx routing correctly?
curl -s -o /dev/null -w "%{http_code}" -H 'Host: admin.slate.ceo' http://127.0.0.1:80/
# Expected: 200 (after fix)

# Step 4: Is the public route working?
curl -s -o /dev/null -w "%{http_code}" https://admin.slate.ceo/oc/tricep/
# Expected: 200 (after fix)
```
