+++
author = "rl1987"
title = "Making heuristics smarter with GPT-3"
date = "2022-10-09"
draft = true
tags = ["automation", "python"]
+++

Sometimes data being scraped is a little fuzzy - easy to understand for human mind,
but not strict and formal enough to be easily tractable by algorithms. This can
get in a way of analysing the data or basing further automations off it. This is
where heuristics come in. A heuristic is an inexact, but quick way to solve a
problem. We will discuss how GPT-3 API can be used to implement heuristic
techniques to deal with somewhat fuzzy data that might otherwise require a
human to take a look into it.

Earlier this year I participated in data bounty that involved sourcing museum
collection data and wrangling all the records into a single database schema.
Some websites provided a great deal of museum collection data, but they also
provided data on private art collections, libraries, universities, schools
and other entitities that were neither art galleries nor museums, meaning that
some data was out of scope. This presented a bit of a problem since some data
needed to be scraped and submitted, but some had to be ignored based on institution
name alone.

So what do we do? Well, given that GPT-3 was trained on massive amounts of text,
it should be able to tell based on institution name if it is of interest for
scraping. We just need to ask it properly. For example, we could give it a
prompt:

```
Answer YES if "National Gallery of Art" is a gallery or museum. Answer NO otherwise.
```

To which it answers:

```
Yes
```

The part of the prompt that we keep changing is the substring between duoble quotes.
We keep everything else the same. We also set the temperature gauge to 0 as we need
no randomisation/"creativity" on AI part to answer this simple question. 

[TODO: screenshot]

Now that we got the prompt right we can use OpenAI client library to develop a Python
script that will filter a scraped list of institutions to shortlist them for further
scraping. 


```python
#!/usr/bin/python3

import csv
import os

import openai

openai.api_key = "[REDACTED]"

FIELDNAMES = ["name", "slug"]


def get_answer(institution_name):
    if "Archive" in institution_name:
        return "NO"

    if "Library" in institution_name or "Libraries" in institution_name:
        return "NO"

    if "Private Collection" in institution_name:
        return "NO"

    if "Museum" in institution_name:
        return "YES"

    if "Gallery" in institution_name:
        return "YES"

    response = openai.Completion.create(
        model="text-davinci-002",
        prompt='Answer YES if "{}" is a gallery or museum. Answer NO otherwise.'.format(
            institution_name
        ),
        temperature=0,
        max_tokens=4,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    answer = response.get("choices")[0].text.upper().strip()

    return answer


def main():
    in_f = open("orgs.csv", "r")
    csv_reader = csv.DictReader(in_f)

    out_f = open("filtered_orgs.csv", "w", encoding="utf-8")
    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    for row in csv_reader:
        name = row.get("name")
        answer = get_answer(name)
        print(name, answer)

        if answer == "YES":
            csv_writer.writerow(row)

    in_f.close()
    out_f.close()


if __name__ == "__main__":
    main()
```

To make things a little faster, we reject or approve some of the entries based
on conclusive-enough substrings in the institution name. We only consult GPT-3
for the entries that remained.

Let us take a look into another example. Hurricane Electric provides a small
[web app](https://bgp.he.net/) to look up autonomous systems and IP ranges gives a company name.
This might be of interest for bug bounty purposes. However, the result data
is somewhat hairy. For example, searching for "Tesla Motors Inc." also gives
results related to "AD Aerodrom 'Nikola Tesla' Beograd", "Tesla Comunicaciones SRL"
and so on. Clearly the result set needs some filtering before it can be used
for further work.

[TODO: screenshot]

Like in our previous example, GPT-3 can be used to implement the heuristic.
A preliminary prompt would something like:

```
Answer YES if "Tesla Motors, Inc." and "Tesla Comunicaciones SRL" are the same company. Answer NO otherwise.
```

Like in previous example, the code would perform string interpolation to generate
a prompt for each entry in the result list.

Since we're doing heuristics here we should not expect the answer to be 100%
correct for each and every entry. Neither GPT-3 nor human intelligence can guarrantee
that. However if we have a lot of fuzzy data to go through GPT-3 can do it far faster
than people.

