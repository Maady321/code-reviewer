import httpx
from app.config.settings import settings
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class GitHubService:
    def __init__(self):
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if settings.GITHUB_TOKEN:
            self.headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

    def _parse_repo_url(self, repo_url: str):
        path = urlparse(repo_url).path.strip('/')
        parts = path.split('/')
        if len(parts) >= 2:
            return parts[0], parts[1]
        raise ValueError("Invalid GitHub repository URL")

    def _parse_pr_url(self, pr_url: str):
        path = urlparse(pr_url).path.strip('/')
        parts = path.split('/')
        if len(parts) >= 4 and parts[2] == "pull":
            return parts[0], parts[1], parts[3]
        raise ValueError("Invalid GitHub Pull Request URL")

    async def fetch_repo_files(self, repo_url: str) -> list[dict]:
        owner, repo = self._parse_repo_url(repo_url)
        
        async with httpx.AsyncClient() as client:
            # First fetch repo metadata to get default branch
            repo_info_url = f"https://api.github.com/repos/{owner}/{repo}"
            info_res = await client.get(repo_info_url, headers=self.headers)
            info_res.raise_for_status()
            default_branch = info_res.json().get("default_branch", "main")
            
            # Now fetch tree for the correct branch
            url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
            res = await client.get(url, headers=self.headers)
            res.raise_for_status()
            tree = res.json().get("tree", [])
            
            # Filter files (blob)
            files = [item for item in tree if item["type"] == "blob"]
            return files

    async def fetch_file_content(self, repo_url: str, file_path: str) -> str:
        owner, repo = self._parse_repo_url(repo_url)
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=self.headers)
            res.raise_for_status()
            import base64
            content = res.json().get("content", "")
            return base64.b64decode(content).decode("utf-8")

    async def fetch_pr_diff(self, pr_url: str) -> str:
        owner, repo, pr_num = self._parse_pr_url(pr_url)
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_num}"
        
        diff_headers = self.headers.copy()
        diff_headers["Accept"] = "application/vnd.github.v3.diff"
        
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=diff_headers)
            res.raise_for_status()
            return res.text

github_service = GitHubService()
