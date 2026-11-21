# -*- coding: utf-8 -*-
"""Windows system inventory. Standard library only; no upload or elevation.

Run: python system_info.py
Import: start_system_info_export()  # non-blocking startup export
"""
import base64
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import threading
from datetime import datetime, timezone

# Explicit allowlist: no process command lines, credentials or environment dump.
QUERIES = {
    'operating_system': ('Win32_OperatingSystem', 'Caption,Version,BuildNumber,OSArchitecture,InstallDate,LastBootUpTime,TotalVisibleMemorySize,FreePhysicalMemory,Locale'),
    'computer': ('Win32_ComputerSystem', 'Name,Manufacturer,Model,SystemType,TotalPhysicalMemory,NumberOfLogicalProcessors,Domain,PartOfDomain'),
    'cpu': ('Win32_Processor', 'Name,Manufacturer,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed,SocketDesignation'),
    'memory_modules': ('Win32_PhysicalMemory', 'BankLabel,DeviceLocator,Capacity,Speed,ConfiguredClockSpeed,Manufacturer,PartNumber,SerialNumber'),
    'motherboard': ('Win32_BaseBoard', 'Manufacturer,Product,Version,SerialNumber'),
    'bios': ('Win32_BIOS', 'Manufacturer,SMBIOSBIOSVersion,SerialNumber,ReleaseDate'),
    'graphics': ('Win32_VideoController', 'Name,VideoProcessor,AdapterRAM,DriverVersion,DriverDate,CurrentHorizontalResolution,CurrentVerticalResolution'),
    'physical_disks': ('Win32_DiskDrive', 'Model,SerialNumber,InterfaceType,MediaType,Size,Partitions,Status'),
    'partitions': ('Win32_DiskPartition', 'DeviceID,DiskIndex,Index,Size,StartingOffset,Type,BootPartition'),
    'volumes': ('Win32_LogicalDisk', 'DeviceID,DriveType,FileSystem,VolumeName,Size,FreeSpace,VolumeSerialNumber'),
    'network_adapters': ('Win32_NetworkAdapter', 'Name,Manufacturer,MACAddress,NetEnabled,NetConnectionStatus,Speed,PhysicalAdapter'),
    'network_configuration': ('Win32_NetworkAdapterConfiguration', 'Description,IPEnabled,IPAddress,IPSubnet,DefaultIPGateway,DNSServerSearchOrder,DHCPEnabled,DHCPServer,MACAddress'),
    'sound_devices': ('Win32_SoundDevice', 'Name,Manufacturer,Status'),
    'monitors': ('Win32_DesktopMonitor', 'Name,MonitorManufacturer,ScreenWidth,ScreenHeight,Status'),
    'battery': ('Win32_Battery', 'Name,BatteryStatus,EstimatedChargeRemaining,EstimatedRunTime'),
    'printers': ('Win32_Printer', 'Name,DriverName,PortName,Default,Network,PrinterStatus'),
    'processes': ('Win32_Process', 'Name,ProcessId,ParentProcessId,ThreadCount,WorkingSetSize,CreationDate'),
    'services': ('Win32_Service', 'Name,DisplayName,State,StartMode,ProcessId'),
    'drivers': ('Win32_PnPSignedDriver', 'DeviceName,Manufacturer,DriverVersion,DriverDate,InfName,IsSigned'),
    'hotfixes': ('Win32_QuickFixEngineering', 'HotFixID,Description,InstalledOn'),
}


