"""Git utilities for getting diffs and repository information."""

import subprocess
from pathlib import Path
from typing import List, Tuple, Optional
import git

class GitDiffError(Exception):
    """Custom exception for git operations."""
    pass

class GitManager:
    """Manages git operations for code review."""
    
    def __init__(self, repo_path: str):
        """
        Initialize GitManager with repository path.
        
        Args:
            repo_path: Path to the git repository
            
        Raises:
            GitDiffError: If the path is not a valid git repository
        """
        try:
            self.repo_path = Path(repo_path).resolve()
            self.repo = git.Repo(self.repo_path)
        except git.InvalidGitRepositoryError:
            raise GitDiffError(f"Not a git repository: {repo_path}")
        except Exception as e:
            raise GitDiffError(f"Error accessing repository: {e}")
    
    def get_current_branch(self) -> str:
        """
        Get the current branch name.
        
        Returns:
            Current branch name
        """
        return self.repo.active_branch.name
    
    def get_branches(self) -> List[str]:
        """
        Get all available branches.
        
        Returns:
            List of branch names
        """
        return [ref.name for ref in self.repo.heads]
    
    def branch_exists(self, branch: str) -> bool:
        """
        Check if a branch exists.
        
        Args:
            branch: Branch name to check
            
        Returns:
            True if branch exists, False otherwise
        """
        try:
            self.repo.heads[branch]
            return True
        except IndexError:
            return False
    
    def get_diff(self, base_branch: str) -> str:
        """
        Get unified diff between current branch and base branch.
        
        Args:
            base_branch: Base branch to compare against (usually 'main' or 'develop')
            
        Returns:
            Unified diff string
            
        Raises:
            GitDiffError: If branch doesn't exist or diff fails
        """
        try:
            # Check if base branch exists
            if not self.branch_exists(base_branch):
                available = self.get_branches()
                raise GitDiffError(
                    f"Branch '{base_branch}' not found.\n"
                    f"Available branches: {', '.join(available)}"
                )
            
            # Get current branch
            current_branch = self.get_current_branch()
            
            if current_branch == base_branch:
                raise GitDiffError(
                    f"You are on the base branch '{base_branch}'.\n"
                    f"Checkout a different branch to review"
                )
            
            # Get the diff
            base_commit = self.repo.heads[base_branch].commit
            current_commit = self.repo.head.commit
            
            # Generate unified diff
            diffs = base_commit.diff(current_commit)
            
            if not diffs:
                return None  # No changes
            
            # Get detailed diff output
            diff_output = base_commit.diff(current_commit, create_patch=True)
            
            return diff_output
            
        except GitDiffError:
            raise
        except Exception as e:
            raise GitDiffError(f"Error getting diff: {e}")
    
    def get_changed_files(self, base_branch: str) -> List[dict]:
        """
        Get list of changed files between branches.
        
        Args:
            base_branch: Base branch to compare against
            
        Returns:
            List of dicts with file info: {path, status, additions, deletions}
        """
        try:
            base_commit = self.repo.heads[base_branch].commit
            current_commit = self.repo.head.commit
            
            diffs = base_commit.diff(current_commit)
            
            changed_files = []
            for diff_item in diffs:
                file_info = {
                    "path": diff_item.b_path or diff_item.a_path,
                    "status": diff_item.status,  # 'M', 'A', 'D', etc.
                    "change_type": self._get_change_type(diff_item.status)
                }
                changed_files.append(file_info)
            
            return changed_files
        except Exception as e:
            raise GitDiffError(f"Error getting changed files: {e}")
    
    @staticmethod
    def _get_change_type(status: str) -> str:
        """Convert git status code to readable text."""
        status_map = {
            'M': 'Modified',
            'A': 'Added',
            'D': 'Deleted',
            'R': 'Renamed',
            'C': 'Copied',
            'T': 'Type Changed',
            'U': 'Unmerged',
            'X': 'Unknown'
        }
        return status_map.get(status[0], 'Unknown')
    
    def get_diff_stats(self, base_branch: str) -> dict:
        """
        Get statistics about the diff.
        
        Args:
            base_branch: Base branch to compare against
            
        Returns:
            Dict with diff statistics
        """
        try:
            base_commit = self.repo.heads[base_branch].commit
            current_commit = self.repo.head.commit
            
            diffs = base_commit.diff(current_commit)
            
            stats = {
                "total_files_changed": len(diffs),
                "files_added": len([d for d in diffs if d.status[0] == 'A']),
                "files_modified": len([d for d in diffs if d.status[0] == 'M']),
                "files_deleted": len([d for d in diffs if d.status[0] == 'D']),
                "lines_added": 0,
                "lines_deleted": 0,
            }
            
            # Try to get line counts
            try:
                diff_output = base_commit.diff(current_commit, create_patch=True)
                if diff_output:
                    for line in diff_output.split('\n'):
                        if line.startswith('+') and not line.startswith('+++'):
                            stats["lines_added"] += 1
                        elif line.startswith('-') and not line.startswith('---'):
                            stats["lines_deleted"] += 1
            except:
                pass
            
            return stats
        except Exception as e:
            raise GitDiffError(f"Error getting diff stats: {e}")