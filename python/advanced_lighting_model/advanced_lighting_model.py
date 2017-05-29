########################################################################################################################
#
#   Ryan Walters
#   Louisiana Tech University
#   2/22/17
#
#   Ray Tracing program that recursively calculates color reflections of a checkerboard with two highly-reflective
#   colored spheres. The checkerboard is also reflective. Objects also are lit and shaded using Phong shading with
#   specular highlights
#
########################################################################################################################

import math
from tkinter import *
from threading import Thread

flaggo = 0

# store the coordinates, colors, and rectangle tkninter objects for easy drawing later
pixel_array = [[0.0, 0.0, '']]
pixel_colors = []
rectangle_array = []

c_size = 500  # canvas dimensions
skip_lines = 1  # whether or not to skip lines
pixel_x = 0
pixel_y = 0

Ip = [1, 1, 1]  # intensity of our point light
Ia = [1, 1, 1]  # ambient intensity in the scene


# Start render procedure, scans through every x and y pixel in the canvas and performs ray tracing algorithm on each.
def render_proc(skiplines):
    global w, pixel_array, pixel_colors, skip_lines, c_size, pixel_x, pixel_y
    w.delete("all")  # clear the canvas
    if skiplines != skip_lines:
        skip_lines = skiplines
    pixel_x, pixel_y, screen_x, screen_y = 1, 1, 0, 0  # start at pixel 1,1
    xs, ys, zs = 0.0, 0.0, -500.0  # center of projection
    ir, ig, ib = 0, 0, 0  # intensity of red, green, and blue primaries
    depth = 5  # maximum ray depth for reflecting objects

    # iterate over every line
    while pixel_x <= c_size:  # 1200
        if pixel_x % skip_lines == 0:
            screen_x = pixel_x - c_size/2
            pixel_y = 1
            print(screen_x)  # kept it in as a progress keeper

            # iterate over every pixel in a line
            while pixel_y <= c_size:
                if pixel_y % skip_lines == 0:
                    screen_y = c_size/2 - pixel_y

                    # compute vector for ray from center of projection through pixel. Vector for light entering eye
                    ray_i = screen_x - xs
                    ray_j = screen_y - ys
                    ray_k = 0 - zs

                    # trace ray depth through the environment to obtain the pixel color
                    # the way I decided to handle the passing of pointers (thus needing multiple variables returned) was
                    # to return a dictionary.
                    trace_dict = trace_ray(0, depth, xs, ys, zs, ray_i, ray_j, ray_k, ir, ig, ib)
                    ir, ig, ib = trace_dict['ir'], trace_dict['ig'], trace_dict['ib']

                    # convert pixel color to hex string and store it in a list, along with the coords
                    pixel_color = '#%02x%02x%02x' % (int(ir), int(ig), int(ib))
                    pixel_array.append([pixel_x, pixel_y, pixel_color])

                pixel_y += 1

        pixel_x += 1

    draw()  # begin the drawing procedure


