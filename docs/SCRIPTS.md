# Game logic in compiled scripts (Human Noble survey)

What the conversations cannot do on their own lives in compiled scripts
(`.ncs`). This records how much there is and how it could be read. File names,
sizes and counts only; no script content.

## What is there

- 195 `.ncs` resources in the `bhn*` pull, 51 distinct scripts (the same
  script sits in several archives). About 620 KB of bytecode in total.
- By kind (from the name): 16 plot scripts (`*pt_*`, 401 KB), 19 trigger
  scripts (`*tr_*`, 53 KB), 9 placeable scripts (`*ip_*`, 78 KB), 5 creature
  scripts (`*cr_*`, 33 KB) and 2 area scripts (`bhn100ar_castle_cousland`,
  `bhn200ar_castle_after_siege`, 58 KB).
- The smallest plot scripts are 17-19 KB, which is mostly shared code compiled
  into each one (plot flag get/set, reward and XP handling). The story logic is
  what comes on top: e.g. about 9 KB for `bhn100pt_father`, 34 KB for
  `bhn100pt_gilmore`.
- The names the scripts reference show what kind of logic it is:
  - moving characters to waypoints when a flag is set (`bhn100pt_father`
    references `bhn100wp_father_upstairs` and `bhn100wp_mother_upstairs`:
    after the opening, Bryce and Eleanor go up to Fergus' room),
  - doors and placeables (`bhn000ip_door_pantry`, `bhn100ip_door_upstairs`),
  - switching to the night castle (`bhn000pt_main` references
    `bhn200ar_castle_after_siege`),
  - setting flags in other plots (codex entries, achievements, the party),
  - rewards and XP.
- Defined plot flags (256 and up, e.g. `GEN_GENDER_MALE`) are computed by these
  scripts too; for now they are passed in as true flags.

So Phase 1 needed none of it, but the castle only "plays" once the plot
scripts' effects exist: parents moving upstairs, the dog quest, the night.

## How to read it

The header is `NCS V1.0B`, the same bytecode family as Neverwinter Nights
scripts (NWScript), which is documented by the community (xoreos). Two ways:

1. **The official Dragon Age: Origins toolset** (`DragonAgeToolset1.01Setup.exe`).
   This is what we use: its database holds the source (`.nss`) of 2,079
   scripts, the whole game, 11.6 MB.
2. **A disassembler in daotools**: no longer needed. NWScript bytecode is
   simple, but Dragon Age adds several hundred engine functions that would have
   to come from community documentation.

The logic gets rewritten in Unreal (Blueprints), plot by plot, driven by the
same "GUID:FLAG" keys the dialogue runner already uses.

### Getting the source

Installing the toolset on Windows 11 with the Steam game took four fixes:

1. **"Dragon Age: Origins game install not found."** Steam does not write the
   registry key the installer reads. Add
   `HKLM\SOFTWARE\WOW6432Node\BioWare\Dragon Age` with `Path` (string, the game
   folder with a trailing backslash), `Installed` (DWORD 1) and `Version`
   ("1.05").
2. **"Error opening file for writing ... Common Files\BioWare\Uninstall Dragon
   Age Toolset.exe"**: run the installer as administrator, and create
   `C:\Program Files (x86)\Common Files\BioWare` by hand first (the installer
   does not create it).
3. **SQL Server**: the installer sets up SQL Server 2005 Express, instance
   `BWDATOOLSET`, under `C:\Program Files (x86)\DAODB`. On a second run, untick
   "Install MS SQL Express".
4. **The content database is not restored** even with "Restore the default
   database" ticked. Restore the shipped backup by hand, as administrator,
   moving the files into the instance's own data folder, then give your Windows
   account access:

   ```bat
   sqlcmd -S .\BWDATOOLSET -E -Q "RESTORE DATABASE bw_dragonage_content FROM DISK = N'<game>\tools\dbbak\bw_dragonage_content.bak' WITH MOVE N'bw_dragonage_content' TO N'C:\Program Files (x86)\DAODB\MSSQL.1\MSSQL\Data\bw_dragonage_content.mdf', MOVE N'bw_dragonage_content_log' TO N'C:\Program Files (x86)\DAODB\MSSQL.1\MSSQL\Data\bw_dragonage_content.ldf'"
   sqlcmd -S .\BWDATOOLSET -E -d bw_dragonage_content -Q "CREATE USER [<PC>\<user>] FOR LOGIN [<PC>\<user>]; EXEC sp_addrolemember N'db_owner', N'<PC>\<user>';"
   ```

   Other folders (e.g. `DAODB\Data`) fail with "Accesso negato": the server
   runs as Network Service.

Then copy the source out (2 s, into git-ignored `extracted/`):

```powershell
py -m daotools toolset scripts --out extracted/scripts/src
py -m daotools toolset scripts --pattern "bhn*" --out extracted/scripts/bhn
```

Source is in `t_Script.Text`, named through `t_ModuleResRefVersion`
(`Name`, `Folder`); each script also has an empty placeholder version.

### What a plot script looks like

`bhn100pt_father` is a switch over its flags, run when a flag is set
(`EVENT_TYPE_SET_PLOT`) or read (`EVENT_TYPE_GET_PLOT`, for defined flags).
Each case uses a small set of helpers: `UT_LocalJump` (move a creature to a
waypoint), `UT_Talk` (start a conversation), `WR_SetObjectActive` (show or
hide a creature), `WR_SetPlotFlag` (set another flag) and `DoAutoSave`.
Waypoint and object names come from `bhn_constants_h`. Porting a plot means
implementing those helpers once in Unreal and the cases per plot.
