import os
import uvicorn

if __name__ == "__main__":
    source_directory = os.path.dirname(os.path.realpath(__file__))
    os.environ["UVICORN_RELOAD_DIRS"] = source_directory

    source_directory = os.path.dirname(os.path.realpath(__file__))
    os.environ["UVICORN_RELOAD_DIRS"] = source_directory
    uvicorn.main()