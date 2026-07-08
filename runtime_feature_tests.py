import ctypes
from typing import Callable, Dict


STATUS_OK = "OK"
STATUS_NO_PROBADO = "NO PROBADO"

kernel32 = ctypes.windll.kernel32
kernel32.VirtualAlloc.restype = ctypes.c_void_p
kernel32.VirtualAlloc.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_ulong, ctypes.c_ulong]
kernel32.VirtualFree.restype = ctypes.c_int
kernel32.VirtualFree.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_ulong]


def _run_machine_code(blob_hex: str) -> str:
    code = bytes.fromhex(blob_hex)
    size = len(code)

    mem_commit = 0x1000
    mem_reserve = 0x2000
    mem_release = 0x8000
    page_execute_readwrite = 0x40

    addr = kernel32.VirtualAlloc(None, size, mem_commit | mem_reserve, page_execute_readwrite)
    if not addr:
        raise OSError("VirtualAlloc failed")

    try:
        ctypes.memmove(ctypes.c_void_p(addr), code, size)
        fn = ctypes.CFUNCTYPE(None)(ctypes.c_void_p(addr).value)
        fn()
    finally:
        kernel32.VirtualFree(addr, 0, mem_release)

    return STATUS_OK


def _not_tested() -> str:
    return STATUS_NO_PROBADO


def test_mmx() -> str:
    """
    Assembly:
        pxor mm0,mm0
        emms
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("0F EF C0 0F 77 C3")

def test_sse() -> str:
    """
    Assembly:
        xorps xmm0,xmm0
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("0F 57 C0 C3")

def test_sse2() -> str:
    """
    Assembly:
        xorpd xmm0,xmm0
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("66 0F 57 C0 C3")

def test_sse3() -> str:
    """
    Assembly:
        addsubpd xmm0,xmm0
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("66 0F D0 C0 C3")

def test_ssse3() -> str:
    """
    Assembly:
        pabsb xmm0,xmm0
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("66 0F 38 1C C0 C3")

def test_sse4_1() -> str:
    """
    Assembly:
        ptest xmm0,xmm0
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("66 0F 38 17 C0 C3")

def test_sse4_2() -> str:
    """
    Assembly:
        crc32 eax,eax
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("F2 0F 38 F1 C0 C3")

def test_avx() -> str:
    """
    Assembly:
        vzeroupper
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("C5 F8 77 C3")

def test_avx2() -> str:
    """
    Assembly:
        vpxor ymm0,ymm0,ymm0
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("C5 FD EF C0 C3")

def test_f16c() -> str:
    """
    Assembly:
        vcvtps2ph xmm0,xmm0,byte 0x0
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("C4 E3 79 1D C0 00 C3")

def test_fma3() -> str:
    """
    Assembly:
        vfmadd132ps xmm0,xmm0,xmm0
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("C4 E2 79 98 C0 C3")

def test_avx512f() -> str:
    """
    Assembly:
        vpxord zmm0,zmm0,zmm0
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("62 F1 7D 48 EF C0 C3")

def test_avx512bw() -> str:
    """
    Assembly:
        vpaddb zmm0,zmm0,zmm0
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("62 F1 7D 48 FC C0 C3")

def test_avx512cd() -> str:
    """
    Assembly:
        vpconflictd zmm0,zmm0
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("62 F2 7D 48 C4 C0 C3")

def test_avx512dq() -> str:
    """
    Assembly:
        vpmullq zmm0,zmm0,zmm0
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("62 F2 FD 48 40 C0 C3")

def test_avx512ifma() -> str:
    """
    Assembly:
        vpmadd52luq zmm0,zmm0,zmm0
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("62 F2 FD 48 B4 C0 C3")

def test_avx512vbmi() -> str:
    """
    Assembly:
        vpermb zmm0,zmm0,zmm0
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("62 F2 7D 48 8D C0 C3")

def test_avx512vbmi2() -> str:
    """
    Assembly:
        vpshldd zmm0,zmm0,zmm0,byte 0x0
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("62 F3 7D 48 71 C0 00 C3")

def test_avx512vl() -> str:
    """
    Assembly:
        vpxord xmm0,xmm0,xmm0
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("62 F1 7D 08 EF C0 C3")

def test_avx512vnni() -> str:
    """
    Assembly:
        vpdpbusd zmm0,zmm0,zmm0
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("62 F2 7D 48 50 C0 C3")

