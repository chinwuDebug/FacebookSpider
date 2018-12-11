# FacebookSpider
crawl facebook public post's information who likes, comments, shares
the main method: 
1. scrapy frame, to crawl post ID
2. splash render JS page and simulate human's action
3. facebook Graph API explorer

**详细内容请见CSDN博客:<http://blog.csdn.net/chinwuforwork>**

***
**2018.12.11更新**

各位上来就 “这个项目要怎么跑通啊？”  “接口不对啊，怎么调啊？” 的朋友，你问这种问题的时候，给我转个大点红包，我教你跑通，也算是知识付费。
但是你要是什么都不懂就想不劳而获，去找其他人吧，邮件我不会回的。

欢迎那些交流具体技术的人来邮件，比如说“splash-scrapy 在国内怎么设置代理”等等。 这种问题我会回复。
***


 主要功能：抓取某keywords关键词public posts information.
 因为项目的原因，删除了部分代码，核心部分代码已经保留下来。
<br />
爬虫的入口是
 
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
- Input:

        {
            "task": task name,
            "keyword": keywords to search,
            "url": default is None,
            "ext":{
                "range": time range in days, defaults to 60 days,
                "max_posts_num": max posts result should return, defaults to 100
            }
        }
        
        e.g:
        job = {"task": "facebook_test", "url": "", "keywords": "3dprinting", "ext": {'range': 60, 'max_posts_num': 5}}
this output is posts about information, likes, shares, and comments.

- Output:

        {   
            "task": task name,
            "type": "facebook_post",
            "keyword": search keyword string,
            "timestamp": spider crawls timestamp,
            "post_data":[{
                    "post_information":{
                        "post_from_user": post from user name,
                        "post_from_user_id": post from user id,
                        "post_id": post's id,
                        "post_type": "posts", "photos", "videos",
                        "post_content": post's content,
                        "post_link": post's article link url,
                        "post_time": post created time,
                        "post_likes_number": the number of post who likes it,
                        "post_shares_number": the number of post who share it,
                        "post_comments_number": the number of post who comment it
                    },

                    "post_likes":
                    [
                        {
                            "id": user's account id,
                            "name": user's name
                        },
                    ...],

                    "post_shares":
                    [
                        {
                            "id": user's account id,
                            "name": user's name
                        },
                    ...],

                    "post_comments":
                    [
                        {
                            "id": user's account id,
                            "name": user's name
                            "comment_content": comment's content
                        },
                    ...]
                    }, ...]    
        }

        e.g:
        {
            "timestamp": "2017-08-31 02:11:57",
            "task": "facebook_test",
            "keyword": "3dprinting",
            "type": "facebook_post",
            "post_data":[{
                                "post_information": {
                                "post_time": "2017-08-10 21:21:16",                                   
                                "post_from_user_id": "1795995493994251",
                                "post_link": "https://www.facebook.com/si.3dprinting/photos/",        
                                "post_comments_number": 0,
                                "post_likes_number": 1,
                                "post_id": "1795995493994251_1904932513100548",                       
                                "post_from_user": "3Dprinting",                                       
                                "post_content": "Another attempt .",
                                "post_shares_number": 0,
                                "post_type": "posts"                                                  
                              },
                                "post_comments": [
                                                  {
                                                      "comment_content": "No more Shark after Dark?",
                                                      "name": "George Longoria",
                                                      "id": "919171418236405"
                                                  }
                                               ],
                                "post_likes": [
                                                  {
                                                      "id": "342765689501430",
                                                      "name": "Beryl Addison"
                                                  }
                                              ],
                                "post_comments": [
                                                      {
                                                          "id": "650698851696529",
                                                           "name": "Danit Peg"
                                                      }
                                                 ]
                        }, ...]
        }           
***
Some issues to send e-mail to chinwu16@126.com
