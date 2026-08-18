# ArchiveCopy: Backup & Integrity Manager

A robust, cross-platform Python CLI tool designed to safely back up files, allowing you to move them across computers and verify their complete integrity using high-speed blake2b checksums.

## Features

* **Cross-Platform Paths:** Seamlessly generate checksums on Windows and verify them on Linux or macOS (and vice versa). All paths are stored consistently in POSIX format.
* **Incremental Checksums:** Only hash new files. If old files are deleted from your source directory, the script handles it gracefully without breaking your existing ledger.
* **Memory Efficient:** Uses Python's native `hashlib.blake2b` with rapid, chunked binary reads. This ensures you can hash massive files (like 50GB video files) without exhausting system RAM.
* **Metadata Preservation:** Safely copy directories while retaining original creation and modification timestamps.

## Prerequisites

* Python 3.8+
* `click` (for CLI argument parsing)

## Installation

We recommend running this tool inside an isolated Python virtual environment.

```bash
# 1. Clone or navigate to the directory
cd archivecopy

# 2. Create a virtual environment
python3 -m venv venv

# 3. Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# 4. Install dependencies
pip install click

# 5. Make the script executable (Linux/macOS)
chmod +x backup_manager.py
```

## Usage

The `backup_manager.py` tool revolves around three primary commands: `checksum`, `copy`, and `verify`.

### 1. Generate Checksums (`checksum`)
Creates or updates the JSON checksum ledger. It skips files it has already hashed, making subsequent runs extremely fast.

```bash
./backup_manager.py checksum <SOURCE_DIRECTORY> <CHECKSUM_FILE>
```

**Example:**
```bash
./backup_manager.py checksum ./my_important_files ./backup_ledger.json
```

### 2. Copy Files (`copy`)
Copies your files from the source to your backup destination (e.g., an external hard drive or network share).

```bash
./backup_manager.py copy <SOURCE_DIRECTORY> <DESTINATION_DIRECTORY>
```

**Example:**
```bash
./backup_manager.py copy ./my_important_files /media/usb_drive/backups/
```

### 3. Verify Integrity (`verify`)
The core verification step. Scans the destination directory against your checksum ledger to guarantee perfect, byte-for-byte integrity.

```bash
./backup_manager.py verify <DESTINATION_DIRECTORY> <CHECKSUM_FILE>
```

**Example:**
```bash
./backup_manager.py verify /media/usb_drive/backups/ ./backup_ledger.json
```

The script will report file statuses in real-time and provide a summary of how many files are `OK`, `FAILED` (corrupted during transfer), or `MISSING`.
