__author__ = 'Ryan Sheffer'
__credits__ = ["Id Software"]

import re
import math

'''
===========================================================================
Copyright (C) 1997-2006 Id Software, Inc.

Some of this file is part of Quake 2 Tools source code.

Quake 2 Tools source code is free software; you can redistribute it
and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the License,
or (at your option) any later version.

Quake 2 Tools source code is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Quake 2 Tools source code; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
===========================================================================
'''

class IdMath:
    EQUAL_EPSILON = 0.001
    vec3_zero = [0.0, 0.0, 0.0]
    Q_PI = 3.14159265358979323846

    @staticmethod
    def VectorMA(va, scale, vb, vc):
        vc[0] = va[0] + scale * vb[0]
        vc[1] = va[1] + scale * vb[1]
        vc[2] = va[2] + scale * vb[2]

    @staticmethod
    def DotProduct(x, y):
        return (x[0] * y[0] + x[1] * y[1] + x[2] * y[2])

    @staticmethod
    def CrossProduct(v1, v2, cross):
        cross[0] = v1[1] * v2[2] - v1[2] * v2[1]
        cross[1] = v1[2] * v2[0] - v1[0] * v2[2]
        cross[2] = v1[0] * v2[1] - v1[1] * v2[0]

    @staticmethod
    def VectorCompare (v1, v2):
        for i in range(0, 3):
            if math.fabs(v1[i] - v2[i]) > EQUAL_EPSILON:
                return False

        return True

    @staticmethod
    def VectorNormalize(v):
        length = 0.0
        for i in range(0, 3):
            length += v[i] * v[i]
        length = math.sqrt(length)
        if length == 0:
            return 0.0

        for i in range(0, 3):
            v[i] /= length

        return length

    @staticmethod
    def VectorScale(v, scale, out):
        out[0] = v[0] * scale
        out[1] = v[1] * scale
        out[2] = v[2] * scale

    @staticmethod
    def VectorSubtract(a, b, c):
        c[0] = a[0] - b[0]
        c[1] = a[1] - b[1]
        c[2] = a[2] - b[2]

    @staticmethod
    def VectorAdd(a, b, c):
        c[0] = a[0] + b[0]
        c[1] = a[1] + b[1]
        c[2] = a[2] + b[2]

    @staticmethod
    def VectorCopy(a, b):
        b[0] = a[0]
        b[1] = a[1]
        b[2] = a[2]

    MAX_POINTS_ON_WINDING = 64
    ON_EPSILON = 0.01
    SIDE_FRONT = 0
    SIDE_ON = 2
    SIDE_BACK = 1
    SIDE_CROSS = -2

    @staticmethod
    def ClipWinding(input, split, keepon):
        dists = [0 for x in range(IdMath.MAX_POINTS_ON_WINDING)]
        sides = [0 for x in range(IdMath.MAX_POINTS_ON_WINDING)]
        counts = [0, 0, 0]

        # determine sides for each point
        for i in range(0, input.numpoints):
            dot = IdMath.DotProduct(input.points[i], split.normal)
            dot -= split.dist
            dists[i] = dot
            if dot > IdMath.ON_EPSILON:
                sides[i] = IdMath.SIDE_FRONT
            elif dot < -IdMath.ON_EPSILON:
                sides[i] = IdMath.SIDE_BACK
            else:
                sides[i] = IdMath.SIDE_ON

            counts[sides[i]] += 1

        sides[i] = sides[0];
        dists[i] = dists[0];

        if keepon and counts[0] == 0 and counts[1] == 0:
            return input

        if counts[0] == 0:
            return None

        if counts[1] == 0:
            return input

        maxpts = input.numpoints + 4;	# can't use counts[0] + 2 because of fp grouping errors
        neww = Id2Map.Winding()
        neww.maxpoints = maxpts

        for i in range(0, input.numpoints):
            p1 = input.points[i]

            if sides[i] == IdMath.SIDE_ON:
                IdMath.VectorCopy(p1, neww.points[neww.numpoints])
                neww.numpoints += 1
                continue

            if sides[i] == IdMath.SIDE_FRONT:
                IdMath.VectorCopy(p1, neww.points[neww.numpoints])
                neww.numpoints += 1

            if sides[i + 1] == IdMath.SIDE_ON or sides[i + 1] == sides[i]:
                continue

            # generate a split point
            p2 = input.points[(i + 1) % input.numpoints];

            dot = dists[i] / (dists[i] - dists[i + 1]);
            for j in range(0, 3):
                # avoid round off error when possible
                if split.normal[j] == 1:
                    mid[j] = split.dist
                elif split.normal[j] == -1:
                    mid[j] = -split.dist
                else:
                    mid[j] = p1[j] + dot * (p2[j] - p1[j])

            IdMath.VectorCopy(mid, neww.points[neww.numpoints])
            neww.numpoints += 1

        if neww.numpoints > maxpts:
            raise Exception('ClipWinding: points exceeded estimate')

        return neww

    baseaxis = [[0,0,1], [1,0,0], [0,-1,0],			# floor
                [0,0,-1], [1,0,0], [0,-1,0],		# ceiling
                [1,0,0], [0,1,0], [0,0,-1],			# west wall
                [-1,0,0], [0,1,0], [0,0,-1],		# east wall
                [0,1,0], [1,0,0], [0,0,-1],			# south wall
                [0,-1,0], [1,0,0], [0,0,-1]]		# north wall

    @staticmethod
    def TextureAxisFromPlane(pln, xv, yv):
        best = 0;
        bestaxis = 0;

        for i in range(0, 6):
            dot = IdMath.DotProduct(pln.normal, baseaxis[i * 3]);
            if dot > best:
                best = dot
                bestaxis = i

        IdMath.VectorCopy(baseaxis[bestaxis * 3 + 1], xv);
        IdMath.VectorCopy(baseaxis[bestaxis * 3 + 2], yv);

    @staticmethod
    def BeginTexturingFace(b, f):
        out_vecs = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        pvecs = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]

        # get natural texture axis
        IdMath.TextureAxisFromPlane(f.plane, pvecs[0], pvecs[1])

        # set shading for face
        # This is an editor thing to give depth to the scene, should just get rid of it
        shade = 0.0 #SetShadeForPlane(f.plane)
        f.color[0] = f.color[1] = f.color[2] = shade

        if f.texdef.scale[0] == 0.0:
            f.texdef.scale[0] = 1.0
        if f.texdef.scale[1] == 0.0:
            f.texdef.scale[1] = 1.0

        # rotate axis
        if f.texdef.rotate == 0:
            sinv = 0
            cosv = 1
        elif f.texdef.rotate == 90:
            sinv = 1
            cosv = 0
        elif f.texdef.rotate == 180:
            sinv = 0
            cosv = -1
        elif f.texdef.rotate == 270:
            sinv = -1
            cosv = 0
        else:
            ang = f.texdef.rotate / 180.0 * IdMath.Q_PI
            sinv = sin(ang)
            cosv = cos(ang)

        if pvecs[0][0]:
            sv = 0
        elif pvecs[0][1]:
            sv = 1
        else:
            sv = 2

        if pvecs[1][0]:
            tv = 0
        elif pvecs[1][1]:
            tv = 1
        else:
            tv = 2

        for i in range(0, 2):
            ns = cosv * pvecs[i][sv] - sinv * pvecs[i][tv]
            nt = sinv * pvecs[i][sv] +  cosv * pvecs[i][tv]
            out_vecs[i][sv] = ns
            out_vecs[i][tv] = nt

        for i in range(0, 2):
            for j in range(0, 3):
                out_vecs[i][j] = out_vecs[i][j] / f.texdef.scale[i];

        return out_vecs

    @staticmethod
    def EmitTextureCoordinates(xyzst, f):
        #float	s, t, ns, nt;
        #float	ang, sinv, cosv;
        #vec3_t	vecs[2];
        #texdef_t	*td;
        vecs = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]

        # get natural texture axis
        IdMath.TextureAxisFromPlane(f.plane, vecs[0], vecs[1])

        td = f.texdef

        ang = td.rotate / 180.0 * IdMath.Q_PI
        sinv = math.sin(ang)
        cosv = math.cos(ang)

        if td.scale[0] == 0:
            td.scale[0] = 1
        if td.scale[1] == 0:
            td.scale[1] = 1

        s = IdMath.DotProduct(xyzst, vecs[0])
        t = IdMath.DotProduct(xyzst, vecs[1])

        ns = cosv * s - sinv * t
        nt = sinv * s +  cosv * t

        s = ns / td.scale[0] + td.shift[0]
        t = nt / td.scale[1] + td.shift[1]

        # gl scales everything from 0 to 1
        s /= 256.0 #q->width (TODO)
        t /= 256.0 #q->height (TODO)

        xyzst[3] = s
        xyzst[4] = t

