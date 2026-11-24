[CmdletBinding()]
param([string]$WorkbookPath)
$ErrorActionPreference='Stop'
$repoRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$workRoot=Join-Path $repoRoot 'Reports\StructTrainClassic\_work\LegacyChecks-20261123'
if(!$WorkbookPath){$WorkbookPath=Join-Path $repoRoot 'Reports\StructTrainClassic\ScientificComparisons.xlsx'}
$figures=Get-Content -LiteralPath (Join-Path $workRoot 'scientific-figures.json') -Raw -Encoding utf8 | ConvertFrom-Json
$data=Get-Content -LiteralPath (Join-Path $workRoot 'scientific-comparison-data.json') -Raw -Encoding utf8 | ConvertFrom-Json
$imageRoot=Join-Path $workRoot 'scientific-excel-charts'
New-Item -ItemType Directory -Force -Path $imageRoot | Out-Null
function Get-ColumnName([int]$columnNumber){$value='';while($columnNumber -gt 0){$columnNumber--;$value=[char](65+$columnNumber%26)+$value;$columnNumber=[Math]::Floor($columnNumber/26)};return $value}
$excel=New-Object -ComObject Excel.Application
$own=(!$excel.Visible -and $excel.Workbooks.Count -eq 0);$book=$null
try {
 if(!$own){throw 'Refusing to use an existing Excel session'}
 $excel.Visible=$false;$excel.DisplayAlerts=$false;$excel.EnableEvents=$false;$excel.AutomationSecurity=3
 $book=$excel.Workbooks.Open((Resolve-Path -LiteralPath $WorkbookPath).Path,0,$true);$excel.CalculateFull()
 $raw=$book.Worksheets.Item('Данные эпох');$plot=$book.Worksheets.Item('SC01 51-61 TP TN')
 $oldTP=$raw.Range('G6').Value2;$oldFN=$raw.Range('I6').Value2
 $before=@($raw.Range('L6').Value2,$plot.Range('C6').Value2)
 $raw.Range('G6').Value2=23;$raw.Range('I6').Value2=27;$excel.CalculateFull()
 $changed=@($raw.Range('L6').Value2,$plot.Range('C6').Value2)
 if([Math]::Abs($changed[0]-.46) -gt 1e-12 -or [Math]::Abs($changed[1]-.46) -gt 1e-12){throw 'Scientific graph does not recalculate from the confusion counts'}
 $raw.Range('G6').Value2=$oldTP;$raw.Range('I6').Value2=$oldFN;$excel.CalculateFull()
 $restored=@($raw.Range('L6').Value2,$plot.Range('C6').Value2)
 if($restored[0] -ne $before[0] -or $restored[1] -ne $before[1]){throw 'Scientific formula restoration failed'}
 $checks=@()
 foreach($figure in $figures){
  $expected=@($data.figures | Where-Object {$_.id -eq $figure.id})[0]
  $sheet=$book.Worksheets.Item($figure.sheet);$sheet.Activate()
  $end=Get-ColumnName $expected.headers.Count;$last=$expected.rows.Count+5
  $values=$sheet.Range(('A6:{0}{1}' -f $end,$last)).Value2
  $checked=0
  for($r=0;$r -lt $expected.rows.Count;$r++){
   for($c=0;$c -lt $expected.headers.Count;$c++){
    $want=$expected.rows[$r][$c];$actual=$values.GetValue($r+1,$c+1)
    if($null -eq $want){if($null -ne $actual -and $actual -ne ''){throw "Unexpected value at $($figure.id) $r $c"}}
    elseif($want -is [ValueType]){if($null -eq $actual -or [Math]::Abs([double]$want-[double]$actual) -gt (1e-10*[Math]::Max(1,[Math]::Abs([double]$want)))){throw "Scientific data mismatch: $($figure.id) $r $c : $want / $actual"}}
    elseif([string]$want -ne [string]$actual){throw "Scientific label mismatch: $($figure.id) $r $c"}
    $checked++
   }
  }
  $obj=$sheet.ChartObjects().Item([int]$figure.index);$chart=$obj.Chart
  if(!$chart.HasTitle -or $chart.ChartTitle.Text -ne $figure.title){throw 'Scientific chart identity mismatch'}
  if(!$chart.Axes(1).HasTitle -or !$chart.Axes(2).HasTitle -or $chart.Axes(1).AxisTitle.Text -ne $figure.x_axis -or $chart.Axes(2).AxisTitle.Text -ne $figure.y_axis){throw "Axis titles missing or changed: $($figure.id)"}
  if([Math]::Abs($chart.Axes(2).MinimumScale-$figure.minimum) -gt 1e-10 -or [Math]::Abs($chart.Axes(2).MaximumScale-$figure.maximum) -gt 1e-10){throw "Scientific axis scale changed: $($figure.id)"}
  if($figure.format -eq '0' -and $figure.maximum -le 11 -and $chart.Axes(2).MajorUnit -ne 1){throw 'Discrete count scale has fractional tick intervals'}
  $seriesChecks=@()
  foreach($nativeSeries in $chart.SeriesCollection()){
   $info=@{points=$nativeSeries.Points().Count}
   if($figure.kind -eq 'line_sparse'){
    $info.marker_size=$nativeSeries.MarkerSize;$info.marker_style=$nativeSeries.MarkerStyle;$info.dash_style=$nativeSeries.Format.Line.DashStyle
    if($info.marker_size -lt 8 -or $info.marker_style -eq -4142 -or $info.dash_style -ne 4){throw "Sparse scientific chart lacks large markers and dashed lines: $($figure.id)"}
    if($info.points -ne $figure.point_count){throw "Scientific point count mismatch: $($figure.id)"}
   }
   if($figure.kind -eq 'line_dense'){
    $info.marker_style=$nativeSeries.MarkerStyle;$info.dash_style=$nativeSeries.Format.Line.DashStyle
    if($info.marker_style -ne -4142 -or $info.dash_style -ne 1){throw 'Dense time trace unexpectedly uses sparse-point styling'}
   }
   $seriesChecks+=$info
  }
  $obj.Width=600;$obj.Height=330
  $obj.Activate();$chart.Refresh();$chart.Axes(2).HasMinorGridlines=$false;$chart.Refresh()
  $destination=Join-Path $imageRoot ($figure.id+'.png');$null=$chart.Export($destination,'PNG')
  if(!(Test-Path -LiteralPath $destination) -or (Get-Item -LiteralPath $destination).Length -eq 0){throw 'Empty scientific chart export'}
  $checks+=@{id=$figure.id;title=$chart.ChartTitle.Text;x_axis=$chart.Axes(1).AxisTitle.Text;y_axis=$chart.Axes(2).AxisTitle.Text;data_cells_checked=$checked;series=$seriesChecks;image=$destination}
 }
 @{passed=$true;workbook_sha256=(Get-FileHash -LiteralPath $WorkbookPath -Algorithm SHA256).Hash;formula_check=@{before=$before;changed=$changed;restored=$restored};charts=$checks;saved_changes=$false} | ConvertTo-Json -Depth 9 | Set-Content -LiteralPath (Join-Path $workRoot 'scientific-native-excel-check.json') -Encoding utf8
 $book.Close($false);$book=$null
 Write-Output "Verified scientific source values, recalculation, large markers, dashed lines, and $($checks.Count) native figures"
}finally{if($book){$book.Close($false)};if($own){$excel.Quit()};[Runtime.InteropServices.Marshal]::FinalReleaseComObject($excel)|Out-Null}
