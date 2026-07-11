import re
from pathlib import Path
import shutil
import subprocess

NASM = shutil.which("nasm") or "nasm"
NDISASM = shutil.which("ndisasm") or "ndisasm"
BASE_DIR = Path(__file__).resolve().parent


TESTS = {
    "mmx": r"""
        pxor mm0, mm0
        emms
        retq
    """,
    "sse": r"""
        xorps xmm0, xmm0
        retq
    """,
    "sse2": r"""
        xorpd xmm0, xmm0
        retq
    """,
    "sse3": r"""
        addsubpd xmm0, xmm0
        retq
    """,
    "ssse3": r"""
        pabsb xmm0, xmm0
        retq
    """,
    "sse4_1": r"""
        ptest xmm0, xmm0
        retq
    """,
    "sse4_2": r"""
        crc32 eax, eax
        retq
    """,
    "avx": r"""
        vzeroupper
        retq
    """,
    "avx2": r"""
        vpxor ymm0, ymm0, ymm0
        retq
    """,
    "f16c": r"""
        vcvtps2ph xmm0, xmm0, byte 0x0
        retq
    """,
    "fma3": r"""
        vfmadd132ps xmm0, xmm0, xmm0
        retq
    """,
    "avx512f": r"""
        vpxord zmm0, zmm0, zmm0
        retq
    """,
    "avx512bw": r"""
        vpaddb zmm0, zmm0, zmm0
        retq
    """,
    "avx512cd": r"""
        vpconflictd zmm0, zmm0
        retq
    """,
    "avx512dq": r"""
        vpmullq zmm0, zmm0, zmm0
        retq
    """,
    "avx512ifma": r"""
        vpmadd52luq zmm0, zmm0, zmm0
        retq
    """,
    "avx512vbmi": r"""
        vpermb zmm0, zmm0, zmm0
        retq
    """,
    "avx512vbmi2": r"""
        vpshldd zmm0, zmm0, zmm0, byte 0x0
        retq
    """,
    "avx512vl": r"""
        vpxord xmm0, xmm0, xmm0
        retq
    """,
    "avx512vnni": r"""
        vpdpbusd zmm0, zmm0, zmm0
        retq
    """,
    "avx512bitalg": r"""
        vpopcntb zmm0, zmm0
        retq
    """,
    "avx512vpopcntdq": r"""
        vpopcntq zmm0, zmm0
        retq
    """,
    "aes": r"""
        aesenc xmm0, xmm0
        retq
    """,
    "pclmulqdq": r"""
        pclmullqlqdq xmm0, xmm0
        retq
    """,
    "vaes": r"""
        vaesenc ymm0, ymm1, ymm1
        retq
    """,
    "vpclmulqdq": r"""
        vpclmullqlqdq ymm0, ymm1, ymm1
        retq
    """,
    "sha": r"""
        sha1msg1 xmm0, xmm1
        retq
    """,
    "gfni": r"""
        gf2p8mulb xmm0, xmm1
        retq
    """,
    "bmi1": r"""
        andn eax, eax, eax
        retq
    """,
    "bmi2": r"""
        pext eax, eax, eax
        retq
    """,
    "popcnt": r"""
        popcnt eax, eax
        retq
    """,
    "lzcnt": r"""
        lzcnt eax, eax
        retq
    """,
    "adx": r"""
        adcx eax, eax
        retq
    """,
    "rdrand": r"""
        rdrand eax
        retq
    """,
    "rdseed": r"""
        rdseed eax
        retq
    """,
    "clflushopt": r"""
        clflushopt [rsp]
        retq
    """,
    "clwb": r"""
        clwb [rsp]
        retq
    """,
    "amx_tile": r"""
        sub rsp, 0x40
        xor eax, eax
        mov [rsp], rax
        mov [rsp+0x8], rax
        mov [rsp+0x10], rax
        mov [rsp+0x18], rax
        mov [rsp+0x20], rax
        mov [rsp+0x28], rax
        mov [rsp+0x30], rax
        mov [rsp+0x38], rax
        mov byte [rsp], 0x1
        mov word [rsp+0x10], 0x40
        mov byte [rsp+0x30], 0x10
        ldtilecfg zword [rsp]
        tilezero tmm0
        tilerelease
        add rsp, 0x40
        retq
    """,
    "amx_int8": r"""
        sub rsp, 0x40
        xor eax, eax
        mov [rsp], rax
        mov [rsp+0x8], rax
        mov [rsp+0x10], rax
        mov [rsp+0x18], rax
        mov [rsp+0x20], rax
        mov [rsp+0x28], rax
        mov [rsp+0x30], rax
        mov [rsp+0x38], rax
        mov byte [rsp], 0x1
        mov word [rsp+0x10], 0x40
        mov word [rsp+0x12], 0x40
        mov word [rsp+0x14], 0x40
        mov byte [rsp+0x30], 0x10
        mov byte [rsp+0x31], 0x10
        mov byte [rsp+0x32], 0x10
        ldtilecfg zword [rsp]
        tilezero tmm0
        tilezero tmm1
        tilezero tmm2
        tdpbssd tmm0, tmm1, tmm2
        tilerelease
        add rsp, 0x40
        retq
    """,
    "amx_bf16": r"""
        sub rsp, 0x40
        xor eax, eax
        mov [rsp], rax
        mov [rsp+0x8], rax
        mov [rsp+0x10], rax
        mov [rsp+0x18], rax
        mov [rsp+0x20], rax
        mov [rsp+0x28], rax
        mov [rsp+0x30], rax
        mov [rsp+0x38], rax
        mov byte [rsp], 0x1
        mov word [rsp+0x10], 0x40
        mov word [rsp+0x12], 0x40
        mov word [rsp+0x14], 0x40
        mov byte [rsp+0x30], 0x10
        mov byte [rsp+0x31], 0x10
        mov byte [rsp+0x32], 0x10
        ldtilecfg zword [rsp]
        tilezero tmm0
        tilezero tmm1
        tilezero tmm2
        tdpbf16ps tmm0, tmm1, tmm2
        tilerelease
        add rsp, 0x40
        retq
    """,
}


