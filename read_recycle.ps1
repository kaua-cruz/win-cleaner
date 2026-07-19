$shell = New-Object -ComObject Shell.Application
$rb = $shell.NameSpace(10)
$items = $rb.Items()
Write-Host ("Itens: " + $items.Count.ToString())
foreach ($item in $items) {
    try {
        $name = $item.Name
        # Tenta coluna 1 (Original Location) e coluna 0 (Name)
        $col1 = $rb.GetDetailsOf($item, 1)
        $col0 = $rb.GetDetailsOf($item, 0)
        Write-Host ($name + "|orig:" + $col1 + "|name:" + $col0)
    } catch {
        Write-Host ("Erro: " + $_.Exception.Message)
    }
}
