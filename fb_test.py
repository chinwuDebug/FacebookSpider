# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest, SplashFormRequest
from scrapy import Selector
from scrapy.http.request import Request
from scrapy.http.request.form import FormRequest
from scrapy.spiders.init import InitSpider
from scrapy.exceptions import CloseSpider
import re
import json
import datetime
import sys
from items import FacebookPosts

reload(sys)
sys.setdefaultencoding('utf-8')

lua_script = """
    local random = math.random
    json = require("json")
    function main(splash)
        local cookies = splash.args.headers['Cookie']
        splash:on_request(
            function(request)
                request:set_header('Cookie', cookies)
            end
        )
        splash:go{splash.args.url, headers=splash.args.headers}
        splash:wait(10)
        --png1 = splash:png{render_all=true}
        -- random wait, be more like a human
        local ok, error = splash:runjs([[window.scrollTo(0, document.body.scrollHeight/2)]])
        splash:wait(math.random(5,10))
        --png2 = splash:png{render_all=true}
        local entries = splash:history()
        -- local last_entry = entries[#entries]
        local last_response = entries[#entries].response
        return {
            url = splash.args.url,
            html = splash:html(),
            http_status = last_response.status,
            headers = last_response.headers,
            cookies = splash:get_cookies(),
            --png1 = png1,
            --png2 = png2,
            data = json.encode(updates),
            har = json.encode(splash:har()),
        }
    end
"""


