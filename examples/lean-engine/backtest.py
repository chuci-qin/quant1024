#!/usr/bin/env python3
"""
Run Mag 7 Alpha + Beta strategy backtest

Usage:
    python run.py

Environment variables (optional):
    QC_USER_ID: QuantConnect User ID
    QC_API_TOKEN: QuantConnect API Token
"""

import os
from quant1024 import qc


# ==================== Configuration ====================
DEFAULT_USER_ID = "459421"
DEFAULT_API_TOKEN = "d138585ac3fdc018d036829365a441cba74a819631b07704d11ac374db2bb228"

STRATEGY_FILE = "main.py"


def main():
    # Get authentication info from environment variables or defaults
    user_id = os.environ.get("QC_USER_ID") or DEFAULT_USER_ID
    api_token = os.environ.get("QC_API_TOKEN") or DEFAULT_API_TOKEN

    # Run backtest
    qc.run_backtest(
        user_id=user_id,
        api_token=api_token,
        strategy_file=STRATEGY_FILE,
        export_json=True,
    )


if __name__ == "__main__":
    main()
