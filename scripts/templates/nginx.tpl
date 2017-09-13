upstream {0} {{
    server unix:///home/{0}/uwsgi.sock;
}}

upstream {0}_api {{
    server 127.0.0.1:{2} fail_timeout=0;
}}

server {{
    listen          443 ssl;
    listen [::]:443;
    server_name     {1};
    ssl on;
    charset     utf-8;
    #access_log      /var/log/nginx/{1}_access.log combined;
    error_log       /var/log/nginx/{1}_error.log error;

    ssl_certificate         /etc/letsencrypt/live/{1}/fullchain.pem;
    ssl_certificate_key     /etc/letsencrypt/live/{1}/privkey.pem;

    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_dhparam /etc/ssl/certs/dhparam.pem;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers 'ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA:ECDHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA256:DHE-RSA-AES256-SHA:ECDHE-ECDSA-DES-CBC3-SHA:ECDHE-RSA-DES-CBC3-SHA:EDH-RSA-DES-CBC3-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:DES-CBC3-SHA:!DSS';
    ssl_prefer_server_ciphers on;
    add_header Strict-Transport-Security max-age=15768000;
    ssl_stapling on;
    ssl_stapling_verify on;

    location / {{
        uwsgi_pass  {0};
        include     /etc/nginx/uwsgi_params;
        proxy_redirect     off;
        uwsgi_read_timeout 300;
        uwsgi_send_timeout 300;

        proxy_cache_bypass  $http_cache_control;
        add_header X-Proxy-Cache $upstream_cache_status;
        proxy_set_header X-Real-IP $remote_addr;

        proxy_set_header   Host              $http_host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header        X-Forwarded-Proto https;
    }}

    location ^~ /.well-known {{
        allow all;
        auth_basic off;
        alias /home/{0}/.well-known/;
    }}

    location /uploads/  {{
        expires 180d;
	    include /etc/nginx/mime.types;
        alias /home/{0}/uploads/;
        add_header Cache-Control "public";
    }}

    location /static/ {{
	    autoindex on;
        expires 180d;
	    include /etc/nginx/mime.types;
        alias /home/{0}/static/;
        add_header Cache-Control "public";
    }}

    location /favicon.ico {{
        alias /home/{0}/uploads/web/favicon.ico;
    }}

    location /robots.txt {{
        alias /home/{0}/static/robots.txt;
    }}

}}

server {{
    listen 80;
    server_name {1};
    #rewrite ^(.*) https://{1}$1 permanent;

    location ^~ /.well-known {{
        allow all;
        auth_basic off;
        alias /home/{0}/well-known/;
    }}
}}

server {{
    listen 80;
    server_name www.{1};
    #rewrite ^(.*) https://{1}$1 permanent;

    location ^~ /.well-known {{
        allow all;
        auth_basic off;
        alias /home/{0}/well-known/;
    }}
}}

server {{
    listen 443;
    server_name www.{1};
    ssl on;
    ssl_certificate         /etc/letsencrypt/live/www.{1}/fullchain.pem;
    ssl_certificate_key     /etc/letsencrypt/live/www.{1}/privkey.pem;
    #rewrite ^(.*) https://{1}$uri permanent;

    location ^~ /.well-known {{
        allow all;
        auth_basic off;
        alias /home/{0}/well-known/;
    }}
}}

server {{
    listen 80;
    server_name api.{1};
    #rewrite ^(.*) https://api.{1}$uri permanent;

    location ^~ /.well-known {{
        allow all;
        auth_basic off;
        alias /home/{0}/api/.well-known/;
    }}
}}

server {{
    listen 443;
    server_name api.{1};

    error_log       /var/log/nginx/api.{1}_error.log error;

    ssl on;
    ssl_certificate         /etc/letsencrypt/live/api.{1}/fullchain.pem;
    ssl_certificate_key     /etc/letsencrypt/live/api.{1}/privkey.pem;

    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_dhparam /etc/ssl/certs/dhparam.pem;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers 'ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA:ECDHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA256:DHE-RSA-AES256-SHA:ECDHE-ECDSA-DES-CBC3-SHA:ECDHE-RSA-DES-CBC3-SHA:EDH-RSA-DES-CBC3-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:DES-CBC3-SHA:!DSS';
    ssl_prefer_server_ciphers on;
    add_header Strict-Transport-Security max-age=15768000;
    ssl_stapling on;
    ssl_stapling_verify on;

    location / {{
        proxy_set_header Host $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header        X-Forwarded-Proto https;

        proxy_pass http://{0}_api;

        proxy_http_version 1.1;

        proxy_redirect     off;

        if ($request_method = 'GET') {{
            add_header 'Access-Control-Allow-Origin' '*';
        }}
    }}

    location ^~ /.well-known {{
        allow all;
        auth_basic off;
        alias /home/{0}/api/.well-known/;
    }}
}}
