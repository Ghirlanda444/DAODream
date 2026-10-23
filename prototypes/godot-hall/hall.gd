# PROTOTYPE - NOT FOR PRODUCTION (prototypes/godot-hall)
# Great Hall style test: Castle Cousland's hall built from primitives at runtime
# and drawn in ink and cel. Every mesh and texture is generated here; nothing
# comes from the original game.
extends Node3D

const TOON := preload("res://spatial_cel_toon.gdshader")
const INK := preload("res://post_ink_outline.gdshader")

const W := 14.0
const L := 26.0
const H := 8.0
const WALL_T := 0.8
const WINDOWS := [-8.5, -3.5, 1.5, 6.5]
const WIN_W := 1.5
const SILL := 3.1
const TOP := 6.7
const SUN_DIR := Vector3(1.0, -1.05, -0.28)

const KINDS := {
	"wall": {"tex": "wall", "tile": 2.4},
	"stone": {"tex": "wall", "tile": 2.4},
	"floor": {"tex": "floor", "tile": 3.2},
	"wood": {"tex": "wood", "tile": 1.6},
	"darkwood": {"tex": "wood", "tile": 2.0, "color": "8a7a6a"},
	"rug": {"tex": "rug", "tile": 2.2, "offset": Vector2(0.5, 0.0)},
	"bannerR": {"tex": "bannerR", "uv": true},
	"bannerB": {"tex": "bannerB", "uv": true},
	"red": {"color": "8b2a25"},
	"blue": {"color": "2c4a7c"},
	"green": {"color": "34452c"},
	"tabard": {"color": "7e2622"},
	"gold": {"color": "c9a24a"},
	"iron": {"color": "45454a"},
	"mail": {"color": "8d8f94"},
	"leather": {"color": "4a3322"},
	"skin": {"color": "d8a284"},
	"hairGrey": {"color": "b9b2a6"},
	"hairDark": {"color": "3a281c"},
	"fur": {"color": "7d6a55"},
	"dog": {"color": "8a6038"},
	"dogDark": {"color": "3e2a1a"},
	"eye": {"color": "15100c"},
	"coal": {"color": "1d1612"},
	"fire": {"color": "ffb050", "emit": 2.6},
	"glass": {"color": "9fb4d8", "emit": 1.3},
}

const MODES := [
	{"name": "Plain", "bands": 0, "ink": false},
	{"name": "Ink & cel", "bands": 3, "ink": true},
	{"name": "Cel, no ink", "bands": 3, "ink": false},
]

var _textures := {}
var _mats := {}
var _mode := 1
var _bands := 3
var _low_spec := false
var _hud_visible := true

var _camera: Camera3D
var _ink_quad: MeshInstance3D
var _sun: DirectionalLight3D
var _fires: Array[OmniLight3D] = []
var _flames: Array[MeshInstance3D] = []
var _actors: Array[Dictionary] = []
var _howe: Dictionary
var _bryce: Dictionary
var _dog_tail: Node3D
var _dog_head: Node3D
var _hud_layer: CanvasLayer
var _stats: Label
var _mode_label: Label

var _target := Vector3(0.3, 1.35, -9.3)
var _yaw := 0.3
var _pitch := 0.14
var _dist := 8.4
var _dragging := false
var _last_input := -10.0
var _sway_on := false
var _sway_start := 0.0
var _sway_base := 0.0
var _time := 0.0
var _frozen := false  # holds the camera still while --shots runs


func _ready() -> void:
	_make_textures()
	_build_environment()
	_build_hall()
	_build_people()
	_build_camera()
	_build_hud()
	_apply_mode(1)
	var shots := _user_arg("shots")
	if shots != "":
		_take_shots(shots)


# ---------- procedural textures (flat tints for cel) ----------

func _h(a: int, b: int, c: int) -> float:
	var x := (a * 73856093) ^ (b * 19349663) ^ (c * 83492791)
	x = (x ^ (x >> 13)) * 1274126177
	x = x ^ (x >> 16)
	return float(x & 0xFFFF) / 65535.0


func _tex(img: Image) -> ImageTexture:
	img.generate_mipmaps()
	return ImageTexture.create_from_image(img)


