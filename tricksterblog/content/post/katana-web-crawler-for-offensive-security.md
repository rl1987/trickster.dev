+++
author = "rl1987"
title = "Katana: web crawler for offensive security"
date = "2024-08-31"
tags = ["security", "web-scraping"]
draft = true
+++

[Katana](https://github.com/projectdiscovery/katana) is CLI tool and Go library
for automatically traversing (crawling) across all pages of given website(s) to
map them out. It can work in two main modes - requests-based and through browser
automation (headful or headless). To allow for discovery of API endpoints it 
can optionally do JavaScript parsing even when running in requests-based mode.
Furthermore, Katana can do passive crawling by leveraging pre-crawled data from
Internet Archive Wayback Machine, CommonCrawl and Alien Vault OTX.
Since mapping out site pages and APIs is useful for security research activities
(e.g bug bounty hunting) Katana is designed to fit into larger automation 
workflows, esp. when used together with other tooling from Project Discovery.

If we simply want to see a list of pages a site has we only have to pass the 
site URL via `-u` parameter:

```
$ katana -u https://public-firing-range.appspot.com/

   __        __                
  / /_____ _/ /____ ____  ___ _
 /  '_/ _  / __/ _  / _ \/ _  /
/_/\_\\_,_/\__/\_,_/_//_/\_,_/							 

		projectdiscovery.io

[INF] Current katana version v1.1.0 (latest)
[INF] Started standard crawling for => https://public-firing-range.appspot.com/
https://public-firing-range.appspot.com/
https://public-firing-range.appspot.com/vulnerablelibraries/index.html
https://public-firing-range.appspot.com/stricttransportsecurity/index.html
https://public-firing-range.appspot.com/urldom/index.html
https://public-firing-range.appspot.com/reverseclickjacking/
https://public-firing-range.appspot.com/reflected/index.html
https://public-firing-range.appspot.com/mixedcontent/index.html
https://public-firing-range.appspot.com/tags/index.html
https://public-firing-range.appspot.com/redirect/index.html
https://public-firing-range.appspot.com/remoteinclude/index.html
https://public-firing-range.appspot.com/insecurethirdpartyscripts/index.html
https://public-firing-range.appspot.com/leakedcookie/index.html
https://public-firing-range.appspot.com/flashinjection/index.html
https://public-firing-range.appspot.com/vulnerablelibraries/jquery.html
...
```

But now we don't see status codes and we're not even sure if all of these pages
load properly. We can use `-mdc` argument with Project Discovery DSL snippet
to filter out only responses with status code 200:

```
$ katana -u https://public-firing-range.appspot.com/ -mdc 'status_code == 200' 
```

We can use this tool to store responses in case you want to separate web 
crawling from HTTP parsing:

```
$ katana -u https://books.toscrape.com/ -store-response
```

This decouples former from the latter so that you can download all the pages
once and then work on code that parses the HTML documents. The above command
creates a new directory named `katana_responses` with an index.txt file listing
requests, status codes and relative file paths:

```
$ head index.txt 
katana_response/books.toscrape.com/3060d727707e12334c7134afe04df480af3f0fdf.txt https://books.toscrape.com/ (200 OK)
katana_response/books.toscrape.com/f77b190299d9ad01298054c2b1ce13f35765e4d1.txt https://books.toscrape.com/static/oscar/js/bootstrap-datetimepicker/locales/bootstrap-datetimepicker.all.js (200 OK)
katana_response/books.toscrape.com/9e4c7d8e5630912730d1194fec599ec3f5f8580e.txt https://books.toscrape.com/static/oscar/js/bootstrap-datetimepicker/bootstrap-datetimepicker.js (200 OK)
katana_response/books.toscrape.com/7fdd4edbfcbe5d86df9904b18b6747e7cf7f0efa.txt https://books.toscrape.com/static/oscar/js/oscar/ui.js (200 OK)
katana_response/books.toscrape.com/cd148dbefc26230ec0d29104eb0408ae640720d2.txt https://books.toscrape.com/static/oscar/js/bootstrap3/bootstrap.min.js (200 OK)
katana_response/books.toscrape.com/0eb507686604bb3002bdf01dc8d1b917c7352867.txt https://books.toscrape.com/static/oscar/css/datetimepicker.css (200 OK)
katana_response/books.toscrape.com/0a63ac4de25fb4ba06a76137240cc663a716b506.txt https://books.toscrape.com/static/oscar/js/bootstrap-datetimepicker/bootstrap-datetimepicker.css (200 OK)
katana_response/books.toscrape.com/a2652354fa625fb0f225b7cd87f035f8f6d6af2c.txt https://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html (200 OK)
katana_response/books.toscrape.com/bf2072cbc394277fe024f4992dde7a498b7d6a9f.txt https://books.toscrape.com/catalogue/libertarianism-for-beginners_982/index.html (200 OK)
katana_response/books.toscrape.com/e4f9cda62c7f551a9e54439e5ed27f6e3306902a.txt https://books.toscrape.com/catalogue/mesaerion-the-best-science-fiction-stories-1800-1849_983/index.html (200 OK)
```

Each of the page snapshot files retain original URL, request/response headers and
response payload:

```
$ head -n 50 books.toscrape.com/f77b190299d9ad01298054c2b1ce13f35765e4d1.txt 
https://books.toscrape.com/static/oscar/js/bootstrap-datetimepicker/locales/bootstrap-datetimepicker.all.js


GET /static/oscar/js/bootstrap-datetimepicker/locales/bootstrap-datetimepicker.all.js HTTP/1.1
Host: books.toscrape.com
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36
Accept-Encoding: gzip



HTTP/1.1 200 OK
Content-Length: 31995
Accept-Ranges: bytes
Connection: keep-alive
Content-Type: application/javascript
Date: Tue, 20 Aug 2024 09:17:54 GMT
Etag: "63e40de9-7cfb"
Last-Modified: Wed, 08 Feb 2023 21:02:33 GMT
Strict-Transport-Security: max-age=0; includeSubDomains; preload

/**
* Arabic translation for bootstrap-datetimepicker
* Ala' Mohammad <amohammad@birzeit.ecu>
*/
;(function($){
	$.fn.datetimepicker.dates['ar'] = {
		days: ["الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"],
		daysShort: ["أحد", "اثنين", "ثلاثاء", "أربعاء", "خميس", "جمعة", "سبت", "أحد"],
		daysMin: ["أح", "إث", "ث", "أر", "خ", "ج", "س", "أح"],
		months: ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"],
		monthsShort: ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"],
		today: "هذا اليوم",
		suffix: [],
		meridiem: [],
		rtl: true
	};
}(jQuery));
/**
 * Bulgarian translation for bootstrap-datetimepicker
 * Apostol Apostolov <apostol.s.apostolov@gmail.com>
 */
;(function($){
	$.fn.datetimepicker.dates['bg'] = {
		days: ["Неделя", "Понеделник", "Вторник", "Сряда", "Четвъртък", "Петък", "Събота", "Неделя"],
		daysShort: ["Нед", "Пон", "Вто", "Сря", "Чет", "Пет", "Съб", "Нед"],
		daysMin: ["Н", "П", "В", "С", "Ч", "П", "С", "Н"],
		months: ["Януари", "Февруари", "Март", "Април", "Май", "Юни", "Юли", "Август", "Септември", "Октомври", "Ноември", "Декември"],
		monthsShort: ["Ян", "Фев", "Мар", "Апр", "Май", "Юни", "Юли", "Авг", "Сеп", "Окт", "Ное", "Дек"],
		today: "днес",
		suffix: [],
```

