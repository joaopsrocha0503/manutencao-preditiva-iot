# PowerShell script to generate realistic industrial sensor data for predictive maintenance simulation.
# Using Invariant Culture to ensure dots ('.') are used as decimal separators regardless of host regional settings.

$culture = [System.Globalization.CultureInfo]::InvariantCulture

# Create directories
New-Item -ItemType Directory -Force -Path "c:\Users\Joao\Documents\FEUP_Manutencao_Preditiva\data" | Out-Null
New-Item -ItemType Directory -Force -Path "c:\Users\Joao\Documents\FEUP_Manutencao_Preditiva\scripts" | Out-Null

$startTime = [DateTime]::Parse("2026-05-20T08:00:00")
$csvData = @("timestamp,temperatura,vibracao,estado_operacional")

for ($i = 0; $i -lt 288; $i++) {
    $currentTime = $startTime.AddMinutes($i * 5)
    $timestamp = $currentTime.ToString("yyyy-MM-dd HH:mm:ss")
    
    # Hour of the day for scheduling anomalies
    $hour = $currentTime.Hour
    $minute = $currentTime.Minute
    $timeInHours = $hour + ($minute / 60.0)
    
    # Base normal parameters
    $temp = 52.0 + [Math]::Sin($timeInHours * [Math]::PI / 12) * 2.0  # Daily thermal cycle
    $vib = 1.2 + [Math]::Cos($timeInHours * [Math]::PI / 6) * 0.2     # Cyclic mechanical loading
    
    # Add random noise
    $randTempNoise = (Get-Random -Minimum -50 -Maximum 50) / 100.0  # -0.5 to +0.5
    $randVibNoise = (Get-Random -Minimum -15 -Maximum 15) / 100.0   # -0.15 to +0.15
    
    $temp += $randTempNoise
    $vib += $randVibNoise
    
    $estado = "Normal"
    
    # Check if we are in the next day
    $daysDiff = ($currentTime - $startTime).Days
    
    # --- Anomaly 1: Incipient Degradation (14:00 to 16:30 of the first day) ---
    if ($daysDiff -eq 0 -and $timeInHours -ge 14.0 -and $timeInHours -lt 16.5) {
        $progress = ($timeInHours - 14.0) / 2.5 # 0.0 to 1.0
        $temp += $progress * 34.0   # Sobe para ~86°C - 90°C (Limiar Alerta > 85°C)
        $vib += $progress * 1.8     # Sobe para ~3.0 - 3.2 mm/s RMS (Limiar Alerta > 2.8 mm/s)
        $estado = "Alerta - Sobreaquecimento Incipiente"
    }
    # --- Anomaly 2: Severe Mechanical Unbalance (20:00 to 21:15 of the first day) ---
    elseif ($daysDiff -eq 0 -and $timeInHours -ge 20.0 -and $timeInHours -lt 21.25) {
        $progress = ($timeInHours - 20.0) / 1.25
        $vib += 3.8 + [Math]::Sin($progress * [Math]::PI) * 0.5 # Vibração sobe para ~5.0 - 5.5 mm/s RMS (Limiar Crítico > 4.5 mm/s)
        $temp += 8.0 + $progress * 4.0 # Temperatura sobe ligeiramente para ~65°C - 68°C
        $estado = "Crítico - Vibração Severa"
    }
    # --- Emergency Shutdown / Cooling (21:15 to 22:30 of the first day) ---
    elseif ($daysDiff -eq 0 -and $timeInHours -ge 21.25 -and $timeInHours -lt 22.5) {
        $progress = ($timeInHours - 21.25) / 1.25 # 0.0 to 1.0
        $temp = 25.0 + [Math]::Exp(-$progress * 3.0) * (68.0 - 25.0) # Thermal decay to ambient 25°C
        $vib = 0.05 + [Math]::Exp(-$progress * 4.0) * (5.5 - 0.05)   # Mechanical decay
        $estado = "Parado - Intervenção de Manutenção"
    }
    # --- Post-Intervention Startup & Normalization (22:30 to 23:30 of the first day) ---
    elseif ($daysDiff -eq 0 -and $timeInHours -ge 22.5 -and $timeInHours -lt 23.5) {
        $progress = ($timeInHours - 22.5) / 1.0
        $temp = 25.0 + $progress * (51.0 - 25.0)
        $vib = 0.5 + $progress * 0.7
        $estado = "Normal (Arranque)"
    }
    
    # Format floats with '.' as decimal separator using Invariant Culture
    $tempStr = $temp.ToString("F2", $culture)
    $vibStr = $vib.ToString("F2", $culture)
    
    $csvData += "$timestamp,$tempStr,$vibStr,$estado"
}

$csvData | Out-File -FilePath "c:\Users\Joao\Documents\FEUP_Manutencao_Preditiva\data\sensores_simulados.csv" -Encoding utf8
Write-Host "Simulated sensor data successfully created at c:\Users\Joao\Documents\FEUP_Manutencao_Preditiva\data\sensores_simulados.csv"
