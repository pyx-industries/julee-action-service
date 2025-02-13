import warnings
from datetime import UTC

def pytest_configure(config):
    # Add multiple warning filters to catch all variations
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        message=".*datetime.datetime.utcnow.*",
        module="botocore.*"
    )
    
    # Add a more general filter as backup
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        message=".*utcnow.*",
        module="botocore.*"
    )
    
    # Force warnings to be treated as errors except for the filtered ones
    warnings.filterwarnings("error")
