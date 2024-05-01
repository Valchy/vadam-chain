# Week 2 Report

## Overview:

During the second week we started to move things a little but once again put too much time into getting code functionalities to work. Most of our time was spent debugging and trying to figure out why we cannot even run the code. This unfortunately, made continuing with new features difficult to implement as well as test since they were not working in the first place.

## What we did:

-   Using the python logger library we were able to implement logging on our network.
-   We integrated testing as per the IPv8 library examples. We are now testing for …. but fail to verify these tests as our functionalities don’t all work yet.
-   We integrated push-based gossip with ring topology and TTL of 3 → needs to be tested.
-   We have balance of users and add / subtract based on transactions.
-   We were able to do most of the logic for blocks → needs to be tested.
-   We wrote pseudo code for block logic but haven’t implemented it yet as we need blocks and gossip first to run correctly.

## Takeaways:

We now understand the strengths of the people in the group and we have adjusted the tasks accordingly. There is still room for improvement which is what we plan to do in week 3.

## Plan for week 3:

-   Finish functionalities we were not able to do in week 2 but had plan from week 1.
-   Think more about the frontend and about the demo we have to do on Friday.

    -   API Layer - here we have a python web server which handles API responses and connects the backend, the blockchain network and the frontend. We keep it simple and limit the functionalities to the bear minimum. Main points:
        -   `POST /login` to authenticate
        -   `GET /users` returns all users (their addresses)
        -   `GET /balance` returns balance of authenticated user
        -   `GET /transactions` returns all approved transactions
        -   `POST /transaction` make a transaction from authenticated account
    -   Frontend Layer - this will be a simple, fast and responsive react app. The user will be able to authenticate with a user name and a password. We will have a set of predefined users e.g 100 generated as mentioned in the task. Main points:
        -   `Authentication` (login) screen
        -   `Authenticated screen` (dashboard to see balance, send and see transactions)
        -   `Account balance` (start with 100 USD by default)
        -   `Send transaction from list of users` (addresses)
