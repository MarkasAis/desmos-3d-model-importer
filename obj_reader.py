import math


def read(name, default_mat=1):
    obj = read_obj(name)
    if obj[2]:
        mats = read_mat(name)
    else:
        mats = [default_mat]

    return [obj[0], obj[1], mats]


def read_obj(name):
    verts = []
    faces = []

    use_materials = False

    file = open(name + ".obj", "r")
    while True:
        line = file.readline().split()
        if line[0] == "mtllib":
            use_materials = True
        elif line[0] == "o":
            break

    if not use_materials:
        faces.append([])

    while True:
        line = file.readline().split()
        if len(line) == 0:
            break

        if line[0] == "v":
            verts.append([float(line[1]), float(line[2]), float(line[3])])
        elif line[0] == "f":
            face = []
            for i in range(1, len(line)):
                face.append(int(line[i])-1)

            faces[-1].append(face)
        elif line[0] == "usemtl":
            faces.append([])

    return [verts, faces, use_materials]


def to_color_index(rgb):
    basic = [
        [199, 68 ,  64],
        [ 45, 112, 179],
        [ 56, 140,  70],
        [250, 126,  25],
        [ 96,  66, 166],
        [  0,   0,   0],
    ]

    min_dist = 195076
    color_index = 0
    for b in range(len(basic)):
        dist = 0
        for i in range(3):
            dist += math.pow(rgb[i]-basic[b][i], 2)

        if dist < min_dist:
            min_dist = dist
            color_index = b

    return color_index+1


def read_mat(name):
    mats = []

    file = open(name + ".mtl", "r")

    for segment in file:
        line = segment.split()
        if len(line) == 0:
            continue

        if line[0] == "Kd":
            rgb = [float(line[1])*255, float(line[2])*255, float(line[3])*255]
            mats.append(to_color_index(rgb))

    return mats
