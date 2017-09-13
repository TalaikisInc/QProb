upstream {0} {{
    server unix:///home/{0}/uwsgi.sock;
}}

upstream {0}_api {{
    server api.{1}:{2} fail_timeout=0;
}}

server {{
    listen          80;
    listen [::]:80;
    server_name     {1};

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
    server_name www.{1};

    location ^~ /.well-known {{
        allow all;
        auth_basic off;
        alias /home/{0}/well-known/;
    }}
}}

server {{
    listen 80;
    server_name api.{1};

    location ^~ /.well-known {{
        allow all;
        auth_basic off;
        alias /home/{0}/api/.well-known/;
    }}
}}
