param(
    [string]$Action = "status",
    [string]$Param = ""
)

Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Networking.Connectivity.NetworkInformation,Windows.Networking.Connectivity,ContentType=WindowsRuntime] | Out-Null
[Windows.Networking.NetworkOperators.NetworkOperatorTetheringManager,Windows.Networking.NetworkOperators,ContentType=WindowsRuntime] | Out-Null
[Windows.Networking.NetworkOperators.NetworkOperatorTetheringOperationResult,Windows.Networking.NetworkOperators,ContentType=WindowsRuntime] | Out-Null
[Windows.Networking.NetworkOperators.TetheringWiFiBand,Windows.Networking.NetworkOperators,ContentType=WindowsRuntime] | Out-Null

$profile = [Windows.Networking.Connectivity.NetworkInformation]::GetInternetConnectionProfile()
if (-not $profile) {
    Write-Host "ERROR:No internet connection profile found."
    exit 1
}

$mgr = [Windows.Networking.NetworkOperators.NetworkOperatorTetheringManager]::CreateFromConnectionProfile($profile)

$asTaskOp = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { 
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' 
})[0].MakeGenericMethod([Windows.Networking.NetworkOperators.NetworkOperatorTetheringOperationResult])

$asTaskAction = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { 
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncAction' 
})[0]

if ($Action -eq "toggle") {
    $Action = if ($mgr.TetheringOperationalState -eq [Windows.Networking.NetworkOperators.TetheringOperationalState]::On) { "stop" } else { "start" }
}

if ($Action -eq "start" -or $Action -eq "on") {
    if ($mgr.TetheringOperationalState -eq [Windows.Networking.NetworkOperators.TetheringOperationalState]::On) {
        Write-Host "ALREADY:ON"
    } else {
        $asyncOp = $mgr.StartTetheringAsync()
        $task = $asTaskOp.Invoke($null, @($asyncOp))
        $task.Wait()
    }
} elseif ($Action -eq "stop" -or $Action -eq "off") {
    if ($mgr.TetheringOperationalState -eq [Windows.Networking.NetworkOperators.TetheringOperationalState]::Off) {
        Write-Host "ALREADY:OFF"
    } else {
        $asyncOp = $mgr.StopTetheringAsync()
        $task = $asTaskOp.Invoke($null, @($asyncOp))
        $task.Wait()
    }
} elseif ($Action -eq "band") {
    $cfg = $mgr.GetCurrentAccessPointConfiguration()
    $targetBand = $Param.ToLower()
    $bandEnum = $null

    if ($targetBand -like "5*") {
        $bandEnum = [Windows.Networking.NetworkOperators.TetheringWiFiBand]::FiveGigahertz
    } elseif ($targetBand -like "2*" -or $targetBand -eq "2.4") {
        $bandEnum = [Windows.Networking.NetworkOperators.TetheringWiFiBand]::TwoPointFourGigahertz
    } elseif ($targetBand -eq "any" -or $targetBand -eq "auto") {
        $bandEnum = [Windows.Networking.NetworkOperators.TetheringWiFiBand]::Auto
    } else {
        Write-Host "ERROR:Invalid band '$Param'. Use '2.4', '5', or 'any'."
        exit 1
    }

    if ($cfg.Band -eq $bandEnum) {
        Write-Host "ALREADY:BAND"
    } else {
        $cfg.Band = $bandEnum
        $actionCall = $mgr.ConfigureAccessPointAsync($cfg)
        $task = $asTaskAction.Invoke($null, @($actionCall))
        $task.Wait()
    }
}

$cfg = $mgr.GetCurrentAccessPointConfiguration()
Write-Host "STATE:$($mgr.TetheringOperationalState)"
Write-Host "SSID:$($cfg.Ssid)"
Write-Host "PASSWORD:$($cfg.Passphrase)"
Write-Host "BAND:$($cfg.Band)"
Write-Host "CLIENTS:$($mgr.ClientCount)"
