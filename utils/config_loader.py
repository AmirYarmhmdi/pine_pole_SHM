# ============================================================
# utils/config_loader.py
# Utility to safely load configuration from config/config.json
# ============================================================

import json
import os


def load_config(config_dir="config", filename="config.json"):
    """
    Load configuration JSON from the specified directory.

    Parameters
    ----------
    config_dir : str, optional
        Directory containing the configuration file (default: 'config')
    filename : str, optional
        JSON file name (default: 'config.json')

    Returns
    -------
    dict
        Parsed configuration data.

    Raises
    ------
    FileNotFoundError
        If the configuration file does not exist.
    ValueError
        If the JSON content is invalid.
    """
    config_path = os.path.join(config_dir, filename)

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"❌ Config file not found at: {config_path}")

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        raise ValueError(f"❌ Invalid JSON format in {config_path}: {e}")


# Example standalone use
if __name__ == "__main__":
    try:
        cfg = load_config()
        print("✅ Configuration loaded successfully:")
        print(json.dumps(cfg, indent=4))
    except Exception as e:
        print(str(e))
