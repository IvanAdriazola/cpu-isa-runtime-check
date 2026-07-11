<?php
declare(strict_types=1);

require __DIR__ . '/../support/helpers.php';
require __DIR__ . '/../models/CpuDiagnosisModel.php';

final class CpuDiagnosisController
{
    public function __construct(private readonly string $projectRoot)
    {
    }

    public function handle(): void
    {
        $model = new CpuDiagnosisModel(
            $this->projectRoot,
            $this->projectRoot . DIRECTORY_SEPARATOR . 'python',
        );

        $viewModel = $model->buildViewModel();

        if ($viewModel['error'] ?? false) {
            header('Content-Type: text/plain; charset=utf-8');
            echo "Diagnostico CPU - ERROR\n\n";
            foreach (($viewModel['attempts'] ?? []) as $attempt) {
                echo 'Intento de Python fallido | exit=' . ($attempt['exit_code'] ?? -1) . "\n";
            }
            return;
        }

        require __DIR__ . '/../views/dashboard.php';
    }
}