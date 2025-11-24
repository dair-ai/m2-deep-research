"""Exa API wrapper for neural web search."""

import httpx
from typing import List, Dict, Any, Optional
from src.utils.config import Config


class ExaTool:
    """Wrapper for Exa API endpoints."""

    def __init__(self):
        """Initialize Exa API client."""
        self.api_key = Config.EXA_API_KEY
        self.base_url = Config.EXA_BASE_URL
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def search(
        self,
        query: str,
        num_results: int = 10,
        start_published_date: Optional[str] = None,
        end_published_date: Optional[str] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        type: str = "auto",
        use_autoprompt: bool = True,
        text: bool = True,
        highlights: bool = True,
    ) -> Dict[str, Any]:
        """
        Perform neural search using Exa API.

        Args:
            query: Search query
            num_results: Number of results to return
            start_published_date: Filter results published after this date (ISO format)
            end_published_date: Filter results published before this date (ISO format)
            include_domains: List of domains to include
            exclude_domains: List of domains to exclude
            type: Content type filter (auto, news, research paper, pdf, etc.)
            use_autoprompt: Let Exa optimize the query
            text: Include full text content
            highlights: Include relevant highlights

        Returns:
            Dictionary containing search results
        """
        url = f"{self.base_url}/search"

        payload = {
            "query": query,
            "numResults": num_results,
            "useAutoprompt": use_autoprompt,
            "type": type,
            "contents": {
                "text": text,
                "highlights": highlights,
            },
        }

        if start_published_date:
            payload["startPublishedDate"] = start_published_date
        if end_published_date:
            payload["endPublishedDate"] = end_published_date
        if include_domains:
            payload["includeDomains"] = include_domains
        if exclude_domains:
            payload["excludeDomains"] = exclude_domains

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {
                "error": str(e),
                "status": "failed",
                "results": [],
            }

    def find_similar(
        self,
        url: str,
        num_results: int = 5,
        exclude_source_domain: bool = True,
        text: bool = True,
        highlights: bool = True,
    ) -> Dict[str, Any]:
        """
        Find similar content to a given URL using Exa's neural similarity search.

        Args:
            url: URL to find similar content for
            num_results: Number of similar results to return
            exclude_source_domain: Exclude results from the same domain
            text: Include full text content
            highlights: Include relevant highlights

        Returns:
            Dictionary containing similar search results
        """
        api_url = f"{self.base_url}/findSimilar"

        payload = {
            "url": url,
            "numResults": num_results,
            "excludeSourceDomain": exclude_source_domain,
            "contents": {
                "text": text,
                "highlights": highlights,
            },
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(api_url, json=payload, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {
                "error": str(e),
                "status": "failed",
                "results": [],
            }

    def get_contents(
        self,
        ids: List[str],
        text: bool = True,
        highlights: bool = True,
    ) -> Dict[str, Any]:
        """
        Get full content for specific result IDs.

        Args:
            ids: List of Exa result IDs
            text: Include full text content
            highlights: Include relevant highlights

        Returns:
            Dictionary containing content for the specified IDs
        """
        url = f"{self.base_url}/contents"

        payload = {
            "ids": ids,
            "contents": {
                "text": text,
                "highlights": highlights,
            },
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {
                "error": str(e),
                "status": "failed",
                "contents": [],
            }

    def format_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format Exa search results into a standardized structure.

        Args:
            results: Raw results from Exa API

        Returns:
            List of formatted result dictionaries
        """
        if "error" in results or "results" not in results:
            return []

        formatted = []
        for result in results.get("results", []):
            formatted_result = {
                "title": result.get("title", "No title"),
                "url": result.get("url", ""),
                "author": result.get("author"),
                "published_date": result.get("publishedDate"),
                "score": result.get("score", 0),
                "text": result.get("text", ""),
                "highlights": result.get("highlights", []),
                "summary": result.get("summary", ""),
            }
            formatted.append(formatted_result)

        return formatted