class Id2Map:
    """
    This class was created from Id software source code porting,
    specifically from the brush.c file located in the QE4 source code.
    It is designed to parse an Id Tech 2 map file and keep a collection
    of entity information and brush data.
    """
    def __init__(self):
        self.entities = []

    def parse_map_file(self, map_file_name):
        """
        Parses a map file
        :param map_file_name: The name of the file to parse
        """
        self.entities = []
        map_file = open(map_file_name, 'rb')
        file_lines = map_file.readlines()
        map_file.close()

        entity_lines = []
        struc_level = 0
        for line in file_lines:
            # add the line to the entity line list
            entity_lines.append(line)
            if line[0] == '{':
                struc_level += 1
            elif line[0] == '}':
                struc_level -= 1
                if struc_level == 0:
                    # end of the entity, pass the lines to a new entity
                    ent = Id2Map.Entity(entity_lines)
                    # add to entities list
                    self.entities.append(ent)
                    entity_lines = []

    class TexDef:
        """
        Information about how the texture should be presented
        """
        def __init__(self):
            self.name = ''
            self.shift = [0, 0]
            self.rotate = 0
            self.scale = [0, 0]
            self.contents = 0
            self.flags = 0
            self.value = 0

        def setup_tex_def(self, tex_name, tex_params):
            self.name = tex_name
            self.shift = (int(tex_params[0]), int(tex_params[1]))
            self.rotate = int(tex_params[2])
            self.scale = (int(tex_params[3]), int(tex_params[4]))
            if len(tex_params) > 5:
                self.contents = int(tex_params[5])
                self.flags = int(tex_params[6])
                self.value = int(tex_params[7])

    class Plane:
        """
        Plane Definition
        """
        def __init__(self):
            self.normal = [0, 0, 0]
            self.dist = 0
            self.type = 0

        def set_plane(self, plane_points):
            """
            From three points, calculate the plane
            """
            edge_vecs = []
            for i in range(0, 3):
                edge_vecs[i] = plane_points[0][i] - plane_points[1][i]
                edge_vecs[i] = plane_points[2][i] - plane_points[1][i]
                edge_vecs[i] = plane_points[1][i]

            IdMath.CrossProduct(t1, t2, self.normal)
            if IdMath.VectorCompare(self.normal, IdMath.vec3_zero):
                raise Exception('WARNING: brush plane with no normal')

            IdMath.VectorNormalize(self.normal)
            self.dist = IdMath.DotProduct(edge_vecs[2], self.normal)

    class Winding:
        BOGUS_RANGE = 18000

        """
        From the plane data, the points that make up the brush
        """
        def __init__(self):
            self.numpoints = 0
            self.maxpoints = 0
            self.points = [[0, 0, 0, 0, 0], # xyzst
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0]]

        @staticmethod
        def base_poly_for_plane(ref_plane):
            """ Get a poly that covers an effectively infinite area """
            max = 0.0
            v = 0.0

            org = [0.0, 0.0, 0.0]
            vright = [0.0, 0.0, 0.0]
            vup = [0.0, 0.0, 0.0]

            w = None

            # find the major axis
            max = -Id2Map.Winding.BOGUS_RANGE
            x = -1
            for i in range(0, 3):
                v = math.fabs(ref_plane.normal[i]);
                if v > max:
                    x = i
                    max = v

            if x == -1:
                raise Exception('BasePolyForPlane: no axis found')

            if x == 0:
                pass
            elif x == 1:
                vup[2] = 1
            elif x == 2:
                vup[0] = 1

            v = IdMath.DotProduct(vup, ref_plane.normal)
            IdMath.VectorMA(vup, -v, ref_plane.normal, vup)
            IdMath.VectorNormalize(vup);

            IdMath.VectorScale(ref_plane.normal, ref_plane.dist, org)

            IdMath.CrossProduct(vup, ref_plane.normal, vright)

            IdMath.VectorScale(vup, 8192, vup);
            IdMath.VectorScale(vright, 8192, vright);

            # project a really big axis aligned box onto the plane
            w = Id2Map.Winding()
            w.maxpoints = 4
            w.numpoints = 4

            IdMath.VectorSubtract(org, vright, w.points[0])
            IdMath.VectorAdd(w.points[0], vup, w.points[0])

            IdMath.VectorAdd(org, vright, w.points[1])
            IdMath.VectorAdd(w.points[1], vup, w.points[1])

            IdMath.VectorAdd(org, vright, w.points[2])
            IdMath.VectorSubtract(w.points[2], vup, w.points[2])

            IdMath.VectorSubtract(org, vright, w.points[3])
            IdMath.VectorSubtract(w.points[3], vup, w.points[3])

            return w


    class Face:
        """
        Face Definition
        """
        def __init__(self):
            self.planepts = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
            self.texdef = Id2Map.TexDef()
            self.plane = Id2Map.Plane()
            self.winding = None
            self.color = [0, 0, 0]

        def set_plane_point(self, point_index, vec_str):
            i = 0
            for var in vec_str.split(' '):
                # As per Ids Brush_SnapPlanepts call, we add 0.5 and floor the result. This is the same as rounding.
                self.planepts[point_index][i] = math.floor(float(var + 0.5))
                i += 1

    class Brush:
        """
        Brush Definition
        """
        def __init__(self):
            self.mins = [99999, 99999, 99999]
            self.maxs = [-99999, -99999, -99999]
            self.faces = []

        def add_face(self, face_line):
            brush_plane_re = re.compile('\(\s([\s|\d|\-|.]+)\s\)\s' # point 1
                                        '\(\s([\s|\d|\-|.]+)\s\)\s' # point 2
                                        '\(\s([\s|\d|\-|.]+)\s\)\s' # point 3
                                        '([\w|/|\d]+)\s'            # texture name
                                        '([\d|\s|.|\-]+)')          # texture params
            match = brush_plane_re.match(face_line)
            if match is not None:
                face = Id2Map.Face()
                groups = match.groups()

                # Set the plane points
                for i in range(0, 3):
                    face.set_plane_point(i, groups[i])

                # create the plane from the points
                face.plane.set_plane(face.planepts)

                # Setup the texture
                face.texdef.setup_tex_def(groups[3], groups[4].split(' '))

                # add to face list
                self.faces.append(face)
            else:
                raise Exception('WARNING: Could not parse face line {0}'.format(line))

        def make_face_windings(self):
            """ creates the visible polygons on the faces """
            for face in self.faces:
                face.winding = self.make_face_winding(face)
                if face.winding == None:
                    continue

                # add to bounding box
                for i in range(0, w.numpoints):
                    for j in range(0, 3):
                        v = face.winding.points[i][j];
                        if v > self.maxs[j]:
                            self.maxs[j] = v
                        if v < self.mins[j]:
                            self.mins[j] = v

                # setup s and t vectors, and set color
                out_vecs = IdMath.BeginTexturingFace(self, face)

                for i in range(0, face.winding.numpoints):
                    IdMath.EmitTextureCoordinates(face.winding.points[i], face)

        def make_face_winding(self, face):
            """
            Creates the visible polygon for a single face
            The general run down is, we create an extremely large polygon on the surface
            of the face plane, and we use the other planes of the brush to cut it up into
            the end resulting polygon.
            """
            past = False
            plane = Id2Map.Plane()

            # get a poly that covers an effectively infinite area
            w = Id2Map.Winding.base_poly_for_plane(face.plane)

            # chop the poly by all of the other faces
            for clip in self.faces:
                if clip == face:
                    past = True
                    continue

                if IdMath.DotProduct(face.plane.normal, clip.plane.normal) > 0.999 and math.fabs(face.plane.dist - clip.plane.dist) < 0.01:
                    # identical plane, use the later one
                    if past:
                        return None;
                    continue

                # flip the plane, because we want to keep the back side
                IdMath.VectorSubtract(IdMath.vec3_zero, clip.plane.normal, plane.normal)
                plane.dist = -clip.plane.dist

                w = IdMath.ClipWinding(w, plane, False)
                if w == None:
                    return None;

            if w.numpoints < 3:
                w = None

            if w == None:
                print('unused plane')

            return w

    class Entity:
        """
        Entity key / value pairs and brush data
        """
        def __init__(self, entity_lines):
            self.brushes = []
            self.properties = {}
            self.parse_entity(entity_lines)

        def parse_entity(self, entity_lines):
            struc_level = 0 # 1 = in entity, 2 = in brush
            in_brush = False
            param_re = re.compile('\"([\w|\d|\s|!|#-/|:-@|[-`|{-~]+)\"\s+\"([\w|\d|\s|!|#-/|:-@|[-`|{-~]*)\"')

            for line in entity_lines:
                if struc_level == 2 and line[0] != '}':
                    cur_brush = self.brushes[len(self.brushes) - 1]
                    cur_brush.add_face(line)
                elif line[0] == '{':
                    if struc_level == 1:
                        self.brushes.append(Brush())
                    struc_level += 1
                elif line[0] == '}':
                    struc_level -= 1
                    # Finished parsing brush, create the visible polygons from the planes
                    cur_brush = self.brushes[len(self.brushes) - 1]
                    cur_brush.make_face_windings()
                else:
                    # Check for a comment line
                    num_forward_slashes = 0
                    for i in range(0, 2):
                        if line[i] == '/':
                            num_forward_slashes += 1

                    if num_forward_slashes != 2:
                        # A parameter line, put it in the dictionary
                        match = param_re.match(line)
                        if match is not None:
                            groups = match.groups()
                            self.properties[groups[0]] = groups[1]
                        else:
                            raise Exception('WARNING: Could not parse property line {0}'.format(line))
                    else:
                        print('skipping comment {0}'.format(line))
