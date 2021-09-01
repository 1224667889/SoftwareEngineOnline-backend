import re
from bs4 import BeautifulSoup


def get_content_parts(main_content):
    """
    :param main_content: a soup need to divide into many parts by h2
    :return: every h2 parts of main_content, return type: list[soup]
    """
    second_titles = main_content.select("h1")
    second_titles.append("")
    content_parts = list()
    for i in range(len(second_titles)):
        second_titles[i] = second_titles[i] = str(second_titles[i]).replace("$", "\$").replace("(", "\(").replace(")", "\)").replace("*", "\*").replace(".", "\.").replace("+", "\+").replace("[", "\[").replace("?", "\?").replace("^", "\^").replace("{", "\{").replace("|", "\|")
    for i in range(len(second_titles) - 1):
        pattern = f"({second_titles[i]}[\s\S]+){second_titles[i + 1]}"
        content_part = re.findall(pattern, str(main_content))
        assert len(content_part) == 1
        content_part = content_part[0]
        content_parts.append(content_part)

    return content_parts


def parse_blog(targets, blog):
    """
    :param targets: a list of title, type: list[str]
    :param blog: html, type: str
    :return: target h2 parts, type: dict[str][str], format: dict[target_title][html_content]
    """
    res = dict()
    soup = BeautifulSoup(blog, "lxml")
    content_parts = get_content_parts(soup)
    for content_part in content_parts:
        title = BeautifulSoup(content_part, "lxml").h1.text
        if title in targets:
            res.update({title: content_part})
    return res
