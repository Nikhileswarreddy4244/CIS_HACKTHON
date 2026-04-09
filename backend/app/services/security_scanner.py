"""
services/security_scanner.py
------------------------------
Scans uploaded files for potential security threats before storing them.

Checks performed (no external dependencies):
  1. Dangerous file extension (exe, bat, ps1, sh, dll, etc.)
  2. Double / hidden extension  (e.g. "invoice.pdf.exe")
  3. Magic-byte mismatch — file content doesn't match its claimed extension
  4. Suspicious script patterns found inside the file bytes
  5. Oversized filename (path-traversal indicator)

Returns a ScanResult dataclass so callers can decide what to do.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


# ── Dangerous extensions ───────────────────────────────────────────────────────
DANGEROUS_EXTENSIONS: set[str] = {
    # Executables
    "exe", "com", "msi", "dll", "so", "dylib",
    # Scripts
    "bat", "cmd", "ps1", "psm1", "psd1", "vbs", "vbe",
    "js", "jse", "wsf", "wsh", "hta",
    "sh", "bash", "zsh", "fish", "csh",
    "py", "pyc", "pyw", "rb", "pl", "php", "php3", "php4", "php5", "phtml",
    "asp", "aspx", "jsp", "jspx",
    # Macros / Office with macros
    "xlsm", "xltm", "xlam", "docm", "dotm", "pptm", "potm", "ppam",
    # Archives that commonly carry malware
    "scr", "cpl", "inf", "reg",
    # Java
    "jar", "war", "ear",
    # Other
    "lnk", "url", "pif", "application", "gadget",
}

# ── Magic byte signatures ──────────────────────────────────────────────────────
# Maps the first N bytes (as hex prefix) → what file type it really is
MAGIC_SIGNATURES: list[tuple[bytes, str]] = [
    (b"MZ",                         "Windows executable (EXE/DLL)"),
    (b"\x7fELF",                    "Linux/Unix executable (ELF)"),
    (b"\xca\xfe\xba\xbe",           "Java class file"),
    (b"PK\x03\x04",                 "ZIP / JAR / Office Open XML archive"),
    (b"\x25\x50\x44\x46",           "PDF document"),
    (b"\xff\xd8\xff",               "JPEG image"),
    (b"\x89PNG\r\n\x1a\n",          "PNG image"),
    (b"GIF87a",                     "GIF image"),
    (b"GIF89a",                     "GIF image"),
    (b"RIFF",                       "WAV/AVI media file"),
    (b"\x1f\x8b",                   "GZIP archive"),
    (b"BZh",                        "BZIP2 archive"),
    (b"\xfd7zXZ\x00",               "XZ archive"),
    (b"Rar!\x1a\x07",               "RAR archive"),
    (b"\x7fELF",                    "ELF binary"),
    (b"#!/",                        "Shell script (shebang)"),
    (b"#!",                         "Script (shebang)"),
]

# Extensions whose magic bytes we explicitly check aren't executables
SAFE_EXTENSIONS: set[str] = {
    "pdf", "png", "jpg", "jpeg", "gif", "bmp", "webp",
    "txt", "csv", "json", "xml", "yaml", "yml", "md",
    "mp3", "mp4", "wav", "ogg", "flac",
    "zip", "rar", "gz", "tar",
    "doc", "docx", "xls", "xlsx", "ppt", "pptx",
}

# ── Suspicious payload patterns ────────────────────────────────────────────────
# Regex patterns checked against first 8 KB of file content (decoded as latin-1
# to avoid unicode errors on binary files)
SUSPICIOUS_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(rb"powershell\s*-(?:enc|encoded|e)\b", re.I),
     "Encoded PowerShell command detected"),
    (re.compile(rb"cmd\.exe\s*/[cCkK]", re.I),
     "Command shell execution string detected"),
    (re.compile(rb"<script[\s>]", re.I),
     "Embedded HTML script tag detected"),
    (re.compile(rb"eval\s*\(", re.I),
     "Dynamic code evaluation (eval) detected"),
    (re.compile(rb"base64_decode\s*\(", re.I),
     "Base64 decode execution pattern detected"),
    (re.compile(rb"os\.system\s*\(|subprocess\.(?:call|run|Popen)", re.I),
     "System command execution code detected"),
    (re.compile(rb"WScript\.Shell|CreateObject\s*\(", re.I),
     "Windows Script Host object detected"),
    (re.compile(rb"\\x[0-9a-f]{2}(?:\\x[0-9a-f]{2}){8,}", re.I),
     "Large hex-encoded shellcode pattern detected"),
    (re.compile(rb"AUTORUN\.INF", re.I),
     "Autorun configuration detected"),
    (re.compile(rb"metasploit|meterpreter", re.I),
     "Known exploit framework signature detected"),
]


# ── Result dataclass ───────────────────────────────────────────────────────────

@dataclass
class ScanResult:
    is_safe: bool = True
    threats: list[str] = field(default_factory=list)
    risk_level: str = "safe"          # "safe" | "warning" | "dangerous"

    def add_threat(self, description: str, level: str = "dangerous") -> None:
        self.is_safe = False
        self.threats.append(description)
        # Escalate risk level
        if level == "dangerous" or self.risk_level == "dangerous":
            self.risk_level = "dangerous"
        else:
            self.risk_level = "warning"

    @property
    def user_message(self) -> str:
        """Plain-English message suitable for showing to the end user."""
        if self.is_safe:
            return ""
        base = (
            "⚠️ This file looks harmful and cannot be stored in your vault.\n\n"
            "Our security scan found the following issue(s):\n"
        )
        bullet_points = "\n".join(f"  • {t}" for t in self.threats)
        return base + bullet_points + (
            "\n\nPlease make sure you are uploading a safe document, image, or media file."
        )


# ── Main scanner ───────────────────────────────────────────────────────────────

def scan_file(filename: str, file_bytes: bytes) -> ScanResult:
    """
    Run all security checks on *file_bytes* with the given *filename*.
    Returns a ScanResult — check `.is_safe` before proceeding.
    """
    result = ScanResult()
    ext = _get_extension(filename)

    # 1. Dangerous extension
    if ext in DANGEROUS_EXTENSIONS:
        result.add_threat(
            f'Files with the ".{ext}" extension are not allowed — '
            f"they can contain executable code that may harm your system.",
            level="dangerous",
        )

    # 2. Double / hidden extension  (e.g. "invoice.pdf.exe")
    stem = Path(filename).stem          # everything except last extension
    inner_ext = _get_extension(stem)
    if inner_ext and inner_ext in DANGEROUS_EXTENSIONS:
        result.add_threat(
            f'This file is disguised — it has a hidden ".{inner_ext}" extension '
            f'(the full name "{filename}" ends in ".{ext}" but hides another dangerous type inside).',
            level="dangerous",
        )

    # 3. Magic byte mismatch — does the content look like an executable?
    magic_type = _detect_magic(file_bytes)
    if magic_type:
        # Only warn if the magic type contradicts the claimed extension
        if ext in SAFE_EXTENSIONS and _is_executable_magic(file_bytes):
            result.add_threat(
                f'This file claims to be a ".{ext}" file, but its contents look like '
                f"a {magic_type}. It may be a disguised executable.",
                level="dangerous",
            )

    # 4. Suspicious script patterns (check first 16 KB)
    sample = file_bytes[:16_384]
    for pattern, description in SUSPICIOUS_PATTERNS:
        if pattern.search(sample):
            result.add_threat(description, level="dangerous")
            break   # one pattern match is enough to flag

    # 5. Oversized filename (path traversal hint)
    if len(filename) > 255 or ".." in filename or "/" in filename or "\\" in filename:
        result.add_threat(
            "The filename contains suspicious characters that could indicate "
            "a path-traversal attack.",
            level="warning",
        )

    return result


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_extension(filename: str) -> str:
    """Return lowercase extension without the dot, or empty string."""
    parts = filename.rsplit(".", 1)
    return parts[-1].lower() if len(parts) == 2 else ""


def _detect_magic(data: bytes) -> str | None:
    """Return a human-readable file type string if a magic signature matches, else None."""
    for signature, label in MAGIC_SIGNATURES:
        if data.startswith(signature):
            return label
    return None


def _is_executable_magic(data: bytes) -> bool:
    """Return True if the magic bytes indicate an executable or script."""
    executable_sigs = [b"MZ", b"\x7fELF", b"\xca\xfe\xba\xbe", b"#!/", b"#!"]
    return any(data.startswith(sig) for sig in executable_sigs)
