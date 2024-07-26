# AQMonitoring

## Dataset

[Kaggle: Carbon Monoxide ppm data for regression](https://www.kaggle.com/datasets/anubhav3242/carbon-monoxide-ppm-data-for-regression)

## Tech Stack

- Flask
- Sklearn
- Streamlit (for the web app)
- MongoDB
- Ollama (llama3 model)

## To run llama3

1. Install the ollama software from [here](https://ollama.com/download/)
2. After installing, Run llama3 models

    ```bash
    ollama run llama3
    ```
    Note : The first time you run ollama it will pull the model 
3. Go to how to run section

## How to run

1. Clone the repository
2. Install the dependencies
3. Set up your IP4_ADDRESS on dashboard.py, IOT Code.ino, and server.py
4. Set up your USER and PASSWORD of MongoDB on server.py
5. Run the Flask server
6. Run the Dashboard Streamlit app
