from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import uvicorn
from log.logging_config import setup_logging
import logging

# Create logger
setup_logging()
logger = logging.getLogger('my_app')

# Create web server
app = FastAPI()

@app.get("/get-transactions/{node_port}")
async def get_transactions(node_port: int):
    logger.info('Getting transactions')
    ipv8_instance = app.ipv8_instances.get(node_port)
    transactions = ipv8_instance.overlays[0].finalized_txs
    print(transactions, len(transactions))

    if not ipv8_instance:
        raise HTTPException(status_code=404, detail="IPv8 instance not found")
    
    return {"status": "OK", "transactions-made": len(transactions)}

@app.post("/send-message/{node_port}")
async def send_message(node_port: int):
    logger.info(f'Send message api called received, node {node_port}')

    # Trying to get ipv8 instance and error handling it
    ipv8_instance = app.ipv8_instances.get(node_port)
    if not ipv8_instance:
        raise HTTPException(status_code=404, detail="IPv8 instance not found")

    # Sending transaction
    ipv8_instance.overlays[0].send_web_transaction()

    # JSON response
    return {"status": "sent"}

# Host static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

def run_web_server(ipv8_instances):
    app.ipv8_instances = ipv8_instances
    port = 8000

    logger.info(ipv8_instances)

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
