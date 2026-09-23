"""Generate the CSS for the hero's crystals.

Each crystal is a convex polyhedron (icosahedra floating, a dodecahedron inside
the glass) built from flat HTML faces: every face is
an element whose clip-path is the face polygon and whose transform is
    translate3d(<corner, in em>) matrix3d(<pure rotation>)
so the whole solid scales with the container's font-size (set in container
units by styles.css). Lighting is baked per face from the reference palette,
evaluated at the crystal's resting orientation.

    python tools/polyhedra.py > crystals.css

No dependencies beyond the standard library.
"""

import itertools
import math

PHI = (1 + 5 ** 0.5) / 2


# ---------------------------------------------------------------- vectors

def sub(a, b): return [a[i] - b[i] for i in range(3)]
def add(a, b): return [a[i] + b[i] for i in range(3)]
def mul(a, k): return [x * k for x in a]
def dot(a, b): return sum(a[i] * b[i] for i in range(3))
def cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def norm(a): return math.sqrt(dot(a, a))
def unit(a): return mul(a, 1 / norm(a))


def matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def apply(M, v):
    return [sum(M[i][k] * v[k] for k in range(3)) for i in range(3)]


# CSS rotation matrices (x right, y down, z toward the viewer)
def Rx(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d))
    return [[1, 0, 0], [0, c, -s], [0, s, c]]


def Ry(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d))
    return [[c, 0, s], [0, 1, 0], [-s, 0, c]]


def Rz(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d))
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def css_rotation(rz, rx, ry):
    """Same composition as `transform: rotateZ() rotateX() rotateY()`."""
    return matmul(matmul(Rz(rz), Rx(rx)), Ry(ry))


# ---------------------------------------------------------------- solids

def icosahedron():
    v = []
    for a, b in itertools.product((-1, 1), repeat=2):
        v += [[0, a, b * PHI], [a, b * PHI, 0], [b * PHI, 0, a]]
    edge = 2.0
    faces = [f for f in itertools.combinations(range(12), 3)
             if all(abs(norm(sub(v[i], v[j])) - edge) < 1e-6 for i, j in itertools.combinations(f, 2))]
    return v, [list(f) for f in faces]


def dodecahedron():
    """12 regular pentagons; face normals are the cyclic permutations of (0, +-phi, +-1)."""
    v = [[x, y, z] for x, y, z in itertools.product((-1, 1), repeat=3)]
    for a, c in itertools.product((-1, 1), repeat=2):
        v += [[0, a / PHI, c * PHI], [a / PHI, c * PHI, 0], [c * PHI, 0, a / PHI]]
    faces = []
    for a, c in itertools.product((-1, 1), repeat=2):
        for n in ([0, a * PHI, c], [a * PHI, c, 0], [c, 0, a * PHI]):
            n = unit(n)
            d = [dot(p, n) for p in v]
            top = max(d)
            idx = [i for i, x in enumerate(d) if x > top - 1e-6]
            cen = mul([sum(v[i][k] for i in idx) for k in range(3)], 1 / len(idx))
            u = unit(sub(v[idx[0]], cen)); w = cross(n, u)
            idx.sort(key=lambda i: math.atan2(dot(sub(v[i], cen), w), dot(sub(v[i], cen), u)))
            faces.append(idx)
    return v, faces


def align(a, b):
    """Rotation matrix taking unit vector a onto unit vector b (Rodrigues)."""
    vx = cross(a, b); c = dot(a, b)
    K = [[0, -vx[2], vx[1]], [vx[2], 0, -vx[0]], [-vx[1], vx[0], 0]]
    K2 = matmul(K, K)
    return [[(1 if i == j else 0) + K[i][j] + K2[i][j] / (1 + c) for j in range(3)] for i in range(3)]


def css_matrix3d(R):
    """CSS matrix3d() for rotation R (column-major)."""
    return 'matrix3d(%s)' % ','.join('%.5f' % x for x in
                                     [R[0][0], R[1][0], R[2][0], 0, R[0][1], R[1][1], R[2][1], 0,
                                      R[0][2], R[1][2], R[2][2], 0, 0, 0, 0, 1])


