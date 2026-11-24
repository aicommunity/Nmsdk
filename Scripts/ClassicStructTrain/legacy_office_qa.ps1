[CmdletBinding()]
param(
 [ValidateSet('ExportSourceCharts','RenderDocx','CheckWorkbook')][string]$Mode,
 [string]$InputPath,
 [string]$OutputPath
)
$ErrorActionPreference='Stop'
$repoRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$workRoot=Join-Path $repoRoot 'Reports\StructTrainClassic\LegacyInferencePlan-20261123\work'
New-Item -ItemType Directory -Force -Path $workRoot | Out-Null
if($Mode -eq 'RenderDocx') {
 $wordApp=New-Object -ComObject Word.Application
 $ownInstance=(!$wordApp.Visible -and $wordApp.Documents.Count -eq 0)
 $document=$null
 try {
  if(!$ownInstance) { throw 'Word returned an existing user instance; refusing to change it.' }
  $wordApp.Visible=$false
  $wordApp.DisplayAlerts=0
  $wordApp.AutomationSecurity=3
  $document=$wordApp.Documents.Open((Resolve-Path -LiteralPath $InputPath).Path,$false,$true,$false)
  $document.ExportAsFixedFormat($OutputPath,17)
 } finally {
  if($document) { $document.Close(0) }
  if($ownInstance) { $wordApp.Quit() }
  [Runtime.InteropServices.Marshal]::FinalReleaseComObject($wordApp) | Out-Null
 }
 exit 0
}
$excelApp=New-Object -ComObject Excel.Application
$ownInstance=(!$excelApp.Visible -and $excelApp.Workbooks.Count -eq 0)
$workbook=$null
try {
 if(!$ownInstance) { throw 'Excel returned an existing user instance; refusing to change it.' }
 $excelApp.Visible=$false
 $excelApp.DisplayAlerts=$false
 $excelApp.AutomationSecurity=3
 $excelApp.EnableEvents=$false
 if($Mode -eq 'ExportSourceCharts') {
  $inventory=Get-Content -LiteralPath (Join-Path $workRoot 'inventory.json') -Raw -Encoding UTF8 | ConvertFrom-Json
  $records=@()
  $chartDir=Join-Path $workRoot 'source-charts'
  New-Item -ItemType Directory -Force -Path $chartDir | Out-Null
  foreach($source in $inventory.documents | Where-Object { $_.extension -eq '.xlsx' -and !$_.duplicate_of -and $_.native_chart_count -gt 0 }) {
   $sourcePath=Join-Path (Join-Path $repoRoot 'Docs\ClassicStructTrainExperiments') $source.path
   $workbook=$excelApp.Workbooks.Open($sourcePath,0,$true)
   foreach($sheet in $workbook.Worksheets) {
    $sheet.Activate()
    foreach($object in $sheet.ChartObjects()) {
     $id='E{0:D3}' -f ($records.Count+1)
     $destination=Join-Path $chartDir "$id.png"
     $chart=$object.Chart
     $oldWidth=$object.Width; $oldHeight=$object.Height
     $object.Width=720; $object.Height=420
     $chart.Refresh()
     $null=$chart.Export($destination,'PNG')
     if(!(Test-Path -LiteralPath $destination) -or (Get-Item -LiteralPath $destination).Length -eq 0) {
      $object.Activate()
      $chart.Refresh()
      Start-Sleep -Milliseconds 250
      $null=$chart.Export($destination,'PNG')
     }
     if(!(Test-Path -LiteralPath $destination) -or (Get-Item -LiteralPath $destination).Length -eq 0) { throw "Chart export is empty: $id" }
     $object.Width=$oldWidth; $object.Height=$oldHeight
     $series=@()
     for($i=1;$i -le $chart.SeriesCollection().Count;$i++) {
      $s=$chart.SeriesCollection($i)
      $series += @{name=$s.Name;formula=$s.Formula}
     }
     $title=if($chart.HasTitle){$chart.ChartTitle.Text}else{''}
     $records += @{id=$id;doc=$source.id;source=$source.path;sheet=$sheet.Name;name=$object.Name;title=$title;series=$series;preview=$destination}
    }
   }
   $workbook.Close($false); $workbook=$null
  }
  $records | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $workRoot 'source-chart-renders.json') -Encoding UTF8
  Write-Output "Exported $($records.Count) source charts"
 } else {
  $workbook=$excelApp.Workbooks.Open((Resolve-Path -LiteralPath $InputPath).Path,0,$true)
  $excelApp.CalculateFull()
  $planSheet=$workbook.Worksheets.Item('План')
  $planSheet.PageSetup.PrintArea='$A$1:$D$10'
  $planSheet.PageSetup.Orientation=2
  $planSheet.PageSetup.Zoom=$false
  $planSheet.PageSetup.FitToPagesWide=1
  $planSheet.PageSetup.FitToPagesTall=1
  $planSheet.ExportAsFixedFormat(0,(Join-Path $workRoot 'plan-native-excel.pdf'))
  $records=@()
  foreach($sheet in $workbook.Worksheets) {
   $records += @{sheet=$sheet.Name;title=$sheet.Range('A2').Value2;rows=$sheet.UsedRange.Rows.Count;columns=$sheet.UsedRange.Columns.Count;charts=$sheet.ChartObjects().Count}
  }
  $inference=$workbook.Worksheets.Item('Сравнение инференса')
  $before=@($inference.Range('W6').Value2,$inference.Range('X6').Value2,$inference.Range('Y6').Value2)
  $inference.Range('S6').Value2=49
  $inference.Range('T6').Value2=0
  $inference.Range('U6').Value2=1
  $inference.Range('V6').Value2=100
  $excelApp.CalculateFull()
  $filled=@($inference.Range('W6').Value2,$inference.Range('X6').Value2,$inference.Range('Y6').Value2)
  $inference.Range('S6:V6').ClearContents()
  $excelApp.CalculateFull()
  $restored=@($inference.Range('W6').Value2,$inference.Range('X6').Value2,$inference.Range('Y6').Value2)
  if($filled[0] -ne 0.99 -or $filled[2] -ne 'Записано' -or $restored[0] -ne '' -or $restored[2] -ne 'Не запускалось') { throw 'Native Excel formula verification failed' }
  @{sheets=$records;live_input_check=@{before=$before;filled=$filled;restored=$restored};saved_changes=$false} | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
  $workbook.Close($false); $workbook=$null
 }
} finally {
 if($workbook) { $workbook.Close($false) }
 if($ownInstance) { $excelApp.Quit() }
 [Runtime.InteropServices.Marshal]::FinalReleaseComObject($excelApp) | Out-Null
}
