# Deep Research Agent

A sophisticated research tool powered by **Minimax M2** with interleaved thinking, **Exa** neural search, and multi-agent orchestration.

## Features

- **Minimax M2 Supervisor**: Uses interleaved thinking to maintain reasoning state across multi-step research
- **Intelligent Planning**: Automatically decomposes research queries into optimized subqueries
- **Neural Web Search**: Leverages Exa API for high-quality, AI-powered web search
- **Comprehensive Reports**: Generates detailed research reports with citations and analysis
- **CLI Interface**: Simple command-line interface with interactive and single-query modes

## Architecture

```
+-----------------------------------------------+
|            Supervisor Agent                   |
|    (Minimax M2 + Interleaved Thinking)        |
+-----------------------------------------------+
                      |
       +--------------+--------------+
       |              |              |
       v              v              v
+------------+ +-------------+ +-----------+
|  Planning  | | Web Search  | | Synthesis |
|   Agent    | |  Retriever  | |   (M2)    |
|  (Gemini)  | |             | |           |
+------------+ +-------------+ +-----------+
                      |
                      v
               +------------+
               |  Exa API   |
               +------------+
```

### Agent Descriptions

1. **Supervisor Agent**:
   - Uses Minimax M2 with Anthropic SDK
   - Implements interleaved thinking (preserves reasoning across turns)
   - Coordinates planning, search, and synthesis
   - Generates final comprehensive research report

2. **Planning Agent**:
   - Uses Gemini 2.5 Flash via OpenRouter
   - Generates 3-5 Exa-optimized subqueries
   - Considers time periods, domains, content types, and priorities

3. **Web Search Retriever**:
   - Uses Gemini 2.5 Flash for synthesis
   - Executes Exa searches with neural search capabilities
   - Finds similar content using Exa's similarity search
   - Organizes findings with sources and highlights

## Installation

### Prerequisites

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) package manager
- API keys for:
  - Minimax (M2 model)
  - OpenRouter (for Gemini)
  - Exa (web search)

### Setup

1. **Install dependencies**:
```bash
cd deep-research-agent
uv sync
```

2. **Configure environment variables**:
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API keys
MINIMAX_API_KEY=your_minimax_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
EXA_API_KEY=your_exa_api_key_here
```

3. **Activate virtual environment** (if needed):
```bash
source .venv/bin/activate
```

## Usage

### Interactive Mode

Run without arguments to enter interactive mode:

```bash
python main.py
```

Then enter your research queries at the prompt:

```
Research Query: What are the latest developments in quantum computing?
```

### Single Query Mode

Run a single research query:

```bash
python main.py -q "What are the latest developments in quantum computing?"
```

### Save Report to File

Save the research report automatically:

```bash
python main.py -q "AI trends in 2025" --save
```

### Verbose Mode

Show detailed progress and thinking blocks:

```bash
python main.py -q "Climate change solutions" --verbose
```

### Interactive Mode Commands

While in interactive mode, you can use these commands:

- `/save <query>` - Save the report to a file
- `/verbose <query>` - Show detailed progress
- `/help` - Show help message
- `exit`, `quit`, or `q` - Exit the program

## How It Works

### 1. Query Planning

When you submit a research query, the **Planning Agent** decomposes it into 3-5 optimized subqueries:

```json
{
  "subqueries": [
    {
      "query": "quantum computing breakthroughs 2025",
      "type": "news",
      "time_period": "recent",
      "priority": 1
    },
    {
      "query": "quantum computing applications cryptography",
      "type": "auto",
      "time_period": "any",
      "priority": 2
    }
  ]
}
```

### 2. Web Search

The **Web Search Retriever** executes each subquery using Exa:

- Performs neural search for each subquery
- Finds similar content for high-priority results
- Extracts highlights and key information
- Organizes findings by relevance

### 3. Synthesis

The **Supervisor Agent** (using Minimax M2 with interleaved thinking):

- Receives all search findings
- Maintains reasoning state across the research process
- Synthesizes a comprehensive report with:
  - Executive summary
  - Key findings organized by theme
  - Detailed analysis
  - Cited sources with URLs

### 4. Interleaved Thinking

The key innovation is **interleaved thinking**:

- The supervisor preserves ALL content blocks (thinking + text + tool_use) in conversation history
- This maintains the reasoning chain across multiple turns
- Results in more coherent, contextualized research reports
- Prevents "state drift" in multi-step workflows

## Project Structure

```
deep-research-agent/
├── README.md                  # This file
├── .env.example               # Environment variables template
├── .env                       # Your API keys (create this)
├── pyproject.toml             # Project dependencies
├── main.py                    # CLI entry point
└── src/
    ├── agents/
    │   ├── supervisor.py           # Minimax M2 supervisor
    │   ├── planning_agent.py       # Query planning
    │   └── web_search_retriever.py # Exa search integration
    ├── tools/
    │   └── exa_tool.py             # Exa API wrapper
    └── utils/
        └── config.py               # Configuration management