func _ashlar(a: Color, b: Color, mortar: Color, rows: int, cols: int, seed: int) -> ImageTexture:
	var s := 512
	var img := Image.create_empty(s, s, false, Image.FORMAT_RGBA8)
	img.fill(mortar)
	var bh := int(s / float(rows))
	var bw := int(s / float(cols))
	var m := 4
	var full := Rect2i(0, 0, s, s)
	for j in rows:
		var off := (j % 2) * int(bw / 2.0)
		for i in range(-1, cols + 1):
			var idx := posmod(i, cols)
			var col := a.lerp(b, _h(seed, j, idx)) * (0.95 + 0.1 * _h(seed + 7, j, idx))
			col.a = 1.0
			var r := Rect2i(i * bw + off + m / 2, j * bh + m / 2, bw - m, bh - m).intersection(full)
			if r.has_area():
				img.fill_rect(r, col)
	return _tex(img)


func _flagstones(a: Color, b: Color, mortar: Color, rows: int, seed: int) -> ImageTexture:
	var s := 512
	var img := Image.create_empty(s, s, false, Image.FORMAT_RGBA8)
	img.fill(mortar)
	var bh := int(s / float(rows))
	var m := 5
	var full := Rect2i(0, 0, s, s)
	var rng := RandomNumberGenerator.new()
	for j in rows:
		rng.seed = seed * 31 + j
		var x := int(rng.randf() * s * 0.3)
		var start := x
		var k := 0
		while x < start + s:
			var w: int = min(int(s * (0.18 + rng.randf() * 0.2)), start + s - x)
			var col := a.lerp(b, _h(seed, j, k))
			col.a = 1.0
			for wrap in [0, -s]:
				var r := Rect2i(x + wrap + m / 2, j * bh + m / 2, w - m, bh - m).intersection(full)
				if r.has_area():
					img.fill_rect(r, col)
			x += w
			k += 1
	return _tex(img)


func _planks(a: Color, b: Color, seam: Color, rows: int, seed: int) -> ImageTexture:
	var s := 512
	var img := Image.create_empty(s, s, false, Image.FORMAT_RGBA8)
	img.fill(seam)
	var bh := int(s / float(rows))
	var rng := RandomNumberGenerator.new()
	rng.seed = seed
	for j in rows:
		var col := a.lerp(b, _h(seed, j, 0))
		col.a = 1.0
		img.fill_rect(Rect2i(0, j * bh + 2, s, bh - 4), col)
		var grain := col.darkened(0.18)
		for g in 5:
			var gy := j * bh + 6 + int(rng.randf() * (bh - 12))
			var amp := 1.0 + rng.randf() * 2.0
			var ph := rng.randf() * 6.0
			for px in s:
				var y := gy + int(sin(px / 40.0 + ph) * amp)
				img.set_pixel(px, clampi(y, 0, s - 1), grain)
		img.fill_rect(Rect2i(int(rng.randf() * (s - 4)), j * bh, 3, bh), seam)
	return _tex(img)


func _cloth(base: Color, trim: Color, pattern: String) -> ImageTexture:
	var s := 256
	var img := Image.create_empty(s, s, false, Image.FORMAT_RGBA8)
	img.fill(base)
	if pattern == "banner":
		var m := int(s * 0.07)
		var t := int(s * 0.035)
		img.fill_rect(Rect2i(m, 0, t, s), trim)
		img.fill_rect(Rect2i(s - m - t, 0, t, s), trim)
		img.fill_rect(Rect2i(0, int(s * 0.06), s, t), trim)
		for y in s:
			for x in s:
				var u := x / float(s)
				var v := y / float(s)
				# chevron under a roundel: a plain heraldic charge
				var top := 0.42 + absf(u - 0.5) * 0.73
				if u > 0.2 and u < 0.8 and v > top and v < top + 0.1:
					img.set_pixel(x, y, trim)
				if Vector2(u - 0.5, v - 0.27).length() < 0.09:
					img.set_pixel(x, y, trim)
	elif pattern == "rug":
		var t := int(s * 0.035)
		img.fill_rect(Rect2i(int(s * 0.06), 0, t, s), trim)
		img.fill_rect(Rect2i(s - int(s * 0.06) - t, 0, t, s), trim)
		for y in s:
			for x in s:
				var u := x / float(s)
				var v := fmod(y / float(s), 0.5) * 2.0
				var dd := absf(u - 0.5) / 0.18 + absf(v - 0.5) / 0.28
				if dd > 0.86 and dd < 1.0:
					img.set_pixel(x, y, trim)
	return _tex(img)