def normalize(line: str) -> str:
    line = line.strip().lower()
    line = re.sub(r"\s*,\s*", ",", line)
    line = re.sub(r"\s+", " ", line)
    return line


def extract_written_mnemonics(source: str) -> list[str]:
    lines = []

    for raw in source.strip().splitlines():
        line = raw.split(";", 1)[0].strip()
        if not line:
            continue
        lines.append(normalize(line))

    return lines


asm_dir = BASE_DIR / "asm"
bin_dir = BASE_DIR / "bin"
roundtrip_dir = BASE_DIR / "roundtrip"

asm_dir.mkdir(exist_ok=True)
bin_dir.mkdir(exist_ok=True)
roundtrip_dir.mkdir(exist_ok=True)

ok = []
failed = []

for name, source in TESTS.items():
    asm = asm_dir / f"{name}.asm"
    bin_file = bin_dir / f"{name}.bin"

    asm.write_text("BITS 64\n\n" + source.strip() + "\n", encoding="utf-8")

    if bin_file.exists():
        bin_file.unlink()

    try:
        subprocess.run(
            [NASM, "-O0", "-f", "bin", str(asm), "-o", str(bin_file)],
            capture_output=True,
            text=True,
            check=True,
        )

        original = bin_file.read_bytes()

        dis = subprocess.run(
            [NDISASM, "-b64", str(bin_file)],
            capture_output=True,
            text=True,
            check=True,
        )

        assembly = []
        for line in dis.stdout.splitlines():
            parts = line.split(None, 2)
            if len(parts) != 3:
                continue
            assembly.append(parts[2])

        recovered = roundtrip_dir / f"{name}.asm"
        recovered.write_text("BITS 64\n\n" + "\n".join(assembly) + "\n", encoding="utf-8")

        regenerated_bin = roundtrip_dir / f"{name}.bin"
        subprocess.run(
            [NASM, "-O0", "-f", "bin", str(recovered), "-o", str(regenerated_bin)],
            capture_output=True,
            text=True,
            check=True,
        )

        regenerated = regenerated_bin.read_bytes()
        if original != regenerated:
            raise RuntimeError(
                "Binary roundtrip mismatch:\n"
                f"  original    = {original.hex(' ').upper()}\n"
                f"  regenerated = {regenerated.hex(' ').upper()}"
            )

        written = extract_written_mnemonics(source)
        disassembled = [normalize(inst) for inst in assembly]
        if written != disassembled:
            raise RuntimeError(
                "Mnemonic roundtrip mismatch (NASM pudo haber elegido una codificacion distinta a la escrita):\n"
                f"  escrito       = {written}\n"
                f"  desensamblado = {disassembled}"
            )

        hex_blob = original.hex(" ").upper()
        ok.append(name)

        print(f"def test_{name}() -> str:")
        print('    """')
        print("    Assembly:")
        for inst in assembly:
            print(f"        {inst}")
        print()
        print("    Binary roundtrip verification:   PASS")
        print("    Mnemonic roundtrip verification: PASS")
        print('    """')
        print(f'    return _run_machine_code("{hex_blob}")')
        print()

    except Exception as error:
        failed.append(name)
        print("# " + "=" * 78)
        print(f"# [FAILED] {name}")

        if isinstance(error, subprocess.CalledProcessError):
            detail = (error.stderr or error.stdout or "").strip()
        else:
            detail = str(error)

        for line in detail.splitlines():
            print(f"# {line}")

        print("# " + "=" * 78)
        print()

print("# " + "=" * 78)
print("# SUMMARY")
print(f"# Compiled : {len(ok)}")
print(f"# Failed   : {len(failed)}")

if failed:
    print("#")
    print("# Remaining:")
    for name in failed:
        print(f"#  - {name}")

print("# " + "=" * 78)