# recursive trace ray function ( actually recurses in the underlying intensity functions). Draws a ray and tests
# everything it hits, reflecting the number of times equal to our assigned depth
def trace_ray(flag, level, xs, ys, zs, ray_i, ray_j, ray_k, ir, ig, ib):
    global flaggo
    flag = 0
    intersect_x, intersect_y, intersect_z = 0.0, 0.0, 0.0  # intersection point of ray and object
    obj_normal_x, obj_normal_y, obj_normal_z = 0.0, 0.0, 0.0  # normal of closest object at intersection point

    if level < 1:  # maximum depth exceeded -- return black
        ir, ig, ib = 0, 0, 0
    else:  # check for intersection of ray with objects and set rgb values corresponding to objects
        t = 100000  # distance to closest object. Set distance of closest object initially to a very large number
        # integer code for the intersected object
        object_code = -1  # initially, no object has been intersected by the ray

        # cast ray and check if ray hits checkerboard
        cb_inter_dict = checkerboard_intersection(xs, ys, zs, ray_i, ray_j, ray_k, t, intersect_x, intersect_y, intersect_z)
        t, intersect_x, intersect_y, intersect_z = cb_inter_dict['t'], cb_inter_dict['intersect_x'], cb_inter_dict['intersect_y'], cb_inter_dict['intersect_z']
        if cb_inter_dict['boolean'] is True:
            object_code = 0

        # cast ray and check if ray hits sphere1
        s1_inter_dict = sphere1_intersection(xs, ys, zs, ray_i, ray_j, ray_k, t, intersect_x, intersect_y, intersect_z, obj_normal_x, obj_normal_y, obj_normal_z)
        t, intersect_x, intersect_y, intersect_z, obj_normal_x, obj_normal_y, obj_normal_z =\
            s1_inter_dict['t'], s1_inter_dict['intersect_x'], s1_inter_dict['intersect_y'], s1_inter_dict['intersect_z'], \
            s1_inter_dict['obj_normal_x'], s1_inter_dict['obj_normal_y'], s1_inter_dict['obj_normal_z']
        if s1_inter_dict['boolean'] is True:
            object_code = 1

        # cast ray and check if ray hits sphere2
        s2_inter_dict = sphere2_intersection(xs, ys, zs, ray_i, ray_j, ray_k, t, intersect_x, intersect_y, intersect_z, obj_normal_x, obj_normal_y, obj_normal_z)
        t, intersect_x, intersect_y, intersect_z, obj_normal_x, obj_normal_y, obj_normal_z =\
            s2_inter_dict['t'], s2_inter_dict['intersect_x'], s2_inter_dict['intersect_y'], s2_inter_dict['intersect_z'], \
            s2_inter_dict['obj_normal_x'], s2_inter_dict['obj_normal_y'], s2_inter_dict['obj_normal_z']
        if s2_inter_dict['boolean'] is True:
            object_code = 2

        # depending on what the ray hit, calculate the color for that pixel
        if object_code == 0:
            cb_pi_dict = checkerboard_point_intensity(level, intersect_x, intersect_y, intersect_z, ir, ig, ib, ray_i, ray_j, ray_k)
            ir, ig, ib = cb_pi_dict['ir'], cb_pi_dict['ig'], cb_pi_dict['ib']
        elif object_code == 1:
            s1_pi_dict = sphere1_point_intensity(level, ray_i, ray_j, ray_k, intersect_x, intersect_y, intersect_z,
                                                      obj_normal_x, obj_normal_y, obj_normal_z, ir, ig, ib)
            ir, ig, ib = s1_pi_dict['ir'], s1_pi_dict['ig'], s1_pi_dict['ib']
        elif object_code == 2:
            s2_pi_dict = sphere2_point_intensity(level, ray_i, ray_j, ray_k, intersect_x, intersect_y, intersect_z,
                                                 obj_normal_x, obj_normal_y, obj_normal_z, ir, ig, ib)
            ir, ig, ib = s2_pi_dict['ir'], s2_pi_dict['ig'], s2_pi_dict['ib']
        else:  # if it hit nothing, then the ray went into the sky. It's blue
            ir, ig, ib = 150, 150, 255

    return {'ir': ir, 'ig': ig, 'ib': ib}


