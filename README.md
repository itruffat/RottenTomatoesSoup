# RottenTomatoesSoup

TLDR; A Python-based RottenTomatoes Scrapper

## Who, Why and What?

I have been wanting to use BeautifulSoup for a long 
time, but I never found a webpage that looked worth 
the hustle. That was until I decided to look at the 
source of RottenTomatoes.com, whose simplicity is 
nothing short of beautiful. So I wanted to make a 
tool to analyze it.

## Isn't there an official rottentomatoes API?

Yes there is, feel free to use it for your projects
instead of this. Remember that scrappers work on 
displayed source, and that's always up to change,
whereas a change in an API will rarely be rushed.

## What limits does this program have?

Right now it simply downloads the reviews of a movie
in a single file. (Called cannedsoup) I might add 
some processing in the future, such as looking at 
score averages and whatnot.

If you want to study an audience aggregate, bare in 
mind RottenTomatoes has a bug with audience reviews, 
in which any page beyond page 51 is not displayed. 
That has nothing to do with library, and it's a bug 
that happens on every page.
