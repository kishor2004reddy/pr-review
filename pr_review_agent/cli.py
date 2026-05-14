"""Command-line interface for PR review agent."""

import click
from pathlib import Path
from pr_review_agent.git_utils import GitManager, GitDiffError

@click.command()
@click.option(
    '--repo',
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=True,
    help='Path to the git repository to review'
)
@click.option(
    '--base',
    type=str,
    default='main',
    help='Base branch to compare against (default: main)'
)
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    help='Verbose output'
)
def main(repo: str, base: str, verbose: bool):
    """
    Review code differences between current branch and base branch.
    
    Example:
        pr-review --repo ./my-project --base main
        pr-review --repo . --base develop
    """
    click.echo("\n" + "="*60)
    click.echo("🚀 PR Review Agent Starting")
    click.echo("="*60 + "\n")
    
    try:
        # Initialize git manager
        click.echo(f"📂 Repository: {repo}")
        git_manager = GitManager(repo)
        
        # Get current branch info
        current_branch = git_manager.get_current_branch()
        click.echo(f"🌿 Current branch: {current_branch}")
        click.echo(f"📍 Base branch: {base}")
        
        # Get diff stats
        click.echo("\n⏳ Analyzing differences...")
        stats = git_manager.get_diff_stats(base)
        
        # Display stats
        click.echo("\n📊 Diff Statistics:")
        click.echo(f"   • Total files changed: {stats['total_files_changed']}")
        click.echo(f"   • Files added: {stats['files_added']}")
        click.echo(f"   • Files modified: {stats['files_modified']}")
        click.echo(f"   • Files deleted: {stats['files_deleted']}")
        click.echo(f"   • Lines added: {stats['lines_added']}")
        click.echo(f"   • Lines deleted: {stats['lines_deleted']}")
        
        # Get changed files
        changed_files = git_manager.get_changed_files(base)
        
        if changed_files:
            click.echo("\n📝 Changed Files:")
            for file_info in changed_files:
                status_emoji = {
                    'Modified': '✏️',
                    'Added': '✨',
                    'Deleted': '🗑️',
                    'Renamed': '↪️',
                    'Copied': '📋',
                }.get(file_info['change_type'], '📄')
                
                click.echo(
                    f"   {status_emoji} {file_info['path']} "
                    f"({file_info['change_type']})"
                )
        else:
            click.echo("\n✅ No changes found!")
            return
        
        # Get diff
        click.echo("\n⏳ Retrieving full diff...")
        diff = git_manager.get_diff(base)
        
        if diff:
            click.echo("\n" + "="*60)
            click.echo("📄 Code Diff:")
            click.echo("="*60 + "\n")
            
            # Show first 50 lines of diff as preview
            diff_lines = diff.split('\n')[:50]
            for line in diff_lines:
                if line.startswith('+') and not line.startswith('+++'):
                    click.secho(line, fg='green')
                elif line.startswith('-') and not line.startswith('---'):
                    click.secho(line, fg='red')
                elif line.startswith('@@'):
                    click.secho(line, fg='blue')
                else:
                    click.echo(line)
            
            if len(diff.split('\n')) > 50:
                click.echo(f"\n... ({len(diff.split(chr(10)))-50} more lines)")
        
        # Next steps
        click.echo("\n" + "="*60)
        click.echo("✅ Diff Retrieved Successfully!")
        click.echo("="*60)
        click.echo("\n📋 Next Steps:")
        click.echo("   1. Security analysis")
        click.echo("   2. Code quality check")
        click.echo("   3. Performance analysis")
        click.echo("   4. Test coverage review")
        click.echo("\n⏳ Starting code review agents...\n")
        
    except GitDiffError as e:
        click.secho(f"\nGit Error: {e}\n", fg='red', bold=True)
        raise SystemExit(1)
    except Exception as e:
        click.secho(f"\nError: {e}\n", fg='red', bold=True)
        if verbose:
            import traceback
            traceback.print_exc()
        raise SystemExit(1)

if __name__ == '__main__':
    main()