# function checks to see if the ray intersected with the checkerboard
def checkerboard_intersection(xs, ys, zs, ray_x, ray_y, ray_z, t, intersect_x, intersect_y, intersect_z):
    # plane defined by the normal (0,1,0) and the offset of -500
    a, b, c, x1, y1, z1, t_object, d, x, y, z  = 0.0, 1.0, 0.0, 0.0, -500.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    denom = a * ray_x + b * ray_y + c * ray_z

    if math.fabs(denom) <= 0.001:  # basically parallel, we can say it didn't intersect
        return {'t': t, 'intersect_x': intersect_x, 'intersect_y': intersect_y, 'intersect_z': intersect_z, 'boolean': False}
    else:
        d = a * x1 + b * y1 + c * z1
        t_object = -(a * xs + b * ys + c * zs - d) / denom
        x = xs + ray_x * t_object
        y = ys + ray_y * t_object
        z = zs + ray_z * t_object
        if z < 0 or z > 8000 or t_object < 0.0:  # no visible intersection
            return {'t': t, 'intersect_x': intersect_x, 'intersect_y': intersect_y, 'intersect_z': intersect_z, 'boolean': False}
        elif t < t_object:  # there's a closer object
            return {'t': t, 'intersect_x': intersect_x, 'intersect_y': intersect_y, 'intersect_z': intersect_z, 'boolean': False}
        else:
            t = t_object
            intersect_x = x
            intersect_y = y
            intersect_z = z
            return {'t': t, 'intersect_x': intersect_x, 'intersect_y': intersect_y, 'intersect_z': intersect_z, 'boolean': True}


# Calculate the color of the pixel attributed to the checkerboard. Recursively calls ray trace
def checkerboard_point_intensity(level, x, y, z, iir, iig, iib, ray_x, ray_y, ray_z):
    # check where we are on the board and give either red or white in a checkerboard pattern dependent on location
    if x >= 0.0:
        color_flag = 1
    else:
        color_flag = 0
    if math.fabs(math.fmod(x, 400.0)) > 200.0:
        color_flag = not color_flag
    if math.fabs(math.fmod(z, 400.0)) > 200.0:
        color_flag = not color_flag
    if color_flag:
        ir, ig, ib = 255, 0, 0  # red
    else:
        ir, ig, ib = 255, 255, 255  # white

    nx, ny, nz = 0, 1, 0  # normal of the plane

    # calculate the recursively given reflected color and the checkerboard color
    ir = .7 * ir + .3 * iir
    ig = .7 * ig + .3 * iig
    ib = .7 * ib + .3 * iib

    # normalize the normal and ray vectors
    magnitude = math.sqrt(ray_x * ray_x + ray_y * ray_y + ray_z * ray_z)
    ray_x_norm = ray_x / magnitude
    ray_y_norm = ray_y / magnitude
    ray_z_norm = ray_z / magnitude
    magnitude = math.sqrt(nx * nx + ny * ny + nz * nz)
    nx_norm = nx / magnitude
    ny_norm = ny / magnitude
    nz_norm = nz / magnitude

    # calculate the reflection vector, finding phi from matrix multiplication
    cosine_phi = (-ray_x_norm) * nx_norm + (-ray_y_norm) * ny_norm + (-ray_z_norm) * nz_norm
    tcphi = 2 * cosine_phi
    rx = ray_x_norm + nx_norm * tcphi
    ry = ray_y_norm + ny_norm * tcphi
    rz = ray_z_norm + nz_norm * tcphi

    # pas our newly found reflection vector as the ray vector in the ray trace function
    t_ray_dict = trace_ray(0, level - 1, x, -499, z, rx, ry, rz, ir, ig, ib)

    # calculate the final pixel intensity and return it to the ray trace function
    ir = .7 * ir + .3 * t_ray_dict['ir']
    ig = .7 * ig + .3 * t_ray_dict['ig']
    ib = .7 * ib + .3 * t_ray_dict['ib']

    return {'ir': ir, 'ig': ig, 'ib': ib}


