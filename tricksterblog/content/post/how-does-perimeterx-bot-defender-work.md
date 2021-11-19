+++
author = "rl1987"
title = "How does PerimeterX Bot Defender work"
date = "2021-11-22"
draft = true
tags = ["scraping", "anti-bot", "security"]
+++

PerimeterX is a prominent vendor of anti-bot technology. It is used by portals such as Zillow, Crunchbase, StockX and many others.

WRITEME: some more introduction

PerimeterX has registered the following US patents:

* [US 10,708,287B2](https://patents.google.com/patent/US20190173900A1/en?assignee=perimeterx&oq=perimeterx) - ANALYZING CLIENT APPLICATION BEHAVIOR TO DETECT ANOMALIES AND PREVENT ACCESS
* [US 10,951,627B2](https://patents.google.com/patent/US20180109540A1/en?assignee=perimeterx&oq=perimeterx) - SECURING ORDERED RESOURCE ACCESS
* [US 2021/064685A1](https://patents.google.com/patent/US20210064685A1/en?assignee=perimeterx&oq=perimeterx) - IDENTIFYING A SCRIPT THAT ORIGINATES SYNCHRONOUS AND ASYNCHRONOUS ACTIONS (pending application)

Let us take a look into these patents to discover key working principles of PerimeterX bot mitigation technology.

US 10,708,287B2 
---------------

The following diagram visualises the overall flow of PerimeterX bot detection system from the client perspective:

https://patentimages.storage.googleapis.com/a1/62/94/7dc9c2325f3243/US20190173900A1-20190606-D00005.png

In this context, "Application Server" is a web server hosting web application. "Client Device" is computer or 
smartphone accessing the site being protected by PerimeterX. "Security Verification System" is PerimeterX
backend. Note that Application Server is allowed to be multi-server system if CDN is used or if web application
is consisting of multiple subsystems. There's another patent that extends the technique discussed herein to enable
it to be used across multiple servers. 

First step of the flow is end user trying to load a page. When PerimeterX Bot Defender is deployed, a JavaScript code
from PerimeterX is being included in the HTML document being downloaded. This code is called Security Loader. As
the browser is rendering the page, Security Loader downloads and executes further JavaScript code called Security Module.
It is retrieved from PerimeterX backend with some parameters on what tests to run in the browser. The purpose of
Security Module is to look for things that may be useful as signal for automation and to check if browsers JavaScript
environment isn't anomalous in some ways. Things that Security Module may check includes:

* JavaScript engine
* HTML elements
* Outbound links
* Cookies
* User input behaviour and timing (mouse movement, clicks, etc.)
* Local storage
* Browser history

When tests are finished, Security Module reports all of this back to Security Verification System, which enriches 
and processes the data. Enrichment involves appending extra fields on IP address, geolocation, User-Agent header and so on.
PerimeterX gathers the data and trains machine learning models to establish baseline for 
normal activity. Security score is computed based on how close test results are to the baseline. Furthermore, some anomalies
may detected at this stage, such as mismatching number of HTML element, mismatching User-Agent header to objects in JS 
environment and so on. For instance, if browser claims to be Google Chrome in the User-Agent header, but does not have
`window.chrome` object it may be the kind of anomaly that causes PerimeterX to block a browser from further interaction
with web application being protected. 

At this point, if security score is high enough PerimeterX may allow the browser to access the resources (with some further
monitoring during the client session). However, the analysis may not be conclusive, which may prompt further tests that may
involve actions from the use (e.g. CAPTCHA solving). Based on the results of these additional tests, PerimeterX may allow
or deny further access to the web app.

When PerimeterX allows an access, it issues Security Token which is cryptographically signed object that contains security score
with information on passed and failed tests. During the client session, Security Module continues to run and provides information
on client side activity to PerimeterX. This enabled further training of ML models and also updates security score if needed.
This also enables PerimeterX to cut off the client session if anomalous activities are detected some time after the initial tests
were done. Furthermore, Security Token is provided to Application Server that might deny the access based on security score.
This is done through Security Enforcement Module that developers are integrating with Application Server.

Note that PerimeterX can also cover mobile apps. When it is integrated with mobile app systems, Security Loader is not present,
but Security Module is integrated in the form of native mobile SDK. Everything else works the same.

US 10,951,627B2 
---------------

Web applications protected by PerimeterX may be loading some content (images, data, etc.) from servers other than the primary
web server. Entities deploying PerimeterX may want these requests to be covered by anti-botting countermeasures as well. This
patent extends the idea from previous one to address this requirement. 

The idea here is that primary web server issues something called Risk Token that has to be provided to secondary servers to
authorize resource access (e.g. as HTTP cookie or URL parameter value). This token is generated from parameters describing 
the request with client side identifiers and expiration date. It may also include client session ID or some further information. 
To prevent forging, token is cryptographically signed by using HMAC or other cryptographic technique.

Resource servers are able to perform verification of the provided token and deny access to the resources if verification fails.

US 2021/064685A1 
----------------

As discussed before, PerimeterX Security Module perform client side activity monitoring to keep watching for anomalous behaviour
once access has been granted. This patent application is about implementing API call monitoring in frontent JavaScript
environment. PerimeterX code overwrites JS functions that it wants to monitor with wrapper code that takes note of API call 
and calls the original function. In case of async actions, callbacks are overwritten in the same way. This lets identification 
of the exact JS script that called a given JS function.  The patent application provides a following example code for 
monitoring calls to `sync()` function:

```javascript
let initiatorScript = null; 
function getCurentScript(){
  if(document.curentScript) {
    return document.curentScript;
  } else {
    // if there no script that is curently being processed - 
    // /then document.curentScript is nul 
    return initiatorScript;
  } 
}
// hold a reference to the original sync API function 
const realSyncAPI = window['sync']; 
window['sync'] = function(url) {
  // use 'document.curentScript' to record whichs script 
  // initiated the call to sync() 
  capture('sync',getCurentScript()); /
  // now cal the original sync API to perform its natural
  // behavior in the browser as it was being overwriten 
  return realSyncAPI(url);
};
```

If extra JS is running in the browser (because of e.g. XSS attack or automation), PerimeterX is able to detect it through this
kind of monitoring.
