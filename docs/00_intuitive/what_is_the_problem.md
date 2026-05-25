# What is the Hadwiger-Nelson problem?

You are given the whole infinite plane. Your job: paint every single point one of $k$ colors, so that any two points that are exactly $1$ unit apart get *different* colors. What is the smallest $k$ that lets you do this?

That smallest $k$ is the **chromatic number of the plane**, written $\chi(\mathbb{R}^2)$. The problem was posed by Hugo Hadwiger and Edward Nelson around 1950. We still do not know the answer.

## What we know

- $k = 1$ doesn't work: pick any point, then a point 1 unit away. They share a color. Fail.
- $k = 2$ doesn't work: take an equilateral triangle of side 1. Three vertices, each at distance 1 from the other two. Any 2-coloring forces two of them to share a color.
- $k = 3$ doesn't work: there is a 7-vertex graph called the **Moser spindle** where every edge is a unit-distance segment, and you cannot 3-color it. So you need at least 4.
- $k = 4$ also doesn't work: in 2018, Aubrey de Grey constructed a 1581-vertex graph where every edge is a unit-distance segment, and you cannot 4-color it. So you need at least 5.
- $k = 7$ does work: there is a clever way to tile the plane with hexagons of slightly-less-than-unit-diameter, color them with 7 colors in a repeating pattern, and make sure same-color hexagons never get close enough for two of their points to be at distance exactly 1.

So:

$$
5 \leq \chi(\mathbb{R}^2) \leq 7.
$$

The truth is either $5$, $6$, or $7$. Nobody knows which.

## Why "exactly 1"?

You might think: if I just avoid distance $1$, why can't I avoid every distance? The answer is that with $k$ colors covering all of the plane, the color classes have to be *big* (by area), and big sets in the plane realize many distances. The unit-distance constraint is the right one because it is the simplest single-distance constraint, and even it is hard.

## Why is this hard?

A typical proof of an upper bound is a coloring (existence). A typical proof of a lower bound is a finite "stubborn" graph (every $k$-coloring fails). To improve the lower bound from $5$ to $6$, somebody has to find a finite unit-distance graph that cannot be $5$-colored. None has been found.

To improve the upper bound from $7$ to $6$, somebody has to construct a coloring scheme using $6$ colors that avoids distance $1$. No such scheme is known.

## What's surprising

The chromatic number of the *rational* plane $\mathbb{Q}^2$ (only rational coordinates) is exactly $2$. So the difficulty is genuinely about the topology of the real line, not just about unit distances or geometry abstractly. This is a clue.

## Next step

Read [`docs/01_undergraduate/moser_spindle.md`](../01_undergraduate/moser_spindle.md) for the explicit construction giving $\chi \geq 4$.