def test_avx512bitalg() -> str:
    """
    Assembly:
        vpopcntb zmm0,zmm0
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("62 F2 7D 48 54 C0 C3")

def test_avx512vpopcntdq() -> str:
    """
    Assembly:
        vpopcntq zmm0,zmm0
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("62 F2 FD 48 55 C0 C3")

def test_aes() -> str:
    """
    Assembly:
        aesenc xmm0,xmm0
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("66 0F 38 DC C0 C3")

def test_pclmulqdq() -> str:
    """
    Assembly:
        pclmullqlqdq xmm0,xmm0
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("66 0F 3A 44 C0 00 C3")

def test_vaes() -> str:
    """
    Assembly:
        vaesenc ymm0,ymm1,ymm1
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("C4 E2 75 DC C1 C3")

def test_vpclmulqdq() -> str:
    """
    Assembly:
        vpclmullqlqdq ymm0,ymm1,ymm1
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("C4 E3 75 44 C1 00 C3")

def test_sha() -> str:
    """
    Assembly:
        sha1msg1 xmm0,xmm1
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("0F 38 C9 C1 C3")

def test_gfni() -> str:
    """
    Assembly:
        gf2p8mulb xmm0,xmm1
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("66 0F 38 CF C1 C3")

def test_bmi1() -> str:
    """
    Assembly:
        andn eax,eax,eax
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("C4 E2 78 F2 C0 C3")

def test_bmi2() -> str:
    """
    Assembly:
        pext eax,eax,eax
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("C4 E2 7A F5 C0 C3")

def test_popcnt() -> str:
    """
    Assembly:
        popcnt eax,eax
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("F3 0F B8 C0 C3")

def test_lzcnt() -> str:
    """
    Assembly:
        lzcnt eax,eax
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("F3 0F BD C0 C3")

def test_adx() -> str:
    """
    Assembly:
        adcx eax,eax
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("66 0F 38 F6 C0 C3")

def test_rdrand() -> str:
    """
    Assembly:
        rdrand eax
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("0F C7 F0 C3")

def test_rdseed() -> str:
    """
    Assembly:
        rdseed eax
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("0F C7 F8 C3")

def test_clflushopt() -> str:
    """
    Assembly:
        clflushopt [rsp]
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("66 0F AE 3C 24 C3")

def test_clwb() -> str:
    """
    Assembly:
        clwb [rsp]
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("66 0F AE 34 24 C3")

def test_amx_tile() -> str:
    """
    Assembly:
        sub rsp,0x40
        xor eax,eax
        mov [rsp],rax
        mov [rsp+0x8],rax
        mov [rsp+0x10],rax
        mov [rsp+0x18],rax
        mov [rsp+0x20],rax
        mov [rsp+0x28],rax
        mov [rsp+0x30],rax
        mov [rsp+0x38],rax
        mov byte [rsp],0x1
        mov word [rsp+0x10],0x40
        mov byte [rsp+0x30],0x10
        ldtilecfg zword [rsp]
        tilezero tmm0
        tilerelease
        add rsp,0x40
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("48 81 EC 40 00 00 00 31 C0 48 89 04 24 48 89 44 24 08 48 89 44 24 10 48 89 44 24 18 48 89 44 24 20 48 89 44 24 28 48 89 44 24 30 48 89 44 24 38 C6 04 24 01 66 C7 44 24 10 40 00 C6 44 24 30 10 C4 E2 78 49 04 24 C4 E2 7B 49 C0 C4 E2 78 49 C0 48 81 C4 40 00 00 00 C3")

