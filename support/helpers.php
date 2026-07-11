<?php
declare(strict_types=1);

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