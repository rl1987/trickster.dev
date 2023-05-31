+++
author = "rl1987"
title = "Prompting the LLM is no substitute for knowledge work"
date = "2023-05-31"
tags = ["ai"]
+++

Artificial intelligence, especially large language models such as ChatGPT are all
the rage now. ChatGPT has the distinction of being the fastest growing product
in the history of technology - it reached the first one million users in just a
few days. As such, it is the talk of the global village now. There is no shortage
of overly excited people posting their takes on how it will change the world 
for the better and what you should be doing right now to benefit from that. 
On the other hand, some are worried about ending up jobless with no place to go 
in the dystopian reality of 2029. Who are right? We cannot tell without knowing
the future, but I don't think any of the extreme predictions are reasonable. In
many cases they are not even intellectually honest (more on that later). I am 
not saying that LLMs are not a big deal. Building the computational machinery
to make human language tractable by software has long been a Holy Grail of 
research fields such as computational linguistics and natural language 
processing. Making that work is a great technical achievement that should not
be taken lightly. However I don't believe in black-and-white thinking. I don't
even believe in grayscale thinking. There is way too much complexity in the
current social, technical, political and cultural realities to be sufficiently
captured by mere notion of "goodness".

Can the LLMs make you jobless by text-generating your job position away? Such
question was posed to sci-fi author Cory Doctorow in 2020, during the Remote
Chaos Experience conference. Back then, ChatGPT was not released, but GPT-3 was
already available. His response was that only people who have very boring, 
terrible jobs should be worried about GPT-3. That answer should not have been
surprising to people who actually played a bit with GPT-3. It can certainly be 
guided into generating text that compares to what a human could write, but if
left unattended it can easily go off the rails and start generating complete
garbage.

