# Data streaming
curl --location 'http://localhost:5000/data/stream' --no-buffer

# Chatting for Flask
curl --location 'http://localhost:5000/chat' --no-buffer \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "ivan",
    "message": "Please tell me a joke about pirates and quantum physics"
}'

# Chatting for FastAPI
curl --location 'http://localhost:5000/chat' --no-buffer \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "ivan",
    "message": "Please tell me a joke about pirates and quantum physics"
}'