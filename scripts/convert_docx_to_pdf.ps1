param(
    [string]$docxPath,
    [string]$pdfPath
)

$docxResolved = (Resolve-Path $docxPath).Path
$pdfResolved = [System.IO.Path]::GetFullPath($pdfPath)

Write-Host "Converting Word document to PDF..."
Write-Host "Source DOCX: $docxResolved"
Write-Host "Target PDF:  $pdfResolved"

$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($docxResolved)
    # wdFormatPDF = 17
    $doc.SaveAs([ref]$pdfResolved, [ref]17)
    $doc.Close()
    Write-Host "Successfully converted DOCX to PDF: $pdfResolved"
} catch {
    Write-Error "Failed to export PDF: $_"
} finally {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
}
