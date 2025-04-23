import os
import uvicorn




if __name__ == "__main__":
    source_directory = os.path.dirname(os.path.realpath(__file__))
    os.environ["UVICORN_RELOAD_DIRS"] = source_directory


    uvicorn.run(
        "backend.src.app:app_factory",
        factory=True,
        reload=True,
        host="127.0.0.1",
        port=8000
    )