def test_amx_int8() -> str:
    """
    Assembly:
        sub rsp,0x40
        xor eax,eax
        mov [rsp],rax
        mov [rsp+0x8],rax
        mov [rsp+0x10],rax
        mov [rsp+0x18],rax
        mov [rsp+0x20],rax
        mov [rsp+0x28],rax
        mov [rsp+0x30],rax
        mov [rsp+0x38],rax
        mov byte [rsp],0x1
        mov word [rsp+0x10],0x40
        mov word [rsp+0x12],0x40
        mov word [rsp+0x14],0x40
        mov byte [rsp+0x30],0x10
        mov byte [rsp+0x31],0x10
        mov byte [rsp+0x32],0x10
        ldtilecfg zword [rsp]
        tilezero tmm0
        tilezero tmm1
        tilezero tmm2
        tdpbssd tmm0,tmm1,tmm2
        tilerelease
        add rsp,0x40
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("48 81 EC 40 00 00 00 31 C0 48 89 04 24 48 89 44 24 08 48 89 44 24 10 48 89 44 24 18 48 89 44 24 20 48 89 44 24 28 48 89 44 24 30 48 89 44 24 38 C6 04 24 01 66 C7 44 24 10 40 00 66 C7 44 24 12 40 00 66 C7 44 24 14 40 00 C6 44 24 30 10 C6 44 24 31 10 C6 44 24 32 10 C4 E2 78 49 04 24 C4 E2 7B 49 C0 C4 E2 7B 49 C8 C4 E2 7B 49 D0 C4 E2 6B 5E C1 C4 E2 78 49 C0 48 81 C4 40 00 00 00 C3")

def test_amx_bf16() -> str:
    """
    Assembly:
        sub rsp,0x40
        xor eax,eax
        mov [rsp],rax
        mov [rsp+0x8],rax
        mov [rsp+0x10],rax
        mov [rsp+0x18],rax
        mov [rsp+0x20],rax
        mov [rsp+0x28],rax
        mov [rsp+0x30],rax
        mov [rsp+0x38],rax
        mov byte [rsp],0x1
        mov word [rsp+0x10],0x40
        mov word [rsp+0x12],0x40
        mov word [rsp+0x14],0x40
        mov byte [rsp+0x30],0x10
        mov byte [rsp+0x31],0x10
        mov byte [rsp+0x32],0x10
        ldtilecfg zword [rsp]
        tilezero tmm0
        tilezero tmm1
        tilezero tmm2
        tdpbf16ps tmm0,tmm1,tmm2
        tilerelease
        add rsp,0x40
        retq

    Binary roundtrip verification:   PASS
    Mnemonic roundtrip verification: PASS
    """
    return _run_machine_code("48 81 EC 40 00 00 00 31 C0 48 89 04 24 48 89 44 24 08 48 89 44 24 10 48 89 44 24 18 48 89 44 24 20 48 89 44 24 28 48 89 44 24 30 48 89 44 24 38 C6 04 24 01 66 C7 44 24 10 40 00 66 C7 44 24 12 40 00 66 C7 44 24 14 40 00 C6 44 24 30 10 C6 44 24 31 10 C6 44 24 32 10 C4 E2 78 49 04 24 C4 E2 7B 49 C0 C4 E2 7B 49 C8 C4 E2 7B 49 D0 C4 E2 6A 5C C1 C4 E2 78 49 C0 48 81 C4 40 00 00 00 C3")


TEST_FUNCTIONS: Dict[str, Callable[[], str]] = {
    "MMX": test_mmx,
    "SSE": test_sse,
    "SSE2": test_sse2,
    "SSE3": test_sse3,
    "SSSE3": test_ssse3,
    "SSE4_1": test_sse4_1,
    "SSE4_2": test_sse4_2,
    "AVX": test_avx,
    "AVX2": test_avx2,
    "F16C": test_f16c,
    "FMA3": test_fma3,
    "AVX512F": test_avx512f,
    "AVX512BW": test_avx512bw,
    "AVX512CD": test_avx512cd,
    "AVX512DQ": test_avx512dq,
    "AVX512IFMA": test_avx512ifma,
    "AVX512VBMI": test_avx512vbmi,
    "AVX512VBMI2": test_avx512vbmi2,
    "AVX512VL": test_avx512vl,
    "AVX512VNNI": test_avx512vnni,
    "AVX512BITALG": test_avx512bitalg,
    "AVX512VPOPCNTDQ": test_avx512vpopcntdq,
    "AES": test_aes,
    "PCLMULQDQ": test_pclmulqdq,
    "VAES": test_vaes,
    "VPCLMULQDQ": test_vpclmulqdq,
    "SHA": test_sha,
    "GFNI": test_gfni,
    "BMI1": test_bmi1,
    "BMI2": test_bmi2,
    "POPCNT": test_popcnt,
    "LZCNT": test_lzcnt,
    "ADX": test_adx,
    "RDRAND": test_rdrand,
    "RDSEED": test_rdseed,
    "CLFLUSHOPT": test_clflushopt,
    "CLWB": test_clwb,
    "AMX_TILE": test_amx_tile,
    "AMX_INT8": test_amx_int8,
    "AMX_BF16": test_amx_bf16,
}


def get_supported_features() -> list[str]:
    return list(TEST_FUNCTIONS.keys())


def run_named_test(feature: str) -> str:
    return TEST_FUNCTIONS[feature]()