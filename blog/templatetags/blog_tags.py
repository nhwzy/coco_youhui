#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: blog_tags.py
@time: 2016/11/2 下午11:10
"""

from django import template
from django.db.models import Q
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
import random
from django.urls import reverse
from blog.models import Coco, Category, Tag, Links, SideBar, LinkShowType
from django.utils.encoding import force_text
from django.shortcuts import get_object_or_404
import hashlib
import urllib
from DjangoBlog.utils import cache_decorator, cache
from django.contrib.auth import get_user_model
from oauth.models import OAuthUser
from DjangoBlog.utils import get_current_site
import logging

logger = logging.getLogger(__name__)

register = template.Library()


@register.simple_tag
def timeformat(data):
    try:
        return data.strftime(settings.TIME_FORMAT)
        # print(data.strftime(settings.TIME_FORMAT))
        # return "ddd"
    except Exception as e:
        logger.error(e)
        return ""


@register.simple_tag
def datetimeformat(data):
    try:
        return data.strftime(settings.DATE_TIME_FORMAT)
    except Exception as e:
        logger.error(e)
        return ""


@register.filter(is_safe=True)
@stringfilter
def custom_markdown(content):
    from DjangoBlog.utils import CommonMarkdown
    return mark_safe(CommonMarkdown.get_markdown(content))


@register.filter(is_safe=True)
@stringfilter
def truncatechars_content(content):
    """
    获得文章内容的摘要
    :param content:
    :return:
    """
    from django.template.defaultfilters import truncatechars_html
    from DjangoBlog.utils import get_blog_setting
    blogsetting = get_blog_setting()
    return truncatechars_html(content, blogsetting.article_sub_length)


@register.filter(is_safe=True)
@stringfilter
def truncate(content):
    from django.utils.html import strip_tags

    return strip_tags(content)[:150]


@register.inclusion_tag('Coco/tags/breadcrumb.html')
def load_breadcrumb(article):
    """
    获得文章面包屑
    :param article:
    :return:
    """
    names = article.get_category_tree()
    from DjangoBlog.utils import get_blog_setting
    blogsetting = get_blog_setting()
    site = get_current_site().domain
    names.append((blogsetting.sitename, '/'))
    names = names[::-1]

    return {
        'names': names,
        'title': article.title
    }


@register.inclusion_tag('Coco/tags/article_tag_list.html')
def load_articletags(article):
    """
    文章标签
    :param article:
    :return:
    """
    tags = article.tags.all()
    tags_list = []
    for tag in tags:
        url = tag.get_absolute_url()
        count = tag.get_article_count()
        tags_list.append((
            url, count, tag, random.choice(settings.BOOTSTRAP_COLOR_TYPES)
        ))
    return {
        'article_tags_list': tags_list
    }


@register.inclusion_tag('Coco/tags/sidebar.html')
def load_sidebar(user, linktype):
    """
    加载侧边栏
    :return:
    """
    logger.info('load sidebar')
    from DjangoBlog.utils import get_blog_setting
    blogsetting = get_blog_setting()
    recent_articles = Coco.objects.filter(
        status='p')[:blogsetting.sidebar_article_count]
    sidebar_categorys = Category.objects.all()
    extra_sidebars = SideBar.objects.filter(
        is_enable=True).order_by('sequence')
    most_read_articles = Coco.objects.filter(status='p').order_by(
        '-views')[:blogsetting.sidebar_article_count]
    dates = Coco.objects.datetimes('created_time', 'month', order='DESC')
    links = Links.objects.filter(is_enable=True).filter(
        Q(show_type=str(linktype)) | Q(show_type=LinkShowType.A))

    # 标签云 计算字体大小
    # 根据总数计算出平均值 大小为 (数目/平均值)*步长
    increment = 5
    tags = Tag.objects.all()
    sidebar_tags = None
    if tags and len(tags) > 0:
        s = [t for t in [(t, t.get_article_count()) for t in tags] if t[1]]
        count = sum([t[1] for t in s])
        dd = 1 if (count == 0 or not len(tags)) else count / len(tags)
        import random
        sidebar_tags = list(
            map(lambda x: (x[0], x[1], (x[1] / dd) * increment + 10), s))
        random.shuffle(sidebar_tags)

    return {
        'recent_articles': recent_articles,
        'sidebar_categorys': sidebar_categorys,
        'most_read_articles': most_read_articles,
        'article_dates': dates,
        'user': user,
        'sidabar_links': links,
        'show_google_adsense': blogsetting.show_google_adsense,
        'google_adsense_codes': blogsetting.google_adsense_codes,
        'open_site_comment': blogsetting.open_site_comment,
        'show_gongan_code': blogsetting.show_gongan_code,
        'sidebar_tags': sidebar_tags,
        'extra_sidebars': extra_sidebars
    }















@register.simple_tag
def query(qs, **kwargs):
    """ template tag which allows queryset filtering. Usage:
          {% query books author=author as mybooks %}
          {% for book in mybooks %}
            ...
          {% endfor %}
    """
    return qs.filter(**kwargs)
