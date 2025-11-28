import argparse
import yaml
import pprint
import json
import numpy as np

import sdf

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
    else:
        size = [m_conf['size']] * 3


    x, y, z = sdf.get(res=res, size=size)
    sizeunit_per_voxel = conf['mesh']['sizeunit_per_voxel'] = max(size) / res
    vol = None
    shift = np.array([0,0,0])


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
        vol = sdf.tpms.gyroid(x, y, z, t, a)


    if vol is None:
        raise ValueError("No geometry defined.")


    try:
        distance = m_conf['thicken']
    except:
        pass
    else:
        logger.info("Offsetting...")
        mgm = conf['mesh']['mean_gradient_magnitude'] = sdf.mean_gradient_magnitude(vol, sizeunit_per_voxel)
        vol = sdf.thicken(vol=vol, distance=distance * mgm, direction='sym')


    try:
        m_conf['cap extremes']
    except:
        pass
    else:
        logger.info("Generating surfaces at bounding box extremes...")
        vol = np.pad(vol, (
            (2,2),
            (2,2),
            (2,2)
            ),
            mode='constant', constant_values=+1.0)
        shift += np.array([-2]*3)


    try:
        distance = m_conf['cuboid heat exchanger']
    except:
        pass
    else:
        try:
            m_conf['thicken']
            m_conf['cap extremes']
            m_conf['cylinder heat exchanger']
        except:
            pass
        else:
            raise ValueError("'heat exchanger' together with 'thicken', 'cap extremes', 'cylinder heat exchanger' not allowed.")

        logger.info("Creating caps for heat exchanger...")
        mgm = conf['mesh']['mean_gradient_magnitude'] = sdf.mean_gradient_magnitude(vol, sizeunit_per_voxel)
        
        logger.info("Offsetting...")
        vola = sdf.offset(vol=vol, distance=(distance / 2) * mgm)
        volb = sdf.offset(vol=vol, distance=-(distance / 2) * mgm)

        p = conf['mesh']['lid pad'] = round(distance / sizeunit_per_voxel)

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

        shift += np.array([-p]*3)

        #vol = np.maximum(-vola,volb) # just lids.
        vol = np.maximum(vola,-volb)

        logger.info("Generating surfaces at bounding box extremes...")
        vol = np.pad(vol, (
            (2,2),
            (2,2),
            (2,2)
            ),
            mode='constant', constant_values=+1.0)
        shift += np.array([-2]*3)


    try:
        distance = m_conf['cylinder heat exchanger']
    except:
        pass
    else:
        try:
            m_conf['thicken']
            m_conf['cap extremes']
            m_conf['cuboid heat exchanger']
        except:
            pass
        else:
            raise ValueError("'heat exchanger' together with 'thicken', 'cap extremes', 'cuboid heat exchanger' not allowed.")

        logger.info("Creating caps for heat exchanger...")

        logger.info("Offsetting...")
        mgm = conf['mesh']['mean_gradient_magnitude'] = sdf.mean_gradient_magnitude(vol, sizeunit_per_voxel)
        vola = sdf.offset(vol=vol, distance=(distance / 2) * mgm)
        volb = sdf.offset(vol=vol, distance=-(distance / 2) * mgm)

        logger.info("Creating Z lids...")

        # Cap inside on Z
        # masks for top and bottom surface
        z_max = z >= size[2] / max(size)
        z_min= z <= -size[2] / max(size)
        # push inside region below iso-surface
        vola[z_max] = -1
        vola[z_min] = -1 

        logger.info("Masking cylinder...")

        R = min(size[0:2]) / max(size) # unit is in extent of voxel space (-1 to 1)

        # cylindrical mask for outer surface 
        ca = (x**2 + y**2)**0.5 - R
        # cylindrical mask for inner surface
        cb = (x**2 + y**2)**0.5 - (R - (distance/max(size)) * 2) # space is -1 to 1 = 2 wide

        # apply cylidrical mask
        k = 8.0
        vola = sdf.smooth_max_lse(vola, ca, k)
        volb = sdf.smooth_max_lse(volb, cb, k)

        logger.info("Thickening Z lids...")

        p = conf['mesh']['lid pad'] = round(distance / sizeunit_per_voxel)

        # thicken outer by extending surface in z
        vola = np.pad(vola, (
            (0,0),
            (0,0),
            (p,p)
            ),
            mode='edge')

        # pad inner by extending surface in z
        volb = np.pad(volb, (
            (0,0),
            (0,0),
            (p,p)
            ),
            mode='edge')

        shift += np.array([0,0,-p])


        # join outer and inner surface
        vol = np.maximum(vola,-volb)
        #vol = -volb
        
        # cap z by padding with positive value (makes negative inside cross iso surface)
        vol = np.pad(vol, (
            (0,0),
            (0,0),
            (2,2)
            ),
            mode='constant', constant_values=+1.0)
        shift += np.array([0,0,-2])



    logger.info("Generating mesh from voxel grid...")
    verts, faces = sdf.mesh.generate(vol=vol, spacing=sizeunit_per_voxel) #, shift=shift)

    # Move verts back to 0,0,0
    shift = shift * sizeunit_per_voxel
    verts = sdf.mesh.translate(verts, shift)
    conf['mesh']['shift'] = shift.tolist()

    conf['mesh']['vertices'] = len(verts)
    conf['mesh']['faces'] = len(faces)
    conf['mesh']['bounding box min'] = str(verts.min(axis=0))
    conf['mesh']['bounding box max'] = str(verts.max(axis=0))


    if args.stl:
        conf['stl'] = {}
        stl = conf['stl']['filename'] = filename + '.stl'
        logger.info("Saving STL file: '" + stl + "'...")
        sdf.mesh.save(verts=verts, faces=faces, filename=stl)

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
        sdf.image.save_png(verts=verts, faces=faces, filename=png)

    logger.info(
        "Configuration:\n" +
        json.dumps(conf, indent=4)
    )

    if args.show:
        logger.info("Showing mesh...")
        sdf.image.show(verts=verts, faces=faces)


