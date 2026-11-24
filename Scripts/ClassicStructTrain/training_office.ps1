[CmdletBinding()]
param()
$ErrorActionPreference='Stop'
$taskRepo=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$taskWork=Join-Path $taskRepo 'Reports/StructTrainClassic/_work/TrainingReproducibility-20261123'
$taskBookPath=Join-Path $taskRepo 'Reports/StructTrainClassic/TrainingReproducibility.xlsx'
$taskFigures=Get-Content -LiteralPath (Join-Path $taskWork 'report-figures.json') -Raw -Encoding utf8 | ConvertFrom-Json
$taskData=Get-Content -LiteralPath (Join-Path $taskWork 'report-data.json') -Raw -Encoding utf8 | ConvertFrom-Json
$taskProvenance=Get-Content -LiteralPath (Join-Path $taskWork 'workbook-provenance.json') -Raw -Encoding utf8 | ConvertFrom-Json
$taskDataHash=(Get-FileHash -LiteralPath (Join-Path $taskWork 'report-data.json') -Algorithm SHA256).Hash
if($taskDataHash -ne $taskProvenance.report_data_sha256){throw 'Workbook and report data snapshots differ'}
$taskImageRoot=Join-Path $taskWork 'excel-charts'
New-Item -ItemType Directory -Force -Path $taskImageRoot | Out-Null
$taskExcel=New-Object -ComObject Excel.Application
$taskOwn=(!$taskExcel.Visible -and $taskExcel.Workbooks.Count -eq 0);$taskBook=$null
try {
 if(!$taskOwn){throw 'Refusing to use an existing Excel session'}
 $taskExcel.Visible=$false;$taskExcel.DisplayAlerts=$false;$taskExcel.EnableEvents=$false;$taskExcel.AutomationSecurity=3
 $taskBook=$taskExcel.Workbooks.Open((Resolve-Path -LiteralPath $taskBookPath).Path,0,$true);$taskExcel.CalculateFull()
 $taskRaw=$taskBook.Worksheets.Item('Распознавание');$taskPlot=$taskBook.Worksheets.Item(@($taskFigures | Where-Object {$_.id -like 'R01*'})[0].sheet)
 $taskBefore=@($taskRaw.Range('O6').Value2,$taskPlot.Range('B6').Value2)
 $taskOriginal=@($taskRaw.Range('B6').Value2,$taskRaw.Range('D6').Value2)
 $taskRaw.Range('B6').Value2=23;$taskRaw.Range('D6').Value2=27;$taskExcel.CalculateFull()
 $taskChanged=@($taskRaw.Range('O6').Value2,$taskPlot.Range('B6').Value2)
 $taskWant=(.46+$taskRaw.Range('E6').Value2/($taskRaw.Range('E6').Value2+$taskRaw.Range('C6').Value2))/2
 if([Math]::Abs($taskChanged[0]-$taskWant) -gt 1e-12 -or [Math]::Abs($taskChanged[1]-$taskWant) -gt 1e-12){throw 'Comparison chart does not recalculate from confusion counts'}
 $taskRaw.Range('B6').Value2=$taskOriginal[0];$taskRaw.Range('D6').Value2=$taskOriginal[1];$taskExcel.CalculateFull()
 $taskRestored=@($taskRaw.Range('O6').Value2,$taskPlot.Range('B6').Value2)
 if($taskRestored[0] -ne $taskBefore[0] -or $taskRestored[1] -ne $taskBefore[1]){throw 'Formula restoration failed'}
 $taskCountRows=@();$taskRow=6
 foreach($taskRecognition in $taskData.recognition){
  foreach($taskPair in @(@('historical',2),@('previous',6))){
   $taskMetrics=$taskRecognition.($taskPair[0]);$taskCol=[int]$taskPair[1]
   foreach($taskName in @('TP','FP','FN','TN')){
    if($taskRaw.Cells.Item($taskRow,$taskCol).Value2 -ne $taskMetrics.$taskName){throw "Historical confusion count mismatch in row $taskRow"};$taskCol++
   }
  }
  $taskNew=@($taskRecognition.new.runs | Where-Object {$_.metrics}) | Select-Object -First 1
  if($taskNew){
   $taskCol=10
   foreach($taskName in @('TP','FP','FN','TN')){if($taskRaw.Cells.Item($taskRow,$taskCol).Value2 -ne $taskNew.metrics.$taskName){throw "New training confusion count mismatch in row $taskRow"};$taskCol++}
  }
  $taskCountRows+=$taskRow;$taskRow++
 }
 $taskFormulaSheets=0
 foreach($taskSheet in $taskBook.Worksheets){
  $taskErrors=$null
  try{$taskErrors=$taskSheet.UsedRange.SpecialCells(-4123,16)}catch{}
  if($null -ne $taskErrors){throw "Native Excel formula error in $($taskSheet.Name): $($taskErrors.Address())"}
  $taskFormulaSheets++
 }
 $taskChecks=@()
 foreach($taskFigure in $taskFigures){
  $taskSheet=$taskBook.Worksheets.Item($taskFigure.sheet);$taskSheet.Activate()
  $taskCellsChecked=0
  if($taskFigure.expected_rows){
   $taskN=$taskFigure.expected_rows.Count;$taskM=$taskFigure.expected_rows[0].Count
   $taskValues=$taskSheet.Range($taskSheet.Cells.Item(6,1),$taskSheet.Cells.Item($taskN+5,$taskM)).Value2
   for($taskR=0;$taskR -lt $taskN;$taskR++){
    for($taskC=0;$taskC -lt $taskM;$taskC++){
     $taskWant=$taskFigure.expected_rows[$taskR][$taskC];$taskActual=$taskValues.GetValue($taskR+1,$taskC+1)
     if($null -eq $taskWant){if($null -ne $taskActual -and $taskActual -ne ''){throw 'Unexpected nonblank chart data'}}
     elseif($taskWant -is [ValueType]){
      if($null -eq $taskActual -or [Math]::Abs([double]$taskWant-[double]$taskActual) -gt 1e-10*[Math]::Max(1,[Math]::Abs([double]$taskWant))){throw "Chart source mismatch in $($taskFigure.id) row $taskR col $taskC"}
      if($taskC -gt 0 -and ([double]$taskActual -lt [double]$taskFigure.min-1e-9 -or [double]$taskActual -gt [double]$taskFigure.max+1e-9)){throw "Chart axis clips measured data in $($taskFigure.id)"}
     }
     elseif([string]$taskWant -ne [string]$taskActual){throw 'Chart category label mismatch'}
     $taskCellsChecked++
    }
   }
  }
  $taskObj=$taskSheet.ChartObjects().Item([int]$taskFigure.index);$taskChart=$taskObj.Chart
  if(!$taskChart.HasTitle -or $taskChart.ChartTitle.Text -ne $taskFigure.title){throw 'Chart identity mismatch'}
  foreach($taskAxis in @(1,2)){if(!$taskChart.Axes($taskAxis).HasTitle){throw "Missing axis title in $($taskFigure.id)"}}
  if($taskChart.Axes(1).AxisTitle.Text -ne $taskFigure.x_axis -or $taskChart.Axes(2).AxisTitle.Text -ne $taskFigure.y_axis){throw "Incorrect axes in $($taskFigure.id)"}
  if([Math]::Abs($taskChart.Axes(2).MinimumScale-$taskFigure.min) -gt 1e-10 -or [Math]::Abs($taskChart.Axes(2).MaximumScale-$taskFigure.max) -gt 1e-10){throw "Axis scale mismatch in $($taskFigure.id)"}
  $taskSeriesChecks=@()
  foreach($taskSeries in $taskChart.SeriesCollection()){
   $taskInfo=@{points=$taskSeries.Points().Count;formula=$taskSeries.Formula}
   if($taskFigure.kind -eq 'line'){
    $taskInfo.marker_size=$taskSeries.MarkerSize;$taskInfo.dash_style=$taskSeries.Format.Line.DashStyle
    if($taskSeries.MarkerSize -lt 8 -or $taskSeries.MarkerStyle -eq -4142 -or $taskSeries.Format.Line.DashStyle -ne 4){throw "Sparse chart lacks large markers and dashed lines: $($taskFigure.id)"}
   }
   if($taskFigure.kind -eq 'line_dense'){
    if($taskSeries.MarkerStyle -ne -4142 -or $taskSeries.Format.Line.DashStyle -ne 1){throw 'Dense training waveform unexpectedly uses sparse styling'}
   }
   $taskSeriesChecks+=$taskInfo
  }
  $taskObj.Width=650;$taskObj.Height=360
  $taskObj.Activate();$taskChart.Refresh();$taskChart.Axes(2).HasMinorGridlines=$false;$taskChart.Refresh()
  $taskDestination=Join-Path $taskImageRoot ($taskFigure.id+'.png');$null=$taskChart.Export($taskDestination,'PNG')
  if(!(Test-Path -LiteralPath $taskDestination) -or (Get-Item -LiteralPath $taskDestination).Length -eq 0){throw 'Empty native chart export'}
  $taskChecks+=@{id=$taskFigure.id;series=$taskSeriesChecks;data_cells_checked=$taskCellsChecked;image=$taskDestination;sha256=(Get-FileHash -LiteralPath $taskDestination -Algorithm SHA256).Hash}
 }
 @{passed=$true;report_data_sha256=$taskDataHash;workbook_sha256=(Get-FileHash -LiteralPath $taskBookPath -Algorithm SHA256).Hash;formula_check=@{before=$taskBefore;changed=$taskChanged;restored=$taskRestored};formula_error_sheets_checked=$taskFormulaSheets;historical_confusion_rows_checked=$taskCountRows;charts=$taskChecks;saved_changes=$false} | ConvertTo-Json -Depth 9 | Set-Content -LiteralPath (Join-Path $taskWork 'native-excel-check.json') -Encoding utf8
 $taskBook.Close($false);$taskBook=$null
 Write-Output "Verified native formulas, historical confusion counts, axis labels, markers, dashes and $($taskChecks.Count) charts"
}finally{if($taskBook){$taskBook.Close($false)};if($taskOwn){$taskExcel.Quit()};[Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskExcel)|Out-Null}
