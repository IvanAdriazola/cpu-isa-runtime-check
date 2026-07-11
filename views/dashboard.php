<?php
declare(strict_types=1);

$platform = $viewModel['platform'] ?? [];
$process = $viewModel['process'] ?? [];
$memory = $viewModel['memory'] ?? [];
$runtime = $viewModel['runtime'] ?? [];
$tableRows = $viewModel['tableRows'] ?? [];
$attempts = $viewModel['attempts'] ?? [];

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
    <div class="card"><div class="k">Python usado</div><div class="v"><?= h((string) ($process['python_label'] ?? 'python')) ?></div></div>
    <div class="card"><div class="k">CPU</div><div class="v"><?= h((string) ($platform['processor'] ?? '')) ?></div></div>
    <div class="card"><div class="k">Sistema</div><div class="v"><?= h((string) ($platform['platform'] ?? '')) ?></div></div>
    <div class="card"><div class="k">Runtime global</div><div class="v"><span class="pill <?= labelClass(($runtime['json']['overall_pass'] ?? false) ? 'PASS' : 'FAIL') ?>"><?= ($runtime['json']['overall_pass'] ?? false) ? 'PASS' : 'FAIL' ?></span></div></div>
    <div class="card"><div class="k">Logical CPUs</div><div class="v"><?= h((string) ($platform['logical_cpus'] ?? '')) ?></div></div>
    <div class="card"><div class="k">RAM disponible</div><div class="v"><?= h((string) ($memory['available_gb'] ?? 'N/A')) ?> GB</div></div>
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
      <?php foreach ($tableRows as $row): ?>
      <?php if ($currentGroup !== $row['group']): ?>
      <tr class="group-row">
        <td colspan="5"><?= h($row['group']) ?></td>
      </tr>
      <?php $currentGroup = $row['group']; ?>
      <?php endif; ?>
      <?php $pfLabel = yn($row['pf']); ?>
      <?php $cpuinfoLabel = yn($row['cpuinfo']); ?>
      <tr>
        <td><strong><?= h($row['tech']) ?></strong></td>
        <td><span class="pill <?= labelClass($pfLabel) ?>"><?= h($pfLabel) ?></span></td>
        <td><span class="pill <?= labelClass($cpuinfoLabel) ?>"><?= h($cpuinfoLabel) ?></span></td>
        <td><span class="pill <?= labelClass($row['runtime']) ?>"><?= h($row['runtime']) ?></span></td>
        <td><span class="pill <?= labelClass($row['real']) ?>"><?= h($row['real']) ?></span></td>
      </tr>
      <?php endforeach; ?>
    </tbody>
  </table>

  <details>
    <summary>Detalles tecnicos</summary>
    <pre><?php
echo 'PHP SAPI: ' . PHP_SAPI . "\n";
echo 'Python: ' . (string) ($process['python_label'] ?? 'python') . "\n";
echo 'Runtime exit: ' . (string) ($runtime['exit_code'] ?? -1) . "\n";
if (!($runtime['ok'] ?? false)) {
    echo 'Runtime status: fallo de ejecucion.' . "\n";
}
echo "\nPython attempts:\n";
foreach ($attempts as $attempt) {
    echo '- intento => ' . (($attempt['ok'] ?? false) ? 'OK' : 'ERROR') . ' (exit=' . (string) ($attempt['exit_code'] ?? -1) . ')' . "\n";
}
?></pre>
  </details>
</div>
</body>
</html>