class FacebookSearchSpider(InitSpider):
    name = 'facebook'
    allowed_domains = ['www.facebook.com',
                       'graph.facebook.com']
    login_url = "https://www.facebook.com/login"
    start_urls = []

    def __init__(self, *args, **kwargs):
        super(FacebookSearchSpider, self).__init__(*args, **kwargs)
        self._task = None
        self.keywords = None
        self.__current_job = None

        self.login_user = "your account"
        self.login_pass = "your account"
        self.facebook_account_id = "your account"
        self.fb_api_req_access_token = "your account"

        self.all_jobs = []
        self.datas = []
        self.post_ids = []

    def spider_idle(self, spider):
        # job = self.tasktool.get_job_from_master()
        # job test
        # defualt url is None. no function to use.
        # 这里是入口！！！！！！！！！！！！！！！！！！！！
        job = {"task": "facebook_test", "url": "", "keywords": "3dprinting", "ext": {'range': 60, 'max_posts_num': 5}}
        if job and self.login_user is not None:
            self.__current_job = job
            self._task = job.get('task', None)
            # Now no function to use url.
            # url = job.get('url', None)
            self.keywords = job.get('keywords', None)
            user_info = job.get("ext", {})
            max_posts_num = user_info.get('max_posts_num', 100)
            range = user_info.get('range', 60)

            fb_api_req_access_token = self.fb_api_req_access_token

            requests = self.make_requests_from_job(self.keywords, max_posts_num, range, fb_api_req_access_token)
            self.crawler.engine.crawl(requests, spider)
        else:
            self.logger.info('facebook spider no more jobs, shutdown.')

    def parse_str(self, str, type):
        # parse return's data, to structure the seq of request url
        if type == 'header':
            return re.sub(',(?P<key>\w+):', ',"\g<key>":', str, 50).replace(' ', '') \
                .replace('{view:', '{"view":').replace('crct', '"crct"')
        elif type == 'tail':
            return re.sub(',(?P<key>\w+):', ',"\g<key>":', str, 50).replace(' ', '').replace('cursor', '"cursor"')
        elif type == 'symb':
            return str.replace('"', '%22').replace('\\', '%5C').replace(':', '%3A').replace(',', '%2C') \
                .replace(' ', '').replace('}', '%7D').replace('{', '%7B')

    def time_control(self, post_time, range):
        # control time range
        # [:-2] delete am and pm
        post_time = datetime.datetime.strptime(post_time[:-2], "%A, %B %d, %Y at %H:%M")
        now_time = datetime.datetime.now()
        return (now_time - post_time).days <= range

    def parse_post(self, page_code, range):
        # parse html, crawl the post information
        html = Selector(text = page_code)
        post_ids = []
        for post in html.xpath('//div[@class="_307z"]'):
            try:
                post_url = post.xpath('.//div[@class="_lie"]/a/@href').extract_first()
                account_inf = post.xpath('.//a[@class="_vwn _8o lfloat _ohe"]/@data-hovercard').extract_first()
                account_id = account_inf[account_inf.find('?id=') + 4:]
                post_url_seq = post_url.split('/')
                if 'posts' in post_url_seq:
                    post_id = post_url_seq[-1]
                    post_type = 'posts'
                elif 'videos' in post_url_seq:
                    post_id = post_url_seq[-2]
                    post_type = 'videos'
                elif 'photos' in post_url_seq:
                    post_id = post_url_seq[-2]
                    post_type = 'photos'
                else:
                    continue
                post_time = post.xpath('.//abbr/@title').extract_first()
                # if today from post's create time is less than range, this post is usable.
                if self.time_control(post_time, range):
                    post_ids.append((account_id + "_" + post_id, post_time, post_type))
                else:
                    continue
            except:
                continue
        return post_ids

    def structure_api_request(self, page_doc, type = None, request_tail = None, data_header = None):
        request_header = "https://www.facebook.com/ajax/pagelet/generic.php/BrowseScrollingSetPagelet?dpr=1&data="
        if type == 'first':
            # parse the first page's posts
            try:
                data_header = re.search(r'{view:"list",encoded_query:.*mrss:true}', page_doc).group() + ','
                data_tail = re.search(r'cursor:.*tr:null', page_doc).group() + '}'
                if len(data_header) < 10 or len(data_tail) < 10:
                    self.logger.info("No more first page's post about keywords %s.spider closed." % self.keywords)
                    request_url = None
                else:
                    request_data = self.parse_str(
                            self.parse_str(data_header, 'header') + self.parse_str(data_tail, 'tail'), 'symb')
                    request_url = request_header + request_data + request_tail
            except:
                self.logger.error("keywords %s first page's posts search error." % self.keywords)
                return "error", "error"
        else:
            # parse the other page's posts
            try:
                data_tail_url = re.search(r'"cursor":.*"tr":null', page_doc).group() + '}'
                if len(data_tail_url) < 10:
                    self.logger.info("No more post about keywords %s.spider closed." % self.keywords)
                    request_url = None
                else:
                    request_url = request_header + self.parse_str(data_header + data_tail_url,
                                                                  'symb') + request_tail
            except:
                self.logger.error("keywords %s search more post error" % self.keywords)
                return "error", "error"
        return request_url, data_header

    def init_request(self):
        # to login
        return Request(
                url = self.login_url,
                callback = self.log_in,
                priority = 10
        )

    def log_in(self, response):
        # fill in username and password
        return FormRequest.from_response(
                response,
                url = self.login_url,
                formid = "login_form",
                formdata = {
                    "email": self.login_user,
                    "pass": self.login_pass
                },
                callback = self.after_login
        )

    def after_login(self, response):
        # check login
        if self.facebook_account_id not in response.body:
            self.logger.error("Failed to login, close spider, check facebook account.")
        # cancel every task to login
        # else:
        #     return self.make_requests_from_job(self.keywords)
        return self.initialized()

    def make_requests_from_job(self, keywords, max_posts_num, range, fb_api_req_access_token):
        post_url = "https://www.facebook.com/search/str/%s/stories-keyword/stories-public" \
                   % keywords.replace(' ', '%2B')
        # save the need of structuring request's parameter
        return SplashRequest(url = post_url,
                             callback = self.parse_js,
                             endpoint = 'execute',
                             args = {'lua_source': lua_script, 'timeout': 3600},
                             cache_args = ['lua_source'],
                             session_id = 1,
                             meta = {
                                 "max_posts_num": max_posts_num,
                                 "range": range,
                                 "fb_api_req_access_token": fb_api_req_access_token,
                             }
                             )

    def parse_js(self, response):
        # parse post page from one by one
        # this is the first page
        fb_api_req_access_token = response.meta.get("fb_api_req_access_token", None)
        max_posts_num = response.meta.get("max_posts_num", 100)
        range = response.meta.get("range", 60)
        loop_times = 0
        page_code = response.body.replace('<!--', '').replace('-->', '')
        not_search_inf = "We couldn't find anything for"
        if not_search_inf in page_code:
            self.logger.info("the keywords: %s can't search post.spider closed." % self.keywords)
        else:
            request_tail = "&__user=%s&__a=1&__dyn=5V4cjEzUGByK5A9UoHaEWC5EWq2WiWF3oyeqrWo8ovyUWdwIhE98n" \
                           "yUdUat0Hx24UJi28rxuF8WUOuVWxeUPxKcxaFQ3uaVVojxCVFEKjGqu58nUnAz8lUlwkEG9J7BwBx66EK2m5K5FLKE" \
                           "gDQ6EvG7ki4e2i8xqawDDhomx22yq3ui9Dx6WK6pESUK8Gm8CBz8swgE-6UCbx-8xnyESbwFxCQEx38y-fXgO&__af" \
                           "=jw&__req=c&__be=-1&__pc=EXP3%%3Aholdout_pkg&__rev=3207279" % str(self.facebook_account_id)
            post_ids = self.parse_post(page_code, range)
            # maybe not search relevant keywords post

            self.post_ids = post_ids
            request_url, data_header = self.structure_api_request(page_code, 'first', request_tail)
            if request_url:
                return Request(
                        url = request_url,
                        callback = self.parse_api_data,
                        priority = 1,
                        dont_filter = False,
                        meta = {
                            "loop_times": loop_times,
                            "range": range,
                            "max_posts_num": max_posts_num,
                            "request_tail": request_tail,
                            "data_header": data_header,
                            "fb_api_req_access_token": fb_api_req_access_token,
                        }
                )

    def parse_api_data(self, response):
        # make a crawl loop
        # equal to continually scroll to the bottom
        # and load to new posts
        # the number of posts should be not more than max_posts_num to control the loop times
        # but the max loop need control
        loop_times = response.meta.get("loop_times", 1)
        max_posts_num = response.meta.get("max_posts_num", 100)
        range = response.meta.get("range", 60)
        fb_api_req_access_token = response.meta.get("fb_api_req_access_token", None)
        request_tail = response.meta.get("request_tail", None)
        data_header = response.meta.get("data_header", None)
        # the max number for scroll to the bottom
        max_loop_times = 10
        if loop_times <= max_loop_times and len(self.post_ids) <= max_posts_num:
            loop_times += 1
            api_code = response.body.replace('for (;;);', '')
            request_url, data_header = self.structure_api_request(api_code, request_tail = request_tail,
                                                                  data_header = data_header)
            # no more request url
            if len(request_url) == 0:
                return self.structure_fbapi_request_url(fb_api_req_access_token)
            # request error
            elif request_url == "error":
                self.logger.info("request url: %s search post error." % response.url)
                return self.structure_fbapi_request_url(fb_api_req_access_token)
            # request urls are normal
            else:
                # post_ids contain (post_id, post_time, post_type)
                post_ids = self.parse_post(json.loads(api_code)["payload"], range)
                if post_ids:
                    # post_ids list, contains all the post_id need to crawl
                    # no suitable time range post, loop once
                    self.post_ids.extend(post_ids)
                return Request(
                        url = request_url,
                        callback = self.parse_api_data,
                        priority = 1,
                        dont_filter = False,
                        meta = {
                            "loop_times": loop_times,
                            "request_tail": request_tail,
                            "max_posts_num": max_posts_num,
                            "data_header": data_header,
                            "fb_api_req_access_token": fb_api_req_access_token,
                        }
                )
        else:
            return self.structure_fbapi_request_url(fb_api_req_access_token)

    def structure_fbapi_request_url(self, fb_api_req_access_token):
        # structure facebook api request url
        api_request_urls = []
        fb_api_req_header = "https://graph.facebook.com/v2.10/"
        # id,created_time,from,message,link,likes.limit(1000),comments.limit(1000){from,message},sharedposts.limit(1000){from}
        fb_api_req_content = "?fields=id%2Ccreated_time%2Cfrom%2Cmessage%2Clink%2Clikes.limit(10000)%2Ccomments" \
                             ".limit(10000)%7Bfrom%2Cmessage%7D%2Csharedposts.limit(10000)%7Bfrom%7D&access_token="
        if set(self.post_ids) > 0:
            for id in set(self.post_ids):
                post_id, post_time, post_type = id
                api_request_url = \
                    fb_api_req_header + post_id + fb_api_req_content + fb_api_req_access_token
                api_request_urls.append((api_request_url, post_id, post_time, post_type))
            return self.request_json_data(api_request_urls)
        else:
            self.logger.info("no post id to search, spider closed.")

    def get_one_job(self):
        if len(self.all_jobs) > 0:
            (url, post_id, post_time, post_type) = self.all_jobs.pop()
            return self.deal_one_job(url, post_id, post_type)
        else:
            return self.save_data()

    def request_json_data(self, url_inf):
        # request facebook API for every post's ID
        self.all_jobs = url_inf
        # get a api request url
        return self.get_one_job()

    def deal_one_job(self, url, post_id, post_type):
        return Request(
                url = url,
                callback = self.parse_json,
                priority = 1,
                dont_filter = False,
                meta = {
                    "post_id": post_id,
                    "post_type": post_type
                }
        )

    def parse_json(self, response):
        json_data = json.loads(response.body)
        post_id = response.meta.get('post_id', None)
        post_type = response.meta.get('post_type', None)
        if "error" in json_data:
            self.logger.info("post %s json return error." % post_id)
            return self.get_one_job()
        else:
            one_post = {}
            one_post["post_information"] = {}
            one_post["post_information"]["post_id"] = post_id
            one_post["post_information"]["post_type"] = post_type
            one_post["post_likes"] = []
            one_post["post_comments"] = []
            one_post["post_shares"] = []
            one_post["post_information"]["post_from_user"] = json_data["from"]["name"]
            one_post["post_information"]["post_from_user_id"] = json_data["from"]["id"]
            one_post["post_information"]["post_content"] = json_data.get("message", None)
            one_post["post_information"]["post_link"] = json_data.get("link", None)
            one_post["post_information"]["post_time"] = json_data["created_time"].replace('T', ' ').replace('+0000', '')
            # post likes
            if "likes" in json_data.keys():
                one_post["post_likes"].extend(json_data["likes"]["data"])
            one_post["post_information"]["post_likes_number"] = len(one_post["post_likes"])
            # post shares
            if "sharedposts" in json_data.keys():
                one_post["post_shares"].extend([share["from"] for share in json_data["sharedposts"]["data"]])
            one_post["post_information"]["post_shares_number"] = len(one_post["post_shares"])
            # post comments
            if "comments" in json_data.keys():
                for comment in json_data["comments"]["data"]:
                    one_comment = comment["from"]
                    one_comment["comment_content"] = comment["message"]
                    one_post["post_comments"].append(one_comment)
            one_post["post_information"]["post_comments_number"] = len(one_post["post_comments"])
            self.datas.append(one_post)
            # make request loop
            return self.get_one_job()

    def save_data(self):
        Post = FacebookPosts()
        Post["timestamp"] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        Post["type"] = "facebook_post"
        Post["keyword"] = self.keywords
        Post["task"] = self._task
        Post["post_data"] = self.datas
        # for test
        with open('post_data', 'wb') as f:
            f.write(json.dumps(dict(Post)))
        yield Post
