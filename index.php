<?php
declare(strict_types=1);

function pythonCandidates(): array
{
    $candidates = [];
    $fixed = __DIR__ . DIRECTORY_SEPARATOR . 'python' . DIRECTORY_SEPARATOR . 'python.exe';
    if (is_file($fixed)) {
        $candidates[] = $fixed;
    }
    $candidates[] = 'python';
    $candidates[] = 'py';
    return array_values(array_unique($candidates));
}

function runJsonScript(string $pythonBinary, string $scriptPath, string $cwd, array $extraArgs = []): array
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

function labelClass(string $value): string
{
    if ($value === 'YES' || $value === 'OK' || $value === 'PASS') {
        return 'yes';
    }
    if ($value === 'NO PROBADO') {
        return 'na';
    }
    if ($value === 'NO' || $value === 'FAIL' || $value === 'ILLEGAL_INSTRUCTION' || $value === 'ERROR') {
        return 'no';
    }
    return 'na';
}

function yn(?bool $value): string
{
    if ($value === null) {
        return 'N/A';
    }
    return $value ? 'YES' : 'NO';
}

function h(string $value): string
{
    return htmlspecialchars($value, ENT_QUOTES, 'UTF-8');
}

function technologyCatalog(): array
{
    return [
        'SIMD clasico' => ['MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4_1', 'SSE4_2'],
        'Vector moderno' => ['AVX', 'AVX2', 'F16C', 'FMA3', 'AVX512F', 'AVX512BW', 'AVX512CD', 'AVX512DQ', 'AVX512IFMA', 'AVX512VBMI', 'AVX512VBMI2', 'AVX512VL', 'AVX512VNNI', 'AVX512BITALG', 'AVX512VPOPCNTDQ'],
        'Criptografia y datos' => ['AES', 'PCLMULQDQ', 'VAES', 'VPCLMULQDQ', 'SHA', 'GFNI'],
        'Bitops y aleatoriedad' => ['BMI1', 'BMI2', 'POPCNT', 'LZCNT', 'ADX', 'RDRAND', 'RDSEED'],
        'Cache y servidor' => ['CLFLUSHOPT', 'CLWB', 'AMX_TILE', 'AMX_INT8', 'AMX_BF16'],
    ];
}

$cwd = __DIR__;
$probePath = __DIR__ . DIRECTORY_SEPARATOR . 'probe_cpu.py';
$runtimePath = __DIR__ . DIRECTORY_SEPARATOR . 'isa_runtime_test.py';
$attempts = [];
$probeOk = null;

foreach (pythonCandidates() as $candidate) {
    $res = runJsonScript($candidate, $probePath, $cwd);
    $res['python'] = $candidate;
    $attempts[] = $res;
    if ($res['ok']) {
        $probeOk = $res;
        break;
    }
}

if ($probeOk === null) {
    header('Content-Type: text/plain; charset=utf-8');
    echo "Diagnostico CPU - ERROR\n\n";
    foreach ($attempts as $at) {
        echo 'Intento de Python fallido | exit=' . ($at['exit_code'] ?? -1) . "\n";
    }
    exit;
}

$probe = $probeOk['json'] ?? [];
$platform = $probe['platform'] ?? [];
$process = $probe['process'] ?? [];
$memory = $probe['memory'] ?? [];
$windowsPf = $probe['windows_pf']['features'] ?? [];
$cpuinfo = $probe['cpuinfo'] ?? [];
$cpuinfoFeatures = $cpuinfo['features'] ?? [];

$runtime = runJsonScript((string)($probeOk['python'] ?? ''), $runtimePath, $cwd, ['--json']);
$runtimeRows = $runtime['json']['rows'] ?? [];
$runtimeByTech = [];
foreach ($runtimeRows as $row) {
    $name = (string)($row['technology'] ?? '');
    if ($name !== '') {
        $runtimeByTech[$name] = (string)($row['status'] ?? 'N/A');
    }
}

$techGroups = technologyCatalog();
$tableRows = [];
foreach ($techGroups as $group => $techs) {
    foreach ($techs as $tech) {
        $pf = array_key_exists($tech, $windowsPf) ? (bool)$windowsPf[$tech] : null;
        $ci = array_key_exists($tech, $cpuinfoFeatures) ? (bool)$cpuinfoFeatures[$tech] : null;
        $rt = $runtimeByTech[$tech] ?? 'NO PROBADO';

        $real = 'NO PROBADO';
        if ($rt === 'OK') {
            $real = 'YES';
        } elseif ($rt === 'ILLEGAL_INSTRUCTION') {
            $real = 'NO';
        }

        $tableRows[] = [
            'group' => $group,
            'tech' => $tech,
            'pf' => yn($pf),
            'cpuinfo' => yn($ci),
            'runtime' => $rt,
            'real' => $real,
        ];
    }
}

