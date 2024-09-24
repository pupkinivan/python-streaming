from locust import HttpUser, task, between


class StreamingUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def get_audio_file_stream(self):
        self.client.get("/audios/file-stream")

    @task
    def get_audio_streaming_response(self):
        self.client.get("/audios/streaming-response")

    @task
    def get_data_stream(self):
        self.client.get("/data/stream")

    @task
    def get_websocket_data(self):
        self.client.get("/data/websocket")

    @task
    def get_chat_response(self):
        self.client.get(
            "/chat",
            data={"message": "Tell me a joke about pirates and quantum physics."}
        )