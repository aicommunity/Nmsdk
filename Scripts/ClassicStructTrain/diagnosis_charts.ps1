[CmdletBinding()]
param([switch] $Checkpoint)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$study = Join-Path $repo 'Reports/StructTrainClassic/DiscrepancyDiagnosis-20261124'
$book = Join-Path $repo 'Reports/StructTrainClassic/outputs/01a20798-0fce-7661-bd9d-b3506770ffc9/DiscrepancyDiagnosis/DiscrepancyDiagnosis.xlsx'
$chartDirectory = Join-Path $study 'charts'
$indexDirectory = $study
if ($Checkpoint) {
    $indexDirectory = Join-Path $study 'checkpoint'
    $chartDirectory = Join-Path $indexDirectory 'charts'
    $book = Join-Path $indexDirectory 'DiscrepancyDiagnosis.xlsx'
}
New-Item -Path $chartDirectory -ItemType Directory -Force | Out-Null
$figures = Get-Content -LiteralPath (Join-Path $indexDirectory 'chart-index.json') -Encoding utf8 -Raw | ConvertFrom-Json
$digest = (Get-FileHash -LiteralPath $book -Algorithm SHA256).Hash
$excel = New-Object -ComObject Excel.Application
$ownExcel = !$excel.Visible -and $excel.Workbooks.Count -eq 0
$workbook = $null
$checks = @()
try {
    if (!$ownExcel) { throw 'An existing Excel session is active' }
    $excel.DisplayAlerts = $false
    $excel.EnableEvents = $false
    $excel.AutomationSecurity = 3
    $workbook = $excel.Workbooks.Open($book, 0, $true)
    $excel.CalculateFull()
    foreach ($sheet in $workbook.Worksheets) {
        $errors = $null
        try { $errors = $sheet.UsedRange.SpecialCells(-4123, 16) } catch {}
        if ($null -ne $errors) { throw "Spreadsheet errors in $($sheet.Name)" }
    }
    foreach ($figure in $figures) {
        $sheet = $workbook.Worksheets.Item($figure.id)
        $sheet.Activate()
        $chartObject = $sheet.ChartObjects().Item(1)
        $chart = $chartObject.Chart
        if ($chart.SeriesCollection().Count -ne $figure.rows[0].Count - 1) {
            throw "Incorrect number of series in $($figure.id)"
        }
        if ($chart.Axes(1).AxisTitle.Text -ne $figure.x -or $chart.Axes(2).AxisTitle.Text -ne $figure.y) {
            throw "Incorrect axis labels for $($figure.id)"
        }
        $lastCell = $sheet.Cells.Item($figure.rows.Count + 3, $figure.rows[0].Count)
        $values = $sheet.Range($sheet.Cells.Item(4, 1), $lastCell).Value2
        $minimum = $chart.Axes(2).MinimumScale
        $maximum = $chart.Axes(2).MaximumScale
        if ($null -ne $figure.major_unit -and $chart.Axes(2).MajorUnit -ne $figure.major_unit) {
            throw "Incorrect major scale unit for $($figure.id)"
        }
        for ($row = 0; $row -lt $figure.rows.Count; $row++) {
            if ([string] $values[($row + 1), 1] -ne [string] $figure.rows[$row][0]) {
                throw "Incorrect category label in $($figure.id)"
            }
            for ($column = 1; $column -lt $figure.rows[$row].Count; $column++) {
                $expected = $figure.rows[$row][$column]
                $actual = $values[($row + 1), ($column + 1)]
                if ($null -eq $expected) {
                    if ($null -ne $actual -and $actual -ne '') { throw "Unexpected value in $($figure.id)" }
                } elseif ($null -eq $actual -or [Math]::Abs($actual - $expected) -gt 1e-9) {
                    throw "Chart source values differ for $($figure.id)"
                } elseif ($actual -lt $minimum -or $actual -gt $maximum) {
                    throw "Value clipped by axis for $($figure.id)"
                }
            }
        }
        $chartObject.Width = 976
        $chartObject.Height = 542
        $png = Join-Path $chartDirectory ($figure.id + '.png')
        if (!$chart.Export($png, 'PNG', $false)) { throw "Chart export failed for $($figure.id)" }
        $checks += [ordered]@{ id = $figure.id; sha256 = (Get-FileHash -LiteralPath $png -Algorithm SHA256).Hash }
    }
} finally {
    if ($null -ne $workbook) { $workbook.Close($false) }
    if ($ownExcel) { $excel.Quit() }
    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($excel)
}
if ($digest -ne (Get-FileHash -LiteralPath $book -Algorithm SHA256).Hash) { throw 'Read only workbook changed' }
[ordered]@{ passed = $true; xlsx_sha256 = $digest; charts = $checks } |
    ConvertTo-Json -Depth 5 |
    Set-Content -LiteralPath (Join-Path $indexDirectory 'native-chart-audit.json') -Encoding utf8
