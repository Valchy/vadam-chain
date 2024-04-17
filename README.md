# VDAM-CHAIN

This code serves as a foundational template for the cs409 - Fundamentals of Blockchain-based Systems. It has been rigorously tested on Ubuntu 20.04 and MacOS 14, and should be compatible with Windows systems.

**Note:** Ensure that Python version 3.8 or higher is installed when running this code locally.

## Before you start

1. Create an virtual environment by running `python -m venv .venv`
2. Activate it bu running `source .venv/Scripts/activate` or `source .venv/bin/activate`
3. Download required packages with `pip install -r requirements.txt`
4. If you need to deactivate the virtual environment run `deactivate`

## Documentation

-   [IPv8 Documentation](https://py-ipv8.readthedocs.io/en/latest/index.html)
-   [Asyncio Documentation](https://docs.python.org/3/library/asyncio.html): Asyncio is extensively utilized in this code's implementation.

## File Structure

-   **src:** Contains all the Python source files.
-   **src/algorithms:** Houses code for various distributed algorithms.
-   **topologies/default.yaml:** Lists the addresses of participating processes in the algorithm.
-   **Dockerfile:** Describes the image used by docker-compose.
-   **docker-compose.yml:** YAML file that describes the system for docker-compose.
-   **docker-compose.template.yml:** YAML file used as a template for the `src/util.py` script.
-   **run_echo.sh:** Script to run the echo example.
-   **run_election.sh:** Script to run the ring election example.

## Topology File

The topology file (located in `./topologies`) defines how nodes in the system are interconnected. It comprises a YAML file listing node IDs along with their corresponding connections to other nodes. To alter the number or type of nodes in a topology, adjust the `util.py` script.

## Remarks

1. This template is provided as a starting point with functioning messaging between distributed processes. You are encouraged to modify any of the files as per your requirements.
2. Ensure the topology is aligned with the assignment specifications. The default `util.py` creates a ring topology. Modify the script if you need a different topology (e.g., fully-connected, sparse network).

## Prerequisites

-   Docker
-   Docker-compose
-   (Python >= 3.8 if running locally)

To install dependencies, use:

```bash
pip install -r requirements.txt
```

The expected output should be identical whether running with docker-compose or locally.

## Docker Examples

### Running 100 nodes

```bash
#!/bin/bash
NUM_NODES=100
python src/util.py $NUM_NODES topologies/blockchain.yaml blockchain
docker compose build
docker compose up --scale node=$NUM_NODES
```

### Echo Algorithm

```bash
NUM_NODES=2
python src/util.py $NUM_NODES topologies/echo.yaml echo
docker compose build
docker compose up
```

**Expected Output:**

```text
in4150-python-template-node1-1  | [Node 1] Starting
in4150-python-template-node0-1  | [Node 0] Starting
in4150-python-template-node0-1  | [Node 0] Got a message from node: 1.   current counter: 1
in4150-python-template-node1-1  | [Node 1] Got a message from node: 0.   current counter: 2
in4150-python-template-node0-1  | [Node 0] Got a message from node: 1.   current counter: 3
in4150-python-template-node1-1  | [Node 1] Got a message from node: 0.   current counter: 4
in4150-python-template-node0-1  | [Node 0] Got a message from node: 1.   current counter: 5
in4150-python-template-node1-1  | [Node 1] Got a message from node: 0.   current counter: 6
in4150-python-template-node0-1  | [Node 0] Got a message from node: 1.   current counter: 7
in4150-python-template-node1-1  | [Node 1] Got a message from node: 0.   current counter: 8
in4150-python-template-node0-1  | [Node 0] Got a message from node: 1.   current counter: 9
in4150-python-template-node1-1  | Node 1 is stopping
in4150-python-template-node1-1  | [Node 1] Got a message from node: 0.   current counter: 10
in4150-python-template-node1-1  | [Node 1] Stopping algorithm
in4150-python-template-node0-1  | Node 0 is stopping
in4150-python-template-node0-1  | [Node 0] Got a message from node: 1.   current counter: 11
in4150-python-template-node0-1  | [Node 0] Stopping algorithm
in4150-python-template-node1-1 exited with code 0
in4150-python-template-node0-1 exited with code 0
```

### Ring Election Algorithm

```bash
NUM_NODES=4
python src/util.py $NUM_NODES topologies/election.yaml election
docker compose build
docker compose up
```

**Expected Output:**

```text
in4150-python-template-node2-1  | [Node 2] Starting
in4150-python-template-node0-1  | [Node 0] Starting
in4150-python-template-node3-1  | [Node 3] Starting
in4150-python-template-node1-1  | [Node 1] Starting
in4150-python-template-node3-1  | [Node 3] Starting by selecting a node: 0
in4150-python-template-node0-1  | [Node 0] Got a message from with elector id: 3
in4150-python-template-node1-1  | [Node 1] Got a message from with elector id: 3
in4150-python-template-node2-1  | [Node 2] Got a message from with elector id: 3
in4150-python-template-node3-1  | [Node 3] Got a message from with elector id: 3
in4150-python-template-node3-1  | [Node 3] we are elected!
in4150-python-template-node3-1  | [Node 3] Sending message to terminate the algorithm!
in4150-python-template-node0-1  | [Node 0] Stopping algorithm
in4150-python-template-node1-1  | [Node 1] Stopping algorithm
in4150-python-template-node2-1  | [Node 2] Stopping algorithm
in4150-python-template-node3-1  | [Node 3] Stopping algorithm
```

## Local Examples

The expected output is consistent with running through docker-compose.

### Echo Algorithm

```bash
python src/run.py 0 topologies/echo.yaml echo &
python src/run.py 1 topologies/echo.yaml echo &
```

### Ring Election Algorithm

```bash
python src/run.py 0 topologies/election.yaml election &
python src/run.py 1 topologies/election.yaml election &
python src/run.py 2 topologies/election.yaml election &
python src/run.py 3 topologies/election.yaml election &
```

# Blockchain Project Report

In our project each member of our team made his impact. We tried to distribute tasks equally. Everyone did their best to complete their tasks.

Here are the tasks that we managed to do:

Periodically create dummy transaction, include also signature and public key
This was done with the crypto library in python, which overcomplicated the whole process and turns out was unnecessary as this functionality is already in ipv8.

On receive: Validate the transaction: if signature is correct

Merkle tree transaction storage
Done via adding Block class in the blockchain.py and merkle_root and merkle_proof in the utils.py.

Run locally multiple peers (~100 nodes)
Done via changes in the docker-compose file.

Report the topology (graph of the topology)
Two graphics get generated using a python library. We plot 200 nodes and connected them sparsely or densely, depending on the algorithm used.

Change the default rules for IPv8 to create sparse topology and very dense (all connected)
Added an overlay, to change the max_peers variable of the community.

Design a simple Push-based Gossip

Preliminary benchmarks and Tests of our system

# Blockchain Design Plan

0. Make sure we use python logger everywhere!

1. Run communities, we need 100 nodes with semi-dense topology.

2. Once we have the network running we need to start testing making transactions.

3. For this we implement push gossip algorithm.

4. Using test library of IPv8 we test and make sure all nodes receive the transaction.

5. Then we start scaling number of transactions, benchmarking and logging the results.

6. Knowing the network's max capacity lets start adjusting the overlay configuration.

7. We iterate and optimise the network as much as possible (pull-based gossip?).

8. Now, let's start creating blocks. We will use proof-of-stake algorithm.

9. We create the API layer and test API requests which will trigger transactions.

10. A web application layer gets added which can interact with the API (backend).

## API Layer

Here we have a python web server which handles API responses and connects the backend, the blockchain network and the frontend. We keep it simple and limit the functionalities to the bear minimum.

Main points:

-   `POST /login` to authenticate
-   `GET /users` returns all users (their addresses)
-   `GET /balance` returns balance of authenticated user
-   `GET /transactions` returns all approved transactions
-   `POST /transaction` make a transaction from authenticated account

## Frontend Layer

This will be a simple, fast and responsive react app. The user will be able to authenticate with a user name and a password. We will have a set of predefined users e.g 100 generated as mentioned in the task.

Main points:

-   Authentication (login) screen
-   Authenticated screen (dashboard to see balance, send and see transactions)
-   See account balance (start with 100 USD by default)
-   Send transaction from list of users (addresses)
