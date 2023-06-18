---
layout: post
title:  "Ruining games with programming: Digits"
date:   2023-06-18 14:08:20 -0400
categories: ruining-games programming
---

If you're looking to fill the Wordle shaped hole in your heart, [Digits](https://www.nytimes.com/games/digits) 
is a fun math game recently released by The New York Times.  The rules are simple:

1.  You're given six numbers, and a separate target number.
2.  Using only addition, subtraction, multiplication, and division, create an expression that evaluates to the target number.
3.  No negative numbers or fractions are allowed, and not all numbers need be used.

If you had fun playing 24 by yourself as a kid, then you'll love this game.  At least, that's what I thought until they gave me this problem:

(Image 0 here, the puzzle that stumped me)

I hope that you solve this one quickly and enjoyably.  I'm embarassed to say I spent 45 minutes trying to figure this one out, while at work, and didn't get the answer.  This infuriating encounter reminded me of this quote I first read in Peter Norvig's [Sudoku](https://norvig.com/sudoku.html) post:

> Sudoku is "a denial of service attack on human intellect".

Why am I spending time number crunching when my computer can do that for me?? I should write a Digits solver for fun and to convince myself never to spend 45 minutes that way again.

### Representation

As you play Digits, you sequentially choose numbers and operations, gradually removing numbers hoping to eventually find the target number.  But what you're actually doing is building an _arithmetic tree_.  For example, if you type `5 + 7`, that's equivalent to the tree below:

(Image 1 Here)

A more complex expression, like `(5 + 7) * 11`, would be equivalent to a more complex tree:

(Image 2 Here)

Notice that complex expressions can be made of integer expressions _or_ complex sub-expressions.  For a particular Digits puzzle, the solution will be a complex expression that evaluates to the puzzle target:

(Image 3 Here)

In our digits game, there are two kinds of expressions; regular integers (like `5`), or binary expressions (like `5 + 7`).  Binary expressions are made up of 
a left hand side, an operator (`+`, `-`, `*`, `/`) and a right hand side.  They're also more interesting because the left & right sides don't need to be just integers, they can also be binary expressions:

{% highlight kotlin %}
enum class Operator {
    PLUS,
    MINUS,
    TIMES,
    DIVIDED_BY;
}

sealed class Expr {

    data class IntExpr(val value: Int) : Expr()

    data class BinaryExpr(private val left: Expr, private val right: Expr, private val operator: Operator): Expr()
}

IntExpr(value = 5)

BinaryExpr(
  left = IntExpr(5),
  right = IntExpr(7),
  operator = Operator.PLUS
)
{% endhighlight %}

Add a little logic for evaluation, and we're done with the data representation of Digit solutions:

{% highlight kotlin %}
sealed class Expr {

    abstract val value: Int

    data class IntExpr(override val value: Int) : Expr() {
        override fun toString() = value.toString()
    }

    data class BinaryExpr(private val left: Expr, private val right: Expr, private val operator: Operator): Expr() {

        override val value get() =
            when (operator) {
                Operator.PLUS -> left.value + right.value
                Operator.MINUS -> left.value - right.value
                Operator.TIMES -> left.value * right.value
                Operator.DIVIDED_BY -> {
                    check(right.value != 0 && (left.value % right.value != 0))
                    left.value / right.value
                }
            }

        override fun toString() = "($left $operator $right)"
    }
}
{% endhighlight %}

### Solver

If a Digits puzzle can be solved with a particular expression tree, then we can find that solution by constructing every possible expression tree from our set of numbers, and choosing the one which evaluates to the target number.  Due to the recursive structure of our expressions, I'm using a recursive, depth first search algorithm as follows:

1.  Consider the base case; if the target number is already in our set of numbers, then the solution is simply an integer expression of the target.  Easy peasy.
2.  Otherwise, create a new subset of numbers to search by applying an operation to a number `n`, and the target number.
3.  Recursively search for a solution with the new target and the remaining numbers.  If one exists, return a new binary expression corresponding to the operation and `n` that we chose.

{% highlight kotlin %}

object Digit {

    fun solve(target: Int, numbers: Set<Int>) = solveInternal(target = target, numbers = numbers)

    private fun solveInternal(target: Int, numbers: Set<Int>): Expr? {
        if (target in numbers) {
            return Expr.IntExpr(target)
        }

        val pairsToSearch =
            Operator
                .values()
                .flatMap { op ->
                    val numbersToSearch =
                        when (op) {
                            Operator.PLUS, Operator.MINUS, Operator.DIVIDED_BY -> numbers
                            Operator.TIMES -> numbers.filter { target % it == 0 }.toSet()
                        }

                    numbersToSearch.map { n ->
                        val newTarget =
                            when (op) {
                                Operator.PLUS -> target - n
                                Operator.MINUS -> target + n
                                Operator.TIMES -> target / n
                                Operator.DIVIDED_BY -> target * n
                            }
                        Triple(n, op, newTarget)
                    }
                }
                .shuffled()

        for ((number, operator, newTarget) in pairsToSearch) {
            val newNumbers = numbers.minus(number)
            val solution = solveInternal(target = newTarget, numbers = newNumbers)

            if (solution != null) {
                return Expr.BinaryExpr(
                    left = solution,
                    operator = operator,
                    right = Expr.IntExpr(number)
                )
            }
        }

        return null
    }
}
{% endhighlight %}

And finally, we solve:

{% highlight kotlin %}
import kotlin.system.measureTimeMillis

fun main(args: Array<String>) {
    Digit.solve(
      target = 469,
      numbers = setOf(5, 7, 11, 13, 19, 23)
    )
}

{% endhighlight %}

### Performance

Some implementation details:
 - The rules dictate that there are no fractions allowed, so we don't need to consider a multiplication operation for numbers `n` that are not fractions of the target.
 - While it is not explicit in the rules, I've never seen a Digits puzzle with duplicate numbers, so a Set<Int> seems like the most performant way to represent the candidate numbers.
 - I introduced `.shuffled()` to avoid deterministic searching, but opted not to do any other kinds of optimization.

For the puzzle that stumped me, `Digits.solve(469, setOf(5, 7, 11, 13, 19, 23))` produces an answer in ~43ms, which is 62,000x faster than me.  On the other hand, it took 30 minutes to write the algorithm, so the total speed has only improved by ~30%.  To keep the speedup factor above 1, I will not be attempting any other optimizations.  If you have ideas for optimizations and improvements, please [play with the code]() and let me know.

Thanks for reading!
