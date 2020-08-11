# Checkers-AI-2

This is another attempt at making a checkers-playing program.
Previous attempts failed largely due to fundamental misunderstandings regarding how to find, format, and execute moves with recursion involved.
Another issue was that the gathering of possible moves was too closely tied to the evaluation and execution of the moves.

These problems, among others, are now solved as follows:

- Move structure is much more clearly defined (each move is a list of pairs of positions)
- The move detection is completely isolated from the board evaluation code
- Magic numbers have been replaced with constant values to make customization easier

This program tries to use alpha-beta pruning to determine the best move available for a given player,
though there may be one or more problems with the actual implementation.
