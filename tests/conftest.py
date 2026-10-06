import pytest
import os
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="session")
def tms_credentials():
    return {
        "host": os.environ.get("TMS_HOST"),
        "port": int(os.environ.get("TMS_PORT", 17159)),
        "token": os.environ.get("TMS_TOKEN"),
    }
