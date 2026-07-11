<?php
declare(strict_types=1);

final class CpuDiagnosisModel
{
    public function __construct(
        private readonly string $projectRoot,
        private readonly string $pythonRoot,
    ) {
    }

    public function buildViewModel(): array
    {
        $attempts = [];
        $probeOk = null;

        foreach ($this->pythonCandidates() as $candidate) {
            $result = $this->runJsonScript($candidate, $this->pythonRoot . DIRECTORY_SEPARATOR . 'probe_cpu.py', $this->pythonRoot);
            $result['python'] = $candidate;
            $attempts[] = $result;

            if ($result['ok']) {
                $probeOk = $result;
                break;
            }
        }

        if ($probeOk === null) {
            return [
                'error' => true,
                'attempts' => $attempts,
            ];
        }

        $probe = $probeOk['json'] ?? [];
        $platform = $probe['platform'] ?? [];
        $process = $probe['process'] ?? [];
        $memory = $probe['memory'] ?? [];
        $windowsPf = $probe['windows_pf']['features'] ?? [];
        $cpuinfo = $probe['cpuinfo'] ?? [];
        $cpuinfoFeatures = $cpuinfo['features'] ?? [];

        $runtime = $this->runJsonScript(
            (string) ($probeOk['python'] ?? ''),
            $this->pythonRoot . DIRECTORY_SEPARATOR . 'isa_runtime_test.py',
            $this->pythonRoot,
            ['--json']
        );

        $runtimeRows = $runtime['json']['rows'] ?? [];
        $runtimeByTech = [];
        foreach ($runtimeRows as $row) {
            $name = (string) ($row['technology'] ?? '');
            if ($name !== '') {
                $runtimeByTech[$name] = (string) ($row['status'] ?? 'N/A');
            }
        }

        $tableRows = [];
        foreach ($this->technologyCatalog() as $group => $techs) {
            foreach ($techs as $tech) {
                $pf = array_key_exists($tech, $windowsPf) ? (bool) $windowsPf[$tech] : null;
                $ci = array_key_exists($tech, $cpuinfoFeatures) ? (bool) $cpuinfoFeatures[$tech] : null;
                $rt = $runtimeByTech[$tech] ?? 'NO PROBADO';

                $tableRows[] = [
                    'group' => $group,
                    'tech' => $tech,
                    'pf' => $pf,
                    'cpuinfo' => $ci,
                    'runtime' => $rt,
                    'real' => $this->normalizeRealStatus($rt),
                ];
            }
        }

        return [
            'error' => false,
            'attempts' => $attempts,
            'probe' => $probe,
            'platform' => $platform,
            'process' => $process,
            'memory' => $memory,
            'runtime' => $runtime,
            'tableRows' => $tableRows,
        ];
    }

    private function pythonCandidates(): array
    {
        $candidates = [];
        $fixed = $this->projectRoot . DIRECTORY_SEPARATOR . 'python' . DIRECTORY_SEPARATOR . 'python.exe';

        if (is_file($fixed)) {
            $candidates[] = $fixed;
        }

        $candidates[] = 'python';
        $candidates[] = 'py';

        return array_values(array_unique($candidates));
    }

    private function runJsonScript(string $pythonBinary, string $scriptPath, string $cwd, array $extraArgs = []): array
    {
        $descriptors = [
            0 => ['pipe', 'r'],
            1 => ['pipe', 'w'],
            2 => ['pipe', 'w'],
        ];

        $command = array_merge([$pythonBinary, $scriptPath], $extraArgs);
        $process = @proc_open($command, $descriptors, $pipes, $cwd, null, ['bypass_shell' => true]);

        if (!is_resource($process)) {
            return [
                'ok' => false,
                'exit_code' => -1,
                'stderr' => 'No se pudo crear el proceso.',
                'stdout' => '',
                'json' => null,
            ];
        }

        fclose($pipes[0]);
        $stdout = stream_get_contents($pipes[1]) ?: '';
        $stderr = stream_get_contents($pipes[2]) ?: '';
        fclose($pipes[1]);
        fclose($pipes[2]);

        $exitCode = proc_close($process);
        $decoded = json_decode($stdout, true);

        return [
            'ok' => $exitCode === 0 && is_array($decoded),
            'exit_code' => $exitCode,
            'stderr' => trim($stderr),
            'stdout' => $stdout,
            'json' => is_array($decoded) ? $decoded : null,
        ];
    }

    private function technologyCatalog(): array
    {
        return [
            'SIMD clasico' => ['MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4_1', 'SSE4_2'],
            'Vector moderno' => ['AVX', 'AVX2', 'F16C', 'FMA3', 'AVX512F', 'AVX512BW', 'AVX512CD', 'AVX512DQ', 'AVX512IFMA', 'AVX512VBMI', 'AVX512VBMI2', 'AVX512VL', 'AVX512VNNI', 'AVX512BITALG', 'AVX512VPOPCNTDQ'],
            'Criptografia y datos' => ['AES', 'PCLMULQDQ', 'VAES', 'VPCLMULQDQ', 'SHA', 'GFNI'],
            'Bitops y aleatoriedad' => ['BMI1', 'BMI2', 'POPCNT', 'LZCNT', 'ADX', 'RDRAND', 'RDSEED'],
            'Cache y servidor' => ['CLFLUSHOPT', 'CLWB', 'AMX_TILE', 'AMX_INT8', 'AMX_BF16'],
        ];
    }

    private function normalizeRealStatus(string $runtimeStatus): string
    {
        if ($runtimeStatus === 'OK') {
            return 'YES';
        }

        if ($runtimeStatus === 'ILLEGAL_INSTRUCTION') {
            return 'NO';
        }

        return 'NO PROBADO';
    }
}