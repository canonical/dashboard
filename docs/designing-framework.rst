===================================
Designing a quality framework
===================================

Objectives
==========

At the heart of the framework are the **objectives** you're working towards. An objective is a particular dimension of quality in your field. (For example, if you want to use the framework to drive up engineering standards, one of the dimensions of quality you focus on might be *automated testing*.)

For each one, there will be multiple **conditions** - measurable, checkable states of affairs that demonstrate progress progress towards the objective. Typically, conditions will be arranged according to the **level** of maturity that they represent, providing a progression.

Here's a part of quality framework, with just two objectives described, for *Inclusive language* and  *Automated spelling checks*:

.. list-table::
    :widths: 18 41 41
    :header-rows: 1
    :stub-columns: 1

    * -
      - Inclusive language
      - Automated spelling checks
    * - Started
      - Team members have taken the provided training.
      - Work has begun to implement automated spelling checks.
    * - First results
      - All existing content has been reviewed against the guidelines.
      - Automated spelling checks can be run locally.
    * - Mature
      - Inclusive language principles are actively applied to content production.

        The team can demonstrate meaningful examples of significant improvement.
      - Automated spelling checks are part of the CI pipeline.


Working incrementally
---------------------

Designing a framework doesn't mean plotting out all its details at the start. The best way to approach its construction is incrementally, from the bottom up and by working on concrete details, and building what you have seen work already.

The risk is that people (and you are probably one of them) love to create frameworks and schemes. It's a way of imposing order and rationality on an untidy world. The pleasure of a quality framework lies in that, but not its value. Its value lies in what it helps change: it must *do* something.

While designing your framework, you will often need to hush your inner rationalist so that your inner pragmatist can be heard.


Defining the framework
----------------------

Objectives
~~~~~~~~~~

Consider a dimension of quality in your field, an aspect that you care about - like *Inclusive language* or *Automated spelling checks*

Whatever it is, it should be something meaningful and recognisable to the people that you expect to work with the framework.

For example, if your framework is concerned with engineering standards, "automated testing" might be a good objective. Even if you haven't said anything about exactly what you want them to do about it, automated testing is the kind of thing that most people in engineering would recognise as a good thing, and that makes perfect sense in the context of engineering standards.

This is especially important for the first objectives that start appearing in your scheme. Later objectives can afford to be more abstruse or represent value that needs some explanation, as long as you have already set out ones that are readily accepted, that people are able to buy into without effort.


Conditions and levels
~~~~~~~~~~~~~~~~~~~~~

For each objective, you need write out some conditions representing measurable, checkable states of affairs that you want to become the case.

Put them in an order of progress or maturity - fundamental ones first, followed by ones that build on them.

By the time you have a few, you will probably see ways of grouping them according to level of maturity. For example:


    **Started**

    * The team understand the significance of automated testing.
    * We have good test coverage information.

    **First results**

    * There is a significant increase in test coverage.

    **Mature**

    * There is 100% test coverage.


Making it work well
-------------------

What makes this a good example?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's have a look at the conditions. They're arranged in three levels: from *Started* via *First results* to *Mature*. It's a reasonable set of levels, and arguably a good default to reach for.

There's an art to defining conditions that represent the progress you want. Remember that you are interested in quality, and that you want that asipiration to become part of how teams work and think.


Securing acceptance
...................

An effective strategy is to use the first group of conditions not so much to achieve results, but to secure acceptance.

**The team understand the significance of automated testing.** There is a subtle genius to this. Consider the options someone has in responding. "Yes, we understand the importance of automated testing." Well, great! We agree! Let's move forward!

And if they demur, they implicitly admit that there's something they don't understand, and invite you to explain it to them until they do. Even if they want to quibble, you have already set the terms for the discourse.

In itself, there's nothing very significant about this condition. It doesn't actually change anything or represent something that has been achieved. But, it's an excellent entry-point, *their* first step into *your* plan, your way of thinking, the language that you want to use.

**We have good test coverage information** similarly doesn't represent a significant advance, but it still matters. You can't improve something in an effective way unless you can measure it. And, requiring people to pay attention to an issue, even if you don't ask them to do anything about it yet, prepares them for future action. If it's an issue that they agree is important, then what they observe in their measuring will serve as a spur.

These *Started* objectives are easy for a team to accept. They don't actually commit to any deliverable, and involve only a minimum of effort, but they set the team on the runway towards your goals.


Qualitative conditions
......................

