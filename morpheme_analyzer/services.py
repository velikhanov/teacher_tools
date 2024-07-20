import re
from time import sleep
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://morphemeonline.ru"
API_URL = f"{BASE_URL}/api/get"


def parse_text(input_text: str) -> list[str]:
    all_matches = re.findall(r"\b\w+\b|[.,;?!]", input_text)
    return [
        f"{{{word}}}" if len(word) > 3 else word
        for word in all_matches
    ]


def clean_page(page: str) -> str:
    morpheme = re.search(r"<div[^>]*class=\"morpheme\"[^>]*>(.*?)</div>", page, re.DOTALL).group(0)
    if "программа института" in morpheme:
        morpheme = "<div class=\"morpheme\">" + re.sub(r".*?программа института<br>", "", morpheme, flags=re.DOTALL)

    return morpheme


def filter_page(page: str) -> list[BeautifulSoup]:
    result = []

    soup = BeautifulSoup(clean_page(page), "html.parser").find("div", class_="morpheme")
    based_span = soup.find("span", class_="based")
    if based_span:
        result.append(based_span)

    ending_span = soup.find("span", class_="ending")
    if ending_span:
        result.append(ending_span)

    suffix_spans = soup.find_all("span", class_="suffix")
    for suffix_span in suffix_spans:
        if "class" in suffix_span.parent.attrs and "based" not in suffix_span.parent["class"]:
            result.append(suffix_span)

    return result


def extract_word_data_from_page(page: str) -> dict[str, str]:
    result = {
        "based": [],
        "ending": {}
    }

    for element in filter_page(page):
        element_class = ".".join(element["class"])
        if element_class == "based":
            for subel in element.children:
                class_name = subel["class"][0]
                content = subel.get_text()
                result["based"].append({class_name: content})
        elif element_class == "suffix":
            class_name = element["class"][0]
            content = element.get_text()
            result["based"].append({class_name: content})
        else:
            if element_class == "ending.nulled":
                result["ending"] = None
            else:
                for subel in element.children:
                    content = subel.get_text()
                    result["ending"] = content
    return result


def normalize_word(word: str) -> str:
    response = requests.post(
        url=API_URL,
        headers={
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest"
        },
        json={"word": word}
    )

    response_json = response.json()
    if response_json["status"] == "ok":
        word = response_json["word_baseform"]
    elif response_json["status"] == "typo":
        word = response_json["status"]["items"][0]

    return word


def analyze_text(parsed_text: list[str]) -> list[dict[str, str]]:
    result = []

    pattern = r'\{(.*?)\}'
    for text_item in parsed_text:
        match = re.search(pattern, text_item)
        if match:
            word = normalize_word(match.group(1))
            url = f"{BASE_URL}/{word[0].upper()}/{word.lower()}"
            response = requests.get(url=url)
            if response.status_code != requests.codes.ok:
                result.append({"default": word})
                continue
            result.append(extract_word_data_from_page(response.text))
            sleep(1)
        else:
            result.append({"default": text_item})

    return result
