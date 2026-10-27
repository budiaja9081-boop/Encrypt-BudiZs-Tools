#!/usr/bin/env python3
# ENCRYPT BUDIZS v3.0
# AES-256-GCM + scrypt
# Python and JavaScript source protection

import os
import sys
import json
import base64
import getpass
import secrets
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes

VERSION = "3.0"
WIDTH = 76

# ==================== NEON COLORS ====================

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

WHITE = "\033[38;5;255m"
GRAY = "\033[38;5;244m"
BANNER_GREEN = "\033[38;5;118m"

GREEN = "\033[38;5;46m"
CYAN = "\033[38;5;51m"
MAGENTA = "\033[38;5;201m"
BLUE = "\033[38;5;39m"
PURPLE = "\033[38;5;141m"
GOLD = "\033[38;5;220m"
RED = "\033[38;5;196m"
ORANGE = "\033[38;5;208m"

# ==================== ORIGINAL BANNER ====================

BANNER = r'''
  _______  _____  ___    ______    _______   ___  ___  _______  ___________
 /"    "|(\"   \|"  \  /" _  "\  /"      \ |"  \/"  ||   __ "\("     _   ")
(: ______)|.\\   \    |(: ( \___)|:        | \   \  / (. |__) :))__/  \\__/
 \/    |  |: \.   \\  | \/ \     |_____/   )  \\  \/  |:  ____/    \\_ /
 // ___)_ |.  \    \. | //  \ _   //      /   /   /   (|  /        |.  |
(:      "||    \    \ |(:   _) \ |:  __   \  /   /   /|__/ \       \:  |
 \_______) \___|\____\) \_______)|__|  \___)|___/   (_______)       \__|

 _______   ____  ____  ________   __   ________    ________
|   _  "\ ("  _||_ " ||"      "\ |" \ ("      "\  /"       )
(. |_)  :)|   (  ) : |(.  ___  :)||  | \___/   :)(:   \___/
|:     \/ (:  |  | . )|: \   ) |||:  |   /  ___/  \___  \
(|  _  \\  \\ \__/ // (| (___\ |||.  |  //  \__    __/  \\
|: |_)  :) /\\ __ //\ |:       :)/\  |\(:   / "\  /" \   :)
(_______/ (__________)(________/(__\_|_)\_______)(_______/
'''

# ==================== CRYPTO SETTINGS ====================
# Keep these parameters identical in both generated loaders.

SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
KEY_SIZE = 32
SALT_SIZE = 16
NONCE_SIZE = 12


# ==================== TERMINAL UI ====================

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def line(char="━", color=CYAN):
    print(f"{color}{char * WIDTH}{RESET}")


def banner():
    print(f"{BANNER_GREEN}{BOLD}{BANNER}{RESET}")
    line("━", CYAN)
    print(f"{WHITE}{BOLD}{'ENCRYPT BUDIZS':^{WIDTH}}{RESET}")
    print(f"{GRAY}{'AES-256-GCM SOURCE PROTECTOR | v' + VERSION:^{WIDTH}}{RESET}")
    line("━", CYAN)


def header(title):
    print()
    line("═", MAGENTA)
    print(f"{CYAN}{BOLD}  ◈ {title}{RESET}")
    line("─", BLUE)


def ok(message):
    print(f"{GREEN}[+] {message}{RESET}")


def info(message):
    print(f"{CYAN}[*] {message}{RESET}")


def warn(message):
    print(f"{GOLD}[!] {message}{RESET}")


def error(message):
    print(f"{RED}[x] {message}{RESET}")


def ask(message):
    try:
        return input(f"{MAGENTA}  {message} {CYAN}› {WHITE}").strip()
    except (EOFError, KeyboardInterrupt):
        print(RESET)
        return ""


def pause():
    input(f"\n{GRAY}Tekan Enter untuk kembali...{RESET}")


# ==================== PASSWORD / ENCRYPTION ====================

def derive_key(password, salt):
    return scrypt(
        password.encode("utf-8"),
        salt,
        KEY_SIZE,
        N=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
    )


def encrypt_source(source, password):
    salt = get_random_bytes(SALT_SIZE)
    nonce = get_random_bytes(NONCE_SIZE)
    key = derive_key(password, salt)

    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce, mac_len=16)
    ciphertext, tag = cipher.encrypt_and_digest(source)

    return {
        "salt": base64.b64encode(salt).decode("ascii"),
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
        "tag": base64.b64encode(tag).decode("ascii"),
    }


def b64(value):
    return base64.b64decode(value)


# ==================== PYTHON PROTECTED LOADER ====================