func _make_textures() -> void:
	_textures["wall"] = _ashlar(Color("b8ab94"), Color("8f8573"), Color("5c554b"), 8, 4, 11)
	_textures["floor"] = _flagstones(Color("77736e"), Color("57534f"), Color("33302c"), 5, 23)
	_textures["wood"] = _planks(Color("75502f"), Color("5c3c22"), Color("2a1a10"), 6, 5)
	_textures["rug"] = _cloth(Color("7d2420"), Color("c39a45"), "rug")
	_textures["bannerR"] = _cloth(Color("862823"), Color("d0a64c"), "banner")
	_textures["bannerB"] = _cloth(Color("2a4673"), Color("d0a64c"), "banner")


func _mat(kind: String) -> ShaderMaterial:
	if _mats.has(kind):
		return _mats[kind]
	var k: Dictionary = KINDS[kind]
	var m := ShaderMaterial.new()
	m.shader = TOON
	m.set_shader_parameter("albedo", Color(k.get("color", "ffffff")))
	if k.has("tex"):
		m.set_shader_parameter("albedo_tex", _textures[k["tex"]])
		m.set_shader_parameter("use_tex", true)
		m.set_shader_parameter("triplanar", not k.get("uv", false))
		m.set_shader_parameter("tile", k.get("tile", 2.0))
		m.set_shader_parameter("tex_offset", k.get("offset", Vector2.ZERO))
	if k.has("emit"):
		m.set_shader_parameter("emission_color", Color(k["color"]))
		m.set_shader_parameter("emission_energy", k["emit"])
		m.set_shader_parameter("albedo", Color(0, 0, 0))
	_mats[kind] = m
	return m


# ---------- mesh helpers ----------

func _add(mesh: Mesh, kind: String, pos: Vector3, parent: Node3D) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.position = pos
	mi.material_override = _mat(kind)
	if KINDS[kind].has("emit"):
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(mi)
	return mi


func _box(size: Vector3, kind: String, pos: Vector3, parent: Node3D = self) -> MeshInstance3D:
	var m := BoxMesh.new()
	m.size = size
	return _add(m, kind, pos, parent)


func _cyl(rt: float, rb: float, h: float, seg: int, kind: String, pos: Vector3, parent: Node3D = self) -> MeshInstance3D:
	var m := CylinderMesh.new()
	m.top_radius = rt
	m.bottom_radius = rb
	m.height = h
	m.radial_segments = seg
	m.rings = 1
	return _add(m, kind, pos, parent)


func _sph(r: float, kind: String, pos: Vector3, parent: Node3D = self, scl := Vector3.ONE, hemi := false) -> MeshInstance3D:
	var m := SphereMesh.new()
	m.radius = r
	m.height = r if hemi else r * 2.0
	m.is_hemisphere = hemi
	m.radial_segments = 16
	m.rings = 8
	var mi := _add(m, kind, pos, parent)
	mi.scale = scl
	return mi


func _group(pos: Vector3, parent: Node3D = self) -> Node3D:
	var g := Node3D.new()
	g.position = pos
	parent.add_child(g)
	return g


# ---------- world ----------

func _build_environment() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("0c0a08")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("8f98bb")
	env.ambient_light_energy = 0.55
	env.tonemap_mode = Environment.TONE_MAPPER_ACES
	env.tonemap_exposure = 1.15
	env.fog_enabled = true
	env.fog_light_color = Color("2a2018")
	env.fog_density = 0.01
	env.glow_enabled = true
	env.glow_intensity = 0.4
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)

	_sun = DirectionalLight3D.new()
	_sun.light_color = Color("fff0dc")
	_sun.light_energy = 1.6
	_sun.shadow_enabled = true
	_sun.directional_shadow_max_distance = 45.0
	add_child(_sun)
	_sun.basis = Basis.looking_at(SUN_DIR.normalized(), Vector3.UP)


