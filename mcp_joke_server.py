import asyncio
import logging
import requests
from pydantic import BaseModel, Field
from fastmcp.server import FastMCP

# --- Configuration ---
LOG_LEVEL = logging.INFO
JOKE_API_URL = "https://official-joke-api.appspot.com/random_joke"
CONTEXT_MODEL_NAME = "joke-context"
CONTEXT_REFRESH_INTERVAL_SECONDS = 60

# --- Logging Setup ---
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Pydantic Schema for our Context ---
# This defines the structure of the data our MCP server will provide.
# Using Pydantic ensures that our context is always well-formed.
class JokeContext(BaseModel):
    """Defines the data structure for the joke context."""
    setup: str = Field(..., description="The setup part of the joke.")
    punchline: str = Field(..., description="The punchline of the joke.")
    source: str = Field(default="Official Joke API", description="The source of the joke.")

# --- Initialize the FastMCP Application ---
# We provide a title and description for the auto-generated OpenAPI docs.
app = FastMCP(
    title="Joke Context MCP Server",
    description="Provides a random joke as a context for AI agents.",
)

# --- Context State Management ---
# In a real application, this might be a more complex object or backed by a database.
# For this demo, a simple dictionary holds our context model.
context_store = {
    "model": JokeContext(
        setup="Why don't scientists trust atoms?",
        punchline="Because they make up everything!"
    )
}

# --- Core Logic to Update Context ---
def fetch_and_update_joke_context():
    """
    Fetches a new joke from the public API and updates the server's context.
    This function includes error handling for the API call.
    """
    try:
        logging.info("Attempting to fetch a new joke from the API...")
        response = requests.get(JOKE_API_URL, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        
        data = response.json()
        
        # Validate that the response has the keys we expect
        if 'setup' in data and 'punchline' in data:
            new_joke = JokeContext(setup=data['setup'], punchline=data['punchline'])
            context_store["model"] = new_joke
            logging.info(f"Successfully updated context. New joke setup: {new_joke.setup}")
        else:
            logging.warning("API response did not contain 'setup' and 'punchline'. Using existing context.")

    except requests.exceptions.RequestException as e:
        logging.error(f"Could not fetch new joke from API: {e}. Using existing context.")
    except Exception as e:
        logging.error(f"An unexpected error occurred during context update: {e}")


# --- Periodic Task to Keep Context Fresh ---
async def periodic_context_updater():
    """
    An asynchronous task that runs in the background to periodically
    call the context update function.
    """
    logging.info(f"Starting periodic context updater. Refresh interval: {CONTEXT_REFRESH_INTERVAL_SECONDS} seconds.")
    while True:
        fetch_and_update_joke_context()
        await asyncio.sleep(CONTEXT_REFRESH_INTERVAL_SECONDS)

# --- Registering the Context Model with FastMCP ---
@app.on_event("startup")
async def startup_event():
    """
    This function runs when the FastAPI application starts up.
    It registers our context model and starts the background task.
    """
    logging.info("Server starting up.")
    
    # Register the model with FastMCP.
    # The lambda function tells FastMCP how to retrieve the current context.
    app.register_model(
        model_name=CONTEXT_MODEL_NAME,
        model_getter=lambda: context_store["model"],
        model_class=JokeContext,
        description="Provides a random joke that is updated periodically."
    )
    logging.info(f"Model '{CONTEXT_MODEL_NAME}' registered successfully.")
    
    # Start the background task to update the joke
    asyncio.create_task(periodic_context_updater())

if __name__ == "__main__":
    import uvicorn
    # This block allows running the server directly for local development.
    # Use `uvicorn mcp_joke_server:app --reload` for development.
    logging.info("Running server in standalone mode for development.")
    uvicorn.run(app, host="0.0.0.0", port=8000)