# calculate whether ray trace hit this sphere, return a boolean as well as the altered variables
def sphere1_intersection(xs, ys, zs, ray_x, ray_y, ray_z, t, intersect_x, intersect_y, intersect_z, obj_normal_x, obj_normal_y, obj_normal_z):
    # center of sphere is -400 and radius is 100
    disc, ts1, ts2, l, m, n, r, asphere, bsphere, csphere, tsphere = 0.0, 0.0, 0.0, 0.0, -400.0, 600.0, 100.0, 0.0, 0.0, 0.0, 0.0

    # compute intersection between ray and sphere
    asphere = ray_x * ray_x + ray_y * ray_y + ray_z * ray_z
    bsphere = 2 * ray_x * (xs-l) + 2 * ray_y * (ys-m) + 2 * ray_z * (zs-n)
    csphere = l*l + m*m + n*n + xs*xs + ys*ys + zs*zs + 2*(-l*xs - m*ys - n*zs) - r*r
    disc = bsphere*bsphere - 4*asphere*csphere  # b**2 - 4ac

    if disc < 0:  # out of radius
        return {'t': t, 'intersect_x': intersect_x, 'intersect_y': intersect_y, 'intersect_z': intersect_z,
                'obj_normal_x': obj_normal_x, 'obj_normal_y': obj_normal_y, 'obj_normal_z': obj_normal_z,
                'boolean': False}
    else:
        # I used several intermediate variables to lower multiplication calls
        sqrtdisc = math.sqrt(disc)
        tasphere = 2 * asphere
        ts1 = (-bsphere + sqrtdisc) / tasphere
        ts2 = (-bsphere - sqrtdisc) / tasphere
        if ts1 >= ts2:
            tsphere = ts2
        else:
            tsphere = ts1
        if t < tsphere:  # another object is closer
            return {'t': t, 'intersect_x': intersect_x, 'intersect_y': intersect_y, 'intersect_z': intersect_z,
                    'obj_normal_x': obj_normal_x, 'obj_normal_y': obj_normal_y, 'obj_normal_z': obj_normal_z,
                    'boolean': False}
        elif tsphere < 0.0:  # no visible intersection
            return {'t': t, 'intersect_x': intersect_x, 'intersect_y': intersect_y, 'intersect_z': intersect_z,
                    'obj_normal_x': obj_normal_x, 'obj_normal_y': obj_normal_y, 'obj_normal_z': obj_normal_z,
                    'boolean': False}
        else:  # there was a visible intersection between sphere ans ray
            t = tsphere
            # intersection point
            intersect_x = xs + ray_x * tsphere
            intersect_y = ys + ray_y * tsphere
            intersect_z = zs + ray_z * tsphere
            # need normals for lighting and reflecting
            obj_normal_x = intersect_x - l
            obj_normal_y = intersect_y - m
            obj_normal_z = intersect_z - n
            return {'t': t, 'intersect_x': intersect_x, 'intersect_y': intersect_y, 'intersect_z': intersect_z,
                    'obj_normal_x': obj_normal_x, 'obj_normal_y': obj_normal_y, 'obj_normal_z': obj_normal_z,
                    'boolean': True}


