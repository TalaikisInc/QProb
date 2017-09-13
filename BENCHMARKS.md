# API (Sanic)

# 2017-05-27, w/o ssl.

## 100 posts:

```text
Running 1m test @ http://api.qprob.com:8080/posts/
  6 threads and 20 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   164.30ms  107.91ms   1.14s    80.35%
    Req/Sec    19.96      8.86    50.00     41.39%
  6819 requests in 1.00m, 340.89MB read
Requests/sec:    113.50
Transfer/sec:      5.67MB
```

## Posts by category

```text
Running 1m test @ http://api.qprob.com:8080/posts/meb_faber_research_stock_market_and/
  6 threads and 20 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    74.88ms   82.90ms   1.56s    96.33%
    Req/Sec    44.74     21.60   111.00     67.67%
  15865 requests in 1.00m, 674.00MB read
Requests/sec:    264.00
Transfer/sec:     11.22MB
```

## 1 post

```text
Running 1m test @ http://api.qprob.com:8080/post/why_you_should_ask_for_uranium_stocks_in_your_stocking_this_holiday_season/
  6 threads and 20 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   238.85ms  132.99ms   1.95s    84.96%
    Req/Sec    14.18      7.01    50.00     82.96%
  4633 requests in 1.00m, 3.14MB read
  Socket errors: connect 0, read 0, write 0, timeout 2
Requests/sec:     77.10
Transfer/sec:     53.53KB
```

# 2017-06-05, w. ssl, through Nginx.

## 100 posts

```text
Running 1m test @ https://api.stckmrktnws.com/posts/
  6 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   535.57ms  467.87ms   2.00s    77.87%
    Req/Sec    33.18     15.43   101.00     67.18%
  11196 requests in 1.00m, 749.21MB read
  Socket errors: connect 0, read 0, write 0, timeout 113
Requests/sec:    186.33
Transfer/sec:     12.47MB
```

```text
Running 1m test @ https://api.stckmrktnws.com/posts/
  6 threads and 20 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    91.90ms   27.09ms 284.12ms   73.57%
    Req/Sec    32.70      8.51    60.00     78.74%
  11759 requests in 1.00m, 786.88MB read
Requests/sec:    195.83
Transfer/sec:     13.10MB
```

# 2017-06-17 w. ssl, v2 (Golang), through Nginx, no cache

## Go, 100 posts

```text
Running 1m test @ https://api.qprob.com/posts/
  6 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   343.57ms   98.95ms   1.42s    79.10%
    Req/Sec    36.33     21.94   141.00     62.45%
  8218 requests in 1.00m, 429.79MB read
  Socket errors: connect 0, read 0, write 0, timeout 210
Requests/sec:    136.90
Transfer/sec:      7.16MB
```

```text
Running 1m test @ https://api.qprob.com/posts/
  6 threads and 20 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   141.84ms   12.53ms 259.61ms   87.50%
    Req/Sec    21.36      7.28    30.00     45.76%
  7607 requests in 1.00m, 397.83MB read
Requests/sec:    126.64
Transfer/sec:      6.62MB
```

## Python. 100 posts

```text
Running 1m test @ https://api.stckmrktnws.com/posts/
  6 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.86s    93.71ms   2.00s    60.00%
    Req/Sec     7.56     12.87    90.00     90.95%
  889 requests in 1.00m, 57.36MB read
  Socket errors: connect 0, read 0, write 0, timeout 789
Requests/sec:     14.80
Transfer/sec:      0.95MB
```

```text
Running 1m test @ https://api.stckmrktnws.com/posts/
  6 threads and 20 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.29s   241.07ms   1.98s    75.90%
    Req/Sec     3.64      5.20    20.00     81.96%
  736 requests in 1.00m, 47.47MB read
  Socket errors: connect 0, read 0, write 0, timeout 97
Requests/sec:     12.26
Transfer/sec:    809.61KB
```

## Go, response cached

```text
Running 1m test @ https://api.qprob.com/posts/
  6 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   356.89ms   61.91ms   1.06s    84.59%
    Req/Sec    43.31     20.60   121.00     64.60%
  15385 requests in 1.00m, 804.61MB read
  Socket errors: connect 0, read 0, write 0, timeout 44
Requests/sec:    256.04
Transfer/sec:     13.39MB
```

```text
Running 1m test @ https://api.qprob.com/posts/
  6 threads and 20 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   135.52ms    7.05ms 195.81ms   83.76%
    Req/Sec    22.40      7.38    30.00     37.50%
  7966 requests in 1.00m, 416.61MB read
Requests/sec:    132.57
Transfer/sec:      6.93MB
```

## Go, db queries & response cached

```text
Running 1m test @ https://api.qprob.com/posts/
  6 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     9.59ms   15.61ms   1.01s    98.59%
    Req/Sec     1.78k   393.18     3.84k    69.67%
  636685 requests in 1.00m, 31.84GB read
Requests/sec:  10594.67
Transfer/sec:    542.49MB
```

```text
Running 1m test @ https://api.qprob.com/posts/
  6 threads and 20 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     2.53ms    4.88ms 171.40ms   97.85%
    Req/Sec     1.38k   308.07     3.03k    69.18%
  494911 requests in 1.00m, 24.75GB read
Requests/sec:   8237.26
Transfer/sec:    421.78MB
```
