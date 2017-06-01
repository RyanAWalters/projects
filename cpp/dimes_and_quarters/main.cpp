//////////////////////////////////////////////////////////////////////////////
//		Ryan Walters 	2/20/2016    CSC 325  Louisiana Tech University     //
//													                        //
// This program recursively works its way down 2 trees, meeting in the      //
// middle of the Dimes and Quarters problem. It finds the path by passing   //
// down a record of "ancestors" with each level in the tree and printing    //
// that record out once two matching states have been found in the 2 lists  //
// created from the leaves of both trees.                                   //
//                                                                          //
//			MUST COMPILE WITH C++11	OR HIGHER!!!           					//
//		 " g++ [thisfile].cpp -o [outputname] -std=c++11 "	                //
//																			//
//				This thing is fast       									//
//	EDIT: Re-uploaded because I made it even faster. About 0.050s for me.	//
//////////////////////////////////////////////////////////////////////////////

#include <iostream>
#include <array>
#include <sstream>
#include <math.h>

using namespace std;

// Prototypes
int WrapAround(int num);
int BinToInt(array<bool, 13> binArray);
void Append(int dataValue, int blankPos, string lineage);
array<bool, 13> MakeMove(int fromWhere, int blankPos, array<bool, 13> subArray);
int BuildList(int blankPos, int prev, array<bool, 13> subArray, int level, string lineage);
void MatchAndPrint();

// Our Linked List Nodes
struct node
{
    string lineage; // We will store the previous ancestors in a string, concatenating each child. Like DNA.
    int data;       // The integer representation of the board
    int bPos;       // The position of the empty slot
    node* next;
    node() : lineage(""), data(0), bPos(0), next(nullptr) {}
};

// Some naming to make things more readable
enum def
{
    FROM_2_LEFT = -2,  // From 2 to the left (i.e., We are "moving" the blank spot 2 places to the left)
    FROM_1_LEFT,       // From 1 to the left
    FROM_1_RIGHT = 1,  // From 1 to the right
    FROM_2_RIGHT,      // From 2 to the right

    HEAD = 0,  // Head pointer
    TEMP,      // Temporary pointer
    CURR       // Current Pointer
};

// Global Variables
node* linkedList[2][3];  // An array of pointers for easy manipulation.
int listNum = 0;         // Which tree we are working on
bool stopSearch = 0;     // Time saving procedure. No need to continue searching if found already.

////////////////////////////////////////////////////////   MAIN   //////////////////////////////////////////////////////
int main()
{
    BuildList(0, 0, { 0,0,1,0,1,0,1,0,1,0,1,0,1 }, 0, "");   // Make list from first tree-half (starting state)
    listNum++;                                               // Switching to work on second tree
    BuildList(0, 0, { 0,1,1,1,1,1,1,0,0,0,0,0,0 }, 0, "");   // Make list from second tree-half (solution state)

    MatchAndPrint();                                         // Find a match from the two generated lists and print it
    cout.flush();
}

////////////// Convert binary string to integer /////////////////
int BinToInt(array<bool, 13> binArray)
{
    int result = 0;
    for (int i = 1; i < 13; i++)
    {
        if (binArray[i])
            result += pow(2, 12 - i);
    }
    return result;
}

///////////////// Add node to linked list ////////////////////
void Append(int dataValue, int blankPos, string lineage)
{
    linkedList[listNum][CURR] = new node;
    linkedList[listNum][CURR]->data = dataValue;
    linkedList[listNum][CURR]->bPos = blankPos;
    linkedList[listNum][CURR]->lineage = lineage;

    if (linkedList[listNum][HEAD] == NULL)
    {
        linkedList[listNum][TEMP] = linkedList[listNum][CURR];
        linkedList[listNum][HEAD] = linkedList[listNum][CURR];
        return;
    }

    linkedList[listNum][TEMP]->next = linkedList[listNum][CURR];
    linkedList[listNum][TEMP] = linkedList[listNum][TEMP]->next;
}


/////////////////// Make a move on the board /////////////////////
array<bool, 13> MakeMove(int fromWhere, int blankPos, array<bool, 13> subArray)
{
    int coinToMove = WrapAround(blankPos + fromWhere);
    subArray[blankPos] = subArray[coinToMove];
    return subArray;
}