```

## API Keys

### Getting API Keys

1. **Minimax M2**: Sign up at [platform.minimax.io](https://platform.minimax.io)
2. **OpenRouter**: Get key at [openrouter.ai](https://openrouter.ai)
3. **Exa**: Register at [exa.ai](https://exa.ai)

### Why These Services?

- **Minimax M2**: Advanced reasoning model with native interleaved thinking support
- **OpenRouter**: Unified API for accessing Gemini and other LLMs
- **Exa**: Neural search engine optimized for research and discovery

## Examples

### Example 1: Technology Research

```bash
python main.py -q "What are the latest breakthroughs in artificial general intelligence?"
```

**Output**: Comprehensive report covering recent AGI developments, key research papers, major announcements, and expert opinions with citations.

### Example 2: Business Intelligence

```bash
python main.py -q "What are the emerging trends in electric vehicle adoption?" --save
```

**Output**: Market analysis with statistics, industry trends, regional adoption rates, and future projections. Report saved to file.

### Example 3: Scientific Research

```bash
python main.py -q "What are the most promising approaches to carbon capture technology?" --verbose
```

**Output**: Technical analysis of carbon capture methods with detailed thinking process visible.

## Advanced Usage

### Customizing Prompts

Edit the system prompts in:
- `src/agents/supervisor.py` - Main coordinator logic
- `src/agents/planning_agent.py` - Query decomposition strategy
- `src/agents/web_search_retriever.py` - Search and synthesis approach

### Adjusting Search Parameters

Modify Exa search parameters in `src/agents/web_search_retriever.py`:
- `num_results`: Number of results per query (default: 5-10)
- `time_period`: Date filtering (recent, past_week, past_month, past_year, any)
- `content_type`: Filter by type (news, research paper, pdf, blog, etc.)

## Troubleshooting

### Configuration Errors

If you see "Missing required API keys":
1. Ensure `.env` file exists (copy from `.env.example`)
2. Verify all API keys are set correctly
3. Check that API keys don't have extra spaces or quotes

### API Errors

If you encounter API errors:
1. Verify your API keys are valid and active
2. Check your API rate limits and quotas
3. Ensure you have sufficient credits/balance

### Import Errors

If you see module import errors:
1. Activate the virtual environment: `source .venv/bin/activate`
2. Install dependencies: `uv sync`
3. Ensure you're running from the project root directory

## Performance

- Average research query: 30-60 seconds
- Depends on:
  - Number of subqueries (3-5)
  - Complexity of search results
  - LLM response times

## Future Enhancements

Potential improvements:
- [ ] Support for additional search engines (Tavily, Perplexity)
- [ ] PDF and document upload for context
- [ ] Multi-turn conversations with follow-up questions
- [ ] Export to different formats (PDF, Markdown, JSON)
- [ ] Web UI interface
- [ ] Caching and result persistence
- [ ] Custom research templates

## License

MIT License - feel free to use and modify for your own projects.

## Acknowledgments

Built with:
- [Minimax M2](https://www.minimax.io/) - Advanced reasoning model
- [Exa](https://exa.ai/) - Neural web search
- [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python) - API client
- [OpenRouter](https://openrouter.ai/) - LLM routing
