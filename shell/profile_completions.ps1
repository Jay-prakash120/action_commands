# ==============================================================================
# Action Commands - PowerShell Argument Completers
# ==============================================================================

# Autocompletion for shutdown and restart
Register-ArgumentCompleter -Native -CommandName 'shutdown', 'restart' -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    @('--now', '--dry-run', '--force') | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }
}

# Autocompletion for killport
Register-ArgumentCompleter -Native -CommandName 'killport' -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    @('3000', '3001', '4000', '4200', '5000', '5173', '8000', '8080', '8888', '9000') | 
        Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
}

# Autocompletion for wifi
Register-ArgumentCompleter -Native -CommandName 'wifi' -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    @('list', 'connect', 'on', 'off', 'status') | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }
}

# Autocompletion for bright / brightness
Register-ArgumentCompleter -Native -CommandName 'bright', 'brightness' -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    @('+10', '-10', '+20', '-20', '25', '50', '75', '100') | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }
}

# Autocompletion for nl / nightlight
Register-ArgumentCompleter -Native -CommandName 'nl', 'nightlight' -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    @('on', 'off', 'status', 'toggle') | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }
}

# Autocompletion for hotspot
Register-ArgumentCompleter -Native -CommandName 'hotspot' -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    $tokens = $commandAst.Tokens
    if ($tokens.Count -ge 2 -and $tokens[1].Value -eq 'band') {
        @('2.4', '5', 'any') | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
    } else {
        @('on', 'off', 'status', 'toggle', 'band') | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
    }
}

# Autocompletion for myip
Register-ArgumentCompleter -Native -CommandName 'myip' -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    @('-r', '--refresh', '-f') | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }
}