def make_python_loader(envelope):
    # No password or derived key is embedded in this file.
    return f'''#!/usr/bin/env python3
# ENCRYPT BUDIZS v{VERSION} — protected Python loader
# Requires: pycryptodome
# The source is decrypted in memory when executed.

import base64
import hashlib
import getpass
import sys

from Crypto.Cipher import AES


_SALT = {envelope["salt"]!r}
_NONCE = {envelope["nonce"]!r}
_CIPHERTEXT = {envelope["ciphertext"]!r}
_TAG = {envelope["tag"]!r}


def _b64(value):
    return base64.b64decode(value)


def _main():
    password = getpass.getpass("Password: ")
    if not password:
        print("Password cannot be empty.")
        raise SystemExit(1)

    salt = _b64(_SALT)
    nonce = _b64(_NONCE)
    ciphertext = _b64(_CIPHERTEXT)
    tag = _b64(_TAG)

    key = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n={SCRYPT_N},
        r={SCRYPT_R},
        p={SCRYPT_P},
        dklen={KEY_SIZE},
        maxmem=64 * 1024 * 1024,
    )

    try:
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce, mac_len=16)
        source = cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError:
        print("Wrong password or damaged payload.")
        raise SystemExit(2)

    # The plaintext exists in process memory while the program runs.
    code = source.decode("utf-8")
    namespace = {{
        "__name__": "__main__",
        "__file__": sys.argv[0],
        "__package__": None,
    }}
    exec(compile(code, sys.argv[0], "exec"), namespace)


if __name__ == "__main__":
    _main()
'''


# ==================== JAVASCRIPT PROTECTED LOADER ====================

def make_javascript_loader(envelope):
    return f'''// ENCRYPT BUDIZS v{VERSION} — protected JavaScript loader
// Requires: Node.js
// The source is decrypted in memory when executed.

"use strict";

const crypto = require("node:crypto");
const readline = require("node:readline/promises");
const {{ stdin, stdout }} = require("node:process");
const Module = require("node:module");
const path = require("node:path");

const SALT = {json.dumps(envelope["salt"])};
const NONCE = {json.dumps(envelope["nonce"])};
const CIPHERTEXT = {json.dumps(envelope["ciphertext"])};
const TAG = {json.dumps(envelope["tag"])};

function decode(value) {{
    return Buffer.from(value, "base64");
}}

async function main() {{
    const rl = readline.createInterface({{ input: stdin, output: stdout }});
    let password;

    try {{
        password = await rl.question("Password: ");
    }} finally {{
        rl.close();
    }}

    if (!password) {{
        console.error("Password cannot be empty.");
        process.exitCode = 1;
        return;
    }}

    const salt = decode(SALT);
    const nonce = decode(NONCE);
    const ciphertext = decode(CIPHERTEXT);
    const tag = decode(TAG);

    const key = crypto.scryptSync(
        password,
        salt,
        {KEY_SIZE},
        {{
            N: {SCRYPT_N},
            r: {SCRYPT_R},
            p: {SCRYPT_P},
            maxmem: 64 * 1024 * 1024
        }}
    );

    let source;

    try {{
        const decipher = crypto.createDecipheriv(
            "aes-256-gcm",
            key,
            nonce
        );

        decipher.setAuthTag(tag);

        source = Buffer.concat([
            decipher.update(ciphertext),
            decipher.final()
        ]).toString("utf8");
    }} catch (error) {{
        console.error("Wrong password or damaged payload.");
        process.exitCode = 2;
        return;
    }}

    // Execute as a CommonJS module, in memory.
    const filename = path.resolve(process.argv[1]);
    const protectedModule = new Module(filename, module);
    protectedModule.filename = filename;
    protectedModule.paths = Module._nodeModulePaths(path.dirname(filename));

    try {{
        protectedModule._compile(source, filename);
    }} catch (error) {{
        throw error;
    }}
}}

main().catch(error => {{
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
}});
'''


# ==================== FILE PROCESSING ====================

def read_password():
    try:
        password = getpass.getpass(
            f"{MAGENTA}  Password untuk penerima: {RESET}"
        )
        confirm = getpass.getpass(
            f"{MAGENTA}  Ulangi password: {RESET}"
        )
    except (EOFError, KeyboardInterrupt):
        print()
        return None

    if not password:
        error("Password tidak boleh kosong.")
        return None

    if password != confirm:
        error("Password tidak cocok.")
        return None

    if len(password) < 12:
        warn("Password pendek. Disarankan minimal 12 karakter.")
        choice = ask("Tetap gunakan password ini? (y/n)").lower()
        if choice != "y":
            return None

    return password


