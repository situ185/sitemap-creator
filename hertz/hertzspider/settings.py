# Scrapy settings for hertz project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'hertzspider'

SPIDER_MODULES = ['hertzspider.spiders']
NEWSPIDER_MODULE = 'hertzspider.spiders'

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": False
}
# PLAYWRIGHT_BROWSER_TYPE = "firefox"
# PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 50000
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'None'
# Obey robots.txt rules
ROBOTSTXT_OBEY = True

SCHEDULER_PRIORITY_QUEUE = 'scrapy.pqueues.DownloaderAwarePriorityQueue'
# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 0
# LOG_ENABLED = True
REACTOR_THREADPOOL_MAXSIZE = 20
# while developing we want to see debug logs
LOG_LEVEL = "DEBUG" # or "INFO" in production
COOKIES_ENABLED = True
REQUEST_DEPTH_MAX = 0

# will cache all request to /httpcache directory which makes running spiders in development much quicker
# tip: to refresh cache just delete /httpcache directory
#HTTPCACHE_ENABLED = True
# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
#DOWNLOAD_TIMEOUT = 30
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 32
#PLAYWRIGHT_MAX_PAGES_PER_CONTEXT = 4
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#     # we should use headers
#    'User-Agent': "hertz-sitemap-builder",
#     'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
#     'Accept-Language': 'en'
#     'x-irac-bot-access':'true'
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True

# The initial download delay
AUTOTHROTTLE_START_DELAY = 5

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'hertz.middlewares.HertzSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
SCRAPEOPS_API_KEY = 'c57a8fea-515c-4a70-9fc1-82ed315d2e4d'
SCRAPEOPS_FAKE_USER_AGENT_ENDPOINT = True
#
DOWNLOADER_MIDDLEWARES = {
    'hertzspider.middlewares.HertzDownloaderMiddleware': 400,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    'hertz.pipelines.HertzPipeline': 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 200000
FEED_EXPORT_ENCODING = "utf-8"