header('Content-Type: text/html; charset=utf-8');
?>
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Diagnostico CPU ISA</title>
<style>
  body { font-family: Segoe UI, Arial, sans-serif; background: #f5f7fa; margin: 0; color: #1f2a36; }
  .wrap { max-width: 1100px; margin: 0 auto; padding: 18px; }
  .head { background: #16324f; color: #fff; border-radius: 10px; padding: 14px 16px; margin-bottom: 14px; }
  .head-actions { margin-top: 12px; }
  .button { display: inline-block; padding: 10px 16px; border-radius: 999px; background: #d7ecff; color: #16324f; text-decoration: none; font-weight: 700; }
  .meta { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px; margin-bottom: 14px; }
  .card { background: #fff; border: 1px solid #d6dde5; border-radius: 10px; padding: 10px; }
  .k { font-size: 12px; text-transform: uppercase; color: #5b6b7a; }
  .v { margin-top: 4px; font-weight: 600; font-size: 14px; word-break: break-word; }
    .note { margin-bottom: 14px; background: #eef4fb; border: 1px solid #d6dde5; border-radius: 10px; padding: 12px; font-size: 14px; color: #30465d; }
  table { width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #d6dde5; border-radius: 10px; overflow: hidden; }
  th { background: #254f77; color: #fff; text-align: left; padding: 10px; font-size: 13px; }
  td { border-top: 1px solid #e2e8ef; padding: 10px; font-size: 14px; }
  tr:nth-child(even) td { background: #f9fbfd; }
    .group-row td { background: #edf3f9 !important; font-weight: 700; color: #1c3550; border-top: 2px solid #d6dde5; }
  .pill { display: inline-block; min-width: 70px; text-align: center; border-radius: 999px; padding: 4px 8px; font-size: 12px; font-weight: 700; }
  .yes { background: #e7f7ec; color: #176b35; }
  .no { background: #fdecee; color: #a01f2d; }
  .na { background: #edf1f6; color: #4c5e70; }
  details { margin-top: 14px; background: #fff; border: 1px solid #d6dde5; border-radius: 10px; padding: 10px; }
  pre { white-space: pre-wrap; word-break: break-word; font-size: 12px; margin: 8px 0 0; background: #f8fafc; border: 1px solid #e3eaf1; border-radius: 8px; padding: 8px; }
</style>
</head>
<body>
<div class="wrap">
  <div class="head">
    <h2 style="margin:0 0 6px;">Diagnostico CPU por tecnologia</h2>
    <div style="font-size:14px;opacity:.95;">Compara deteccion por Windows PF, py-cpuinfo y test de ejecucion real de instrucciones.</div>
    <div class="head-actions"><a class="button" href="?run=1">Ejecutar de nuevo</a></div>
  </div>

  <div class="meta">
    <div class="card"><div class="k">Python usado</div><div class="v"><?= h((string)($process['python_label'] ?? 'python')) ?></div></div>
    <div class="card"><div class="k">CPU</div><div class="v"><?= h((string)($platform['processor'] ?? '')) ?></div></div>
    <div class="card"><div class="k">Sistema</div><div class="v"><?= h((string)($platform['platform'] ?? '')) ?></div></div>
    <div class="card"><div class="k">Runtime global</div><div class="v"><span class="pill <?= labelClass(($runtime['json']['overall_pass'] ?? false) ? 'PASS' : 'FAIL') ?>"><?= ($runtime['json']['overall_pass'] ?? false) ? 'PASS' : 'FAIL' ?></span></div></div>
    <div class="card"><div class="k">Logical CPUs</div><div class="v"><?= h((string)($platform['logical_cpus'] ?? '')) ?></div></div>
    <div class="card"><div class="k">RAM disponible</div><div class="v"><?= h((string)($memory['available_gb'] ?? 'N/A')) ?> GB</div></div>
  </div>

    <div class="note">
        Esta tabla mezcla tres niveles de evidencia. <strong>Windows PF</strong> cubre pocas banderas expuestas por Windows, <strong>py-cpuinfo</strong> lista muchas mas, y <strong>Runtime test</strong> ahora llama siempre a una funcion por tecnologia. Si una prueba aun no esta hecha, la funcion devuelve <strong>NO PROBADO</strong>.
    </div>

  <table>
    <thead>
      <tr>
        <th>Tecnologia</th>
        <th>Windows PF</th>
        <th>py-cpuinfo</th>
        <th>Runtime test</th>
        <th>Acceso real</th>
      </tr>
    </thead>
    <tbody>
            <?php $currentGroup = null; ?>
            <?php foreach ($tableRows as $r): ?>
            <?php if ($currentGroup !== $r['group']): ?>
            <tr class="group-row">
                <td colspan="5"><?= h($r['group']) ?></td>
            </tr>
            <?php $currentGroup = $r['group']; ?>
            <?php endif; ?>
      <tr>
        <td><strong><?= h($r['tech']) ?></strong></td>
        <td><span class="pill <?= labelClass($r['pf']) ?>"><?= h($r['pf']) ?></span></td>
        <td><span class="pill <?= labelClass($r['cpuinfo']) ?>"><?= h($r['cpuinfo']) ?></span></td>
        <td><span class="pill <?= labelClass($r['runtime']) ?>"><?= h($r['runtime']) ?></span></td>
        <td><span class="pill <?= labelClass($r['real']) ?>"><?= h($r['real']) ?></span></td>
      </tr>
      <?php endforeach; ?>
    </tbody>
  </table>

  <details>
    <summary>Detalles tecnicos</summary>
    <pre><?php
echo 'PHP SAPI: ' . PHP_SAPI . "\n";
echo 'Python: ' . (string)($process['python_label'] ?? 'python') . "\n";
echo 'Runtime exit: ' . (string)($runtime['exit_code'] ?? -1) . "\n";
if (!$runtime['ok']) {
    echo 'Runtime status: fallo de ejecucion.' . "\n";
}
echo "\nPython attempts:\n";
foreach ($attempts as $at) {
    echo '- intento => ' . (($at['ok'] ?? false) ? 'OK' : 'ERROR') . ' (exit=' . (string)($at['exit_code'] ?? -1) . ')' . "\n";
}
    ?></pre>
  </details>
</div>
</body>
</html>