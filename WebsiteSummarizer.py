# OwensKey
# 42582b3c16d744ba9061736318ed7a6c.qzTHH9U2hT1H353eWhhlOE8P

import subprocess
from bs4 import BeautifulSoup
import re
from collections import Counter
from ollama import Client

summary_str = ""

url = input("Enter a URL: ")

webpage = subprocess.run(["curl", url], capture_output=True)

soup = BeautifulSoup(webpage.stdout, "html.parser")

for tags in soup(["script", "style"]):
    tags.extract()

summary_str += "\nHeadings:\n"
heading = []
for headings in soup(["h1", "h2", "h3", "h4", "h5", "h6"]):
    heading.append(re.findall(r"[a-zA-Z0-9!@#$%^&*()\-_=+|\":;,./? ]+", headings.text))
for h in heading:
    summary_str += h[0] + "\n"
summary_str += "\n\n\n"

summary_str += "Links:\n"
link = []
linkText = []
for links in soup(["a"]):
    if re.findall(r"https://[a-zA-Z0-9.\-/]+\.[a-zA-Z0-9\-/+=?&%$:;]+", str(links)) != []:
        link.append(re.findall(r"https://[a-zA-Z0-9.\-/]+\.[a-zA-Z0-9\-/+=?&%$]+", str(links)))
        linkText.append(links.get_text())
link_idx = 0
for l in link:
    if l[0].strip() == linkText[link_idx].strip():
        summary_str += l[0] + "\n"
        link_idx += 1
    elif linkText[link_idx].strip() == "":
        summary_str += l[0] + "\n"
        link_idx += 1
    else:
        summary_str += linkText[link_idx] + " | " + l[0] + "\n"
        link_idx += 1
summary_str += "\n\n\n"

summary_str += "Images:\n"
images = []
imageText = []
for imgs in soup(["img"]):
    if re.findall(r"https://[a-zA-Z0-9.\-/]+\.[a-zA-Z0-9\-/+=?&%$;:]+", str(imgs)) != []:
        images.append(re.findall(r"https://[a-zA-Z0-9.\-/]+\.[a-zA-Z0-9\-/+=?&%$;:]+", str(imgs)))
        alt = imgs.get("alt")
        imageText.append(alt)
img_index = 0
for i in images:
    if imageText[img_index] is None or imageText[img_index] == "":
        summary_str += i[0] + "\n"
        img_index += 1
    else:
        summary_str += imageText[img_index] + " | " + i[0] + "\n"
        img_index += 1
summary_str += "\n\n\n"

summary_str += "Emails:\n"
emails = re.findall(r"[a-zA-Z0-9!#$%^&*\-_=+'{}|`~.]+@[a-zA-Z0-9!#$%^&*\-_=+'{}|`~.]+\.[a-zA-Z]{1,3}", soup.get_text())
for email in emails:
    summary_str += email + "\n"
summary_str += "\n\n\n"

summary_str += "Phone numbers:\n"
numbers = re.findall(r"\(*[0-9]{3}\)*[-. ]+[0-9]{3}[-. ]+[0-9]{4}", soup.get_text())
for number in numbers:
    summary_str += number + "\n"
summary_str += "\n\n\n"

summary_str += "Word count:\n"
word_count = subprocess.run(["wsl", "wc", "-w"], input=soup.get_text(), capture_output=True, encoding="utf-8")
summary_str += word_count.stdout
summary_str += "\n\n\n"

summary_str += "Top 10 most frequently used words:\n"
words = re.findall("[a-zA-z]+", soup.get_text())
frequent_words = Counter(words).most_common(10)
for word in frequent_words:
    summary_str += word[0] + " - " + str(word[1]) + " apperances\n"
summary_str += "\n\n\n"

print(summary_str)

print("LLM Summary:\n")

api_key = "42582b3c16d744ba9061736318ed7a6c.qzTHH9U2hT1H353eWhhlOE8P"

client = Client(
    host="https://ollama.com",
    headers={'Authorization': 'Bearer ' + api_key}
)

messages = [
  {
    'role': 'user',
    'content': 'Based on the following information that was gathered about a webpage, generate a 1-5 sentence overall summary of what the webpage is about. Also, try to detect any bias within the information on the webpage:' + summary_str,
  },
]

for part in client.chat('gpt-oss:120b', messages=messages, stream=True):
  print(part['message']['content'], end='', flush=True)