def output_folder():
    folder = Path("encrypted_output")
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def protect_file(path, password, destination):
    path = Path(path).expanduser()

    if not path.exists() or not path.is_file():
        error(f"File tidak ditemukan: {path}")
        return False

    suffix = path.suffix.lower()

    if suffix not in {".py", ".js"}:
        error("Versi ini mendukung file .py dan .js saja.")
        return False

    try:
        source = path.read_bytes()
    except OSError as exc:
        error(f"Gagal membaca file: {exc}")
        return False

    # The tool encrypts the original bytes; loaders decode UTF-8 source.
    try:
        source.decode("utf-8")
    except UnicodeDecodeError:
        error("Source harus berupa teks UTF-8.")
        return False

    envelope = encrypt_source(source, password)

    if suffix == ".py":
        output = make_python_loader(envelope)
        output_path = destination / f"{path.stem}_protected.py"
    else:
        output = make_javascript_loader(envelope)
        output_path = destination / f"{path.stem}_protected.js"

    try:
        output_path.write_text(output, encoding="utf-8")
        ok(f"Protected file: {output_path}")
        info(f"Original size: {len(source)} bytes")
        info(f"Output size: {output_path.stat().st_size} bytes")
        return True
    except OSError as exc:
        error(f"Gagal menulis output: {exc}")
        return False


def encrypt_single():
    header("PROTECT SINGLE FILE")

    path = ask("Path file .py atau .js")
    if not path:
        error("Path kosong.")
        return

    password = read_password()
    if password is None:
        return

    protect_file(path, password, output_folder())


def batch_encrypt():
    header("BATCH PROTECT")

    folder_text = ask("Path folder")
    if not folder_text:
        error("Path kosong.")
        return

    folder = Path(folder_text).expanduser()
    if not folder.is_dir():
        error("Folder tidak ditemukan.")
        return

    files = sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in {".py", ".js"}
        and not p.stem.endswith("_protected")
    )

    if not files:
        info("Tidak ada file .py atau .js.")
        return

    info(f"Ditemukan {len(files)} file.")
    if ask("Lanjutkan? (y/n)").lower() != "y":
        info("Dibatalkan.")
        return

    password = read_password()
    if password is None:
        return

    destination = output_folder()
    success = 0

    for index, path in enumerate(files, 1):
        print(f"\n{BLUE}[{index}/{len(files)}] {path.name}{RESET}")
        if protect_file(path, password, destination):
            success += 1

    print()
    ok(f"Batch selesai: {success}/{len(files)} file berhasil.")


def about():
    header("ABOUT")
    print(f"{WHITE}{BOLD}ENCRYPT BUDIZS v{VERSION}{RESET}")
    print(f"{CYAN}Algorithm : AES-256-GCM{RESET}")
    print(f"{CYAN}KDF       : scrypt{RESET}")
    print(f"{CYAN}Targets   : Python and JavaScript{RESET}")
    print()
    warn("Password tidak disimpan di file output.")
    warn("Password yang hilang tidak dapat dipulihkan oleh tool.")
    warn("Loader Python membutuhkan pycryptodome di perangkat penerima.")
    warn("Loader JavaScript membutuhkan Node.js.")
    print()
    print(
        f"{GRAY}Ini melindungi payload saat tersimpan, bukan "
        f"mencegah penerima menganalisis source ketika berjalan.{RESET}"
    )


# ==================== MAIN MENU ====================

def main_menu():
    clear()
    banner()

    print()
    line("─", CYAN)
    print(f"{WHITE}{BOLD}{'MAIN MENU':^{WIDTH}}{RESET}")
    line("─", CYAN)

    print(f"  {GREEN}[1]{RESET} {WHITE}Protect single file{RESET}")
    print(f"  {BLUE}[2]{RESET} {WHITE}Batch protect{RESET}")
    print(f"  {PURPLE}[3]{RESET} {WHITE}About / security info{RESET}")
    print(f"  {RED}[0]{RESET} {WHITE}Exit{RESET}")

    line("─", CYAN)
    return ask("Pilih menu")


def main():
    while True:
        choice = main_menu()

        if choice == "1":
            encrypt_single()
            pause()
        elif choice == "2":
            batch_encrypt()
            pause()
        elif choice == "3":
            about()
            pause()
        elif choice == "0":
            clear()
            print(f"{BANNER_GREEN}{BOLD}{BANNER}{RESET}")
            line("━", CYAN)
            print(f"{GREEN}ENCRYPT BUDIZS — EXIT{RESET}")
            break
        else:
            error("Pilihan tidak valid.")
            pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Program dihentikan.{RESET}")
        sys.exit(130)
