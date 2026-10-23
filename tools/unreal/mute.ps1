# Mutes or unmutes a program in the Windows volume mixer (its audio sessions on the default speakers).
# pie.py mutes the Unreal editor for the length of a test: its own sound switches (game sound, editor
# sounds) were off and the house still heard it (2026-10-23).
#   powershell -NoProfile -ExecutionPolicy Bypass -File mute.ps1 -Name UnrealEditor -Mute 1
param([string]$Name = "UnrealEditor", [int]$Mute = 1)
Add-Type -TypeDefinition @"
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;

[Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDeviceEnumerator { int EnumAudioEndpoints(); [PreserveSig] int GetDefaultAudioEndpoint(int flow, int role, out IMMDevice device); }
[Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDevice { [PreserveSig] int Activate(ref Guid iid, int ctx, IntPtr p, [MarshalAs(UnmanagedType.IUnknown)] out object o); }
[Guid("77AA99A0-1BD6-484F-8BC7-2C654C9A9B6F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IAudioSessionManager2 { int GetAudioSessionControl(); int GetSimpleAudioVolume(); [PreserveSig] int GetSessionEnumerator(out IAudioSessionEnumerator e); }
[Guid("E2F5BB11-0570-40CA-ACDD-3AA01277DEE8"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IAudioSessionEnumerator { [PreserveSig] int GetCount(out int n); [PreserveSig] int GetSession(int i, out IAudioSessionControl2 s); }
[Guid("bfb7ff88-7239-4fc9-8fa2-07c950be9c6d"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IAudioSessionControl2 {
    int GetState(); int GetDisplayName(); int SetDisplayName(); int GetIconPath(); int SetIconPath(); int GetGroupingParam();
    int SetGroupingParam(); int RegisterNotification(); int UnregisterNotification(); int GetSessionIdentifier();
    int GetSessionInstanceIdentifier(); [PreserveSig] int GetProcessId(out uint pid);
}
[Guid("87CE5498-68D6-44E5-9215-6DA47EF883D8"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface ISimpleAudioVolume { int SetMasterVolume(); int GetMasterVolume(); [PreserveSig] int SetMute(bool mute, ref Guid ctx); [PreserveSig] int GetMute(out bool mute); }
[ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")] class MMDeviceEnumerator { }

public static class Mixer {
    public static int SetMute(int[] pids, bool mute) {
        var devices = (IMMDeviceEnumerator)new MMDeviceEnumerator();
        IMMDevice speakers; devices.GetDefaultAudioEndpoint(0, 1, out speakers);  // render, multimedia
        Guid iid = typeof(IAudioSessionManager2).GUID; object o;
        speakers.Activate(ref iid, 23, IntPtr.Zero, out o);
        IAudioSessionEnumerator sessions; ((IAudioSessionManager2)o).GetSessionEnumerator(out sessions);
        int n, done = 0; sessions.GetCount(out n);
        var wanted = new HashSet<int>(pids);
        for (int i = 0; i < n; i++) {
            IAudioSessionControl2 s; sessions.GetSession(i, out s);
            uint pid; s.GetProcessId(out pid);
            if (!wanted.Contains((int)pid)) continue;
            Guid none = Guid.Empty; ((ISimpleAudioVolume)s).SetMute(mute, ref none); done++;
        }
        return done;
    }
}
"@
$ids = @(Get-Process -Name $Name -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
if ($ids.Count -eq 0) { "no $Name running"; exit 0 }
"$Name sessions " + $(if ($Mute) { "muted" } else { "unmuted" }) + ": " + [Mixer]::SetMute([int[]]$ids, [bool]$Mute)
