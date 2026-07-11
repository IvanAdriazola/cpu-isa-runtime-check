<?php
declare(strict_types=1);

require __DIR__ . '/controllers/CpuDiagnosisController.php';

$controller = new CpuDiagnosisController(__DIR__);
$controller->handle();