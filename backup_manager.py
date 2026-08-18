#!/usr/bin/env python3
import json
import hashlib
import shutil
from pathlib import Path

import click

def compute_hash(file_path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Computes the blake2b hash of a file in chunks to minimize memory usage."""
    hasher = hashlib.blake2b()
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()

@click.group()
def cli():
    """A cross-platform file backup and integrity manager."""
    pass

@cli.command()
@click.argument('source_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.argument('checksum_file', type=click.Path(dir_okay=False, path_type=Path))
def checksum(source_dir: Path, checksum_file: Path):
    """
    Generates or updates the checksum ledger.
    
    Reads SOURCE_DIR and records hashes of new files in CHECKSUM_FILE.
    Does not remove entries for deleted source files.
    """
    if checksum_file.exists():
        with open(checksum_file, 'r', encoding='utf-8') as f:
            try:
                ledger = json.load(f)
            except json.JSONDecodeError:
                click.secho("Error: Checksum file is corrupted or not valid JSON.", fg="red")
                return
    else:
        ledger = {}

    new_files_count = 0
    click.echo(f"Scanning {source_dir}...")

    # Iterate through all files in the source directory
    for file_path in source_dir.rglob('*'):
        if file_path.is_file():
            # Generate a relative POSIX path for cross-platform compatibility
            rel_path = file_path.relative_to(source_dir).as_posix()

            if rel_path not in ledger:
                # Compute hash only for new files
                file_hash = compute_hash(file_path)
                ledger[rel_path] = file_hash
                new_files_count += 1
                click.echo(f"Added: {rel_path}")

    if new_files_count > 0:
        # Ensure the parent directory for checksum_file exists
        checksum_file.parent.mkdir(parents=True, exist_ok=True)
        with open(checksum_file, 'w', encoding='utf-8') as f:
            json.dump(ledger, f, indent=2)
        click.secho(f"Successfully added {new_files_count} new files to {checksum_file.name}.", fg="green")
    else:
        click.echo("No new files found. Checksum ledger is up to date.")

@cli.command()
@click.argument('source_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.argument('dest_dir', type=click.Path(file_okay=False, dir_okay=True, path_type=Path))
def copy(source_dir: Path, dest_dir: Path):
    """
    Copies files from source to destination.
    
    Preserves file metadata (timestamps) using shutil.copy2.
    """
    click.echo(f"Copying files from {source_dir} to {dest_dir}...")
    try:
        # dirs_exist_ok=True allows merging into an existing destination directory (Python 3.8+)
        shutil.copytree(source_dir, dest_dir, copy_function=shutil.copy2, dirs_exist_ok=True)
        click.secho("Copy operation complete.", fg="green")
    except Exception as e:
        click.secho(f"Copy failed: {e}", fg="red")

@cli.command()
@click.argument('dest_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.argument('checksum_file', type=click.Path(exists=True, dir_okay=False, path_type=Path))
def verify(dest_dir: Path, checksum_file: Path):
    """
    Verifies destination files against the checksum ledger.
    
    Checks that every file in CHECKSUM_FILE exists in DEST_DIR and matches its hash.
    """
    with open(checksum_file, 'r', encoding='utf-8') as f:
        try:
            ledger = json.load(f)
        except json.JSONDecodeError:
            click.secho("Error: Checksum file is corrupted or not valid JSON.", fg="red")
            return

    ok_count = 0
    failed_count = 0
    missing_count = 0

    click.echo(f"Verifying {len(ledger)} files in {dest_dir}...")

    for rel_path_str, expected_hash in ledger.items():
        # Convert POSIX relative path from JSON back to an OS-native Path object
        file_path = dest_dir / Path(rel_path_str)

        if not file_path.exists() or not file_path.is_file():
            click.secho(f"MISSING: {rel_path_str}", fg="yellow")
            missing_count += 1
            continue

        actual_hash = compute_hash(file_path)
        if actual_hash == expected_hash:
            ok_count += 1
        else:
            click.secho(f"FAILED:  {rel_path_str}", fg="red")
            failed_count += 1

    click.echo("\n--- Verification Summary ---")
    click.echo(f"Total entries: {len(ledger)}")
    
    if ok_count == len(ledger) and len(ledger) > 0:
        click.secho(f"OK:      {ok_count} (All files verified successfully!)", fg="green")
    else:
        click.secho(f"OK:      {ok_count}", fg="green" if ok_count > 0 else "white")
        
    if failed_count > 0:
        click.secho(f"FAILED:  {failed_count}", fg="red")
    if missing_count > 0:
        click.secho(f"MISSING: {missing_count}", fg="yellow")

if __name__ == '__main__':
    cli()
