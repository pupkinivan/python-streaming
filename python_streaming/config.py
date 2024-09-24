import os

from dotenv import load_dotenv, dotenv_values

load_dotenv()
BUFFER_SIZE = int(os.getenv("BUFFER_SIZE", 4096))
RANGED_REQUEST_BUFFERS = int(os.getenv("RANGED_REQUEST_BUFFERS", 10))
HTTP_PORT = int(os.getenv("PORT", 5000))
