import pytest
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()


@pytest.fixture(scope="session")
def tms_credentials():
    return {
        "host": os.environ.get("TMS_HOST"),
        "port": int(os.environ.get("TMS_PORT", 17159)),
        "token": os.environ.get("TMS_TOKEN"),
    }
