// PROTOTYPE - NOT FOR PRODUCTION (prototypes/godot-hall). Targets Forward+, Mobile and Compatibility.
// Cel shading for the hall: light is cut into flat bands, surfaces take their
// pattern from world position (no UVs needed on the box-built castle), and a
// baked-looking darkening near the floor stands in for ambient occlusion.
// bands = 0 gives smooth, unstylised lighting for the "Plain" comparison.
shader_type spatial;

uniform vec4 albedo : source_color = vec4(1.0);
uniform sampler2D albedo_tex : source_color, filter_linear_mipmap_anisotropic, repeat_enable, hint_default_white;
uniform bool use_tex = false;
uniform bool triplanar = false;
uniform float tile = 2.0;
uniform vec2 tex_offset = vec2(0.0);
uniform int bands = 3;
uniform float band_bias = 0.35;
uniform float ao_floor = 0.62;
uniform vec4 emission_color : source_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform float emission_energy = 0.0;

varying vec3 world_pos;
varying vec3 world_nrm;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	world_nrm = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

vec3 triplanar_sample(vec3 p, vec3 n) {
	vec3 w = pow(abs(n), vec3(4.0));
	w /= (w.x + w.y + w.z);
	vec3 x = texture(albedo_tex, p.zy / tile + tex_offset).rgb;
	vec3 y = texture(albedo_tex, p.xz / tile + tex_offset).rgb;
	vec3 z = texture(albedo_tex, p.xy / tile + tex_offset).rgb;
	return x * w.x + y * w.y + z * w.z;
}

void fragment() {
	vec3 c = albedo.rgb;
	if (use_tex) {
		c *= triplanar ? triplanar_sample(world_pos, normalize(world_nrm)) : texture(albedo_tex, UV).rgb;
	}
	float k = mix(ao_floor, 1.0, smoothstep(0.0, 1.6, world_pos.y));
	k *= 1.0 - 0.3 * smoothstep(5.5, 8.0, world_pos.y);
	ALBEDO = c * k;
	ROUGHNESS = 1.0;
	SPECULAR = 0.0;
	EMISSION = emission_color.rgb * emission_energy;
}

void light() {
	float lit = clamp(dot(NORMAL, LIGHT), 0.0, 1.0) * ATTENUATION;
	if (bands > 0) {
		float b = float(bands);
		lit = clamp(floor(lit * b + band_bias) / b, 0.0, 1.0);
	}
	DIFFUSE_LIGHT += LIGHT_COLOR / PI * lit;
}
