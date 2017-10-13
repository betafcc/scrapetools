from typing import Union, List

from functools import partial
from urllib.request import urlopen
from lxml import html  # type: ignore


Url = str
Html = str
Matches = Union[List[html.HtmlElement],
                List[List[html.HtmlElement]],
                List[str],
                List[List[str]],
                ]


def scrape(data     : Union[Url, Html, html.HtmlElement] = None,
           css      : str = None,
           xpath    : str = None,
           base_url : str = None,
           flatten  : bool = True,
           ) -> Union[Matches, partial]:
    if not data:
        return partial(scrape,
                       css=css,
                       xpath=xpath,
                       base_url=base_url,
                       flatten=flatten,
                       )

    # 'data' WILL contain a lxml.html.HtmlElement after this clause
    if isinstance(data, str):
        # 'data' WILL contain a html string after this clause
        if data.startswith('http'):
            base_url = base_url or data

            with urlopen(data) as response:
                data = response.read()

        if base_url:
            data = html.fromstring(data, base_url=base_url)
        else:
            data = html.fromstring(data)

    # If possible, resolve relative links
    if base_url:
        data = html.make_links_absolute(
            data,
            base_url=base_url,
        )

    if not (css or xpath):
        return [data]

    if css and xpath:
        result = [
            el.xpath(xpath)
            for el in data.cssselect(css)
        ]

        if flatten:
            result = [el for row in result for el in row]
        return result
    elif css:
        return data.cssselect(css)
    elif xpath:
        return data.xpath(xpath)

    raise TypeError("Invalid arguments")