# Calculate the color of the pixel attributed to the first sphere. Recursively calls ray trace
def sphere1_point_intensity(level, ray_x, ray_y, ray_z, x, y, z, nx, ny, nz, ir, ig, ib):
    rx, ry, rz = 0.0, 0.0, 0.0  # reflection vector

    # normalize incoming vector and normal vector
    magnitude = math.sqrt(ray_x * ray_x + ray_y * ray_y + ray_z * ray_z)
    ray_x_norm = ray_x / magnitude
    ray_y_norm = ray_y / magnitude
    ray_z_norm = ray_z / magnitude
    magnitude = math.sqrt(nx * nx + ny * ny + nz * nz)
    nx_norm = nx / magnitude
    ny_norm = ny / magnitude
    nz_norm = nz / magnitude

    # find cosine phi cheaply by vector multiplication
    cosine_phi = (-ray_x_norm) * nx_norm + (-ray_y_norm) * ny_norm + (-ray_z_norm) * nz_norm
    # intermediate temporary variables to save processing
    tcphi = 2*cosine_phi
    rxn_tcphi = (-ray_x_norm) / tcphi
    ryn_tcphi = (-ray_y_norm) / tcphi
    rzn_tcphi = (-ray_z_norm) / tcphi

    if cosine_phi > 0:  # above
        rx = nx_norm - rxn_tcphi
        ry = ny_norm - ryn_tcphi
        rz = nz_norm - rzn_tcphi
    if cosine_phi == 0:  # parallel to
        rx = ray_x_norm
        ry = ray_y_norm
        rz = ray_z_norm
    if cosine_phi < 0:  # under
        rx = -nx_norm + rxn_tcphi
        ry = -ny_norm + ryn_tcphi
        rz = -nz_norm + rzn_tcphi

    # pass reflection vector to ray trace function
    t_ray_dict = trace_ray(0, level - 1, x, y, z, rx, ry, rz, ir, ig, ib)
    ir, ig, ib = t_ray_dict['ir'], t_ray_dict['ig'], t_ray_dict['ib']

    # apply lighting model using normal vector for this pixel
    phong = light([nx,ny,nz],0.3,0.9,0.3)

    # calculate final color of pixel taking into account, lighting, reflections, and base color
    ir = 0.5 * ir + 0.3 * phong[0] + 0.2 * 0
    ig = 0.5 * ig + 0.3 * phong[1] + 0.2 * 0
    ib = 0.5 * ib + 0.3 * phong[2] + 0.2 * 255

    return {'ir': ir, 'ig': ig, 'ib': ib}


# identical function to sphere1_intersection, with altered radius and offset. I won't bother commenting it
def sphere2_intersection(xs, ys, zs, ray_x, ray_y, ray_z, t, intersect_x, intersect_y, intersect_z, obj_normal_x, obj_normal_y, obj_normal_z):
    disc, ts1, ts2, l, m, n, r, asphere, bsphere, csphere, tsphere = 0.0, 0.0, 0.0, -200.0, -300.0, 1000.0, 250.0, 0.0, 0.0, 0.0, 0.0

    asphere = ray_x * ray_x + ray_y * ray_y + ray_z * ray_z
    bsphere = 2 * ray_x * (xs - l) + 2 * ray_y * (ys - m) + 2 * ray_z * (zs - n)
    csphere = l * l + m * m + n * n + xs * xs + ys * ys + zs * zs + 2 * (-l * xs - m * ys - n * zs) - r * r
    disc = bsphere * bsphere - 4 * asphere * csphere

    if disc < 0:
        return {'t': t, 'intersect_x': intersect_x, 'intersect_y': intersect_y, 'intersect_z': intersect_z,
                'obj_normal_x': obj_normal_x, 'obj_normal_y': obj_normal_y, 'obj_normal_z': obj_normal_z,
                'boolean': False}
    else:
        sqrtdisc = math.sqrt(disc)
        tasphere = 2 * asphere
        ts1 = (-bsphere + sqrtdisc) / tasphere
        ts2 = (-bsphere - sqrtdisc) / tasphere
        if ts1 >= ts2:
            tsphere = ts2
        else:
            tsphere = ts1
        if t < tsphere:
            return {'t': t, 'intersect_x': intersect_x, 'intersect_y': intersect_y, 'intersect_z': intersect_z,
                    'obj_normal_x': obj_normal_x, 'obj_normal_y': obj_normal_y, 'obj_normal_z': obj_normal_z,
                    'boolean': False}
        elif tsphere < 0.0:
            return {'t': t, 'intersect_x': intersect_x, 'intersect_y': intersect_y, 'intersect_z': intersect_z,
                    'obj_normal_x': obj_normal_x, 'obj_normal_y': obj_normal_y, 'obj_normal_z': obj_normal_z,
                    'boolean': False}
        else:
            t = tsphere
            intersect_x = xs + ray_x * tsphere
            intersect_y = ys + ray_y * tsphere
            intersect_z = zs + ray_z * tsphere
            obj_normal_x = intersect_x - l
            obj_normal_y = intersect_y - m
            obj_normal_z = intersect_z - n
            return {'t': t, 'intersect_x': intersect_x, 'intersect_y': intersect_y, 'intersect_z': intersect_z,
                    'obj_normal_x': obj_normal_x, 'obj_normal_y': obj_normal_y, 'obj_normal_z': obj_normal_z,
                    'boolean': True}