ChatGPT (a.k.a. GPT-3.5-turbo) is not exactly immune to generating nonsense 
either. Let us do a quick experiment with [aichat](https://github.com/sigoden/aichat) -
one of the OpenAI API clients.

```
$ aichat
Welcome to aichat 0.8.0
Type ".help" for more information.
〉.model gpt-3.5-turbo

〉.prompt What online courses could be taken to learn JavaScript deobfuscation?

Ｐ〉
Ｐ〉;
There are a few online courses that could help you learn JavaScript deobfuscation:

1. "Advanced JavaScript Concepts" by Udemy: This course covers advanced JavaScript topics, including deobfuscation techniques.

2. "JavaScript Deobfuscation and Malware Analysis" by Pluralsight: This course focuses specifically on JavaScript deobfuscation and how to analyze malware that uses obfuscated JavaScript.

3. "Practical Malware Analysis" by the Malware Unicorn: This course covers malware analysis techniques, including how to deobfuscate JavaScript used in malware.

4. "JavaScript Deobfuscation for Web Developers" by Packt: This course focuses on deobfuscation techniques for JavaScript used in web development.

5. "Reverse Engineering Malware" by OpenSecurityTraining: This course covers a variety of reverse engineering techniques, including deobfuscating JavaScript used in malware.
```

We can see a factually wrong output here. Courses 2 and 4 don't exist. Courses 
1, 3 and 5 do exist, but they are not very relevant to JS deobfuscation. So we
got an answer that is factually wrong, but written in a very confident wording.
We got a problem of trust here. If we rely on ChatGPT to produce a text that
is factually correct we cannot accept the possibility of some percentage of
output being simply wrong. Thus it cannot be trusted to do all the work for us -
to benefit from ChatGPT and similar systems, we have to work _with them_ to
achieve a desired result. That includes checking the generated text for factual
correctness.

But we're talking fairly obscure, niche stuff here. In fact, I kind of did it
on purpose to demonstrate a major failure mode of LLMs. But what if ChatGPT was used
to help with something more relevant to general society, such as preparing a
lawsuit against an airline? One Steven Schwartz, an attorney with some three
decades of experience, was using ChatGPT for (scary quotes) "research" when 
preparing paperwork to sue a certain airline over an injury allegedly sustained
by a customer. That went horribly, scandalously wrong. Like in our quick
experiment above, ChatGPT hallucinated references to prior legal cases and
court decisions that simply did not happen. Schwartz himself got in trouble
for submitting legal paperwork with false data and the story made it's rounds
across the press outlets. You know you really fuck up your work when your oopsie
[makes it's way to New York Times](https://web.archive.org/web/20230530005520/https://www.nytimes.com/2023/05/27/nyregion/avianca-airline-lawsuit-chatgpt.html).

GPT-4 is more advanced than ChatGPT, but is susceptible to hallucinating stuff
as well (just ask the same question about deobfuscation courses). But what if 
there was a sufficiently advanced LLM that did not hallucinate and only 
generated text that was factually correct (unless specifically instructed to
write fiction)? Realistically that is not even possible, as it relies on
perfectly correct information being sourced for training of such model. However,
for the sake of argument, let us assume that there is such a system running. If
we have a perfect knowledge machine, can we use it to replace a human work?
Well, the thing is, we still need to tell it what to do. Even a perfect LLM is
GIGO: garbage in, garbage out. When it comes to non-trivial things (such as
developing large software systems), describing them in sufficient detail in a
way that captures all nuances and edge cases is quite difficult type of work. 
This can be seen in real world software projects, especially when they involve
non-technical stakeholders. It's naive for manager or entrepreneur to assume that
soon enough they will be able to get rid of those pesky developers, as they will
just tell a chatbot what code it should write. Quite likely the activity
of getting an LLM to do things (generate or edit blog post, develop code,
write marketing copy, etc.) will be new kind of work - prompt design/engineering.

Sure, you can use ChatGPT or GPT-4 to assist in software development work - 
generate code snippets, do some refactoring, get advice on improvements and so
on. But at the end of the day LLM is merely a tool AI. It does not have it's
own judgement, values or will that human possesses. Even worse, it is debatable
to what extent it _knows_ things, as the fundamental way it operates is
predicting what text should be generated next. It is the user that drives the
LLM who is supposed to know what they are doing. For example, ChatGPT may
generate a code snippet that is mostly correct in the light of provided 
requirements. It's up to the user to make it completely correct. Now, what if 
the user was a non-technical entrepreneur? How well would it work out for them?

By amplifying, not replacing, human effort LLMs can be said to provide a 
leverage. As the leverage increases, the value of sound judgement increases as
well. When it's easier to turn your decision into a reality, the quality of 
these decisions starts to matter a whole lot more.

But the AI hype wave is in full swing now. There's all kinds of social media
influencers and content creators telling you to do this or that to benefit
from the AI revolution to get rich. A lot of these people are digital snake oil
merchants who are jumping from trend to trend. Some propose completely silly,
unrealistic money making schemes just to get your attention. It's all part of
make-money-online content creation playbook. The truth is, these people mostly
don't make money from the thing they promote. Instead, they make money by 
promoting the thing they are promoting through ad revenue (esp. on Youtube), 
affiliate offers and their own info products. During the Bitcoin bull
run and NFT craze there was no shortage of characters talking loudly about how
you have to "invest" into this or that thingy on the blockchain. I suspect the
vast majority of them could not tell the difference between Base64 and AES. Now
you have great deal of people talking the same way about AI (mostly LLMs). How
many of these newly minted "AI experts" even know what the fuck a linear
regression is?

That is not to say that nobody ever gets rich doing gold rush. Some people swiftly
grab a transient opportunity and milk it for what it's worth. Others do some
equivalent of selling shovels and pick axes during the Wild West period. Some
simply gamble and happen to be winning. Speaking about LLM-based SaaS apps 
specifically, there's a certain problem. If you have some SaaS app that has
OpenAI API as a hard, critical dependency that means your SaaS business is 
essentially at the mercy of OpenAI. Right now, there are some important 
questions that pertain to generative AI. What exactly should and
should not it be allowed to generate? If some data is scraped to train 
the LLM what happens to related copyrights? What will be done against 
gray hat and black hat usage of LLMs, such as fake product review generation, 
harassment, phishing, influence operations? Depending on how things play
out, your entire SaaS business could die overnight by being cut off from API
access as it may turn out not be kosher anymore in the light of new legislation
or newly introduced corporate policy. Remember that Twitter API was free and open
in the early years. There were many companion apps for Twitter users built on
that API - unofficial clients, automation tools and the like. But over time
Twitter introduced many restrictions into the official API and most of them
had to die. This is something that indie hackers who rely on the goodwill
and interest alignment from OpenAI (or Anthropic, or Google...) should keep in 
mind. 

Furthermore, using an LLM that you don't self-host can be problematic from data
security and privacy perspective, as you are literally telling some other
entity the specifics of your work. There was already a scandal of Samsung
employees leaking trade secrets to OpenAI by using ChatGPT to help with their
regularly scheduled programming. That is the reason why the usage of
ChatGPT is explicitly banned in some corporations. A fundamental problem with
information society is that many things are data driven, but we mostly don't have
any control how data about people and companies is processed, stored, transferred. 
Information functions by being always in motion and largely has a life of it's 
own. If you tell your trade secrets to ChatGPT, can you trust ChatGPT not to 
tell them to your competitor?

Times are difficult now. We're only 3.5 years into 2020s and so far we had 
a global pandemic, energy crisis, murderous Taliban psychos winning the 
Afghan war, a new major conflict in Ukraine, inflation wave causing cost of
living crisis, tech downturn and banks failing. But even now I advice everyone 
to keep their heads cool. You probably cannot prompt your way into quick wealth, 
especially if you're about average on coming up with LLM prompts. In economics
there's a concept of alpha. It's a number quantifying how well an asset
outperforms the overall market. Dumb luck aside, to achieve exceptional results 
that greatly outperform most of the competition one must posses or do something 
exceptional. The problem with doing easy things (e.g. generating basic ad copy) 
is that they don't stay easy for very long in a competitive environment. It is 
also that ChatGPT, GPT-4 and other AI systems will make everyone jobless 
due to considerations I have discussed. These systems are merely tools subservient to
a human will and there will be a need for people working with them. Perhaps
the daily reality of many occupations will change, perhaps some people will need
to learn how to do something else, but I don't except the fully AI-driven world
to happen anytime soon.

We cannot know what the future will be like. In a sense, we don't even have a
(predictable) future when things are so crazy, volatile and fucked up. All we 
can do is hedge our bets and roll the dice.

Keep calm and seek your alpha.
