# Unreal Engine setup (Windows)

Connects Claude Code to the running Unreal Editor through Epic's official MCP
server and the "Unreal Engine Skills for Claude Code" plugin, following the
course in the project notes. Everything below runs on your PC.

You need: Unreal Engine 5.8 (Epic Games Launcher), Git for Windows (already
installed), and a Claude subscription for Claude Code.

## 1. Git LFS (one time)

Unreal assets are large binary files. Git LFS stores them efficiently.

```powershell
cd E:\DAODream
git lfs install
git pull
```

`git pull` brings in `.gitattributes` (which routes `.uasset`/`.umap` through
LFS) and `Unreal/.gitignore` (which keeps Unreal's caches out of git).

## 2. Create the project

1. Launch Unreal Engine 5.8 from the Epic Games Launcher.
2. **Games** → **Third Person**. Settings: **Blueprint**, **Desktop**,
   **Maximum** quality, **Starter Content** on.
3. Project location: `E:\DAODream\Unreal` (created under
   `C:\Users\joshu\Documents\DAODream` and moved to E: on 2026-10-16, when C:
   ran out of space)
   Project name: `Cousland`
4. **Create**. The editor opens with the third-person sample level. Press
   **Play** (Alt+P) once to check you can run around, then stop (Esc).

## 3. Turn on Unreal's MCP server

In the editor:

1. **Edit → Plugins**, search **Unreal MCP** (internal name
   `ModelContextProtocol`) and tick it. Search **AllToolsets** and tick it too.
   Restart the editor when asked. Both are needed: the first is the server,
   the second supplies the tools.
2. **Edit → Editor Preferences → General → Model Context Protocol**: turn on
   **Auto Start Server**.
3. Open the console with the **~** key (on an Italian keyboard it may be
   **\\** or **ò**; or **Window → Output Log** and type in the box at the
   bottom) and run:

   ```
   ModelContextProtocol.GenerateClientConfig ClaudeCode
   ```

   This writes `.mcp.json` next to `Cousland.uproject`. The server listens on
   port 8000 on your machine only.

## 4. Install Claude Code

In PowerShell:

```powershell
irm https://claude.ai/install.ps1 | iex
```

Close and reopen PowerShell, then run `claude` once and sign in.

## 5. Install Epic's plugin and start Claude in the project

```powershell
cd E:\DAODream\Unreal\Cousland
claude
```

Claude Code must start in the folder that holds `Cousland.uproject`, or it
won't find `.mcp.json`. It also reads this repo's `CLAUDE.md` from the
parent folders.

Inside Claude Code:

```
/plugin install unreal-engine-skills-for-claude-code@claude-plugins-official
```

If it says the marketplace is missing, first run
`/plugin marketplace add anthropics/claude-plugins-official`, then repeat.
Restart Claude Code after installing (`/exit`, then `claude`).

## 6. Check the connection

1. `/plugin`: **unreal-engine-skills-for-claude-code** is listed as enabled.
2. `/mcp`: **unreal-mcp** is connected. (The editor must be open.)
3. Send this read-only prompt:

   ```
   /unreal-mcp Inspect the open Unreal Editor project. Read only, change
   nothing. Report the active level's name, the main actors in it, and
   whether a Player Start and a Third Person character exist.
   ```

If it names real things from your level, the link works.

## 7. Save a restore point

Close the editor first (so files aren't locked), then:

```powershell
cd E:\DAODream
git add -A
git commit -m "Create Cousland Unreal project"
```

## Rules for every session

- **Commit before you start.** Claude gets full control of the editor, and not
  every change can be undone. A commit lets you roll back in seconds.
- **Keep permission prompts on.** Never start Claude with
  `--dangerously-skip-permissions` in this project.
- **Stop Play** before asking for changes, and **don't send prompts while
  shaders or code are compiling**.
- **One system per prompt**, test it, commit. Say what "done" means and what
  must not change, and ask for a list of everything it created.
- **Port 8000 has no password.** Don't expose it outside your PC.
- **No game files in the Unreal project yet.** Greybox and your own or Fab
  assets only. Anything imported from your DAO install stays out of git
  (see `CLAUDE.md`).

## First build: the great hall of Castle Cousland

Start a new empty level first: **File → New Level → Basic**, save it as
`/Game/Cousland/Maps/L_GreatHall`, then send:

```
/unreal-mcp Build a greybox of the great hall of Castle Cousland (from
Dragon Age: Origins) in the current level, L_GreatHall.
First, read only: confirm the level name and whether a Player Start exists.

Layout, in metres (1 m = 100 Unreal units):
- A stone hall about 30 long, 14 wide and 10 high, with a ceiling.
- Main double doors in the middle of the south wall, 4 wide and 5 high,
  leading out to a short courtyard stub (6 x 6, open sky).
- At the north end, a raised dais 1 high and 8 wide with steps, and a large
  high-backed chair (a simple block) on it facing the doors.
- Two rows of five square pillars, 1 x 1, running north-south, 3 metres in
  from each long wall.
- A big fireplace (an opening 3 wide, 2.5 high) in the middle of the east wall.
- Two doorways, 2 wide and 3 high: one in the west wall near the dais
  leading to a 10-metre corridor stub ("family quarters"), and one in the
  east wall near the doors leading to a 10-metre corridor stub ("kitchen").
- Put the Player Start just inside the main doors, facing the dais.

Use simple shapes and plain grey materials only. No final art.
Keep every opening and the space between the pillars free to walk through.
Light it so the whole hall is readable: a few point lights near the walls,
a warm light in the fireplace, and sky light over the courtyard stub.
Make sure the default Third Person character can play in this level.

Done means: I press Play and walk from the Player Start to the chair on the
dais, into both corridor stubs and out to the courtyard stub without getting
stuck or falling through anything.

When finished, list every actor and asset you created, and take a
screenshot from the Player Start looking toward the dais.
If a step fails or a tool is missing, stop and tell me. Don't work around
it silently.
```

**Check it:** press Play and walk the route: dais, both corridors,
courtyard. If something blocks you or you fall through, tell Claude exactly
where and ask for that one fix. When it holds, close the editor and commit.

Then send me the screenshot. The next step is the first conversation:
Bryce and Howe in this hall, driven by the dialogue data from `daotools`.
