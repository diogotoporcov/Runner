# Runner
Runner is a Discord bot that securely executes code inside Docker containers. It isolates user-submitted code in a sandboxed environment, returning output directly to Discord while protecting the host system.

### How to Run the Code
#### Prerequisites
- Python 3.11 or newer
- Docker installed and running

#### Steps to Run

1. **Create and Activate a Virtual Environment (Recommended)**  
   It is recommended to use a virtual environment to manage dependencies cleanly.

    ```bash
    python -m venv .venv
    ```

    Activate the environment:

    - On **Windows**:
      ```bash
      .venv\Scripts\activate
      ```
    - On **macOS/Linux**:
      ```bash
      source .venv/bin/activate
      ```

2. **Install dependencies**  
   With the virtual environment activated, install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

3. **Set up `.env`**  
   Create a file named `.env` in the project’s root directory with the following content:
    ```dotenv
    TOKEN=bot-token-here
    PREFIX=!
    ```

4. **Run the Runner script**  
   You can execute Python code snippets inside a Docker container using:

    ```bash
    python main.py
    ```

   The script will handle:
   - Launching a temporary Docker container
   - Executing the provided code
   - Monitoring execution time
   - Returning output or killing the process if it exceeds the timeout
    
## Example Usage
Once the bot is running, you can execute code directly from Discord by:
- Simply tagging the bot and supply code enclosed in triple backticks and the language identifier. For example:

    ![Example](https://i.imgur.com/h1FpS74.png)

- Simply tagging the bot and uploading a file in the same message. For Example:
  
    ![Example](https://i.imgur.com/IYLx8wq.png)


## Supported Programming Languages
- Python


## License

This project is licensed under the MIT License — see the `LICENSE` file for more information.
