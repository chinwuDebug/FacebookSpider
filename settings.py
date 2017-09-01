# -*- coding: utf-8 -*-
# ==============================Scrapy Settings==============================#

# url list's name is "urls:SPIDER_NAME"
# doc results list's name is "docs:SPIDER_NAME"
SPIDER_NAMES = ["facebook"]

# some sane limits by default
CONCURRENT_ITEMS = 100
CONCURRENT_REQUESTS = 1
# CONCURRENT_REQUESTS_PER_DOMAIN = 1
CONCURRENT_REQUESTS_PER_IP = 1
DOWNLOAD_TIMEOUT = 120
DOWNLOAD_DELAY = 180

# https://doc.scrapy.org/en/latest/topics/settings.html#urllength-limit
URLLENGTH_LIMIT = 1024 * 20

# retry request
RETRY_ENABLED = True
RETRY_TIMES = 2
RETRY_HTTP_CODES = [400, 500, 502, 503, 504, 408]

COOKIES_ENABLED = True
# http request redirect enable
REDIRECT_ENABLED = True
# max redirect times pre request
REDIRECT_MAX_TIMES = 3
# crawl ajax content
AJAXCRAWL_ENABLED = True

# close telnet console
TELNETCONSOLE_ENABLED = False
# set listening port to None or 0 means dynamic port
TELNETCONSOLE_PORT = 0
# close web service
WEBSERVICE_ENABLED = False
# close stats dump after crawl
STATS_DUMP = True

# DEPTH_PRIORITY = 1
# SCHEDULER_DISK_QUEUE = 'scrapy.squeue.PickleFifoDiskQueue'
# SCHEDULER_MEMORY_QUEUE = 'scrapy.squeue.FifoMemoryQueue'

MEMUSAGE_ENABLED = True
MEMUSAGE_LIMIT_MB = 1500
# MEMUSAGE_REPORT = True

# cookie debug
COOKIES_DEBUG = False
SPLASH_COOKIES_DEBUG = False

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36'
# Not all user-agent is linkedin supported, you must test before add them below.
USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/602.4.8 (KHTML, like Gecko) Version/10.0.3 Safari/602.4.8',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36',
]

DOWNLOADER_MIDDLEWARES = {
    # 'engine.middleware.RandomUserAgent': 2,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

# pipeline with smaller value will run earlier
ITEM_PIPELINES = {
    # 'engine.pipelines.LangFilter':10,
    'engine.pipelines.RedisPipeline': 100,
    # 'engine.pipelines.LogPipeline':999,
    # 'engine.pipelines.ESPipeline':100,
}

HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'

# log properties
LOG_FILE = ''
LOG_LEVEL = 'INFO'
LOG_STDOUT = True
