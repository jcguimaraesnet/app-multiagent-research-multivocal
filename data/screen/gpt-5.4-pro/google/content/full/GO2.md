![Thumbnail (1920x1080)](https://i.ytimg.com/vi/cObBj2UpWK8/maxresdefault.jpg)
# [RAG for Code Generation, an AI Hacker Cup example](https://www.youtube.com/watch?v=cObBj2UpWK8)

**Visibility**: Public
**Uploaded by**: [Weights & Biases](https://www.youtube.com/@WeightsBiases)
**Uploaded at**: 2024-08-29
**Published at**: 2024-08-28
**Length**: 52:10
**Views**: 3209
**Likes**: 45
**Category**: Science & Technology

## Description

```
Explore the advancements in LLM-powered competitive programming through this in-depth analysis of Retrieval Augmented Generation (RAG) for code generation agents. As presented at the NeurIPS HackerCup AI Competition (HAC) 2024 lecture series, this video showcases how RAG can be utilized to enhance agent-based strategies for tackling complex coding challenges.

Key discussion points include:
- Addressing the specific challenges of competitive programming with LLMs
- Designing RAG architectures for robust code generation
- Implementing AST-based similarity search for rapid code retrieval
- Integrating structural and semantic similarity in a multi-stage retrieval process
- Enhancing few-shot learning with enriched example programming scenarios
- Promoting AI self-reflection and iterative improvement

Discover how advanced agentic systems can leverage existing problem solutions, employ multi-agent strategies, and apply state-of-the-art techniques to push the boundaries of AI agents in the competitive programming arena.
```

## Transcript

cool hello everyone we are back again
for this series of lectures on the news
Harker cup Challenge and yeah have been
a a ride and today we at with barath a
colleague of mine that that has put
together some really nice examples on
using rag to to tackle these complex
problems and who can you get started
using Rag and and maybe apply some of
these techniques to get your yourself a
working solution these hoger cap 2024
hello
bra Hey Thomas um yeah thank you um let
me begin with sharing my screen let me
know if you guys can see my screen go
ahead
um there you go perfect
perfect okay uh
slideshow all
right let me know if you guys you I be
monitoring YouTube and and checking for
questions and I may interrupt you at
some point like if we have some some
questions sure so go ahead um all right
so like before we get started I'm but I
work at Wes and biases I'm a machine
learning engineer for the last year I've
been building I've built this rag
application called onebot and onebot is
um a developer assistant that answers
quaries on Discord and slack which based
off of like weights and biases
documentation and I've used that
experience a bit and some of the
learnings that I've that I've had from
that you know experience to build this
code generation agent for this
competition right so uh before we get
started like I wanted to understand for
myself what
um AI for problem solving meant and how
uh agents and you know llms can be used
for problem solving and I was reading
through the hacker cup you know problem
statement and going through some of the
stter code and I realized that you know
there are a few key challenges right uh
first these problems are you know based
off of complex algorithms we already
have like gp4 being able to solve some
algorithmic problems we are able to like
you know ask it for some code and like
it's able to R some code but then these
problems have like more intricate data
structures or or you know um or use more
intricate data structures and they are
also no novel problems that is problems
that these models have not seen before
and they have memory and time
constraints and also like you know the
descriptions themselves can be quite
convoluted overall and all of these
things put together can make these
problems very hard even for humans and
experience programmers and that is why I
think there is like separate breed of
programmers who are like competitive
coding programmers and therefore like
you know uh I found that like when I
just put this problem at like on chat
gbt I couldn't like get the model to
generate anything
useful right so that is where I thought
hey why not like build um you know a rag
generation a code generation agent based
off of rag because I've been using
retrieval augmented generation for like
a year and I thought why not put this
together with an agent um and that
that's what resulted in this like you
know complex pipeline that you see on
the right side but then this pipeline
while it might look complex it's it's
made out of like few key components and
that includes uh a data set of of like
similar problem solution pairs that is
you know I found a data set that had
like a few million problem problems and
there corresponding Solutions all from
competitive
coding uh you know competitive coding um
places and or you know um
websites and then you know first thing
we had to do was like you know build
some sort of similarity search and then
build a multi-agent framework and then
build and then you know put in some few
short learning into that multi- agent
framework and then add some
self-reflection and refinement to make
this whole like you know thing an agent
take workflow now I Ed like a lot of
terms and like you know made it very
look very complex but I'll like the
whole point of this presentation is like
to go over each of these components to
describe like how these can be built and
how you can probably utilize this to
like build your own agent and maybe even
like win the competition with something
like this right um yeah so uh the again
going back like build up the some of the
key things that I had to do while like
building these different key components
was like you know build that massive
data set right and to do that the first
thing that I did was leverage this code
contest data set which was released as
part of this uh Alpha code paper and as
part of that they released these um
similar you know problem solution Pairs
and the whole idea stems on the fact
that hey can we go and find when you
when when you present an llm with an
with a problem and ask it to generate a
solution can you give it examples of
previous problem solution Pairs and make
it like make sort of make it understand
that hey here are like similar problems
and solutions that you have seen in the
past and learn from these examples in
context as like in form of few short
examples and then like you know uh
generate a new solution based off of
that right but then to do this um you
know you have to have like some sort of
code data set and I you could have I
could have as well relied on like past
competition data which from from like
the same hacker cup competition but then
I thought hey if there is a much larger
data set there is more chance of us
being able to like find more problem
solution Pairs and that's where I went
ahead and like you know downloaded this
code contest data
set and um basically it this data set
has like a problem and multiple
Solutions because you know in code
contest like you can sort of write
different solutions to the same
problem um and some of the steps that I
like take do is to like you know use
abstract syntax trees to pass these code
examples there is a specific reason to
that and I will like share that next but
uh you know I pass these into abstract
syntax trees representation and then
like you know uh use hugging phase data
set because overall this is like about
1.4 million records and it takes like
quite some time to process and I'm we
are only like focused on Python 3
Solutions in the data set the data set
has like bunch of other programming
languages but for the sake of this like
you know task I just focus on Python 3
Solutions on the right you can see like
the data set and some of the and a simp
and a sample record that has like you
know some description and some code and
some samp sample inputs after like we
get the we process this data set for our
use case right now one of the main
things one of the main issues with
finding similar code is if you take a
look at if you take look at this example
on the right you can see that there are
two functions one is called sum to it
has two arguments A and B and sums up A
and B and returns that sum right and
another is called like add to it has X
and Y arguments and returns that now if
you run like a simple similarity or text
based similarity you're never going to
get like the same uh you're you're never
going to get these um match to match
right so if you try to look up hey can
you if you write a function and then try
to like look up for similar functions in
a data set you're never going to find
the same function because you might be
using different variable names or
different function names and other stuff
right so we want to be able to focus on
like the structure of the code the
implementation of say depth first search
will probably remain similar
irrespective of the variable names and
function names and other you know
details that you put in same thing you
know uh same thing same thing is the
case with like you know a merge sort
implementation right so when you're
trying to retrieve code you might want
to like retrieve code that looks
structurally similar and this is where
ASD passing comes in and we use like I
used ASD passing to like pass these
functions into these tokens that sort of
look
that look similar at least when there
are when two functions are structurally
similar now why go through all of this
because overall we have like 1.5
million problems and we have to be able
to quickly search through these problems
we could have like done some sort of
like code embedding and you know you we
could have used open AI embeddings but
then like you know embedding 1.5 million
documents or problems and like you know
being able to search through them
efficiently is going to be like you know
quite problematic or you know especially
given that you have a time limit and
you're supposed to like be able to like
generate code in within that time limit
right so that's where but obviously you
know searching for um structurally
similar code doesn't necessarily result
in um code that is semantically similar
right so you're we're trying to look for
you know I've implemented a function a
function to solve a problem and then I'm
trying to see if there are similar
problems that you know that I've that
I've encountered in the past and learn
from those problems right so what we do
is we we take this two two-step approach
where we first like you know go and find
all the similar problems or structurally
similar problems using bm25 algorithm
and you know the ASD passing that I just
explained and then like you know
contextually Rank and you know sort of
narrow down these 50 problems into like
three most similar problems that I can
sort of learn from or that I can get an
llm agent or model to learn from right
so that is where like you know we we
follow this two-step process and you
know do some sort of you know candidate
generation and then you know narrow down
these
candidates right once we have these you
know similar query solution pairs from
the past so here's where we are right we
have an llm agent it's generated an
initial draft solution to a problem
we've gone to the we've gone to our
database and fetched three similar
problems that look very similar to the
problem that we are trying to solve or
we are asking the llm agent to solve
right and then obviously you know just
put just sticking in this problem and
solution is not going to really help the
llm agent in being able to reason
through the problem that it is currently
solving right so in order to like you
know sort of um teach the llm agent or
llm model um the kind of steps that it
needs to follow what we do is we enrich
the retrieve problem statements using
another llm but this llm has a much
simpler task right it has it has a
problem and it has a solution so if you
see this if you look at the image on the
right you can see that you we provide
the problem description and a solution
to the model and then we say hey given
this problem and solution
can you explain the core question that
the problem is related to and can you
extract the key problem information can
you also explain the algorithm and like
you know develop a high level tutorial
and put come up with a stepbystep plan
to you know create the solution and also
generate language agnostic pseudo code
so all of these steps enrich whatever
data or whatever problem solution pair
we've retrieved
from the database right and this helps
us create few short learning examples we
can then like you know create an
instruction set to a new llm and say hey
here are like you know previous problems
where you where you have started at a
question and then done these steps done
these six steps wherein you have
extracted the key problem and you've
like described the problem and then
arrived at a solution but these are
actually problem solution pairs that
we've actually written from our database
and not like really told the llm that is
generated right but we sort of giving
the llm some context and we're telling
it hey here is how similar problems were
solved and here's a new problem and your
task is to solve this new problem and
this very simple few short learning and
we've seen this like quite a happen
quite a few times or used quite often
right we we give examples to LMS and ask
them to mimic the the same task that was
in the example
right um yeah so this is what like this
is how we
then use rag that is we start with we
start with like a um we start with a
initial draft solution so we have this
uh draft solution and then the draft
solution is then like you know um run
against some test cases and then in this
case the test case is whatever we've
generated as a test case and uh you know
we run we run the model against that
test case we we take this draft solution
go and retrieve some similar problem
solution pairs enrich those problem
solution pairs give it to the model and
say hey you've like here are some
examples of how you've done this in the
past now here's like you know try to
solve this problem in the step-by-step
manner so you're sort of like enriching
the chain of thought process of the llm
by sort of adding all of these extra
examples of how it has solved similar
problems right and this is very similar
to like you know how a how a human
programmer would go ahead and solve
these tasks so you would go and look at
hey what what are other people solved or
what are like you know how do I
Implement you know binary search or how
do I Implement Dynamic programs and you
you sort of look at examples and then
come back and solve for your particular
problem right in the same way like we're
teaching an LM to do that but then
obviously it might you know fail in some
of these tasks even when it is given
like some solution right and this is
where we use this concept of
self-reflection wherein we say we prompt
another llm agent and say hey here's
like a problem and here's an incorrect
solution that you've like sort of
generated for this problem and here's
the test result uh that sort of shows
what the incorrect result was I want you
to reflect on the uh the error or the
mistake in the code and like you know
identify like key elements and identify
a step-by-step solution with some
revision and provide general advice to
yourself like when you're trying to
resolve this this concept is called
reflection and is widely used like in
many problem solving um you know llms
and agents right so this we use this to
sort
of instruct an llm to help
help our agent reflect on errors that it
has made and then we put this back into
um into the whole like evaluation Loop
right so if you go back to like go back
to this like you know example you can
see that we start with like a simple rag
solver and we have some sort of a loop
we start with like an initial solution
from an agent we ask that agent to
generate a draft solution and once we
have that draft solution solution we um
you know look up examples in our
database and see if there are like
similar solution problem question uh you
know problem solution pairs that we have
encountered in the past and then we ask
an llm to describe these
examples and then we we try to generate
uh a new output or a new solution based
off of these described you know few
short examples right and then if and
then again we check for correctness if
we if we if we are correct at this pass
we just say huh right like you know we
got this right and return the result
otherwise we rework the solution using
reflection and try to provide an
improved solution and check for
correctness and then repeat this in a
loop a few number of times right this is
what this is like the entire gist of the
agent that we've built or I built and it
you know I try to test this agent in
these three different settings the first
setting being like zero shot examples
wherein it's not um where we just prompt
an llm and say hey here's a problem
hydrogenator solution right and then the
second setting that I that we tested is
in this rag setting where we go fetch
these examples from the data set and
then um you know show in llm the
examples and then say hey can you um now
try to generate and solve for this right
and then it tries to solve for that and
then the third setting is is this
reflect loop self-reflection loop
wherein the llm uses rag first to
generate a solution and if it fails it
reflects upon its errors and then tries
to like you regenerate and then tries to
like you know uh run this and then I
evaluated this with two different models
like a fast model the gbt 40 mini and
then uh like you know slightly stronger
model gbd 40 and some and few different
temperatures temperatures 0 0.5 and one
and yeah you could see like the code
that I used to like sort of run this all
of this code is on GitHub in the starta
kits and like you can sort of like take
a look and hopefully this inspires you
but yeah no surprise that like you know
um you can see in this like graph that
um this is just a simple evaluation
dashboard of uh the three different
models so you can see that I have the
zero shot agent I have the rag agent and
the rag reflection agent the zero shot
agent like got like none of the five so
I tested on the five different problems
from last year's practice uh samples and
found that like you know zero shot agent
did not get like any of the problems
right you can see that the rag agent got
like one problem right and then you can
also see the self-reflection agent like
get two problems right right and if you
like look at like for example if you
look at this example you can see how
this is the dimsum delivery example and
you can see that you know both the zero
short agent and the rag agent like sort
of get it wrong um but then the rag
agent solution is like slightly better
than the zero short agent solution and
then like it gets even better with cell
you got the de some to pass yeah and
then we got like the self reflection
agent to like pass the uh whole you know
you talk a little bit more because yeah
everyone has shown this problem and that
this is one of the hard ones and oh did
it grab like the r part grab like
similar problems that related I don't
know to maybe moving on a grid
or I don't know if you explore explored
more of what what was the actual yeah
are you able to see this part of my
screen yeah yeah perfect okay so here's
like this particular uh um you know
reflection agent right and we were
talking about um yeah we were talking
about comparing the dimsum problem
dimsum delivery right okay
um so basically you said that the rack
is not was not enough this is of course
this is not deterministic but like the
rack part was was not even if it retriev
something couldn't yeah it couldn't
produce but the self reflect ction help
to actually come up with the
solution that's right so I'm just like
opening up the trace so that we can like
work work through this right um right so
here's like you can see the
self-reflection agent um it's tried
first like a zero shot solution and you
can see like the solution here it's you
can also like open up the source code
and do it in code form right
yeah for people we don't know like we
work at weights and biases this is
weights and biases weave is our tool to
inspect interactions urlm so we're
seeing the stack trace of um all the
execution of the
pipeline yeah thanks uh Thomas for
setting that stage but uh I hope I'm
seeing the right Trace here uh just give
me one moment to double check
if you open that evaluation you should
see like the five problems and then like
you can open the specific one
yeah
uh so that's yeah that's a zero show oh
no that's a rag with self effect then
like you should have problem name
somewhere
here yeah that's the trace for Dimson
yeah I never could make this pass like
dimsum is a
nightmare if you have watched the other
lectures like basically this problem has
a super simple solution but llm to like
try to explore the full space and once
they like start doing that they never
come back to that simpler solution yeah
um so they get stuck in that like kind
of
behavior yeah so according to like this
it's gone and fetched and like you know
it's done these steps it's like sort of
created a drop solution and there are
like five hidden calls here but it's
like used that dra solution and was able
to like just because we have this you
know examples in them it was able to use
that solution to open one of the
retrievals
um uh yeah let me find a different
problem for retrieval and show you that
right okay so this is the rag solver
and right so you can see see this and
you can see here that we create some
examples right uh if you're not able to
see my screen clearly let me open it up
so that and make it
bigger
yeah uh right so if you look at like
each example you can sort of go through
what an example that we retrieved in
this case looks like so here's like one
example that's showing the Heap trace
for and like you know here's some code
and it's like a question the problem
statement is about something related to
a US Farmer and the initial rag solution
that was
generated um or the initial zero shot
solver sort of generates a draft
solution and you can look at that draft
solution here
and
yeah you you can see that it's like the
problem itself is um related
to weights in know graph and the core
question is about hey given like two
different weights in a graph can you
like identify how to find and the more
details of the problem itself is here I
guess yeah here apple a day this is two
apples a day problem and I'm showing
this stray because it shows like this
Loop of being able to to like generate a
draft solution and then go check for
correctness and then go and generate and
like you know look for simple look look
for examples in our database and then
describe those
examples and take all of those like you
know five descriptions of examples and
generate a solution for the problem
itself and um in that did did it pass
like the score can you open the last
call yeah it oh it fail it fa yeah
because I also limit the number of
iterations to just like make things
little faster but uh if this
self-reflection Loop of like you know
trying a solution finding similar
problems going back and trying more you
know problems like that and uh and
finding more similar problems this Loop
in a way works and that's what like my
initial evaluation chose obviously
there's like lot of scope for a lot more
work this dashboard I wanted to show is
that like you know if you look at it we
got like two out of the five problems
that we tried most of the time you see
that the rag reflection agent gets two
of them at least correct right that's
high like and then you see that the rag
agent sometimes gets two of them correct
and sometimes it gets only one of them
correct but then the zero shot agent
either gets one correct or gets Z
correct the cheeseburger coral one
that's like the easiest one yeah so it
usually gets the zero shot agent gets
the cheeseburger Coral ones correct most
of the time but otherwise it's um it's
always otherwise like getting the uh
evaluations wrong when it is in a zero
shot setting right yeah and how do you
feel like in that I feel that just to
put like some context here like we have
been playing with the data set for a
while we the practice folder has been
like like test bed for our experiments
and encourage people to actually
download the 2023 data set run it on CH
gbd not even like write code and play
with it and to get an idea and a grasp
of what we are so then come to Discord
can chat like that's why I was saying
like dimsum is like a hard problem I
would say one of the hardest on that
batch and it it got that one correct and
but for instance the the there's like
two cheeseburger problems and the second
part
may need the first part are you like
piping the solution from the first part
to the second
part uh no I'm not I did not make that
get three three out of
five yeah possible but um what I um I I
do treat them as individual problems but
there was there were some interesting
other interesting observations that I
did make in some of these like
evaluations that I was comparing which
was the fact that you know
um uh I could see that in some some
setting the zero shot solution timed out
like the model whatever you know it was
trying timed out in the zero shot
setting but then um in the rag
setting it was erroring out with a
mistake and in the um you know um in the
rag with reflection setting it had
almost gotten very close to the answer
and if I run it for like a longer number
of iterations in terms of this rag
reflection step itation is like self
reflection no like fixing that's right
okay each iteration is basically you
know create a solution try to find try
to reflect on errors in the solution
improve that solution and if that fails
go back to the database find new Sol new
like you know examples to learn from and
then try again so that's one iteration
right so I I just stop I always usually
stop at like two iterations because yeah
this even with two iterations this only
reaches like around 2 and a half minutes
so I feel like there is more like you
know it could yeah we have six minutes
we should be we should be using all our
time yes so
I feel like you could I could spend some
more I mean the model could have spent
some more time on some of these
iterations and generated better
Solutions but yeah yeah that's that has
been like one observation that I made um
I feel that like there is like a how do
you feel and what is like
possible exploring directions because I
feel like if the the everything is based
at the beginning on the Zero shot
solution that if the code it generates
is super far away from the real solution
we're kind of screwed no
like that's absolutely search everything
with that code base in
mind yeah and I feel like um one of the
these there are like some of these um uh
you
know problems with these agents you're
right that if you start with like a
initial bad solution and immediately
start doing r over it you will end up
with like a bad trajectory that you will
fall in and that is where I think the
first step of self-reflection comes in
and if you if we had done
self-reflection slightly before we even
did rag maybe we could have corrected
that right but then without the rag
examples in place the self-reflection
loop also sometimes puts things in a bad
trajectory yeah so it's slightly a
chicken and egg problem wherein
um you know you start with like a bad
problem and you end up with like a list
of bad problems but then if you're able
to catch that during your
self-reflection step you might be able
to come out of that you know Loop of
going into bad problems and solutions
but then another like way to mitigate
this is to be able to increase the
diversity of problem solution pairs that
you get from your database right right
now we are like trying to find ASD
similarity uh we could like improve
prove it with something like you know um
maximum margin relevance and you know
try to find different clusters of
problems that are similar to the problem
that you're currently working on and
then sample from those clusters and give
those as F short examples which would
sort of show the LM different ways to
solve like for the task I obviously did
not try out all the
solution uh or all the types of
solutions that I
that I had in mind I put myself on like
a time constraint to solve the problem
but yeah um there are there the
possibilities of trying like different
things are like quite a bit how do you
feel like because like the problem is
multiple pieces has like the scription
code and the solu yeah and the solution
in code um searching like searching
similarity on the description of the
problem may also help
or uh that's right
and problem description
similarity so actually that's where the
um you know the step where we rerank the
documents comes in can you zoom in a
little bit
yeah yeah that's better so when we do
get when we rerank the documents you can
see that as part of the reranking we
actually give the problem the problem
it's the solution the initial solution
that our llm came up with and each
retrieved document also has its
description and code right so when we
are reranking and when we are getting
these embeddings per um you know per
problem description pair we are actually
um you know getting both or getting
our embeddings for both the problem and
this and the description basically right
um so we are like we are getting
embeddings for both both the description
and the code for
both the initial solution and problem
that we are trying to solve and the
problems and solutions that we have
retrieved but this is only happening for
a small candidate set of like you know
documents that we trying to rerank or
you know examples that we're trying to
rerank which is in this case like 50
documents but then uh with the like you
know but then we only run like you know
um the ASC similarity match for the rest
of the code so on the 1 million
documents we running code search but on
the 50 documents we sort of actually
running we're checking for problems as
well as solutions that looks that looks
similar to problem solution pair that we
are currently working
on
okay and do you do you feel that that
embedding part like slows down your yeah
you could do that
beforehand that's right you could do
that beforehand you could like I I I
feel like the constraint was in this
case like if you if I had like a I I'm
running this off of my laptop right so
there is and I'm imagining a lot of
people will might use apis but they'll
be doing their development on like much
smaller systems or you know they might
not have access to like really large
production machines to run all of this
and if you're like uh running or storing
1 million or 1.5 million embeddings
you're going to take up a lot of space
in terms of disk and RAM and when you're
trying to do similarity search wherein
you're trying to do like you know
similarity search with one of these you
know new Vector databases like Lance TV
or quadrant or chroma or you know any of
these you're going to you're going to
have like suddenly have to tackle issues
with memory and issues with dis space
and things like that and the whole point
of like you know trying to do this as
similarity and come you know narrow down
to a shorter
subset was to like you know avoid all of
these other issues that you will
otherwise have to deal with when you're
building like production rag
systems okay yeah I agree yeah it's but
this looks promising like you are
tapping into a lot of very specific
knowledge that may be useful to actually
solve these
problems maybe embedding and putting in
the database the previous years's
problem like with a higher
ranking um but I suppose if this is
curated correctly the like previous year
problem shouldn't be very useful for
these I I don't know maybe I'm I'm just
we will need to ask smk or someone that
has been doing this for well in a way
that was also my thought process like I
I generally thought hey like coding
competitions might not have um I mean if
you take at least the same competition
like if you take hacker
cup you might not have the same sort of
problems from previous years in this
year right but if you look at like
different coding competitions from
different years from different like
platforms and try to like compile a
database and that's what this code uh
you know the data set that I was using
uh code contest data set that's what it
does like it took like data uh data from
different competitions and different
like you know sources and put them all
together and uh it was this data set
actually is used to fine-tune a
Model A large language model but I just
used this as like a knowledge base for a
rag system right uh I'm sure like people
who are on the fine-tuning track might
also find this data set quite useful if
they're like building these code you
know fine-tune code generation agents we
have a couple of questions like one of
the questions is can you showcase like
token differences between three
approaches I would expect like rack plus
self reflection is more lengthy in
tokens uh yeah that's true um rag plus
self-reflection does result in more
number of tokens per call uh here I have
I think um per evaluation per model call
I might be able to find you should be on
the like the right side of the
Evo token
[Music]
zero I think I have some error in my
code in like measuring the number of
tokens per model
but yeah we can we can share that info
afterwards like I'm yeah I can like drop
that info later sorry another people
asking about like yeah trying he tried
similarity search but my LM keeps
hallucinating as I use as I using a
large data set who to make my rag
extract the relevant information like
that's basically Al
the the golden
question um I feel like um adding some
sort of you know structured output
Generation Um with validation allows
normally gets you to reduce the number
of hallucinations so one of the things
that I used was um pantic and the
instructor library to sort of reduce the
number of like you know off off topic
things or you know off I I specifically
instructed it to generate like you know
code and I used um XML tags to say hey
you need to put things Within These XML
tags and then like you know par and
extract from these XML tags uh but then
specifically with code generation it's
still like bound to hallucinate and
create um you know methods and variables
and stuff that might not actually work
in real time yeah and um we can test the
code we can run it and see if it's it
works so basically you have a uni test
that lets you that's true and that's
where I think the testing and
self-reflection loop with the test case
output really helps um
yeah and someone is saying that maybe
you can train your
retriever um I don't I don't know much
about that um yeah see for for instance
there is there there are other code to
code um
based uh embedding models like for
instance there is Gina to code to code
embedding which basically is trained for
this task you um you know query with
some code and you get similar code right
and these might actually be quite useful
uh you can also like take the same code
contest Thea set and fine-tune a model
to basically say hey here's a problem
statement here's a uh code solution and
like you know F tune the model for this
given a problem statement find similar
code Solutions and then just directly
use your problem statement rather than
asking the llm to generate uh you know
an uh a initial draft solution which was
one of the problems that you were
highlighting right Thomas where you said
hey if it goes in the wrong trajectory
initially then you're like you're just
going to put you're screwed you're
screwed you're going to put your entire
Pipeline on a toss so if you have this
like specially fine-tuned model where
you're basically doing this contrastive
learning and
saying um yeah and and like you know
identifying problem solution Pairs and
training like a R retrieval model for
that you essentially have this you can
like go find similar similar Solutions
or retrieve similar Solutions just based
off of the problem statement which might
actually be quite useful in
itself okay yeah I have I have like a
following question you said that some of
these um problems were solved in like
two to three minutes so we still have
time because rest remember is like six
minute you should unze your problem
folder
generate your code and like check your
output and submit so like some people
are asking like maybe trying different
Vector database and retriever methods
and then like combining them all
together but that actually can be be
done in parallel so we shouldn't add
that much overlap would you spend more
time on the retrieval side or like more
on the
algorithmic uh
part I think for me um I mean in in this
test that that I ran see the BM 25s
retriever is quite fast like if I when
you run it it runs in under under a
second to retrieve like top 50 examples
similarly when you run open AI
embeddings uh you at least for the
embedding calls when you run them
asynchronously for 50 examples you get
them pretty quickly like you get them in
under 5 seconds so between these two you
like you know initial candidate
generation and open AI embedding
generation and retrieval you're totally
spending like somewhere around 25 to 30
seconds to find candidates right but the
most amount of time is actually spent on
the large model calls like the gp4 calls
wherein you've generated all these few
short examples you given it to a model
and you're asking it to
like solve based off of this now your
prompt is much longer because you have
like few short examples in it you have
different problem descriptions and
solutions and then you also like you
know you ask the model to generate so
that's one of the longest time-taking
steps but also I think the other long
steps other longest step that I noticed
was the self-reflection step wherein
yeah it needs to actually uncover the
mistake and then try a new solution to
the problem and then like you know
submit it's very it's very chatty it
will like output a bunch like 2,000
tokens and one so that's true yeah so
it's going to take a couple of
seconds I'm curious like yeah I I you
said like you we retrieve and then we
basically you using rag to retrieve to
put on Inc yeah in context examples um
few shot examples so there's multiple
ways of adding your few shot examples
and and like from these mods that have
like churn base conversations like you
have a assistant and then code and
assistant user assistant user so you end
up with this list of huge huge messages
at the end like I remember in my ex
example I had like 15 messages for each
like trajectory how are you adding the
retried examples are you adding them
like as a conversation like hey you
asked for that and you got that or you
summarize them on a prompt or like can
you give us some tips on that because
that's like super
important that's yeah that's very very
good question Thomas um so what I've
found or this is very
anecdotal this needs more like you know
no let's go anotal
like yeah this needs more like proper
experimental evidence but my anecdotal
like you know experimentation with this
has been that uh if you look at like the
screenshot here you can see that I stick
in the examples into the system PRT okay
oh and the main reason for this was when
given as when given as part of the
system prompt I found that at least gp4
models I don't know how Cloud models
work when given part of when given as
part of the system prong it follows the
instructions much better or it follows
the prompting format instructions it
like you know it like it's much closer
to following the instructions when
things are as part of the system promt
but then when you do this user assistant
turn
I find that like you know it's able to
deviate from the initial system prompt
instructions that we gave it by like you
know suddenly like you know in one of
the turns like it suddenly chooses not
to follow like past conversation or past
uh pattern that it was yeah we have all
seen that like you ask to solve
something and they it come ups with the
same solution again that's
true and that I've observed and I've
also observed that if I ask it to solve
in these in this step by-step Manner and
say hey first identify like the core
question and then come up with like some
steps to solve what it does is when you
have this long user assistant user
assistant U you know turns it suddenly
stops following those instructions and
just s directly jumps into like
generating code instead of planning step
by step or things like that and that's
where I feel like you know adding these
examples or few short examples into the
system prompt usually works better okay
can we yeah you're going to share the
code with everyone so people will be
able to run this and see how it works
but most of the time what I see is
myself and other people end up like
appending infinitely to this huge
message list and the system problem
never changed at the beginning and but
so you are like you have different chat
lists but because at some point like you
get these examples back and you change
the system prompt from the original
one that's like you you like Fork into a
new conversation basically yeah that's
right okay and that really helps keep
things in context for like you have
different llm calls and you have like
you've forked into a different
conversation come back yeah but yeah
basically it's like you're in chbt you
have your conversation you got a lot of
info you create new empty conversation
and like you reformat stuff so you can
redir the the the model to to get what
you are looking for and I think that's
something that yeah you it needs
some yeah you need to think on on a
different way yeah of course there's
multiple ways of like injecting into to
the few examples but I haven't never
tried injecting with a system prompt
like I I'm going to
try there's a lot of insight in what you
have um shown
us um I don't know if there's more
questions people are asking if it's
possible to use claw um I suppose yes
um uh trajectory optimization something
I suppose related to what dpy showed
yesterday yeah that's another Beast I
would say you can mix all the different
solutions that people have shown in the
webinars
but um you need to be under six minutes
that's the game
basically that's right so let's wrap it
up and I think it has been pretty fun
actually yeah I had a lot of fun like
trying to come up with like a solution I
spent a few days on this but it was
really insightful I learned a lot about
like code generation and how bad llms
are with code in the code generation
task and how difficult um you know
competitive coding can be and code
synthesis I think llms are very good at
code fix or L correction but they're
very very bad at code synthesis
especially when it comes to these
algorithmic data structure problems they
generate things that look like they they
look very nice and complicated and like
you know oh this code will work and then
you try it and it actually has like
major
flaws um in
them um yeah and with that like I want
to also add uh that you know soon we'll
be releasing this course on Rag and
um which in which we've just like put
together all of the learnings that we've
had over the past year building rag
systems that we've put in production for
a lot of um you know users and um yeah I
just wanted to share you can like scan
the QR code or go to this link wb. me
slra course and sign up it's a free
course and you'll learn a lot of such
insights from that course um yeah thank
you thank you Barra this was really
useful and yeah sign up for the course
you want to check and see you around um
thank
you see you