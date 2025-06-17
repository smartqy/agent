# Marketing Analytics Agent Project

This project implements a marketing analytics agent using LangChain and OpenAI's GPT-4 to analyze campaign and user behavior data. The agent uses a graph database (Neo4j) to store and query data.

## Project Structure

- `app/agent.py`: The core agent class that processes user queries.
- `app/tools.py`: Defines the tools used by the agent for analysis.
- `app/data_loader.py`: Loads and inserts data into Neo4j.
- `app/main.py`: Demonstrates how to run the agent.
- `ui/streamlit_app.py`: A Streamlit app for data loading and visualization.
- `config/.env_loader`: Environment variables for Neo4j and OpenAI API.
- `data/dummy_graph_data.json`: Mock graph data for testing.
- `requirements.txt`: Lists all project dependencies.

## Setup Instructions

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**

   Create a `.env_loader` file in the `config` directory with the following content:

   ```
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your-password
   OPENAI_API_KEY=your-api-key
   ```

3. **Run the Agent**

   ```bash
   python app/main.py
   ```

4. **Run the Streamlit App**

   ```bash
   streamlit run ui/streamlit_app.py
   ```

## Example Usage

The agent is configured to analyze campaign and user behavior data. You can modify the query in `app/main.py` to test different analysis requests.

## Next Steps

- Integrate with a real graph database (e.g., Neo4j).
- Implement more advanced querying and analysis features.
- Add a web interface for interactive queries.
