"""Web Search Retriever Agent using Exa API."""

import json
import httpx
from typing import Dict, Any, List
from src.tools.exa_tool import ExaTool
from src.utils.config import Config


class WebSearchRetriever:
    """
    Agent that executes Exa searches for provided subqueries and synthesizes findings.
    Uses OpenRouter with Gemini 2.5 Flash for synthesis.
    """

    def __init__(self):
        """Initialize Web Search Retriever."""
        self.exa = ExaTool()
        self.api_key = Config.OPENROUTER_API_KEY
        self.base_url = Config.OPENROUTER_BASE_URL
        self.model = Config.OPENROUTER_MODEL

        self.system_prompt = """You are a web search retrieval specialist.

Your job is to:
1. Execute Exa searches for each provided subquery
2. Use find_similar() on the best results to discover related content
3. Organize findings by relevance and topic
4. Extract key insights from the search results

Return structured results with:
- URLs and titles
- Summaries of key findings
- Relevant quotes/highlights
- How each source contributes to answering the research query

Be comprehensive but focused. Prioritize high-quality, authoritative sources."""

    def search_with_subqueries(self, subqueries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute Exa searches for all subqueries.

        Args:
            subqueries: List of subquery dictionaries from planning agent

        Returns:
            List of search results for each subquery
        """
        all_results = []

        for subquery in subqueries:
            query_text = subquery.get("query", "")
            content_type = subquery.get("type", "auto")
            time_period = subquery.get("time_period", "any")
            include_domains = subquery.get("include_domains")
            exclude_domains = subquery.get("exclude_domains")
            priority = subquery.get("priority", 3)

            # Map time period to date filters (approximate)
            start_date = None
            if time_period == "recent" or time_period == "past_week":
                # Exa uses ISO format dates
                start_date = "2025-11-17T00:00:00.000Z"  # Approximate for recent
            elif time_period == "past_month":
                start_date = "2025-10-24T00:00:00.000Z"
            elif time_period == "past_year":
                start_date = "2024-11-24T00:00:00.000Z"

            # Execute search with more results for deeper research
            search_results = self.exa.search(
                query=query_text,
                num_results=20 if priority <= 2 else 15,  # Increased for deeper research
                start_published_date=start_date,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
                type=content_type,
            )

            # Format results
            formatted_results = self.exa.format_results(search_results)

            # Find similar content for more queries (priority <= 3 instead of <= 2)
            similar_results = []
            if formatted_results and priority <= 3:
                top_url = formatted_results[0].get("url")
                if top_url:
                    similar_response = self.exa.find_similar(
                        url=top_url,
                        num_results=5,  # Increased from 3 to 5
                    )
                    similar_results = self.exa.format_results(similar_response)

            all_results.append({
                "subquery": query_text,
                "priority": priority,
                "results": formatted_results,
                "similar_results": similar_results,
            })

        return all_results

    def synthesize_findings(
        self,
        research_query: str,
        search_results: List[Dict[str, Any]]
    ) -> str:
        """
        Use LLM to synthesize search results into organized findings.

        Args:
            research_query: Original research query
            search_results: Results from Exa searches

        Returns:
            Synthesized findings as a string
        """
        # Prepare context from search results
        context_parts = []
        for result_set in search_results:
            subquery = result_set.get("subquery", "")
            results = result_set.get("results", [])

            context_parts.append(f"\n## Subquery: {subquery}")

            for i, result in enumerate(results[:10], 1):  # Top 10 per subquery for deeper research
                title = result.get("title", "No title")
                url = result.get("url", "")
                highlights = result.get("highlights", [])
                text_excerpt = result.get("text", "")[:1000]  # Increased to 1000 chars for more context

                context_parts.append(f"\n### Result {i}: {title}")
                context_parts.append(f"URL: {url}")
                if highlights:
                    context_parts.append(f"Highlights: {', '.join(highlights[:5])}")  # More highlights
                if text_excerpt:
                    context_parts.append(f"Excerpt: {text_excerpt}...")

        context = "\n".join(context_parts)

        # Create synthesis request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": f"""Research Query: {research_query}

Search Results:
{context}

Organize these findings into a comprehensive, detailed summary. Include:
1. Key findings organized by topic/theme with extensive details
2. Important sources with URLs and brief descriptions
3. Relevant quotes and highlights with context
4. How the sources address the research query
5. Connections and patterns across different sources
6. Notable experts, institutions, or authoritative voices
7. Data, statistics, or concrete examples when available

Be thorough and detailed - this will feed into a comprehensive research report.""",
                },
            ],
            "temperature": 0.5,
            "max_tokens": 6000,  # Increased for more comprehensive synthesis
        }

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]

        except Exception as e:
            return f"Error synthesizing findings: {str(e)}"

    def retrieve(self, research_query: str, subqueries_json: str) -> str:
        """
        Execute web search retrieval for given subqueries.
        This method is called by the supervisor via tool execution.

        Args:
            research_query: Original research query
            subqueries_json: JSON string containing subqueries from planning agent

        Returns:
            Synthesized findings as a string
        """
        try:
            # Parse subqueries
            subqueries_data = json.loads(subqueries_json)
            subqueries = subqueries_data.get("subqueries", [])

            if not subqueries:
                return "Error: No subqueries provided"

            # Execute searches
            search_results = self.search_with_subqueries(subqueries)

            # Synthesize findings
            findings = self.synthesize_findings(research_query, search_results)

            return findings

        except json.JSONDecodeError as e:
            return f"Error parsing subqueries: {str(e)}"
        except Exception as e:
            return f"Error in retrieval: {str(e)}"
