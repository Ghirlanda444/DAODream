struct FCastle
{
    float H(float2 p) { return frac(sin(dot(p, float2(127.1, 311.7))) * 43758.5453); }
    float N(float2 p)
    {
        float2 i = floor(p);
        float2 u = frac(p);
        u = u * u * (3.0 - 2.0 * u);
        return lerp(lerp(H(i), H(i + float2(1, 0)), u.x), lerp(H(i + float2(0, 1)), H(i + float2(1, 1)), u.x), u.y);
    }
    float F(float2 p)
    {
        float v = 0.0;
        float a = 0.5;
        for (int k = 0; k < 4; k++) { v += a * N(p); p *= 2.03; a *= 0.5; }
        return v;
    }
    // mode 0: ashlar (running bond), 1: flagstones (random offsets), 2: planks (long, staggered)
    float4 Pat(float2 uv, float mode, float2 size, float mortar, float3 ca, float3 cb, float3 cm, out float ao)
    {
        float2 q = uv / size;
        float row = floor(q.y);
        if (mode < 0.5) q.x += 0.5 * fmod(abs(row), 2.0);
        else q.x += 0.37 * H(float2(row, 7.0));
        float2 cell = floor(q);
        float2 f = frac(q);
        float2 d = min(f, 1.0 - f) * size;
        float edge = min(d.x, d.y);
        // chipped edges: the joint wanders a little
        edge += (N(uv * 0.15 + cell * 3.1) - 0.5) * mortar * 0.8;
        float m = 1.0 - smoothstep(mortar * 0.35, mortar, edge);
        float t = H(cell + 0.5);
        float detail = F(uv * 0.05 + t * 13.0);
        float3 c;
        float r;
        if (mode > 1.5)
        {
            float g = F(float2(uv.x * 0.015, uv.y * 0.45) + t * 9.0);
            float rings = 0.5 + 0.5 * sin(g * 18.0);
            c = lerp(ca, cb, saturate(g * 0.9 + rings * 0.25 + t * 0.3 - 0.25));
            r = lerp(0.55 + 0.2 * detail, 0.9, m);
        }
        else
        {
            c = lerp(ca, cb, saturate(t * 0.7 + detail * 0.5 - 0.1));
            c *= 0.88 + 0.24 * F(uv * 0.35);
            // a few darker, weathered stones
            c *= lerp(1.0, 0.8, step(0.85, H(cell + 3.7)));
            r = lerp(0.7 + 0.25 * detail, 0.95, m);
        }
        c = lerp(c, cm, m);
        ao = 1.0 - 0.6 * m;
        return float4(c, r);
    }
};
FCastle S;
float3 w = pow(abs(Nrm), 6.0);
w /= (w.x + w.y + w.z);
float a1;
float a2;
float a3;
float4 px = S.Pat(WP.yz, Mode, Size.xy, Mortar, CA, CB, CM, a1);
float4 py = S.Pat(WP.xz, Mode, Size.xy, Mortar, CA, CB, CM, a2);
float4 pz = S.Pat(WP.xy, Mode, Size.xy, Mortar, CA, CB, CM, a3);
AO = a1 * w.x + a2 * w.y + a3 * w.z;
return px * w.x + py * w.y + pz * w.z;
