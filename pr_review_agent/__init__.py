"""PR Review Agent - Intelligent code review using AI agents."""

__version__ = "0.1.0"
__author__ = "Yarramaddi Kishor Kumar Reddy"
__email__ = "kishor04reddy@gmail.com"

from pr_review_agent.git_utils import GitManager, GitDiffError

__all__ = ["GitManager", "GitDiffError"]