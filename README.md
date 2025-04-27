# Runner

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/) [![Docker](https://img.shields.io/badge/docker-ready-blue)](https://www.docker.com/) [![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/diogotoporcov/Runner/blob/refactor/core-logic/LICENSE)

Runner is a Discord bot that securely executes code inside Docker containers. It isolates user-submitted code in a sandboxed environment, returning output directly to Discord while protecting the host system.

---

### How to Run the Code

#### Prerequisites

-   Python 3.9 or newer
    
-   Docker installed and running
    

#### Steps to Run

1.  **Create and Activate a Virtual Environment (Recommended)**  
    It is recommended to use a virtual environment to manage dependencies cleanly.
    
    ```bash
    python -m venv .venv
    ```
    
    Activate the environment:
    
    -   On **Windows**:
        
        ```bash
        .venv\Scripts\activate
        ```
        
    -   On **macOS/Linux**:
        
        ```bash
        source .venv/bin/activate
        ```
        
2.  **Install dependencies**  
    With the virtual environment activated, install the required packages:
    
    ```bash
    pip install -r requirements.txt
    ```
    
3.  **Set up `.env`**  
    Create a file named `.env` in the project’s root directory with the following content:
    
    ```dotenv
    TOKEN=bot-token-here
    PREFIX=!
    ```
    
4.  **Run Runner**  
    Once everythinng is configured, you can use the following command to run the bot:
    
    ```bash
    python main.py
    ```
    

The Bot will handle:

-   Launching a temporary Docker container
    
-   Executing the provided code
    
-   Monitoring execution time
    
-   Returning output or killing the process if it exceeds the timeout

## Example Usage

Once the bot is running, you can execute code directly from Discord by:

-   Tagging the bot and supplying code enclosed in triple backticks and the language identifier.  
    Example:
    
    ![Example](https://i.imgur.com/h1FpS74.png)
    
-   Tagging the bot and uploading a file in the same message.  
    Example:
    
    ![Example](https://i.imgur.com/IYLx8wq.png)


## Limitations

Currently, the bot does not support interactive inputs such as `input()` in Python or other forms of keyboard/mouse interaction. If the received code contains input prompts, it will likely time out since the bot cannot handle real-time user input.

## License

This project is licensed under the MIT License — see `LICENSE` file for more information.
