from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import uvicorn
from log.logging_config import setup_logging
import logging
from pydantic import BaseModel

class TransactionBodySend(BaseModel):
    node_id: int
    peer_id: int
    amount: int

class TransactionBodySwap(BaseModel):
    node_id: int
    coin: str
    amount: int

# Create logger
setup_logging()
logger = logging.getLogger('my_app')

# Create web server
app = FastAPI()

@app.get("/get-transactions/{node_port}")
async def get_transactions(node_port: int):
    logger.info('Received API requst to GET Transactions...')

    ipv8_instance = app.ipv8_instances.get(node_port)
    pending_transactions = ipv8_instance.overlays[0].pending_txs
    finalized_transactions = ipv8_instance.overlays[0].finalized_txs
    transactions = []

    for tx in pending_transactions:
        transactions.append({
            "status": "pending",
            "hash_id": tx.tx_id,
            "amount": tx.amount,
            "sender": tx.sender,
            "receiver": tx.receiver
        })

    for tx in finalized_transactions:
        transactions.append({
            "status": "processed",
            "hash_id": tx.tx_id,
            "amount": tx.amount,
            "sender": tx.sender,
            "receiver": tx.receiver
        })
    
    return {"status": "OK", "transactions": transactions}

@app.post("/send-transaction")
async def send_message(data: TransactionBodySend):
    logger.info(f'Send message api called received, node {data.node_id}...')

    # Todo: Error handling if node_id and peer_id are valid

    # Sending transaction
    ipv8_instance = app.ipv8_instances.get(data.node_id).overlays[0]
    ipv8_instance.send_web_transaction(data.peer_id, int(data.amount))

    # JSON response
    return {"status": "sent", "node_id": data.node_id, "peer_id": data.peer_id, "amount": data.amount}

@app.post('/swap-currency')
async def swap_currency(data: TransactionBodySwap):
    # Sending transaction
    ipv8_instance = app.ipv8_instances.get(data.node_id).overlays[0]
    ipv8_instance.web_uniswap_transaction(data.coin, int(data.amount))

    # JSON response
    return {"status": "sent", "node_id": data.node_id, "coin": data.coin, "amount": data.amount}

# Host static files
app.mount("/", StaticFiles(directory="frontend/build", html=True), name="static")

def run_web_server(ipv8_instances):
    app.ipv8_instances = ipv8_instances
    port = 8000

    while True:
        try:
            logger.info(f'Trying to start web server on port {port}...')
            uvicorn.run(app, host="127.0.0.1", port=port)
            break  # If the server starts successfully, break the loop
        except OSError as e:
            if e.errno == 98:  # Error code for address already in use
                logger.warning(f"Port {port} is already in use. Trying the next one...")
                port += 1
            else:
                raise  # Reraises any other exception

if __name__ == "__main__":
    run_web_server()
