import ctypes
import importlib
import importlib.util
import json
import os
import platform
from pathlib import Path
import sys

PF_FEATURES = {
    "MMX": 3,
    "SSE": 6,
    "SSE2": 10,
    "SSE3": 13,
    "SSSE3": 36,
    "SSE4_1": 37,
    "SSE4_2": 38,
    "AVX": 39,
    "AVX2": 40,
    "AVX512F": 41,
}

CPUINFO_FLAGS = {
    "MMX": "mmx",
    "SSE": "sse",
    "SSE2": "sse2",
    "SSE3": "pni",
    "SSSE3": "ssse3",
    "SSE4_1": "sse4_1",
    "SSE4_2": "sse4_2",
    "AVX": "avx",
    "AVX2": "avx2",
    "AVX512F": "avx512f",
    "AES": "aes",
    "PCLMULQDQ": "pclmulqdq",
    "F16C": "f16c",
    "FMA3": "fma",
    "BMI1": "bmi1",
    "BMI2": "bmi2",
    "SHA": "sha",
    "POPCNT": "popcnt",
    "LZCNT": "abm",
    "RDRAND": "rdrand",
    "RDSEED": "rdseed",
    "ADX": "adx",
    "CLFLUSHOPT": "clflushopt",
    "CLWB": "clwb",
    "GFNI": "gfni",
    "VAES": "vaes",
    "VPCLMULQDQ": "vpclmulqdq",
    "AVX512BW": "avx512bw",
    "AVX512CD": "avx512cd",
    "AVX512DQ": "avx512dq",
    "AVX512IFMA": "avx512ifma",
    "AVX512VBMI": "avx512vbmi",
    "AVX512VBMI2": "avx512vbmi2",
    "AVX512VL": "avx512vl",
    "AVX512VNNI": "avx512vnni",
    "AVX512BITALG": "avx512bitalg",
    "AVX512VPOPCNTDQ": "avx512vpopcntdq",
    "AMX_TILE": "amx_tile",
    "AMX_INT8": "amx_int8",
    "AMX_BF16": "amx_bf16",
}

CPUINFO_FLAG_ALIASES = {
    "RDRAND": ["rdrand", "rdrnd"],
}


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def get_memory_info() -> dict:
    try:
        mem = MEMORYSTATUSEX()
        mem.dwLength = ctypes.sizeof(mem)
        ok = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
        if not ok:
            raise ctypes.WinError()
        return {
            "available": True,
            "total_gb": round(mem.ullTotalPhys / 1024 ** 3, 1),
            "available_gb": round(mem.ullAvailPhys / 1024 ** 3, 1),
            "memory_load_percent": mem.dwMemoryLoad,
        }
    except Exception as exc:
        return {
            "available": False,
            "error": str(exc),
        }


def get_windows_pf_features() -> dict:
    result = {
        "available": False,
        "features": {},
    }

    if platform.system() != "Windows":
        result["error"] = "IsProcessorFeaturePresent solo aplica en Windows"
        return result

    try:
        kernel32 = ctypes.windll.kernel32
        kernel32.IsProcessorFeaturePresent.restype = ctypes.c_int
        kernel32.IsProcessorFeaturePresent.argtypes = [ctypes.c_uint32]

        features = {}
        for name, pf_id in PF_FEATURES.items():
            features[name] = bool(kernel32.IsProcessorFeaturePresent(pf_id))

        result["available"] = True
        result["features"] = features
        result["pf_ids"] = PF_FEATURES
        return result
    except Exception as exc:
        result["error"] = str(exc)
        return result


def get_cpuinfo_block() -> dict:
    if importlib.util.find_spec("cpuinfo") is None:
        return {
            "available": False,
            "error": "py-cpuinfo no esta instalado",
            "features": {},
        }

    try:
        cpuinfo = importlib.import_module("cpuinfo")
        info = cpuinfo.get_cpu_info()
        flags = set(info.get("flags", []))
        features = {}
        for name, flag in CPUINFO_FLAGS.items():
            aliases = CPUINFO_FLAG_ALIASES.get(name, [flag])
            features[name] = any(alias in flags for alias in aliases)

        return {
            "available": True,
            "brand_raw": info.get("brand_raw"),
            "arch": info.get("arch"),
            "bits": info.get("bits"),
            "count": info.get("count"),
            "python_version": info.get("python_version"),
            "cpuinfo_version": info.get("cpuinfo_version_string"),
            "flags_sample": sorted(flags)[:40],
            "features": features,
        }
    except Exception as exc:
        return {
            "available": False,
            "error": str(exc),
            "features": {},
        }


def main() -> None:
    windows_pf = get_windows_pf_features()
    cpuinfo_block = get_cpuinfo_block()
    executable_name = Path(sys.executable).name if sys.executable else "python"

    data = {
        "process": {
            "python_label": executable_name,
        },
        "platform": {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "logical_cpus": os.cpu_count(),
        },
        "memory": get_memory_info(),
        "windows_pf": windows_pf,
        "cpuinfo": cpuinfo_block,
    }

    if cpuinfo_block.get("brand_raw"):
        data["platform"]["processor"] = cpuinfo_block["brand_raw"]

    json.dump(data, sys.stdout, ensure_ascii=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()