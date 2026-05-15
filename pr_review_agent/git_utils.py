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
        try:
            self.repo_path = Path(repo_path).resolve()
            self.repo = git.Repo(self.repo_path)
        except git.InvalidGitRepositoryError:
            raise GitDiffError(f"Not a git repository: {repo_path}")
        except Exception as e:
            raise GitDiffError(f"Error accessing repository: {e}")

    def get_current_branch(self) -> str:
        return self.repo.active_branch.name

    def get_branches(self) -> List[str]:
        return [ref.name for ref in self.repo.heads]

    def branch_exists(self, branch: str) -> bool:
        try:
            self.repo.heads[branch]
            return True
        except IndexError:
            return False

    def get_diff(self, base_branch: str) -> str:
        try:
            if not self.branch_exists(base_branch):
                available = self.get_branches()
                raise GitDiffError(
                    f"Branch '{base_branch}' not found.\n"
                    f"Available branches: {', '.join(available)}"
                )

            current_branch = self.get_current_branch()
            if current_branch == base_branch:
                raise GitDiffError(
                    f"You are on the base branch '{base_branch}'.\n"
                    f"Checkout a different branch to review"
                )

            current_commit = self.repo.head.commit
            merge_base = self.repo.merge_base(base_branch, current_commit)
            if not merge_base:
                raise GitDiffError(f"No common ancestor found between '{base_branch}' and current branch.")
            base_commit = merge_base[0]

            diffs = base_commit.diff(current_commit)
            if not diffs:
                return None

            patches = [
                item.diff.decode('utf-8', errors='replace')
                for item in base_commit.diff(current_commit, create_patch=True)
            ]
            return '\n'.join(patches) if patches else None

        except GitDiffError:
            raise
        except Exception as e:
            raise GitDiffError(f"Error getting diff: {e}")

    def get_changed_files(self, base_branch: str) -> List[dict]:
        try:
            current_commit = self.repo.head.commit
            base_commit = self.repo.merge_base(base_branch, current_commit)[0]

            diffs = base_commit.diff(current_commit)

            changed_files = []
            for diff_item in diffs:
                ct = diff_item.change_type
                file_info = {
                    "path": diff_item.b_path or diff_item.a_path,
                    "status": ct,
                    "change_type": self._get_change_type(ct)
                }
                changed_files.append(file_info)

            return changed_files
        except Exception as e:
            raise GitDiffError(f"Error getting changed files: {e}")

    @staticmethod
    def _get_change_type(status: str) -> str:
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
        try:
            current_commit = self.repo.head.commit
            base_commit = self.repo.merge_base(base_branch, current_commit)[0]

            diffs = base_commit.diff(current_commit)

            stats = {
                "total_files_changed": len(diffs),
                "files_added": len([d for d in diffs if d.change_type == 'A']),
                "files_modified": len([d for d in diffs if d.change_type == 'M']),
                "files_deleted": len([d for d in diffs if d.change_type == 'D']),
                "lines_added": 0,
                "lines_deleted": 0,
            }

            try:
                for diff_item in base_commit.diff(current_commit, create_patch=True):
                    patch = diff_item.diff.decode('utf-8', errors='replace')
                    for line in patch.split('\n'):
                        if line.startswith('+') and not line.startswith('+++'):
                            stats["lines_added"] += 1
                        elif line.startswith('-') and not line.startswith('---'):
                            stats["lines_deleted"] += 1
            except Exception:
                pass

            return stats
        except Exception as e:
            raise GitDiffError(f"Error getting diff stats: {e}")
