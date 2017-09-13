user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
	worker_connections 10000;
}

worker_rlimit_nofile 22000;

http {
	open_file_cache max=200000 inactive=20s;
	open_file_cache_valid 60s;
	open_file_cache_min_uses 2;
	open_file_cache_errors on;

	access_log off;

	sendfile on;
	tcp_nopush on;
	tcp_nodelay on;
	keepalive_timeout 10;
	keepalive_requests 100;
	types_hash_max_size 2048;
	server_tokens off;

	server_names_hash_bucket_size 64;

	include /etc/nginx/mime.types;
	default_type application/octet-stream;

	access_log /var/log/nginx/access.log;
	error_log /var/log/nginx/error.log;

	gzip on;
	gzip_disable "msie6";
	gzip_min_length 10240;
	gzip_vary on;
	gzip_proxied expired no-cache no-store private auth;
	gzip_comp_level 6;
	gzip_buffers 16 8k;
	gzip_http_version 1.1;
	gzip_types text/plain text/css application/json application/x-javascript text/xml application/xml application/xml+rss text/javascript;

	client_body_timeout 10;
	send_timeout 2;

	limit_conn_zone $binary_remote_addr zone=conn_limit_per_ip:10m;
	limit_req_zone $binary_remote_addr zone=req_limit_per_ip:10m rate=5r/s;
	client_body_buffer_size  128k;

	include /etc/nginx/sites-enabled/*;
}