func _build_hall() -> void:
	_box(Vector3(W + 2, 0.2, L + 2), "floor", Vector3(0, -0.1, 0))
	_box(Vector3(2.2, 0.02, 19), "rug", Vector3(0, 0.011, -0.5))
	_box(Vector3(W + 2, 0.3, L + 2), "darkwood", Vector3(0, H + 0.15, 0))
	var z := -11.5
	while z <= 11.5:
		_box(Vector3(W, 0.42, 0.36), "wood", Vector3(0, H - 0.21, z))
		z += 3.3
	_box(Vector3(W + 2, H, WALL_T), "wall", Vector3(0, H / 2, -L / 2 - WALL_T / 2))
	_box(Vector3(W + 2, H, WALL_T), "wall", Vector3(0, H / 2, L / 2 + WALL_T / 2))
	_box(Vector3(2.4, 3.6, 0.2), "darkwood", Vector3(0, 1.8, L / 2 - 0.05))
	for sx in [-1.0, 1.0]:
		_side_wall(sx)
	for px in [-4.0, 4.0]:
		for pz in WINDOWS:
			_cyl(0.42, 0.46, H - 0.8, 18, "stone", Vector3(px, H / 2 - 0.2, pz))
			_box(Vector3(1.15, 0.4, 1.15), "stone", Vector3(px, 0.2, pz))
			_box(Vector3(1.05, 0.4, 1.05), "stone", Vector3(px, H - 0.62, pz))
	# dais and throne
	_box(Vector3(8.4, 0.3, 4.6), "stone", Vector3(0, 0.15, -10.7))
	_box(Vector3(6.2, 0.3, 3.1), "stone", Vector3(0, 0.45, -11.45))
	var throne := _group(Vector3(0, 0.6, -12.1))
	_box(Vector3(1.3, 0.5, 1.0), "wood", Vector3(0, 0.25, 0), throne)
	_box(Vector3(1.4, 2.5, 0.22), "wood", Vector3(0, 1.25, -0.45), throne)
	_box(Vector3(1.05, 0.12, 0.85), "red", Vector3(0, 0.56, 0.02), throne)
	_box(Vector3(0.95, 1.5, 0.06), "red", Vector3(0, 1.35, -0.32), throne)
	for s in [-1.0, 1.0]:
		_box(Vector3(0.16, 0.5, 0.95), "wood", Vector3(s * 0.62, 0.75, 0.02), throne)
		_sph(0.1, "gold", Vector3(s * 0.6, 2.55, -0.45), throne)
	# banners on the back wall
	for b in [[-2.7, "bannerR"], [2.7, "bannerB"]]:
		var q := QuadMesh.new()
		q.size = Vector2(1.5, 3.8)
		var banner := _add(q, b[1], Vector3(b[0], 4.6, -L / 2 + 0.06), self)
		banner.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		var rod := _cyl(0.04, 0.04, 1.8, 8, "gold", Vector3(b[0], 6.55, -L / 2 + 0.12))
		rod.rotation.z = PI / 2
	# long table and benches
	var table := _group(Vector3(-5.7, 0, -1))
	_box(Vector3(1.15, 0.1, 9.5), "wood", Vector3(0, 0.8, 0), table)
	for lz in [-4.3, 0.0, 4.3]:
		for s in [-1.0, 1.0]:
			_box(Vector3(0.1, 0.75, 0.1), "wood", Vector3(s * 0.45, 0.38, lz), table)
	for s in [-1.0, 1.0]:
		_box(Vector3(0.36, 0.08, 9.0), "wood", Vector3(s * 0.9, 0.46, 0), table)
	var tz := -4.0
	while tz <= 4.0:
		_cyl(0.13, 0.11, 0.02, 14, "iron", Vector3(-0.25, 0.86, tz), table)
		_cyl(0.04, 0.03, 0.14, 8, "gold", Vector3(0.25, 0.92, tz + 0.2), table)
		tz += 0.9
	# braziers
	for p in [Vector2(-2.1, -6.5), Vector2(2.1, -6.5), Vector2(-2.1, 2.5), Vector2(2.1, 2.5)]:
		_cyl(0.06, 0.09, 1.0, 8, "iron", Vector3(p.x, 0.5, p.y))
		_cyl(0.5, 0.28, 0.32, 16, "iron", Vector3(p.x, 1.12, p.y))
		_cyl(0.42, 0.42, 0.04, 16, "coal", Vector3(p.x, 1.27, p.y))
		var fg := _group(Vector3(p.x, 1.28, p.y))
		for i in 3:
			var f := _cyl(0.0, 0.22 - i * 0.05, 0.75 - i * 0.12, 8, "fire", Vector3((i - 1) * 0.1, 0.34 - i * 0.03, (i % 2) * 0.08 - 0.04), fg)
			f.set_meta("phase", randf() * 6.0)
			_flames.append(f)
		var light := OmniLight3D.new()
		light.light_color = Color("ffb070")
		light.light_energy = 1.7
		light.omni_range = 13.0
		light.position = Vector3(p.x, 1.9, p.y)
		light.set_meta("phase", randf() * 6.0)
		add_child(light)
		_fires.append(light)


