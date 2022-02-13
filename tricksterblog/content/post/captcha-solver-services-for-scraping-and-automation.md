+++
author = "rl1987"
title = "CAPTCHA solver services for scraping and automation"
date = "2022-02-13"
tags = ["web-scraping", "automation", "python", "captcha"]
+++

CAPTCHA (Completely Automated Public Turing test to tell Computers and Humans Apart) is a type of automation
countermeasure. It is based on challenge-response approach that involves asking user to perform an action
that only human is supposed to be able to perform, such as:

* Writing down characters or words from distorted image.
* Performing based mathematical operations that are presented in distorted image.
* Recognizing specific object within a set of images, possibly with distortion.
* Solving simple puzzles.
* Hearing a word on audio and writing it down.

Once the user passes the challenge, access is granted. 

CAPTCHAs can be used for security purposes (e.g. to prevent password bruteforcing) or to fight any kind of automation
(scraping, auto-purchasing eCommerce products, etc.). 

One prominent example of CAPTCHA you have seen on the web is [Google reCaptcha version 2](https://developers.google.com/recaptcha/docs/display). 
It works by having the user to tick a checkbox to indicate that they are not a robot. Depending on risk assessment that is
running in background, it may also ask the user to perform a basic image recognition task. For example, they may be asked
to make images with cars. Once user completes the task, client side JS SDK encodes the response and submits it to Google API.
Google API gives a token in return. This token is then submitted to the website via a hidden input in a form or via API
parameter. Website then has to verify it on server side with Google. Google also allows web developers to integrate reCaptcha
in invisible mode. In this case, only the most suspicious traffic is asked to integrate with the CAPTCHA.

Another prominent CAPTCHA service is [hCaptcha](https://docs.hcaptcha.com/). It is meant to be a drop-in replacement for 
reCaptcha that does not belong to Google and has a different business model. It works pretty much the same way as reCaptcha, 
but may also allow including users IP address into API request as additional security measure.

As developer working in web scraping and automation, you should try to avoid the situation of your code having to directly
face CAPTCHAs. For example, you may be able to use proxy pool to avoid the site or app asking for
CAPTCHA solution due to detecting excessive requests from a single IP address. Using CAPTCHA solving services introduces 
significant delays into your code that can be avoided in many cases.

With that being said, let us discuss CAPTCHA solving services that you may need to use in some cases. The foundational idea
behind most of the CAPTCHA solving services is that if CAPTCHA solving requires humans, then it can be outsourced by giving
the work to cheap clickworkers somewhere far away. Although AI models can solve some CAPTCHAs in some cases, the big picture
of CAPTCHA solving services is that cheap labour is used for this purpose most of the time.

You typically interface to CAPTCHA solvers by using their REST API. In somes cases a client library will be available to make
this easier.

Let us try using [Anti-captcha](https://anti-captcha.com/) service through the [official Python module](https://github.com/AdminAnticaptcha/anticaptcha-python).

To solve a basic image CAPTCHA, you would post a [task](https://anti-captcha.com/apidoc/task-types/ImageToTextTask) 
Anti-captcha API containing the Base64-encoded image data. Then you would wait for task to be completed. If you are directly
talking to REST API, you would need to poll it every few seconds for status report. If you are using a client library that
would be done automatically. Once solution is available, `status` in API response would be `ready` and `solution` would contain
the text in the image. 

However, image captchas are dying and it's more interesting to solve reCaptcha. To solve reCaptcha, we need to get a site key.
This is unique ID that is used for identifying a site within Google systems for integration purposes. It can be found in API
requests via Chrome DevTools. Some sites also have it somewhere in the HTML document, which means you can scrape it from there.
Once we have site key we can create [`RecaptchaV2TaskProxyless`](https://anti-captcha.com/apidoc/task-types/RecaptchaV2TaskProxyless) via 
Anti-Captcha API. We need to include page URL and site key in the API request. Some seconds later we will receive a reCaptcha
token that we can submit to the site as if we have solved the CAPTCHA ourselves manually.

The following code exemplifies solving reCaptcha v2 with Anti-Captcha service:

```python
#!/usr/bin/python3

import requests
from lxml import html

from anticaptchaofficial.recaptchav2proxyless import *

def main():
    resp1 = requests.get("https://www.google.com/recaptcha/api2/demo")

    tree = html.fromstring(resp1.text)

    sitekey = tree.xpath('//div[@id="recaptcha-demo"]/@data-sitekey')[0]

    solver = recaptchaV2Proxyless()
    solver.set_verbose(1)
    solver.set_key("[REDACTED]")
    solver.set_website_url(resp1.url)
    solver.set_website_key(sitekey)

    g_response = solver.solve_and_return_solution()

    assert g_response != 0

    form_data = {
        'g-recaptcha-response': g_response
    }

    resp2 = requests.post('https://www.google.com/recaptcha/api2/demo', data=form_data)

    print(resp2.text)


if __name__ == "__main__":
    main()
    
```

To solve hCaptcha, you would need to proceed in more or less the same way, but depending on IP address check being used you
would need to submit either [`HCaptchaTask`](https://anti-captcha.com/apidoc/task-types/HCaptchaTask) with IP and credentials
of your proxy or [`HCaptchaTaskProxyless`](https://anti-captcha.com/apidoc/task-types/HCaptchaTaskProxyless) that is meant
to be used when IP check is disabled.

Some other proxy solving services you may want to check out are:

* [2captcha](https://2captcha.com/)
* [DeathByCaptcha](https://www.deathbycaptcha.com/)
* [BestCaptchaSolver](https://bestcaptchasolver.com/)
* [AZcaptcha](https://azcaptcha.com/)

