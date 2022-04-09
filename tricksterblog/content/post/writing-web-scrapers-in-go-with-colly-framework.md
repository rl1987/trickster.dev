+++
author = "rl1987"
title = "Writing web scrapers in Go with Colly framework"
date = "2022-04-09"
tags = ["web-scraping", "golang"]
+++

[Colly](http://go-colly.org/) is a web scraping framework for Go programming language. The
feature set of Colly largely overlaps with that of Scrapy framework from Python ecosystem:

* Built-in concurrency.
* Cookie handling.
* Caching of HTTP response data.
* Automatic heeding of robots.txt rules.
* Automatic throttling of outgoing traffic.

Furthermore, Colly supports distributed scraping out-of-the-box through a Redis-based task queue
and can be integrated with Google App Engine. This makes it a viable choice for large-scale
web scraping projects.

In a [previous post](introduction-to-scrapy-framework/) we have shown how to scrape
[books.toscrape.com](https://books.toscrape.com/) with Scrapy framework. We will develop
a similar scraper with Colly. The following assumes that you have a working and up-to-date 
Go development environment.

In a new project directory we run `go mod init` and `go get github.com/gocolly/colly`.
Then we create main.go file with Colly being imported as dependency:

```golang
package main

import (
	"fmt"

	"github.com/gocolly/colly"
)

func main() {
}
```

Let's get some crawling going. A central Colly object that we have to interact with is
called collector. It is similar to Scrapy spider. Therefore the
first thing we do in our `main()` function is instantiating it:

```golang
        c := colly.NewCollector(colly.AllowedDomains("books.toscrape.com"))
```

Now we have to register some callbacks that Colly will call during scraping. By providing
code that will react to various things that happen during scraping/crawling we will implement
our scraper in event-driven way. Events we can hook into include request being sent,
HTTP error being detected, response headers being received, entire HTTP response being
received, elements matching CSS selector being detected on HTML document and
elements matching XPath query being detected on HTML/XML document.

Let us start simple by printing an URL of each HTTP request just before it is sent to the
server:

```golang
	c.OnRequest(func(r *colly.Request) {
		fmt.Printf("Visiting %s...\n", r.URL.String())
	})
```

Also, let us have a similar callback to all HTTP requests that we receive:

```golang
	c.OnResponse(func(r *colly.Response) {
		fmt.Printf("Visited %s\n", r.Request.URL)
	})
```

These are good for debuggability, but implement no real functionality. Let us register a
callback for CSS selector that matches category links on right-hand pane and Next page
button on the bottom. Callback functions will merely extract the URL and generate a 
follow up request. We don't need to worry about URLs possibly being relative to the
current page - Colly will fix them for us.

```golang
	c.OnHTML("div.side_categories * > a", func(e *colly.HTMLElement) {
		e.Request.Visit(e.Attr("href"))
	})

	c.OnHTML("li.next > a", func(e *colly.HTMLElement) {
		e.Request.Visit(e.Attr("href"))
	})
```

This crawls the category lists, but we also need to go into product pages. Thus we register
one more callback based on XPath query that will match a product link on category pages:

```golang
	c.OnXML("//article[@class=\"product_pod\"]/h3/a", func(e *colly.XMLElement) {
		e.Request.Visit(e.Attr("href"))
	})
```

To activate Colly for crawling, we call `Visit()` method on collector after we have finished
setting everything up:

```golang
        c.Visit("https://books.toscrape.com")
```

The main.go file at this point looks as follows:

```golang
package main

import (
	"fmt"

	"github.com/gocolly/colly"
)

func main() {
	c := colly.NewCollector(colly.AllowedDomains("books.toscrape.com"))

	c.OnRequest(func(r *colly.Request) {
		fmt.Printf("Visiting %s...\n", r.URL.String())
	})

	c.OnHTML("div.side_categories * > a", func(e *colly.HTMLElement) {
		e.Request.Visit(e.Attr("href"))
	})

	c.OnHTML("li.next > a", func(e *colly.HTMLElement) {
		e.Request.Visit(e.Attr("href"))
	})

	c.OnXML("//article[@class=\"product_pod\"]/h3/a", func(e *colly.XMLElement) {
		e.Request.Visit(e.Attr("href"))
	})

	c.OnResponse(func(r *colly.Response) {
		fmt.Printf("Visited %s\n", r.Request.URL)
	})

	c.Visit("https://books.toscrape.com")
}
```

When we compile and run it we notice that crawling is performed without concurrency - just
a single page at a time. That's because we did not enable asynchronous mode. We fix it by
updating a call to `NewCollector` with one more argument:

```golang
        c := colly.NewCollector(colly.AllowedDomains("books.toscrape.com"), colly.Async(true))
```

We also need to call `Wait()` method on collector at the end. Otherwise, the code will quit immediately
without scraping anything.

Let us define a Go struct for the book data - this will be an equivalent for Scrapy item
class:

```golang
type Book struct {
	Title        string
	Description  string
	UPC          string
	PriceExclTax float64
	PriceInclTax float64
	Availability string
	NReviews     int
}
```

Inspection of HTML code of web pages reveal that product pages always have the following element
in them:

```html
<article class="product_page"><!-- Start of product page -->
```

Category pages do not have this element. Furthemore, this `<article>` thing has all the elements
with data we want to extract as children. Therefore, it is desirable to make a callback with 
XPath query for this element and provide a callback function that will extract all the data into
fields of Go struct we just defined:

```golang
	c.OnXML("//article[.//div[@id=\"product_description\"]]", func(e *colly.XMLElement) {
		title := e.ChildText(".//h1")
		description := e.ChildText("./p")
		upc := e.ChildText(".//tr[./th[contains(text(), \"UPC\")]]/td")

		priceStrExclTax := e.ChildText(".//tr[./th[contains(text(), \"Price (excl. tax)\")]]/td")
		priceStrExclTax = strings.Replace(priceStrExclTax, "£", "", 1)
		priceExclTax, _ := strconv.ParseFloat(priceStrExclTax, 64)

		priceStrInclTax := e.ChildText(".//tr[./th[contains(text(), \"Price (incl. tax)\")]]/td")
		priceStrInclTax = strings.Replace(priceStrInclTax, "£", "", 1)
		priceInclTax, _ := strconv.ParseFloat(priceStrInclTax, 64)

		availability := e.ChildText(".//tr[./th[contains(text(), \"Availability\")]]/td")
		nReviews, _ := strconv.Atoi(e.ChildText(".//tr[./th[contains(text(), \"Number of reviews\")]]/td"))

		book := Book{
			Title:        title,
			Description:  description,
			UPC:          upc,
			PriceExclTax: priceExclTax,
			PriceInclTax: priceInclTax,
			Availability: availability,
			NReviews:     nReviews,
		}

		fmt.Println(book)
	})
```

At this point we are not exporting scraped data anywhere and just printing it into the standard output.
We can verify that our code is correctly scraping the data:

```
Visited https://books.toscrape.com/catalogue/category/books/sports-and-games_17/index.html
Visiting https://books.toscrape.com/catalogue/naturally-lean-125-nourishing-gluten-free-plant-based-recipes-all-under-300-calories_479/index.html...
Visiting https://books.toscrape.com/catalogue/the-book-of-basketball-the-nba-according-to-the-sports-guy_232/index.html...
Visiting https://books.toscrape.com/catalogue/friday-night-lights-a-town-a-team-and-a-dream_158/index.html...
Visiting https://books.toscrape.com/catalogue/icing-aces-hockey-2_25/index.html...
Visiting https://books.toscrape.com/catalogue/settling-the-score-the-summer-games-1_50/index.html...
Visiting https://books.toscrape.com/catalogue/sugar-rush-offensive-line-2_108/index.html...
Visited https://books.toscrape.com/catalogue/the-genius-of-birds_843/index.html
Visited https://books.toscrape.com/catalogue/the-bridge-to-consciousness-im-writing-the-bridge-between-science-and-our-old-and-new-beliefs_840/index.html
{The Genius of Birds Birds are astonishingly intelligent creatures. In fact, according to revolutionary new research, some birds rival primates and even humans in their remarkable forms of intelligence. Like humans, many birds have enormous brains relative to their size. Although small, bird brains are packed with neurons that allow them to punch well above their weight. InThe Genius of Birds, Birds are astonishingly intelligent creatures. In fact, according to revolutionary new research, some birds rival primates and even humans in their remarkable forms of intelligence.  Like humans, many birds have enormous brains relative to their size. Although small, bird brains are packed with neurons that allow them to punch well above their weight. In The Genius of Birds, acclaimed author Jennifer Ackerman explores the newly discovered brilliance of birds and how it came about. As she travels around the world to the most cutting-edge frontiers of research— the distant laboratories of Barbados and New Caledonia, the great tit communities of the United Kingdom and the bowerbird habitats of Australia, the ravaged mid-Atlantic coast after Hurricane Sandy and the warming mountains of central Virginia and the western states—Ackerman not only tells the story of the recently uncovered genius of birds but also delves deeply into the latest findings about the bird brain itself that are revolutionizing our view of what it means to be intelligent.Consider, as Ackerman does, the Clark’s nutcracker, a bird that can hide as many as 30,000 seeds over dozens of square miles and remember where it put them several months later; the mockingbirds and thrashers, species that can store 200 to 2,000 different songs in a brain a thousand times smaller than ours; the well-known pigeon, which knows where it’s going, even thousands of miles from familiar territory; and the New Caledonian crow, an impressive bird that makes its own tools. But beyond highlighting how birds use their unique genius in technical ways, Ackerman points out the impressive social smarts of birds. They deceive and manipulate. They eavesdrop. They display a strong sense of fairness. They give gifts. They play keep-away and tug-of-war. They tease. They share. They cultivate social networks. They vie for status. They kiss to console one another. They teach their young. They blackmail their parents. They alert one another to danger. They summon witnesses to the death of a peer. They may even grieve. This elegant scientific investigation and travelogue weaves personal anecdotes with fascinating science. Ackerman delivers an extraordinary story that will both give readers a new appreciation for the exceptional talents of birds and let them discover what birds can reveal about our changing world. Incredibly informative and beautifully written, The Genius of Birds richly celebrates the triumphs of these surprising and fiercely intelligent creatures. ...more 42d0d7c92b75fc1c 17.24 17.24 In stock (15 available) 0}
Visited https://books.toscrape.com/catalogue/the-death-of-humanity-and-the-case-for-life_932/index.html
Visited https://books.toscrape.com/catalogue/love-lies-and-spies_622/index.html
Visited https://books.toscrape.com/catalogue/the-stranger_861/index.html
Visited https://books.toscrape.com/catalogue/proofs-of-god-classical-arguments-from-tertullian-to-barth_538/index.html
{The Death of Humanity: and the Case for Life Do you believe human life is inherently valuable? Unfortunately, in the secularized age of state-sanctioned euthanasia and abortion-on-demand, many are losing faith in the simple value of human life. To the disillusioned, human beings are a cosmic accident whose intrinsic value is worth no more than other animals.The Death of Humanity explores our culture's declining respe Do you believe human life is inherently valuable? Unfortunately, in the secularized age of state-sanctioned euthanasia and abortion-on-demand, many are losing faith in the simple value of human life. To the disillusioned, human beings are a cosmic accident whose intrinsic value is worth no more than other animals.The Death of Humanity explores our culture's declining respect for the sanctity of human life, drawing on philosophy and history to reveal the dark road ahead for society if we lose our faith in human life. ...more bd261725b99f5983 58.11 58.11 In stock (16 available) 0}
{Love, Lies and Spies Juliana Telford is not your average nineteenth-century young lady. She’s much more interested in researching ladybugs than marriage, fashionable dresses, or dances. So when her father sends her to London for a season, she’s determined not to form any attachments. Instead, she plans to secretly publish their research.Spencer Northam is not the average young gentleman of lei Juliana Telford is not your average nineteenth-century young lady. She’s much more interested in researching ladybugs than marriage, fashionable dresses, or dances. So when her father sends her to London for a season, she’s determined not to form any attachments. Instead, she plans to secretly publish their research.Spencer Northam is not the average young gentleman of leisure he appears. He is actually a spy for the War Office, and is more focused on acing his first mission than meeting eligible ladies. Fortunately, Juliana feels the same, and they agree to pretend to fall for each other. Spencer can finally focus, until he is tasked with observing Juliana’s traveling companions . . . and Juliana herself. ...more 9546d537fbf99eb6 20.55 20.55 In stock (12 available) 0}
```

We miss the data exporting part, so let us implement writing book data to CSV files. We open a new
file for writing and instantiate CSV writer object from `encoding/csv` package:

```golang
	outF, err := os.OpenFile("books.csv", os.O_RDWR|os.O_CREATE, 0755)
	if err != nil {
		panic(err)
	}

        csvWriter := csv.NewWriter(outF)
```

Since this CSV writer only takes slices of string for each row we have to explicitly write out
the header row:

```golang
        csvWriter.Write([]string{"title", "description", "upc", "price_excl_tax", "price_incl_tax", "availability", "n_reviews"})
```

At this point, we have `Book` struct that we instantiate for each product page we have scraped. Let us
implement a helper method that will return CSV field values in the order that match the columns:

```golang
func (b *Book) ToCSVRow() []string {
	return []string{
		b.Title,
		b.Description,
		b.UPC,
		fmt.Sprintf("%.2f", b.PriceExclTax),
		fmt.Sprintf("%.2f", b.PriceInclTax),
		b.Availability,
		fmt.Sprintf("%d", b.NReviews),
	}
}
```

One more thing we need to set up is a mutex that will prevent multiple writes to the file in parallel
that may result in some messed up CSV lines. We just need to declare a variable for it during preparation
to scrape.

```golang
        var mtx sync.Mutex
```

We update the final part of callback function to lock the mutex, write out CSV row and then unlock the mutex:

```golang
		mtx.Lock()
		fmt.Println(book)
		csvWriter.Write(book.ToCSVRow())
		mtx.Unlock()
```

The entire scraper code we have implemented is as follows:

```golang
package main

import (
	"encoding/csv"
	"fmt"
	"os"
	"strconv"
	"strings"
	"sync"

	"github.com/gocolly/colly"
)

type Book struct {
	Title        string
	Description  string
	UPC          string
	PriceExclTax float64
	PriceInclTax float64
	Availability string
	NReviews     int
}

func (b *Book) ToCSVRow() []string {
	return []string{
		b.Title,
		b.Description,
		b.UPC,
		fmt.Sprintf("%.2f", b.PriceExclTax),
		fmt.Sprintf("%.2f", b.PriceInclTax),
		b.Availability,
		fmt.Sprintf("%d", b.NReviews),
	}
}

func main() {
	c := colly.NewCollector(colly.AllowedDomains("books.toscrape.com"), colly.Async(true))

	c.OnRequest(func(r *colly.Request) {
		fmt.Printf("Visiting %s...\n", r.URL.String())
	})

	c.OnHTML("div.side_categories * > a", func(e *colly.HTMLElement) {
		e.Request.Visit(e.Attr("href"))
	})

	c.OnHTML("li.next > a", func(e *colly.HTMLElement) {
		e.Request.Visit(e.Attr("href"))
	})

	c.OnHTML("article.product_pod > h3 > a", func(e *colly.HTMLElement) {
		e.Request.Visit(e.Attr("href"))
	})

	outF, err := os.OpenFile("books.csv", os.O_RDWR|os.O_CREATE, 0755)
	if err != nil {
		panic(err)
	}

	var mtx sync.Mutex

	csvWriter := csv.NewWriter(outF)
	csvWriter.Write([]string{"title", "description", "upc", "price_excl_tax", "price_incl_tax", "availability", "n_reviews"})

	c.OnXML("//article[@class=\"product_page\"]", func(e *colly.XMLElement) {
		title := e.ChildText(".//h1")
		description := e.ChildText("./p")
		upc := e.ChildText(".//tr[./th[contains(text(), \"UPC\")]]/td")

		priceStrExclTax := e.ChildText(".//tr[./th[contains(text(), \"Price (excl. tax)\")]]/td")
		priceStrExclTax = strings.Replace(priceStrExclTax, "£", "", 1)
		priceExclTax, _ := strconv.ParseFloat(priceStrExclTax, 64)

		priceStrInclTax := e.ChildText(".//tr[./th[contains(text(), \"Price (incl. tax)\")]]/td")
		priceStrInclTax = strings.Replace(priceStrInclTax, "£", "", 1)
		priceInclTax, _ := strconv.ParseFloat(priceStrInclTax, 64)

		availability := e.ChildText(".//tr[./th[contains(text(), \"Availability\")]]/td")
		nReviews, _ := strconv.Atoi(e.ChildText(".//tr[./th[contains(text(), \"Number of reviews\")]]/td"))

		book := Book{
			Title:        title,
			Description:  description,
			UPC:          upc,
			PriceExclTax: priceExclTax,
			PriceInclTax: priceInclTax,
			Availability: availability,
			NReviews:     nReviews,
		}

		mtx.Lock()
		fmt.Println(book)
		csvWriter.Write(book.ToCSVRow())
		mtx.Unlock()
	})

	c.OnResponse(func(r *colly.Response) {
		fmt.Printf("Visited %s\n", r.Request.URL)
	})

	c.Visit("https://books.toscrape.com")
	c.Wait()

	csvWriter.Flush()
	outF.Close()
}
```