func _side_wall(sx: float) -> void:
	var x := sx * (W / 2 + WALL_T / 2)
	var z0 := -L / 2
	for wz in WINDOWS:
		var a: float = wz - WIN_W / 2
		var b: float = wz + WIN_W / 2
		_box(Vector3(WALL_T, H, a - z0), "wall", Vector3(x, H / 2, (z0 + a) / 2))
		_box(Vector3(WALL_T, SILL, WIN_W), "wall", Vector3(x, SILL / 2, wz))
		_box(Vector3(WALL_T, H - TOP, WIN_W), "wall", Vector3(x, (H + TOP) / 2, wz))
		var q := QuadMesh.new()
		q.size = Vector2(WIN_W, TOP - SILL)
		var glass := _add(q, "glass", Vector3(x + sx * 0.38, (SILL + TOP) / 2, wz), self)
		glass.rotation.y = -PI / 2 if sx > 0 else PI / 2
		_box(Vector3(0.12, TOP - SILL, 0.12), "stone", Vector3(x + sx * 0.3, (SILL + TOP) / 2, wz))
		z0 = b
	_box(Vector3(WALL_T, H, L / 2 - z0), "wall", Vector3(x, H / 2, (z0 + L / 2) / 2))


# ---------- people ----------

func _person(o: Dictionary) -> Dictionary:
	var build: float = o.get("build", 1.0)
	var tunic: String = o["tunic"]
	var legs: String = o.get("legs", "leather")
	var g := _group(Vector3.ZERO)
	var body := _group(Vector3.ZERO, g)
	for s in [-1.0, 1.0]:
		_cyl(0.075 * build, 0.065, 0.62, 10, legs, Vector3(s * 0.11, 0.48, 0), body)
		_cyl(0.08, 0.09, 0.2, 10, "leather", Vector3(s * 0.11, 0.1, 0.02), body)
	_cyl(0.25 * build, 0.32 * build, 0.52, 18, tunic, Vector3(0, 0.8, 0), body)
	_cyl(0.27 * build, 0.25 * build, 0.42, 18, tunic, Vector3(0, 1.27, 0), body)
	_cyl(0.07, 0.24 * build, 0.12, 18, tunic, Vector3(0, 1.54, 0), body)
	_cyl(0.245 * build, 0.245 * build, 0.07, 18, "gold", Vector3(0, 1.06, 0), body)
	var arms := []
	for s in [-1.0, 1.0]:
		var sh := _group(Vector3(s * 0.3 * build, 1.46, 0), body)
		_cyl(0.07, 0.06, 0.34, 10, tunic, Vector3(0, -0.17, 0), sh)
		var el := _group(Vector3(0, -0.33, 0), sh)
		_cyl(0.058, 0.05, 0.28, 10, tunic, Vector3(0, -0.14, 0), el)
		_sph(0.055, "skin", Vector3(0, -0.31, 0.01), el)
		sh.rotation.z = s * 0.12
		el.rotation.x = -0.35
		arms.append({"sh": sh, "el": el})
	_cyl(0.05, 0.056, 0.12, 10, "skin", Vector3(0, 1.6, 0), body)
	var head := _group(Vector3(0, 1.73, 0), body)
	_sph(0.115, "skin", Vector3.ZERO, head, Vector3(1, 1.12, 1.03))
	_box(Vector3(0.03, 0.05, 0.05), "skin", Vector3(0, -0.01, 0.115), head)
	for s in [-1.0, 1.0]:
		_sph(0.014, "eye", Vector3(s * 0.042, 0.02, 0.1), head)
	if o.has("hair"):
		var cap := _sph(0.124, o["hair"], Vector3(0, 0.012, -0.012), head, Vector3(1, 1.12, 1.05), true)
		cap.rotation.x = -0.35
	if o.has("beard"):
		_sph(0.08, o["beard"], Vector3(0, -0.085, 0.055), head, Vector3(1.15, 0.95, 0.8))
	if o.has("helmet"):
		_sph(0.135, o["helmet"], Vector3(0, 0.02, 0), head, Vector3(1, 1.1, 1.05), true)
		_cyl(0.14, 0.14, 0.03, 16, o["helmet"], Vector3(0, -0.005, 0), head)
		_box(Vector3(0.025, 0.11, 0.03), o["helmet"], Vector3(0, -0.04, 0.13), head)
	if o.has("cape"):
		var cape := _box(Vector3(0.62 * build, 1.28, 0.04), o["cape"], Vector3(0, 0.86, -0.3 * build), body)
		cape.rotation.x = 0.08
	if o.has("collar"):
		var t := TorusMesh.new()
		t.inner_radius = 0.15 * build
		t.outer_radius = 0.26 * build
		_add(t, o["collar"], Vector3(0, 1.53, -0.01), body)
	if o.get("spear", false):
		var sp := _group(Vector3(0.36 * build, 0.08, 0.14), body)
		_cyl(0.022, 0.022, 2.3, 8, "wood", Vector3(0, 1.15, 0), sp)
		_cyl(0.0, 0.045, 0.24, 8, "iron", Vector3(0, 2.42, 0), sp)
		arms[1]["sh"].rotation.z = 0.2
		arms[1]["el"].rotation.x = -0.9
	var a := {"g": g, "body": body, "head": head, "arms": arms, "phase": randf() * 6.0}
	_actors.append(a)
	return a


