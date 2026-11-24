[CmdletBinding()]
param([string]$WorkbookPath)
$ErrorActionPreference='Stop'
$repoRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$workRoot=Join-Path $repoRoot 'Reports\StructTrainClassic\_work\LegacyChecks-20261123'
if(!$WorkbookPath){$WorkbookPath=Join-Path $repoRoot 'Reports\StructTrainClassic\LegacyModelChecks.xlsx'}
$figures=Get-Content -LiteralPath (Join-Path $workRoot 'figures.json') -Raw -Encoding utf8 | ConvertFrom-Json
$imageRoot=Join-Path $workRoot 'excel-charts'
New-Item -ItemType Directory -Force -Path $imageRoot | Out-Null
$excelApp=New-Object -ComObject Excel.Application
$ownInstance=(!$excelApp.Visible -and $excelApp.Workbooks.Count -eq 0)
$workbook=$null
try {
 if(!$ownInstance){throw 'Excel returned a user instance; refusing to modify it.'}
 $excelApp.Visible=$false;$excelApp.DisplayAlerts=$false;$excelApp.EnableEvents=$false;$excelApp.AutomationSecurity=3
 $workbook=$excelApp.Workbooks.Open((Resolve-Path -LiteralPath $WorkbookPath).Path,0,$true)
 $excelApp.CalculateFull()
 $sheet=$workbook.Worksheets.Item('Сохранённые модели')
 $oldValue=$sheet.Range('G6').Value2;$before=@($sheet.Range('K6').Value2,$sheet.Range('M6').Value2)
 $sheet.Range('G6').Value2=0;$excelApp.CalculateFull()
 $changed=@($sheet.Range('K6').Value2,$sheet.Range('M6').Value2)
 $sheet.Range('G6').Value2=$oldValue;$excelApp.CalculateFull()
 $restored=@($sheet.Range('K6').Value2,$sheet.Range('M6').Value2)
 if($changed[0] -ne '' -or $changed[1] -ne 0.5 -or $restored[0] -ne $before[0] -or $restored[1] -ne $before[1]){throw 'Native Excel recalculation check failed'}
 $exports=@()
 foreach($figure in $figures){
  $sheet=$workbook.Worksheets.Item($figure.sheet);$sheet.Activate()
  $object=$sheet.ChartObjects().Item([int]$figure.index);$chart=$object.Chart
  if(!$chart.HasTitle -or $chart.ChartTitle.Text -ne $figure.title){throw "Chart identity mismatch: $($figure.id)"}
  $pointCounts=@();foreach($nativeSeries in $chart.SeriesCollection()){$pointCounts+=@($nativeSeries.Points().Count)}
  if($figure.sheet -eq 'Проекции Iris' -and ($pointCounts -join ',') -ne '50,50,50,10,1,1'){throw "Invalid Iris series point counts: $($figure.id): $($pointCounts -join ',')"}
  $oldWidth=$object.Width;$oldHeight=$object.Height
  $object.Width=540;$object.Height=280
  if($figure.sheet -in @('Сигналы','Переходы')){$object.Height=240}
  $object.Activate();$chart.Refresh()
  # Imported charts retain a narrow cached label gutter when resized. Reserve
  # enough room for complete native axis labels in the DOCX-sized export.
  $chart.PlotArea.InsideLeft=72
  $chart.PlotArea.InsideWidth=$object.Width-84
  $chart.Axes(2).HasMinorGridlines=$false
  $chart.Refresh()
  $destination=Join-Path $imageRoot ($figure.id+'.png')
  $null=$chart.Export($destination,'PNG')
  if(!(Test-Path -LiteralPath $destination) -or (Get-Item -LiteralPath $destination).Length -eq 0){
   $object.Activate();$chart.Refresh();Start-Sleep -Milliseconds 250;$null=$chart.Export($destination,'PNG')
  }
  if(!(Test-Path -LiteralPath $destination) -or (Get-Item -LiteralPath $destination).Length -eq 0){throw "Empty native chart export: $($figure.id)"}
  $object.Width=$oldWidth;$object.Height=$oldHeight
  $exports+=@{id=$figure.id;sheet=$figure.sheet;title=$chart.ChartTitle.Text;series=$chart.SeriesCollection().Count;image=$destination}
 }
 @{formula_check=@{before=$before;changed=$changed;restored=$restored};charts=$exports;saved_changes=$false} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $workRoot 'native-excel-check.json') -Encoding utf8
 $workbook.Close($false);$workbook=$null
 Write-Output "Verified formulas and exported $($exports.Count) native charts"
}finally{
 if($workbook){$workbook.Close($false)}
 if($ownInstance){$excelApp.Quit()}
 [Runtime.InteropServices.Marshal]::FinalReleaseComObject($excelApp) | Out-Null
}
