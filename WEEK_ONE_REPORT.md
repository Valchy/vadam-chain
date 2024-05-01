# Week 1 Report

## Overview:

In our project each member of our team made his impact. We tried to distribute tasks equally. Everyone did their best to complete their tasks.

During the first week of this project, as a team, we realised we had actually underestimated the complexity of the project. Another issue we faced was the collaboration the project required. As we started splitting and giving each person a task, we soon found that some functionalities depended on others which started slowing us down as we missed any management in the group.

## What we did:

-   We were able to run project within a docker container and simulate a bloackchain environemtn with roughly around 100 nodes running at the same time.
-   Periodically create dummy transaction, include also signature and public key
    This was done with the crypto library in python, which overcomplicated the whole process and turns out was unnecessary as this functionality is already in ipv8.
-   We have graphs of dense and sparse topology which get generated with a python script. Two images then get saved in a “graphs” directory.
-   Merkle tree database for storing transactions. We also have a memory pool array for unprocessed ones.

## Plan for week 2

We created a rough plan for the following week to come of the functionalities we wanted our end project to contain and the steps to achieve them:

0. Make sure we use python logger everywhere!
1. Run communities, we need 100 nodes with semi-dense topology.
2. Once we have the network running we need to start testing making transactions.
3. For this we implement push gossip algorithm.
4. Using test library of IPv8 we test and make sure all nodes receive the transaction.
5. Then we start scaling number of transactions, benchmarking and logging the results.
6. Knowing the network's max capacity lets start adjusting the overlay configuration.
7. We iterate and optimise the network as much as possible (pull-based gossip?).
8. Now, let's start creating blocks. We will use proof-of-work algorithm.
9. We create the API layer and test API requests which will trigger transactions.
10. A web application layer gets added which can interact with the API (backend).