def geodesic(freq=2):
    """Icosahedron with each face split into freq^2 triangles, pushed to the sphere."""
    v, faces = icosahedron()
    v = [unit(p) for p in v]
    out_v, out_f, cache = [], [], {}

    def vid(p):
        key = tuple(round(x, 6) for x in p)
        if key not in cache:
            cache[key] = len(out_v)
            out_v.append(p)
        return cache[key]

    for a, b, c in faces:
        A, B, C = v[a], v[b], v[c]
        grid = {}
        for i in range(freq + 1):
            for j in range(freq + 1 - i):
                k = freq - i - j
                p = unit(add(add(mul(A, i / freq), mul(B, j / freq)), mul(C, k / freq)))
                grid[(i, j)] = vid(p)
        for i in range(freq):
            for j in range(freq - i):
                out_f.append([grid[(i, j)], grid[(i + 1, j)], grid[(i, j + 1)]])
                if j + i + 1 < freq:
                    out_f.append([grid[(i + 1, j)], grid[(i + 1, j + 1)], grid[(i, j + 1)]])
    return out_v, out_f


# ---------------------------------------------------------------- shading

def hex2rgb(h):
    h = h.lstrip('#')
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def rgb2hex(c):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(x))) for x in c)


def shade(world_n, probes, ambient, sharp=4.0):
    """Blend probe colours by how directly the face points at each probe."""
    total, acc = 0.18, mul(hex2rgb(ambient), 0.18)
    for d, colour, k in probes:
        w = max(0.0, dot(world_n, unit(d))) ** sharp * k
        acc = add(acc, mul(hex2rgb(colour), w))
        total += w
    return mul(acc, 1 / total)


def lighten(c, k):
    return [x + (255 - x) * k for x in c]


def darken(c, k):
    return [x * (1 - k) for x in c]


# ---------------------------------------------------------------- CSS output

def emit(selector, verts, faces, radius_em, rest, probes, ambient, extra=None):
    """Faces scaled so the circumradius is `radius_em`; shading at rotation `rest`."""
    r = max(norm(p) for p in verts)
    V = [mul(p, radius_em / r) for p in verts]
    R = rest if isinstance(rest[0], list) else css_rotation(*rest)
    lines = []
    for i, f in enumerate(faces, 1):
        P = [V[k] for k in f]
        centre = mul([sum(p[j] for p in P) for j in range(3)], 1 / len(P))
        n = unit(cross(sub(P[1], P[0]), sub(P[2], P[0])))
        if dot(n, centre) < 0:                     # make the winding face outward
            P = P[::-1]
            n = mul(n, -1)
        ex = unit(sub(P[1], P[0]))
        ey = cross(n, ex)                           # ex x ey = n  (right-handed)
        loc = [(dot(sub(p, P[0]), ex), dot(sub(p, P[0]), ey)) for p in P]
        minx, maxx = min(x for x, _ in loc), max(x for x, _ in loc)
        miny, maxy = min(y for _, y in loc), max(y for _, y in loc)
        w, h = maxx - minx, maxy - miny
        corner = add(add(P[0], mul(ex, minx)), mul(ey, miny))
        poly = ', '.join('%.2f%% %.2f%%' % ((x - minx) / w * 100, (y - miny) / h * 100) for x, y in loc)
        m = [ex[0], ex[1], ex[2], 0, ey[0], ey[1], ey[2], 0, n[0], n[1], n[2], 0, 0, 0, 0, 1]

        base = shade(apply(R, n), probes, ambient)
        if extra:
            base = extra(f, len(f), apply(R, n), base)
        top, bottom = rgb2hex(lighten(base, .10)), rgb2hex(darken(base, .24))
        lines.append(
            '%s > i:nth-child(%d){width:%.4fem;height:%.4fem;clip-path:polygon(%s);'
            'transform:translate3d(%.4fem,%.4fem,%.4fem) matrix3d(%s);'
            'background:linear-gradient(160deg,%s,%s)}'
            % (selector, i, w, h, poly, corner[0], corner[1], corner[2],
               ','.join('%.5f' % x for x in m), top, bottom))
    return '\n'.join(lines), len(faces)


