import argparse
import yaml
import tpms
import pprint
import json
import numpy as np

import logging
logger = logging.getLogger(__name__)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    req_grp = parser.add_argument_group(title='required')

    parser.add_argument(
                        '--log', 
                        default='WARNING', 
                        help='DEBUG, INFO, WARNING', 
                        type=str 
                        )

    req_grp.add_argument('--conf',
                        help='Your configuration file.', 
                        type=str, 
                        required=True 
                        )

    parser.add_argument(
                        '--stl',
                        default=None,
                        help='Save mesh to STL. Will overwrite if exist.',
                        action='store_true'
                        )

    parser.add_argument(
                        '--txt',
                        default=None,
                        help='Save conf and extra data to a text file as prettyfied json. Will overwrite if exist.',
                        action='store_true'
                        )

    parser.add_argument(
                        '--png',
                        default=None,
                        help='Save a PNG. Will overwrite if exist.',
                        action='store_true'
                        )

    parser.add_argument(
                        '--show',
                        default=False,
                        help='Show generated mesh in a window.',
                        action='store_true'
                        )

    args = parser.parse_args()
    
    loglevel = args.log
    getattr(logging, loglevel.upper())
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level)


    logger.info("Loading configuration file...")
    #conf_file = os.getcwd() + '/' + args.conf
    conf_file = args.conf
    with open(conf_file, encoding='utf-8') as stream:
        conf = yaml.safe_load(stream)


    logger.info("Reading metadata...")
    try:
        filename = conf['metadata']['filename']
    except:
        raise ValueError("Missing required metadata conf: 'filename'")


    logger.info("Reading mesh configuration...")
    try:
        m_conf = conf['mesh']
        res = m_conf['resolution']
        size = m_conf['size']
    except:
        raise ValueError("Missing required mesh conf: 'resolution' or 'size'")


    if not isinstance(size, (list, int, float)):
        raise ValueError("'size' shall be int, float or array.")

    if isinstance(size, list):
        if not len(size) == 3:
            raise ValueError("'size' have wrong length.")
        size = np.array(size)
    else:
        size = np.array([m_conf['size'], m_conf['size'], m_conf['size']])


    sizeunit_per_voxel = conf['mesh']['sizeunit_per_voxel'] = size.max() / res
    vol = None
    shift = 0


    try:
        g_conf = conf['gyroid']
    except:
        pass
    else:
        logger.info("Reading gyroid configuration...")
        try:
            a = g_conf['periodicity']
            t = g_conf['strut param']
        except:
            raise ValueError("Missing required gyroid conf: 'periodicity' or 'strut param'")

        logger.info("Generating gyroid...")
        vol = tpms.gyroid.get_gyroid(t=t, a=a, res=res, size=size)


    if vol is None:
        raise ValueError("No geometry defined.")


    distance = 1
    #mgm = 0.5
    p = conf['mesh']['lid pad'] = round(distance / sizeunit_per_voxel)
    #shift = shift + p * sizeunit_per_voxel


    mgm = conf['mesh']['mean_gradient_magnitude'] = tpms.mesh.mean_gradient_magnitude(vol, sizeunit_per_voxel)


    x, y, z = tpms.gyroid.get_voxel_grid(res=res, size=size)
    R = size[0] / size.max() #1




    vola = tpms.mesh.voxel_offset(vol=vol, distance=(distance / 2) * mgm)
    volb = tpms.mesh.voxel_offset(vol=vol, distance=-(distance / 2) * mgm)



    '''
    ca = (x**2 + y**2) <= (R-0.1)**2
    #ca = (x**2 + y**2) <= R**2
    #cb = (x**2 + y**2) <= (R-0.1)**2
    cb = (x**2 + y**2) <= R**2    

    vola[~ca] = 0     # push outside region far above iso-surface
    volb[~cb] = -2    # push outside region far above iso-surface
    '''

    #size[0] / size.max()



    z_max = z >= size[2] / size.max() #1
    z_min= z <= -size[2] / size.max() #1
    vola[z_max] -= 2
    vola[z_min] -= 2


    ca = (x**2 + y**2)**0.5 - R
    #ca = (x**2 + y**2)**0.5 - R + (distance/size.max()) * 2
    cb = (x**2 + y**2)**0.5 - R + (distance/size.max()) * 2 # space is -1 to 1 = 2 wide
    #cb = (x**2 + y**2)**0.5 - R

    '''
    def smin(a, b, k):
        # smooth min: k controls smoothness
        return -np.log(np.exp(-k*a) + np.exp(-k*b)) / k
    '''
        
    def smax(a, b, k):
        return np.log(np.exp(k*a) + np.exp(k*b)) / k

    '''
    def smin_poly(a, b, k):
        h = np.clip(0.5 + 0.5*(b - a)/k, 0.0, 1.0)
        return b*(1-h) + a*h - k*h*(1-h)

    def smax_poly(d1, d2, k):
        h = np.clip(0.5 + 0.5 * (d1 - d2) / k, 0.0, 1.0)
        return d1 * h + d2 * (1 - h) + k * h * (1 - h)
    '''
    
    k = 8.0   # higher = sharper; 5–20 is typical
    vola = smax(vola, ca, k)
    volb = smax(volb, cb, k)

    #k = 0.01  # smooth blending radius
    #vola = smax_poly(vola, ca, k)
    #volb = smax_poly(volb, cb, k)

    #def smoothstep(edge0, edge1, x):
        #t = np.clip((x - edge0) / (edge1 - edge0), 0, 1)
        #return t*t*(3 - 2*t)


    #w = 0.05       # smoothing width
    #ca = 1.0 - smoothstep(R - w, R + w, d)


    #vola = np.maximum(vola, ca)
    #volb = np.maximum(volb, cb)

    vola = np.pad(vola, (
        (0,0),
        (0,0),
        (2,2)
        ),
        #mode='constant', constant_values=-1.0)
        mode='edge')



    vola = np.pad(vola, (
        (0,0),
        (0,0),
        (2,2)
        ),
        mode='constant', constant_values=+1.0)
        #mode='constant', constant_values=0)

    

    volb = np.pad(volb, (
        (0,0),
        (0,0),
        (4,4)
        ),
        #mode='constant', constant_values=-10.0)
        mode='edge')
        #mode='constant')

    '''
    volb = np.pad(volb, (
        (0,0),
        (0,0),
        (2,2)
        ),
        mode='constant', constant_values=-1.0)
        #mode='constant', constant_values=0)
    '''

    '''
    c = (x**2 + y**2)**0.5 - R
    ca = np.pad(c, (
        (0,0),
        (0,0),
        #(2,2)
        (4,4)
        ),
        #mode='constant', constant_values=-1)
        mode='edge')
    c = (x**2 + y**2)**0.5 - R-0.1
    cb = np.pad(c, (
        (0,0),
        (0,0),
        #(2,2)
        (4,4)
        ),
        mode='constant', constant_values=-1)
        #mode='edge')
    vola = np.maximum(vola, ca)
    volb = np.maximum(volb, -cb)
    '''

    #vola = tpms.mesh.voxel_offset(vol=vol, distance=(distance / 2) * mgm)
    #volb = tpms.mesh.voxel_offset(vol=vol, distance=-(distance / 2) * mgm)
    
    vol = np.maximum(vola,-volb)
    #vol = np.maximum(vola,volb)
    #vol = np.maximum(-vola,volb)
    #vol = vola
    vol, cap_shift = tpms.mesh.voxel_cap_extremes(vol, spacing=sizeunit_per_voxel)
    



    try:
        distance = m_conf['thicken']
    except:
        pass
    else:
        logger.info("Offsetting...")
        mgm = conf['mesh']['mean_gradient_magnitude'] = tpms.mesh.mean_gradient_magnitude(vol, sizeunit_per_voxel)
        vol = tpms.mesh.voxel_offset(vol=vol, distance=distance * mgm, direction='sym')



    try:
        m_conf['cap extremes']
    except:
        pass
    else:
        logger.info("Generating surfaces at bounding box extremes...")
        vol, cap_shift = tpms.mesh.voxel_cap_extremes(vol, spacing=sizeunit_per_voxel)
        shift = shift + cap_shift


    try:
        distance = m_conf['heat exchanger']
    except:
        pass
    else:
        try:
            m_conf['thicken']
            m_conf['cap extremes']
        except:
            pass
        else:
            raise ValueError("'heat exchanger' together with 'thicken' or 'cap extremes' not allowed.")

        logger.info("Creating caps for heat exchanger...")
        mgm = conf['mesh']['mean_gradient_magnitude'] = tpms.mesh.mean_gradient_magnitude(vol, sizeunit_per_voxel)
        
        logger.info("Offsetting...")
        vola = tpms.mesh.voxel_offset(vol=vol, distance=(distance / 2) * mgm)
        volb = tpms.mesh.voxel_offset(vol=vol, distance=-(distance / 2) * mgm)

        p = conf['mesh']['lid pad'] = round(distance / sizeunit_per_voxel)
        shift = shift + p * sizeunit_per_voxel

        logger.info("Creating lids...")
        vola = np.pad(vola, (
            (p,p),
            (0,0),
            (0,0)
            ),
            mode='edge')

        vola = np.pad(vola, (
            (0,0),
            (p,p),
            (p,p)
            ),
            mode='constant', constant_values=-1.0)

        volb = np.pad(volb, (
            (0,0),
            (p,p),
            (0,0)
            ),
            mode='edge')

        volb = np.pad(volb, (
            (p,p),
            (0,0),
            (p,p)
            ),
            mode='constant', constant_values=+1.0)

        #vol = np.maximum(-vola,volb) # just lids.
        vol = np.maximum(vola,-volb)

        logger.info("Generating surfaces at bounding box extremes...")
        vol, cap_shift = tpms.mesh.voxel_cap_extremes(vol, spacing=sizeunit_per_voxel)
        shift = shift + cap_shift


    logger.info("Generating mesh from voxel grid...")
    verts, faces = tpms.mesh.get_mesh(vol=vol, spacing=sizeunit_per_voxel, shift=shift)
    conf['mesh']['shift'] = shift

    conf['mesh']['vertices'] = len(verts)
    conf['mesh']['faces'] = len(faces)
    conf['mesh']['bounding box min'] = str(verts.min(axis=0))
    conf['mesh']['bounding box max'] = str(verts.max(axis=0))


    if args.stl:
        conf['stl'] = {}
        stl = conf['stl']['filename'] = filename + '.stl'
        logger.info("Saving STL file: '" + stl + "'...")
        tpms.save_stl(verts=verts, faces=faces, filename=stl)

    if args.txt:
        conf['txt'] = {}
        txt = conf['txt']['filename'] = filename + '.txt'
        logger.info("Saving TXT file: '" + txt + "'...")
        with open(txt, "w") as file: 
            json.dump(conf, file, indent=4)

    if args.png:
        conf['png'] = {}
        png = conf['png']['filename'] = filename + '.png'
        logger.info("Saving PNG file: '" + png + "'...")
        tpms.save_png(verts=verts, faces=faces, filename=png)

    logger.info(
        "Configuration:\n" +
        json.dumps(conf, indent=4)
    )

    if args.show:
        logger.info("Showing mesh...")
        tpms.show(verts=verts, faces=faces)