func _build_people() -> void:
	_bryce = _person({"tunic": "blue", "hair": "hairGrey", "beard": "hairGrey", "cape": "red", "collar": "fur", "build": 1.05})
	_bryce["g"].position = Vector3(0.95, 0.6, -10.7)
	_bryce["g"].rotation.y = 0.15
	_howe = _person({"tunic": "green", "hair": "hairDark", "beard": "hairDark", "cape": "leather", "collar": "fur"})
	_howe["g"].position = Vector3(0.15, 0, -7.6)
	_howe["g"].rotation.y = PI + 0.25
	for gd in [[-3.3, -10.2, 0.25], [3.3, -10.2, -0.25]]:
		var guard := _person({"tunic": "tabard", "legs": "mail", "helmet": "iron", "spear": true})
		guard["g"].position = Vector3(gd[0], 0.3, gd[1])
		guard["g"].rotation.y = gd[2]
	# the mabari
	var dog := _group(Vector3(-0.75, 0.6, -10.2))
	dog.rotation.y = 0.35
	var cap := CapsuleMesh.new()
	cap.radius = 0.2
	cap.height = 0.9
	var torso := _add(cap, "dog", Vector3(0, 0.56, 0), dog)
	torso.rotation.x = PI / 2
	_sph(0.23, "dog", Vector3(0, 0.62, 0.22), dog, Vector3(1, 1, 1.1))
	for p in [Vector2(-0.12, 0.25), Vector2(0.12, 0.25), Vector2(-0.12, -0.25), Vector2(0.12, -0.25)]:
		_cyl(0.055, 0.045, 0.45, 8, "dog", Vector3(p.x, 0.23, p.y), dog)
	_dog_head = _group(Vector3(0, 0.84, 0.44), dog)
	_sph(0.15, "dog", Vector3.ZERO, _dog_head, Vector3(1.05, 0.95, 1))
	_box(Vector3(0.15, 0.11, 0.18), "dogDark", Vector3(0, -0.04, 0.15), _dog_head)
	for s in [-1.0, 1.0]:
		var ear := _cyl(0.0, 0.05, 0.1, 6, "dogDark", Vector3(s * 0.08, 0.13, -0.02), _dog_head)
		ear.rotation.z = -s * 0.3
		_sph(0.016, "eye", Vector3(s * 0.06, 0.04, 0.12), _dog_head)
	_dog_tail = _group(Vector3(0, 0.68, -0.42), dog)
	var tail := _cyl(0.025, 0.035, 0.28, 6, "dog", Vector3(0, 0.12, -0.04), _dog_tail)
	tail.rotation.x = -0.6