# Rest orientations match the CSS in styles.css, so the baked light is right.
BIG_REST = (-14, -18, 24)
SMALL_REST = (10, -22, -30)
def crystal_pose():
    """World pose of the dodecahedron inside the glass, chosen against the reference:
    one pentagon turned toward the viewer with a flat edge at the bottom, then
    rotateZ(10) rotateX(-8) rotateY(184) so the left and lower faces catch magenta."""
    v, faces = dodecahedron()
    f0 = faces[0]
    n0 = unit(mul([sum(v[i][k] for i in f0) for k in range(3)], 1 / 5))
    A = align(n0, [0, 0, 1])
    pts = [apply(A, v[i]) for i in f0]
    low = max(range(5), key=lambda k: (pts[k][1] + pts[(k + 1) % 5][1]))
    p, q = pts[low], pts[(low + 1) % 5]
    spin = -math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))
    return matmul(matmul(matmul(Rz(10), Rx(-8)), Ry(184)), matmul(Rz(spin), A))


CRYSTAL_REST = crystal_pose()

MAGENTA = [((-0.2, -0.3, 1), '#f101ef', 1.0), ((0.8, -0.6, 0.3), '#8a0de8', 1.1),
           ((-0.7, 0.6, 0.4), '#ff5cf4', 1.0), ((0, -1, 0), '#ff4bf0', 0.7),
           ((0.6, 0.7, 0.2), '#4a06b0', 0.9)]
VIOLET = [((0, -0.2, 1), '#a400ff', 1.2), ((-0.9, 0.2, 0.3), '#2f1cff', 1.4),
          ((0.8, 0.3, 0.4), '#ff10f0', 1.6), ((0.1, -0.9, 0.3), '#d23cff', 0.9),
          ((0.2, 1, 0.1), '#5a06c8', 0.8)]
INDIGO = [((0.1, -0.1, 1), '#050878', 2.6), ((0.9, -0.5, 0.6), '#0b0f8e', 1.2),
          ((0, -1, 0.3), '#0a0c6c', 1.0), ((-1, 0.1, 0.2), '#ff10f0', 2.2),
          ((0, 1, 0.2), '#f414e6', 1.8), ((-0.3, 1, 0.4), '#ff2a8a', 0.8),
          ((1, 0.3, 0.2), '#2a16c4', 0.8)]
AQUA = [((0.1, -0.1, 1), '#0b3f7c', 1.8), ((-1, 0.1, 0.3), '#3fd4ff', 1.3),
        ((0, 1, 0.3), '#7a5cf0', 1.1), ((1, 0, 0.3), '#2b36ff', 1.0), ((0, -1, 0.3), '#8ff0ff', 0.8)]


if __name__ == '__main__':
    out = ['/* generated by tools/polyhedra.py — do not edit by hand */']

    v, f = icosahedron()
    css, n = emit('.gem-big .poly', v, f, 0.5, BIG_REST, MAGENTA, '#3d0a8a')
    out += ['/* floating icosahedron, %d faces */' % n, css]

    css, n = emit('.gem-small .poly', v, f, 0.5, SMALL_REST, VIOLET, '#2a0a7a')
    out += ['/* small floating icosahedron, %d faces */' % n, css]

    v, f = dodecahedron()
    out += [':root { --crystal-pose: %s; }' % css_matrix3d(CRYSTAL_REST)]
    css, n = emit('.crystal-indigo .poly', v, f, 0.5, CRYSTAL_REST, INDIGO, '#06084a')
    out += ['/* dodecahedral crystal inside the glass, %d faces */' % n, css]
    css, _ = emit('.crystal-aqua .poly', v, f, 0.5, CRYSTAL_REST, AQUA, '#07243f')
    out += [css]

    print('\n'.join(out))