/////////////////////////// Follow the tree and create a list from the leaves /////////////////////////////
int BuildList(int blankPos, int prev, array<bool, 13> subArray, int level, string lineage)
{
    if (level > 8)
        return 0;

    if (level == 8) {
        Append(BinToInt(subArray), blankPos, lineage); // Add data to new node and link it
        return 0;
    }

    if (level == 0)
    {
        if (listNum == 0) // If first tree, start going in positive direction
        {
            BuildList(WrapAround(blankPos + FROM_1_RIGHT), FROM_1_RIGHT,
                      MakeMove(FROM_1_RIGHT, blankPos, subArray), level + 1, lineage);

            BuildList(WrapAround(blankPos + FROM_2_RIGHT), FROM_2_RIGHT,
                      MakeMove(FROM_2_RIGHT, blankPos, subArray), level + 1, lineage);
            return 0;
        }
        else              // If second tree, go in opposite direction
        {
            BuildList(WrapAround(blankPos + FROM_1_LEFT), FROM_1_LEFT,
                      MakeMove(FROM_1_LEFT, blankPos, subArray), level + 1, lineage);

            BuildList(WrapAround(blankPos + FROM_2_LEFT), FROM_2_LEFT,
                      MakeMove(FROM_2_LEFT, blankPos, subArray), level + 1, lineage);
            return 0;
        }
    }
    else // This block makes sure you only make moves that do not conflict with the previous move
    {
        lineage += to_string(blankPos) + " ";

        if (prev != FROM_2_RIGHT)
            BuildList(WrapAround(blankPos + FROM_2_LEFT), FROM_2_LEFT,
                      MakeMove(FROM_2_LEFT, blankPos, subArray), level + 1, lineage);

        if (prev != FROM_1_RIGHT)
            BuildList(WrapAround(blankPos + FROM_1_LEFT), FROM_1_LEFT,
                      MakeMove(FROM_1_LEFT, blankPos, subArray), level + 1, lineage);

        if (prev != FROM_1_LEFT)
            BuildList(WrapAround(blankPos + FROM_1_RIGHT), FROM_1_RIGHT,
                      MakeMove(FROM_1_RIGHT, blankPos, subArray), level + 1, lineage);

        if (prev != FROM_2_LEFT)
            BuildList(WrapAround(blankPos + FROM_2_RIGHT), FROM_2_RIGHT,
                      MakeMove(FROM_2_RIGHT, blankPos, subArray), level + 1, lineage);
    }
    return 0;
}

//////////////// Search linked lists and find 2 nodes that match then print them ////////////////////
void MatchAndPrint()
{
    linkedList[0][TEMP] = linkedList[0][HEAD];
    linkedList[1][TEMP] = linkedList[1][HEAD];

    while (linkedList[0][TEMP] != NULL)
    {
        if (stopSearch == 1) // Time saving procedure. Break out if already found
            break;

        while (linkedList[1][TEMP] != NULL)
        {
                if (linkedList[1][TEMP]->data == linkedList[0][TEMP]->data &&
                    linkedList[1][TEMP]->bPos == linkedList[0][TEMP]->bPos) // If the board and blank position match
                {
                    cout << linkedList[0][TEMP]->lineage; // Print ancestry of leaf from first tree in order

                    // Reverse the order of ancestry of leaf from second tree
                    string reverse("");
                    string word;
                    istringstream iss(linkedList[1][TEMP]->lineage);
                    while (iss >> word)
                        reverse = word + " " + reverse;

                    reverse.erase(0, 2); // Remove the redundant first character
                    cout << reverse << "0"
                         << endl; // Print the reversed ancestry and a 0 (which must be the last move of any solution)

                    stopSearch = 1;
                    break;
                }
            linkedList[1][TEMP] = linkedList[1][TEMP]->next;
        }
        linkedList[0][TEMP] = linkedList[0][TEMP]->next;
        linkedList[1][TEMP] = linkedList[1][HEAD];
    }
}

/////////////////// Keep numbers between 0 and 12 ////////////////////////
int WrapAround(int num)
{
    if (num < 0)
        return 13 + num;
    if (num > 12)
        return num - 13;
}