# Calculate the color of the pixel attributed to the second sphere. Recursively calls ray trace. Identical function
# to sphere1_point_intensity with an altered base color of the sphere. I won't bother commenting
def sphere2_point_intensity(level, ray_x, ray_y, ray_z, x, y, z, nx, ny, nz, ir, ig, ib):
    rx, ry, rz = 0.0, 0.0, 0.0

    magnitude = math.sqrt(ray_x * ray_x + ray_y * ray_y + ray_z * ray_z)
    ray_x_norm = ray_x / magnitude
    ray_y_norm = ray_y / magnitude
    ray_z_norm = ray_z / magnitude
    magnitude = math.sqrt(nx * nx + ny * ny + nz * nz)
    nx_norm = nx / magnitude
    ny_norm = ny / magnitude
    nz_norm = nz / magnitude

    cosine_phi = (-ray_x_norm) * nx_norm + (-ray_y_norm) * ny_norm + (-ray_z_norm) * nz_norm
    tcphi = 2 * cosine_phi
    rxn_tcphi = (-ray_x_norm) / tcphi
    ryn_tcphi = (-ray_y_norm) / tcphi
    rzn_tcphi = (-ray_z_norm) / tcphi

    if cosine_phi > 0:
        rx = nx_norm - rxn_tcphi
        ry = ny_norm - ryn_tcphi
        rz = nz_norm - rzn_tcphi
    if cosine_phi == 0:
        rx = ray_x_norm
        ry = ray_y_norm
        rz = ray_z_norm
    if cosine_phi < 0:
        rx = -nx_norm + rxn_tcphi
        ry = -ny_norm + ryn_tcphi
        rz = -nz_norm + rzn_tcphi

    t_ray_dict = trace_ray(0, level - 1, x, y, z, rx, ry, rz, ir, ig, ib)
    ir, ig, ib = t_ray_dict['ir'], t_ray_dict['ig'], t_ray_dict['ib']

    phong = light([nx,ny,nz], 0.9, 0.2, 0.3)

    # implement phone here for the last digits?
    ir = 0.5 * ir + 0.3 * phong[0] + 0.2 * 0
    ig = 0.5 * ig + 0.3 * phong[1] + 0.2 * 255
    ib = 0.5 * ib + 0.3 * phong[2] + 0.2 * 0

    return {'ir': ir, 'ig': ig, 'ib': ib}


# take normal and calculate phong shaded lighting with specular reflection for input pixel
def light(norm, kd1, kd2, kd3):
    view = [pixel_x, pixel_y, -500]  # vector to the camera
    global Ia, Ip
    Kd = [kd1, kd2, kd3]  # diffuse reflectivity of object
    Ks = 0.8  # specular reflectivity of object
    Kn = 8  # shininess of object

    light = [-0.5, -1.0, 1.0]  # normal vector to the light
    d = 1  # distance of the light. 1 means ignore

    I = [0.0, 0.0, 0.0]  # lighting intensity vector for r,b,g

    # normalize every vector
    a = math.sqrt(math.pow(norm[0], 2) + math.pow(norm[1], 2) + math.pow(norm[2], 2))
    n = [norm[0] / a, norm[1] / a, norm[2] / a]
    a = math.sqrt(math.pow(view[0], 2) + math.pow(view[1], 2) + math.pow(view[2], 2))
    v = [view[0] / a, view[1] / a, view[2] / a]
    a = math.sqrt(math.pow(light[0], 2) + math.pow(light[1], 2) + math.pow(light[2], 2))
    l = [light[0] / a, light[1] / a, light[2] / a]

    ndotl = n[0]*l[0] + n[1]*l[1] + n[2]*l[2]
    # get specular reflection from reflection function
    r = getR(n, l)
    rdotv = r[0] * v[0] + r[1] * v[1] + r[2] * v[2]

    # take the ambient color, add shading, then add specular highlights
    for i in range(len(I)):
        I[i] = Ia[i] * Kd[i]
        I[i] += Ip[i] * Kd[i] * ndotl / d
        I[i] += Ip[i] * Ks * math.pow(rdotv, Kn) * 255

    return I


