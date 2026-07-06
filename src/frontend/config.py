# UI Configuration Constants
import os

# Available security firms for trading environment
SECURITY_FIRMS = {
    "FUTUSG": "Futu SG (Singapore)",
    "FUTUSECURITIES": "Futu Securities (US)",
    "FUTUINC": "Futu Inc (US)",
    "FUTUAU": "Futu AU (Australia)",
    "FUTUJP": "Futu JP (Japan)",
    "FUTUCA": "Futu CA (Canada)",
    "FUTUMY": "Futu MY (Malaysia)",
}

# Default OpenD settings
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 11111

# Risk profile options
RISK_PROFILES = {
    1: "Very Conservative",
    2: "Conservative",
    3: "Moderate-Conservative",
    4: "Moderate",
    5: "Moderate-Aggressive",
    6: "Aggressive",
    7: "Very Aggressive",
    8: "Growth",
    9: "High Growth",
    10: "Maximum Growth",
}