def tool_directory():
    """Never use cwd or PyInstaller's temporary extraction directory."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def powershell_program():
    query_json = json.dumps(QUERIES, ensure_ascii=True)
    return r'''
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$queries = ConvertFrom-Json @'
''' + query_json + r'''
'@
$result = [ordered]@{}
foreach ($entry in $queries.PSObject.Properties) {
    try {
        $className = $entry.Value[0]
        $fields = $entry.Value[1].Split(',')
        $rows = @(Get-CimInstance -ClassName $className -OperationTimeoutSec 12 -ErrorAction Stop | Select-Object -Property $fields)
        $result[$entry.Name] = @{status='ok'; items=$rows; error=$null}
    } catch {
        $result[$entry.Name] = @{status='error'; items=@(); error=$_.Exception.Message}
    }
}
try {
    # Registry inventory avoids Win32_Product's installer repair side effects.
    $locations = @(
        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
        'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
        'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*'
    )
    $software = @()
    foreach ($location in $locations) {
        $root = $location.Substring(0, $location.Length - 2)
        if (Test-Path -LiteralPath $root) {
            $software += @(Get-ItemProperty -Path $location -ErrorAction Stop |
                Where-Object { $_.DisplayName } |
                Select-Object DisplayName,DisplayVersion,Publisher,InstallDate)
        }
    }
    $software = @($software | Sort-Object DisplayName,DisplayVersion,Publisher -Unique)
    $result['installed_software'] = @{status='ok'; items=$software; error=$null}
} catch {
    $result['installed_software'] = @{status='error'; items=@(); error=$_.Exception.Message}
}
ConvertTo-Json -InputObject $result -Depth 8 -Compress
'''


def collect_system_info():
    report = {
        'schema_version': 1,
        'collected_at': datetime.now(timezone.utc).isoformat(),
        'status': 'complete',
        'tool_directory': str(tool_directory()),
        'runtime': {'system': platform.system(), 'release': platform.release(),
                    'machine': platform.machine(), 'python': platform.python_version()},
        'units': {'Capacity': 'bytes', 'Size': 'bytes', 'FreeSpace': 'bytes',
                  'WorkingSetSize': 'bytes', 'TotalPhysicalMemory': 'bytes',
                  'TotalVisibleMemorySize': 'KiB', 'FreePhysicalMemory': 'KiB',
                  'MaxClockSpeed': 'MHz', 'Speed': 'context dependent: memory MHz, network bits/s'},
        'notes': [
            'Inventory is limited to readable fields; not all system information is accessible.',
            'CIM dates use PowerShell JSON date serialization; raw provider values are preserved.',
            'Graphics AdapterRAM may be inaccurate above 4 GiB; monitor data may be absent.',
            'Software inventory covers uninstall registry entries, not every portable or Store app.',
            'Null fields mean the provider did not supply a value; empty lists can be normal.',
        ],
        'sections': {},
        'errors': [],
    }
    if os.name != 'nt':
        report['status'] = 'partial'
        report['errors'].append('Detailed inventory is supported only on Windows.')
        return report
    encoded = base64.b64encode(powershell_program().encode('utf-16-le')).decode('ascii')
    executable = str(Path(os.environ.get('SystemRoot', r'C:\Windows')) /
                     'System32' / 'WindowsPowerShell' / 'v1.0' / 'powershell.exe')
    try:
        proc = subprocess.run(
            [executable, '-NoLogo', '-NoProfile', '-NonInteractive', '-EncodedCommand', encoded],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=180, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
        )
        if proc.returncode != 0:
            raise RuntimeError('PowerShell exit {}: {}'.format(
                proc.returncode, proc.stderr.decode('utf-8', errors='replace')[:2000]))
        sections = json.loads(proc.stdout.decode('utf-8-sig'))
        if not isinstance(sections, dict):
            raise ValueError('PowerShell returned a non-object JSON value')
        report['sections'] = sections
        expected = set(QUERIES) | {'installed_software'}
        for name in sorted(expected):
            section = sections.get(name)
            if not isinstance(section, dict) or section.get('status') != 'ok':
                report['errors'].append({'section': name, 'error':
                    section.get('error') if isinstance(section, dict) else 'Missing section'})
        if report['errors']:
            report['status'] = 'partial'
    except (OSError, subprocess.TimeoutExpired, ValueError, RuntimeError) as exc:
        report['status'] = 'partial'
        report['errors'].append('{}: {}'.format(type(exc).__name__, exc))
    return report


def export_system_info():
    """Write atomically beside this module (or packaged EXE). Raise on write failure."""
    report = collect_system_info()
    destination = tool_directory() / 'system_info.json'
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                         dir=str(destination.parent),
                                         prefix='.system_info-', suffix='.tmp',
                                         delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(report, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(str(temporary), str(destination))
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return destination, report


def _background_export():
    try:
        path, report = export_system_info()
        message = 'System inventory {}: {}'.format(report['status'], path)
        print(message)
    except Exception as exc:
        message = 'System inventory export failed: {}: {}'.format(type(exc).__name__, exc)
        try:
            print(message, file=sys.stderr)
        except Exception:
            pass
    try:
        (tool_directory() / 'system_info_export.log').write_text(
            datetime.now(timezone.utc).isoformat() + ' ' + message + '\n', encoding='utf-8')
    except OSError:
        pass  # An unwritable tool directory cannot hold an error log either.


def start_system_info_export():
    # Non-daemon: normal application exit waits for the report to finish.
    worker = threading.Thread(target=_background_export, name='system-info-export', daemon=False)
    worker.start()
    return worker


if __name__ == '__main__':
    try:
        saved, data = export_system_info()
        print('Saved: {}'.format(saved))
        print('Status: {}; sections: {}; errors: {}'.format(
            data['status'], len(data['sections']), len(data['errors'])))
        sys.exit(0 if data['status'] == 'complete' else 2)
    except Exception as exc:
        print('Export failed: {}: {}'.format(type(exc).__name__, exc), file=sys.stderr)
        sys.exit(1)