# ---------- camera, ink pass, HUD ----------

func _build_camera() -> void:
	_camera = Camera3D.new()
	_camera.fov = 45.0
	_camera.near = 0.1
	_camera.far = 80.0
	add_child(_camera)
	_camera.make_current()
	_ink_quad = MeshInstance3D.new()
	var q := QuadMesh.new()
	q.size = Vector2(2, 2)
	_ink_quad.mesh = q
	var m := ShaderMaterial.new()
	m.shader = INK
	_ink_quad.material_override = m
	_ink_quad.extra_cull_margin = 16384.0
	_ink_quad.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_camera.add_child(_ink_quad)
	_place_camera()


func _place_camera() -> void:
	var off := Vector3(sin(_yaw) * cos(_pitch), sin(_pitch), cos(_yaw) * cos(_pitch)) * _dist
	var p := _target + off
	p.x = clampf(p.x, -6.3, 6.3)
	p.z = clampf(p.z, -12.4, 12.4)
	p.y = clampf(p.y, 0.4, 7.4)
	_camera.position = p
	_camera.look_at(_target, Vector3.UP)


func _build_hud() -> void:
	_hud_layer = CanvasLayer.new()
	add_child(_hud_layer)
	var title := Label.new()
	title.text = "DAODream · Castle Cousland\nGreat Hall style test (Godot)"
	title.position = Vector2(20, 16)
	title.add_theme_font_size_override("font_size", 22)
	_hud_layer.add_child(title)
	_mode_label = Label.new()
	_mode_label.position = Vector2(20, 84)
	_mode_label.add_theme_font_size_override("font_size", 18)
	_mode_label.add_theme_color_override("font_color", Color("d1a94e"))
	_hud_layer.add_child(_mode_label)
	_stats = Label.new()
	_stats.position = Vector2(20, 116)
	_stats.add_theme_font_size_override("font_size", 16)
	_hud_layer.add_child(_stats)
	var help := Label.new()
	help.text = "Drag: look around   Wheel: zoom   1 Plain   2 Ink & cel   3 Cel, no ink   B bands   L low-spec   V vsync   H hide text   F12 screenshot"
	help.anchor_top = 1.0
	help.anchor_bottom = 1.0
	help.offset_top = -40
	help.offset_left = 20
	help.add_theme_font_size_override("font_size", 15)
	help.add_theme_color_override("font_color", Color("b8a985"))
	_hud_layer.add_child(help)
	for lbl in [title, _mode_label, _stats, help]:
		lbl.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.85))
		lbl.add_theme_constant_override("outline_size", 6)


func _apply_mode(i: int) -> void:
	_mode = i
	var bands: int = MODES[i]["bands"]
	if bands > 0:
		bands = _bands
	for m in _mats.values():
		m.set_shader_parameter("bands", bands)
	_ink_quad.visible = MODES[i]["ink"]
	_update_mode_label()


func _update_mode_label() -> void:
	var t: String = MODES[_mode]["name"]
	if MODES[_mode]["bands"] > 0:
		t += "  ·  %d light bands" % _bands
	if _low_spec:
		t += "  ·  low-spec (60%% render scale, no shadows, no MSAA)"
	_mode_label.text = t