In *First results*, there is a concrete demand: *a significant increase in test coverage*. It *doesn't* say (for example) "at least 50%".

Why not? (After all, 50% is more precise. It's more measurable. It's less subject to debate. "A significant increase" invites questions and doubt.)

**Purpose**: The problem is with a target like 50%, you also give every incentive to work to the measurement, rather than the intention. The purpose falls out of the story. It's extremely easy to create quantities of low-quality automated tests that produce a 50% coverage score, and don't really represent your intentions.

**Meaningfulness**: "50% test coverage" is actually meaningless, as far as quality is concerned. It's an arbitrary number, that you have imposed on them. "Why not 40%?" If you give people something meaningless, you can expect them to behave meaninglessly. There is something insulting about having an arbitrary number imposed on you. So it's not only for people easy to game the system, you've just made them more likely to want to do that.

**Engagement**: It's true that "a significant increase" invites questions, but *that is what we want*. As soon as you hear the question "What do you mean by significant?" you and the engineering team are in this together, working *together* to decide on what counts. "What do *you* think would be significant?" And now a conversation can take place, framed by your goals.

The moment your counterpart says: "Perhaps we should aim to ..." they have already accepted the idea of *significant*, and they are working with you to determine what it should mean.

This is a conversation orders of magnitude more valuable than one in which people are tempted to quibble or negotiate about numbers. You will hear *them* say things like: "Well of course they need to be meaningful, useful tests, that address the most fragile part of the code base first." This becomes a commitment that they own, because they have helped define it.

In practice you will often find that they want to take on *too much* - their eagerness becomes something you can harness, instead of something you have to try to generate.

**Opportunity to explain**: You're the expert; you should be delighted to discuss what a "significant" increase in test coverage might look like, and why it counts as significant. You ought to be able to draw people in with your enthusiasm and passion for the topic. What would be exciting about 50%?

**Ambition**: Who has aspirations to "50%"? If that's the metric you set, you lower the sights of the people whom you want to look upwards. You're encouraging them to think small and you've made your own ambitions for them look petty and pedantic.

The use of the qualititative ("significant") really stands out here, but note that it's also employed in the *Started* list: "We have good test coverage information." Use it confidently and intentionally.

In "There is 100% test coverage" 100% isn't just a number: it's completion. But, it only makes useful sense coming *after* the previous conditions, that prepare the mindset and establish the terms of the what we care about and are working towards.


Progression
...........

The conditions in the three levels represent getting in motion, achieving results, and completion. It's a good progression, but it's not the only good one.

Another effective progression, also using three levels, can be to use *Started* to establish a baseline or discover what is actually the case, *First results* to demonstrate substantive progress and *Mature* for evidence of long-term and systematic changes in practice.

The important thing in any case is that each successive level should make use of what has been achieved already, to build on it, and where possible to lock in the results of those so that they can't be lost.

And don't make anything more complicated than it needs to be. It can be perfectly effective for a particular objective to have a small handful of conditions, all listed under the sole level *Done*.


Objective groups
----------------

Once your framework reaches a certain size you'll probably want to categorise your objectives into groups. Automated testing is not the only kind of testing practice that you want to see pursued - perhaps you'll have integration testing and user testing objectives too.

It's partly a matter of convenience, but categorising things also has a useful forcing function. It obliges you to think about the structure and relations in your framework. Even if you don't start creating groups (and you shouldn't until they actually bring some value), you should already be thinking about what they might be.


Unstarted reasons
=================

If an objective hasn't attained one of the defined levels, then it is *unstarted*. There are different reasons why an objective might be unstarted. A reasonable default set is:

* *Deferred* (work is expected to be planned, but not yet)
* *Not applicable* (this objective doesn't apply to this particular project)
* *Blocked* (the work should be done, but some external factor prevents it)
* *Planned* (there is a commitment to start work in the current cycle)

*Blocked* has a forcing function. It highlights a problem that is getting in the way of progress.


Project agreement statuses
==========================

A sensible default set:

* *Deferred* (the team is not yet in a position to make any agreements for the project)
* *Agreed* (the project is being tracked and planned in the dashboard)
* *Planned* (there is no agreement yet, but there will be)


Project review statuses
=======================

In the review phase, each project's *Review status* should be set.

A suggested set of statuses:

* *Unmet* (the team has failed to meet expectations)
* *Mostly met* (expectations have largely been met, with notable gaps) - should be used sparingly
* *Needs review* (the work has been reviewed, but further review is required)
* *Planned* (there is a commitment to start work in the current cycle)

