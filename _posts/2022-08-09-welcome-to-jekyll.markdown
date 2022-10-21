---
layout: post
title:  "Playing Math; How To Ruin A Game With Analysis"
date:   2022-08-09 14:08:20 -0400
categories: jekyll update
---
My friend Marlee is a teacher.  In March of 2021, we realized that *both* of us are
ridiculed by close friends & family for being grown ass adults who like to play math games.  To celebrate, 
she introduced me to one of her favorite games, which we call Playing Math.

It goes like this:
1.  Choose an integer between 1 and 200
2.  Filter all face cards out of a deck of playing cards
3.  Deal 6 random cards from the deck
4.  Find an algebraic expression using each card value exactly once (Aces have value 1)
5.  Repeat steps 1-5 until the bell rings

I love this game because it can be competitive (race and get points when you find an answer first) or
cooperative (everyone talks through their thought process for the hard ones).  To the chagrine of 
our friends in Tahoe, I played for 90 minutes during that introduction.


{% highlight kotlin %}
sealed class SExp {

  data class Leaf(val num: Double) : SExp()

  data class Expr(val operation: Operation,
                  val left: SExp,
                  val right: SExp) : SExp()

  override fun toString() = when (this) {
    is Leaf -> "$num"
    is Expr -> when (this.operation) {
      PLUS -> "$left + $right"
      MINUS -> "$left - ($right)"
      TIMES -> "$left * ($right)"
      DIVIDED_BY -> "$left / ($right)"
    }
  }
}
{% endhighlight %}

You’ll find this post in your `_posts` directory. Go ahead and edit it and re-build the site to see your changes. You can rebuild the site in many different ways, but the most common way is to run `jekyll serve`, which launches a web server and auto-regenerates your site when a file is updated.

Jekyll requires blog post files to be named according to the following format:

`YEAR-MONTH-DAY-title.MARKUP`

Where `YEAR` is a four-digit number, `MONTH` and `DAY` are both two-digit numbers, and `MARKUP` is the file extension representing the format used in the file. After that, include the necessary front matter. Take a look at the source for this post to get an idea about how it works.

Jekyll also offers powerful support for code snippets:

{% highlight ruby %}
def print_hi(name)
  puts "Hi, #{name}"
end
print_hi('Tom')
#=> prints 'Hi, Tom' to STDOUT.
{% endhighlight %}

Check out the [Jekyll docs][jekyll-docs] for more info on how to get the most out of Jekyll. File all bugs/feature requests at [Jekyll’s GitHub repo][jekyll-gh]. If you have questions, you can ask them on [Jekyll Talk][jekyll-talk].

[jekyll-docs]: https://jekyllrb.com/docs/home
[jekyll-gh]:   https://github.com/jekyll/jekyll
[jekyll-talk]: https://talk.jekyllrb.com/
