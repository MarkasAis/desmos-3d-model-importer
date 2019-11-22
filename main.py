import obj_reader as OBJReader
import desmos_interactor as DI
import math
import sys, getopt


def import_model(name, wireframe=True, fill=True, batch_size=30):
    DI.create_folder("Model Data")
    model = OBJReader.read(name)
    print("Assigned materials: ", model[2])

    real_values = model[0]
    for i in range(len(model[0])):
        for j in range(len(model[0][i])):
            real_values[i][j] = round(model[0][i][j], 5)

    DI.define_table(["x1", "y1", "z1"], real_values)

    for b in range(int(math.ceil(len(model[0])/batch_size))):
        batch_start = b * batch_size
        cur_size = min(batch_size, len(model[0])-batch_start)
        batch_values = [[0] * 8 for i in range(cur_size)]
        batch_index = str(b+1)

        for i in range(cur_size):
            global_index = str(i+batch_start+1)
            local_index = str(i+1)

            batch_values[i][0] = "RXy(y1[" + global_index + "],z1[" + global_index + "])"
            batch_values[i][1] = "RXz(y1[" + global_index + "],z1[" + global_index + "])"

            batch_values[i][2] = "RYx(x1[" + global_index + "],r1Z" + batch_index + "[" + local_index + "])"
            batch_values[i][3] = "RYz(x1[" + global_index + "],r1Z" + batch_index + "[" + local_index + "])"

            batch_values[i][4] = "RZx(r2X" + batch_index + "[" + local_index + "],r1Y" + batch_index + "[" + local_index + "])"
            batch_values[i][5] = "RZy(r2X" + batch_index + "[" + local_index + "],r1Y" + batch_index + "[" + local_index + "])"

            batch_values[i][6] = "Fx(r3X" + batch_index + "[" + local_index + "],r3Y" + batch_index + "[" + local_index + "],r2Z" + batch_index + "[" + local_index + "])"
            batch_values[i][7] = "Fy(r3X" + batch_index + "[" + local_index + "],r3Y" + batch_index + "[" + local_index + "],r2Z" + batch_index + "[" + local_index + "])"

        DI.comment("")
        DI.comment("Batch #" + str(b+1))
        DI.define_table(["r1Y" + batch_index, "r1Z" + batch_index, "r2X" + batch_index, "r2Z" + batch_index, "r3X" + batch_index, "r3Y" + batch_index, "x2" + batch_index, "y2" + batch_index], batch_values)

    polygon_blocks = []
    for f_type in range(len(model[1])):
        polygon_blocks.append([])
        for f in range(len(model[1][f_type])):
            face = model[1][f_type][f]
            vertices = []
            for v in face:
                vertex_batch = str(int(v/batch_size)+1)
                local_index = str(v % batch_size+1)
                vertex = ["x2" + vertex_batch + "[" + local_index + "]", "y2" + vertex_batch + "[" + local_index + "]"]
                vertices.append(vertex)

            polygon_blocks[-1].append(DI.define_polygon(vertices))

    DI.toggle_edit_mode()
    for p_type in range(len(polygon_blocks)):
        for p in polygon_blocks[p_type]:
            DI.toggle_expression_edit_mode(p)

            if not wireframe:
                DI.toggle_wireframe()
            if not fill:
                DI.toggle_face()

            DI.set_color(model[2][p_type])

    DI.toggle_edit_mode()
    DI.end_folder()


def setup_engine():
    DI.start()
    DI.set_degree_mode()

    DI.create_folder("Options")
    DI.define_variable("rotationX", 0, -180, 180)
    DI.define_variable("rotationY", 0, -180, 180)
    DI.define_variable("rotationZ", 0, -180, 180)
    DI.define_variable("fov", 90, 0, 180)
    DI.define_variable("cameraZ", -2, -10, -1)
    DI.end_folder(False)

    DI.create_folder("Engine")
    DI.define_variable("planeZ", "1/tan(fov/2)")
    DI.define_variable("sX", "sin(rotationX)")
    DI.define_variable("sY", "sin(rotationY)")
    DI.define_variable("sZ", "sin(rotationZ)")
    DI.define_variable("cX", "cos(rotationX)")
    DI.define_variable("cY", "cos(rotationY)")
    DI.define_variable("cZ", "cos(rotationZ)")

    DI.define_function("Px", ["x", "z"], "x*(planeZ/z)")
    DI.define_function("Py", ["y", "z"], "y*(planeZ/z)")

    DI.define_function("RXy", ["y", "z"], "ycX+zsX")
    DI.define_function("RXz", ["y", "z"], "zcX-ysX")

    DI.define_function("RYx", ["x", "z"], "xcY-zsY")
    DI.define_function("RYz", ["x", "z"], "xsY+zcY")

    DI.define_function("RZx", ["x", "y"], "xcZ+ysZ")
    DI.define_function("RZy", ["x", "y"], "ycZ-xsZ")

    DI.define_function("Fx", ["x", "y", "z"], "Px(x, z-cameraZ)")
    DI.define_function("Fy", ["x", "y", "z"], "Px(y, z-cameraZ)")
    DI.end_folder()


def main(argv):
    print(argv)

    model_location = "models/default"
    draw_wireframe = True
    draw_faces = True

    for i in range(0, len(argv), 2):
        opt = argv[i]
        arg = argv[i+1]
        if opt == '-h':
            print
            'main.py -m <model_location> -w <draw_wireframe> -f <draw_faces>'
            sys.exit()
        elif opt == "-m":
            model_location = arg
        elif opt == "-w":
            draw_wireframe = True if arg == "True" else False
        elif opt == "-f":
            draw_faces = True if arg == "True" else False

    if not isinstance(model_location, str):
        print("Model location: '", model_location, "' is invalid")
        sys.exit()

    print("Importing model: '", model_location, "'. Wireframe: ", "ON" if draw_wireframe else "OFF", "   Faces: ", "ON" if draw_faces else "OFF")

    setup_engine()
    import_model(model_location, draw_wireframe, draw_faces)


if __name__ == "__main__":
   main(sys.argv[1:])