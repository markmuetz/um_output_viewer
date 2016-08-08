def domain_mean(cube):
    return cube.data.mean(axis=(-2, -1))