func _set_low_spec(on: bool) -> void:
	_low_spec = on
	var vp := get_viewport()
	vp.scaling_3d_scale = 0.6 if on else 1.0
	vp.msaa_3d = Viewport.MSAA_DISABLED if on else Viewport.MSAA_2X
	_sun.shadow_enabled = not on
	_update_mode_label()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			_dragging = event.pressed
			_last_input = _time
			_sway_on = false
		elif event.button_index == MOUSE_BUTTON_WHEEL_UP and event.pressed:
			_dist = clampf(_dist - 0.5, 2.5, 11.0)
			_last_input = _time
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN and event.pressed:
			_dist = clampf(_dist + 0.5, 2.5, 11.0)
			_last_input = _time
	elif event is InputEventMouseMotion and _dragging:
		_yaw -= event.relative.x * 0.005
		_pitch = clampf(_pitch + event.relative.y * 0.004, -0.2, 1.0)
		_last_input = _time
	elif event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_1: _apply_mode(0)
			KEY_2: _apply_mode(1)
			KEY_3: _apply_mode(2)
			KEY_B:
				_bands = 2 + (_bands - 1) % 3
				_apply_mode(_mode)
			KEY_L: _set_low_spec(not _low_spec)
			KEY_V:
				var on := DisplayServer.window_get_vsync_mode() != DisplayServer.VSYNC_DISABLED
				DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED if on else DisplayServer.VSYNC_ENABLED)
			KEY_H:
				_hud_visible = not _hud_visible
				_hud_layer.visible = _hud_visible
			KEY_F12: _save_screenshot("user://hall-%d.png" % Time.get_unix_time_from_system())
			KEY_ESCAPE: get_tree().quit()


func _process(delta: float) -> void:
	_time += delta
	if not _frozen and _time - _last_input > 3.0 and not _dragging:
		if not _sway_on:
			_sway_on = true
			_sway_start = _time
			_sway_base = _yaw
		_yaw = _sway_base + sin((_time - _sway_start) * 0.16) * 0.55
	_place_camera()

	for f in _flames:
		var p: float = f.get_meta("phase")
		f.scale = Vector3(1, 0.85 + 0.25 * sin(_time * 9.0 + p) * sin(_time * 5.3 + p * 2.0), 1)
		f.rotation.y = _time * 0.8 + p
	for l in _fires:
		var p: float = l.get_meta("phase")
		l.light_energy = 1.7 * (0.88 + 0.12 * sin(_time * 11.0 + p) * sin(_time * 7.1 + p))
	for a in _actors:
		a["body"].scale.y = 1.0 + 0.008 * sin(_time * 1.6 + a["phase"])
		a["head"].rotation.y = 0.18 * sin(_time * 0.35 + a["phase"])
	_howe["arms"][0]["sh"].rotation.x = -0.35 - 0.25 * (0.5 + 0.5 * sin(_time * 0.9))
	_howe["arms"][0]["el"].rotation.x = -0.9
	_bryce["arms"][1]["el"].rotation.x = -0.6
	_dog_tail.rotation.y = sin(_time * 7.0) * 0.5
	_dog_head.rotation.x = 0.05 * sin(_time * 1.3)

	_stats.text = "%d fps   %d draw calls   %dk triangles\n%s   RAM %d MB   VRAM %d MB" % [
		Engine.get_frames_per_second(),
		Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),
		int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME) / 1000.0),
		RenderingServer.get_current_rendering_method(),
		int(OS.get_static_memory_usage() / 1048576.0),
		int(Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED) / 1048576.0),
	]


# ---------- screenshots ----------

func _user_arg(key: String) -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--%s=" % key):
			return a.split("=", true, 1)[1]
	return ""


func _save_screenshot(path: String) -> void:
	var img := get_viewport().get_texture().get_image()
	img.save_png(path)
	print("Saved ", ProjectSettings.globalize_path(path))


# Run with: godot --path . -- --shots=<folder>  to save one image per mode and quit.
func _take_shots(folder: String) -> void:
	DirAccess.make_dir_recursive_absolute(folder)
	_frozen = true
	for i in 120:
		await get_tree().process_frame
	for i in MODES.size():
		_apply_mode(i)
		for f in 20:
			await get_tree().process_frame
		_save_screenshot(folder.path_join("mode%d.png" % (i + 1)))
	_apply_mode(1)
	_set_low_spec(true)
	for f in 20:
		await get_tree().process_frame
	_save_screenshot(folder.path_join("mode2-lowspec.png"))
	print("STATS ", _stats.text.replace("\n", " | "))
	get_tree().quit()