# Get specular highlight for a pixel given a normal and the light vector
def getR(n, l):
    tcphi = 2*(n[0]*l[0]+n[1]*l[1]+n[2]*l[2])  # 2 cos phi
    if tcphi > 0:
        r = [n[0]-l[0]/tcphi, n[1]-l[1]/tcphi, n[2]-l[2]/tcphi]
    elif tcphi == 0:
        r = [-l[0], -l[1], -l[2]]
    else:
        r = [-n[0]+l[0]/tcphi, -n[1]+l[1]/tcphi, -n[2]+l[2]/tcphi]
    a = math.sqrt(r[0]**2 + r[1]**2 + r[2]**2)
    return [r[0]/a, r[1]/a, r[2]/a]


# alter color of pixel
def put_pixel(ar):
    w.itemconfig(ar[0], fill=ar[1])


# create a pixel
def create_pixel(ar):
    w.create_rectangle(ar[0], ar[1], ar[0] + 1, ar[1] + 1, width=0, fill=ar[2])


# ---------------------------------------------------------------------

# clear canvas and initialize the canvas
def draw():
    w.delete("all")
    init_canvas()


# color the pixels
def color_pixels(c):
    for this in c:
        put_pixel(this)


# for every pixel ( and associated color) create a single point at that location with that color
def init_canvas():
    global pixel_array
    for this in pixel_array:
        create_pixel(this)


# restart procedures in a new thread, waiting for old one to end
def refresh():
    global t
    t.join()
    t1 = Thread(target=render_proc, args=(skip_lines,))
    t1.start()


# function called when changing the dropdown selection
def changed(g):
    global c_size
    global rectangle_array
    if g == 'tiny':
        c_size = 150
    elif g == 'small':
        c_size = 300
    elif g == 'medium':
        c_size = 600
    elif g == 'large':
        c_size = 750
    elif g == 'huge':
        c_size = 900

    w.config(width=c_size)
    w.config(height=c_size)

    rectangle_array = []
    render_proc(1)


# function called when changing the dropdown selection
def changed2(g):
    global skip_lines, rectangle_array
    if g == 'full':
        skip_lines = 1

    rectangle_array = []
    refresh()


# -------------- UI ------------
root = Tk()
root.resizable(width=False, height=False)  # no resizing the canvas!
outerframe = Frame(root)
outerframe.pack()
w = Canvas(outerframe, width=c_size, height=c_size)
w.pack()

scalecontrolssteps = Frame(outerframe, borderwidth=4, relief=RIDGE)
scalecontrolssteps.pack(side=LEFT)

scaleUpButton = Button(scalecontrolssteps, text="refresh", command=refresh)
scaleUpButton.pack()

optionList = ('tiny', 'small', 'medium', 'large', 'huge')
optionList2 = ('full', 'half', 'quarter', 'full skipping')
v = StringVar()
v.set(optionList[2])
v2 = StringVar()
v2.set(optionList2[1])
om = OptionMenu(scalecontrolssteps, v, *optionList, command=changed)
om.pack()
om2 = OptionMenu(scalecontrolssteps, v2, *optionList2, command=changed2)
om2.pack()

# start main program in a new thread. Allows visualization of pixels being drawn
t = Thread(target=render_proc, args=(skip_lines,))
t.start()

root.mainloop()

