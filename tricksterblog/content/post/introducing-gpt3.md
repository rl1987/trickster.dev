+++
author = "rl1987"
title = "Introducing GPT-3: Playground and API"
date = "2021-11-26"
tags = ["ai", "gpt3", "automation"]
+++

GPT-3 is a large scale natural language processing system based on deep learning and developer by 
OpenAI. It is now generally available for developers and curious people.

GPT-3 is the kind of AI that works exclusively on text. Text is both input and output for GPT-3. 
One can provide questions and instructions in plain English and receive fairly coherent responses. However, GPT-3 is not:

* HAL from _2001: Space Odyssey_
* Project 2501 from _Ghost In the Shell_
* T-800 from _The Terminator_
* AM from _I Have No Mouth And I Must Scream_

What GPT-3 is a tool AI (as opposed to agent AI). Given textual input (prompt) it gives an output based on both the input 
and all the datasets it was trained with. The quality of output is strongly dependant on the quality of input. Prompt Engineering
(also known as Prompt Design or Prompt Programming) is the practice of crafting inputs for GPT-3 to acquire an output of 
sufficiently high quality. Some say that this will be a new kind of computer programming and that crafting prompts for systems like
GPT-3 will become an established occupation in the future.

The simplest way to experiment with GPT-3 is to use the [Playground](https://beta.openai.com/playground). You enter your
prompt into the big text field and press the green button to generate an output. Let us go through various
configuration options on the right-hand side.

The engine is the sub-model of GPT-3. There are 4 base engines available (ordered from most to least powerful):

1. `davinci`
2. `curie`
3. `babbage`
4. `ada`

Using a more powerful engine cost more time and credits than using a less powerful one. Base engines are meant for general-purpose
tasks. 

Instruct engines are made to understand and follow instructions. At this point, there are 3 of them:

1. `davinci-instruct-beta-v3`
2. `davinci-instruct-beta`
3. `curie-instruct-beta`

The temperature slider controls how random and creative the responses will be. For tasks and questions that have very clear, definite
answers we want to set temperature to 0. For maximum creativity, we want it to be 1.

Response length is measured in tokens (one token is approx. 4 English letters). 

Stop sequences are up to 4 strings that will terminate the generation of output.

Top P is a lot like temperature but defined in terms of token probabilities. If we set it to 0.1 it will consider only tokens
that are within 10% of probability mass.

Frequency penalty let us make repetitions less like by penalizing tokens based on their frequency in the already generated text.

Presence penalty is similar to frequencey penalty, but it penalizes tokens based on their presence (not frequency) in the text
generated so far.

"Best of" option will make the model generates a given amount of outputs and will choose the best one out of them.

If we wanted, we can enable Playground to visualize probabilities of tokens in the generated text.

"Inject start text" and "Inject restart text" deal with prompts that will appear when GPT-3 is used as chatbot - see [Chat](https://beta.openai.com/playground/p/default-chat) example.

Let us use default settings to play with the model a little.

> **Who is Mark Zuckerberg?**
>
> Mark Elliot Zuckerberg is an American computer programmer and Internet entrepreneur. He is best known as one of five co-founders of the social networking site Facebook.
>
> Zuckerberg launched Facebook from his Harvard University dormitory room on February 4, 2004. He was assisted by his college roommates and fellow Harvard students Eduardo Saverin, Andrew McCollum, Dustin Moskovitz, and Chris Hughes. The group then introduced Facebook to other college campuses. Facebook expanded rapidly, reaching one billion users by 2012.
> 
> Mark Zuckerberg is also the founder of fwd.us, a political action committee which he launched in 2013. He was ranked number one on the Forbes list of ‘The World’s Most Powerful People’ in the same year.
>
> Mark Zuckerberg has won numerous awards for his work at Facebook, including Time Person of the Year in 2010, and the Marconi Prize in 2014. He has been included in the Time 100 most influential people in the world list from 2010 to 2015.
>
> In 2012, Zuckerberg was ranked number one on the Forbes list of ‘The World’s Billionaires’, after his estimated net worth rose to US$17.5 billion.
>
> In 2014, Zuckerberg was ranked the 5th richest person in the world, with an estimated net worth of US$35.3 billion.
>
> Mark Zuckerberg is married to Priscilla Chan, who is a dentist. They met at a frat party at Harvard, and married in 2012. They have a daughter named Maxima Chan Zuckerberg

That not too bad, huh?

Let's try to check some logical reasoning (or lack thereof).

> **If Epimenides is from Crete and all Cretans are liars, is Epimenides a liar?**
>
> Answer: Yes.
>
> Why?
>
> Answer: Because all Cretans are liars (Epimenides is from Crete)
>
> This is why the argument is valid. The conclusion follows logically from the premises.
>
> The conclusion follows logically from the premises.
>
> This is why the

It generated this much before warning me about unsafe content, but essentially gave a correct answer. I guess asking the AI about liars can lead to some controversial answers.

Let's push this angle of questioning a bit further and introduce what Douglas Hofstadter calls a Strange Loop.

> **If Epimenides is from Crete says that all Cretans are liars, is Epimenides lying?**
>
> If Epimenides is from Crete, is it false that Epimenides is from Crete?
> 
> If Epimenides is from Crete, is Epimenides from Crete?
>
> If Epimenides is from Crete, is it true that Epimenides is from Crete?
>
> For example, the following arguments are valid, where “Epimenides is from Crete” is a sentence that is true if and only if Epimenides is from Crete:
>
> Epimenides is from Crete.
>
> Epimenides is from Crete.
>
> Epimenides is from Crete.
>
> Epimenides is from Crete.
>
> Epimenides is from Crete.
>
> Epimenides is from Crete.
>
> Epimenides is from Crete.
>
> Epimenides is from Crete.
>
> Epimenides is from Crete.
>
> Epimenides is from Crete.

Well, that went nowhere real quick.

Let's try doing something a bit more practical by switching to `davinci-instruct-beta-v3` engine and asking it the following:

> **Write a Facebook ad copy for handheld holographic projector**
> 
> Bring your favorite movies and games to life with the world's first handheld holographic projector! The perfect entertainment for any occasion, the projector features advanced optics that allow you to view holograms in stunning detail.

I'm no copywriter and this is at the very least superior to the ad copy that I could write.

What about something more technical? Can it generate some code?

> **Write a Python script that takes a list of integers via standard input and prints a sum of them**
>
> def sum(nums):
> 
> total = 0
>
> for i in nums:
>
> total = total + i
>
> return total

Well, it seems it won't be replacing software developers any time soon. Not only it's formatted all wrong, but this is merely a Python function, not the entire program.

Speaking of Python programming, GPT-3 provides a REST API with several client libraries, Python being one of them. In fact, if we press View Code button in the playground, we
can get a Python snippet that reproduces API call with the settings we have in the Playground:

```python
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

response = openai.Completion.create(
  engine="davinci-instruct-beta-v3",
  prompt="Write a Python script that takes a list of integers via standard input and prints a sum of them",
  temperature=0.7,
  max_tokens=64,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)
```

To read more about GPT-3 API, take a look at official documentation at: https://beta.openai.com/docs/introduction

`openai` Python module includes a CLI tool that we can use to interact with GPT-3, provided that we have `OPENAI_API_KEY` environment variable set to our API key:

```
$ openai api engines.list
[organization=user-fpeechvtioklyst4iyrcy5c2] {
  "data": [
    {
      "created": null,
      "id": "ada",
      "max_replicas": null,
      "object": "engine",
      "owner": "openai",
      "permissions": null,
      "ready": true,
      "ready_replicas": null,
      "replicas": null
    },
    {
      "created": null,
      "id": "babbage",
      "max_replicas": null,
      "object": "engine",
      "owner": "openai",
      "permissions": null,
      "ready": true,
      "ready_replicas": null,
      "replicas": null
    },
    {
      "created": null,
      "id": "curie",
      "max_replicas": null,
      "object": "engine",
      "owner": "openai",
      "permissions": null,
      "ready": true,
      "ready_replicas": null,
      "replicas": null
    },
    {
      "created": null,
      "id": "curie-instruct-beta",
      "max_replicas": null,
      "object": "engine",
      "owner": "openai",
      "permissions": null,
      "ready": true,
      "ready_replicas": null,
      "replicas": null
    },
    {
      "created": null,
      "id": "davinci",
      "max_replicas": null,
      "object": "engine",
      "owner": "openai",
      "permissions": null,
      "ready": true,
      "ready_replicas": null,
      "replicas": null
    },
    {
      "created": null,
      "id": "davinci-instruct-beta",
      "max_replicas": null,
      "object": "engine",
      "owner": "openai",
      "permissions": null,
      "ready": true,
      "ready_replicas": null,
      "replicas": null
    },
    {
      "created": null,
      "id": "davinci-instruct-beta-v3",
      "max_replicas": null,
      "object": "engine",
      "owner": "openai",
      "permissions": null,
      "ready": true,
      "ready_replicas": null,
      "replicas": null
    }
  ],
  "object": "list"
}
```

