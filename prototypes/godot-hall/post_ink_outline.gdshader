// PROTOTYPE - NOT FOR PRODUCTION (prototypes/godot-hall). Targets Forward+, Mobile and Compatibility.
// Ink contours as a full-screen pass: a quad drawn over the view reads the
// depth buffer and darkens pixels where depth jumps (silhouettes) or bends
// (creases between walls, floor and steps). Works on Forward+, Mobile and
// Compatibility; only depth is used, so it needs no normal buffer.
shader_type spatial;
render_mode unshaded, depth_draw_never, depth_test_disabled, cull_disabled, fog_disabled, shadows_disabled;

uniform sampler2D screen_tex : hint_screen_texture, filter_linear, repeat_disable;
uniform sampler2D depth_tex : hint_depth_texture, filter_nearest, repeat_disable;
uniform float thickness = 1.5;
uniform vec4 ink_color : source_color = vec4(0.07, 0.055, 0.05, 1.0);
uniform float saturation = 1.1;
uniform float vignette = 0.18;

void vertex() {
	POSITION = vec4(VERTEX.xy, 1.0, 1.0);
}

float lin_depth(vec2 uv, mat4 inv_proj) {
	float d = texture(depth_tex, uv).x;
#if CURRENT_RENDERER == RENDERER_COMPATIBILITY
	vec3 ndc = vec3(uv, d) * 2.0 - 1.0;
#else
	vec3 ndc = vec3(uv * 2.0 - 1.0, d);
#endif
	vec4 v = inv_proj * vec4(ndc, 1.0);
	return -v.z / v.w;
}

void fragment() {
	vec2 o = thickness * max(1.0, VIEWPORT_SIZE.y / 900.0) / VIEWPORT_SIZE;
	float c = lin_depth(SCREEN_UV, INV_PROJECTION_MATRIX);
	float l = lin_depth(SCREEN_UV - vec2(o.x, 0.0), INV_PROJECTION_MATRIX);
	float r = lin_depth(SCREEN_UV + vec2(o.x, 0.0), INV_PROJECTION_MATRIX);
	float u = lin_depth(SCREEN_UV + vec2(0.0, o.y), INV_PROJECTION_MATRIX);
	float d = lin_depth(SCREEN_UV - vec2(0.0, o.y), INV_PROJECTION_MATRIX);
	float sil = max(max(abs(l - c), abs(r - c)), max(abs(u - c), abs(d - c))) / c;
	// Inverse depth is linear across a flat surface on screen, so its second
	// difference is zero on planes and spikes only where the surface bends.
	float ic = 1.0 / c;
	float lap = (abs(1.0 / l + 1.0 / r - 2.0 * ic) + abs(1.0 / u + 1.0 / d - 2.0 * ic)) / ic;
	float edge = max(smoothstep(0.035, 0.07, sil), smoothstep(0.004, 0.012, lap));

	vec3 col = texture(screen_tex, SCREEN_UV).rgb;
	float lum = dot(col, vec3(0.299, 0.587, 0.114));
	col = mix(vec3(lum), col, saturation);
	col = mix(col, ink_color.rgb, edge);
	float vig = smoothstep(1.2, 0.35, length((SCREEN_UV - 0.5) * vec2(1.25, 1.0)));
	col *= mix(1.0 - vignette, 1.0, vig);
	ALBEDO = col;
}
