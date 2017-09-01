# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FacebookPosts(scrapy.Item):
    # task name from Redis
    task = scrapy.Field()
    # the keyword for search
    keyword = scrapy.Field()
    # the post's type: facebook_post
    type = scrapy.Field()
    # run the task's timestamp
    timestamp = scrapy.Field()
    # post's data, like:
    # {
    #   "post_information": {
    #     "post_time": "2017-08-10 21:21:16",                                   # post creat time
    #     "post_from_user_id": "1795995493994251",
    #     "post_link": "https://www.facebook.com/si.3dprinting/photos/",        # post inner url link
    #     "post_comments_number": 0,
    #     "post_likes_number": 1,
    #     "post_id": "1795995493994251_1904932513100548",                       # post ID: userID_postID
    #     "post_from_user": "3Dprinting",                                       # user's name
    #     "post_content": "Another attempt .",
    #     "post_shares_number": 0,
    #     "post_type": "posts"                                                  # post type: posts, photos, videos
    #   },
    #     "post_comments": [
    #                       {
    #                           "comment_content": "No more Shark after Dark?",
    #                           "name": "George Longoria",
    #                           "id": "919171418236405"
    #                       }
    #                    ],
    #     "post_likes": [
    #                       {
    #                           "id": "342765689501430",
    #                           "name": "Beryl Addison"
    #                       }
    #                   ],
    #     "post_comments": [
    #                           {
    #                               "id": "650698851696529",
    #                                "name": "Danit Peg"
    #                           }
    #                      ]
    # }
    post_data = scrapy.Field()
