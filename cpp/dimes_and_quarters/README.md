This program was created to find optimal solutions to problems, as well as a test of making extremely complicated algorithms and data structures more efficient.

The Dimes and Quarters problem goes like this:

You have 12 coins in a circle with one empty space among them (13 spaces). The coins alternate between dimes and quarters, each coin sitting in a numbered position. To solve the puzzle, you must get all dimes and all quarters grouped together. I.e., go from DQDQDQDQDQDQ to DDDDDDQQQQQQ or QQQQQQDDDDDD.

You have 4 valid options for a move:
1. You can swap the empty space with the coin DIRECTLY to the LEFT of it
2. You can swap the empty space with the coin DIRECTLY to the RIGHT of it
3. You can swap the empty space with the coin TWO SPACES to the LEFT of it
4. You can swap the empty space with the coin TWO SPACES to the RIGHT of it

This program does NOT solve the puzzle, as that's trivial. This program *finds* the optimal solution to this puzzle.

Before I started coding, I looked at the logic and possible implementation of the problem. The structure we need to find the solution is a tree of all possible moves, each path down the tree representing a sequence of moves. We need to traverse down this tree until we find a solved state. The path that leads to the solved state is the correct sequence of moves. The problem with this? Every node begets 4 more nodes (one for each possible next move). So the number of iterations is 4^(number of moves). The complexity is O(4^n). Not good. Even if it took just 10 moves, Thats over a million iterations we need to check, and each time we check, we have to iterate through the array of 12 coins. Without optimization, the program took a several minutes to complete. I got it down to 0.05 seconds. So how did I optimize this?

As you can start the puzzle going either left or right and there are technically 2 solutions, we can go ahead and split the tree in half (only use 2 of the 4 children in the first level of the tree, as the other two will just give you the reversed solution). Another observation is that at every turn (save for the first), one of the available moves is just undoing the previous one. So if I moved one left on one move, I shouldn't move one right on the next (undo). So we cut the size in half, then we made the number of nodes equal 3^(number of moves). This gives us a final 2*3^(n-1) rather than 4^n, which is much better. So for 10 moves, our new tree has just a bit over 39,000 nodes, as opposed to the over 1,000,000 we had before. These give us a 2,664% increase in efficiency all together.

We should also use to our advantage the fact that we know where we are trying to get. So we can build a second tree up from the solution and meet in the middle, working the problem from both ends. As the trees grow exponentially, having 2 trees half as big is MUCH more efficient than have one full sized tree. So instead of having (2*3^9) = 39,366 nodes, we will have 2*(2*3^5) = 972 nodes. That's an over 4,000% increase in efficiency on top of our previous increases!

Although there are three states (dime, quarter, and empty), I represented the puzzle as a binary array and just used a pointer to point to the empty slot. This offered yet another boost to efficiency.

Lastly, instead of tracing our way down the tree to our current node to check for the matching move sequence (which must be done every node), I thought of a more efficient strategy. Each node instead carries its lineage in a variable like DNA from ancestors. Then we just ask the node for the history of moves that led to it. One single access rather than accessing each node in the sequence and following its pointers down the tree.

You can just read the code from here and it should be self-explanatory. The optimal solution is just 7 moves with a solution sequence of {1, 12, 10, 9, 7, 5, 3, 8, 7, 5, 3, 1, 12, 0}, as found by my program. The sequence is which slot to swap our empty space to during a given move.
