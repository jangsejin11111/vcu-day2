param([string]$Site = 'http://localhost:5174', [string]$Model = 'qwen3:4b-instruct')
$projectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $projectRoot
python scripts/vad_worker.py --site $Site --model $Model
