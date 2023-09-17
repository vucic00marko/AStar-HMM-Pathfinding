import numpy as np

def choose_position(probabMat: np.ndarray):
    '''Returns tuple: (position_from_top_left_corner, relative_position_from_centre)'''
    n = probabMat.shape[0]
    antiSimmetricMat = [(i, j) for i in range(-(n - 1) // 2, (n + 1) // 2) for j in range(-(n - 1) // 2, (n + 1) // 2)]
    indexMat = [(i, j) for i in range(n) for j in range(n)]
    probab = probabMat.flatten()/probabMat.sum()
    d1Indexes = np.arange(n**2)
    chosen = np.random.choice(d1Indexes, 1, p=probab)
    return indexMat[chosen[0]], antiSimmetricMat[chosen[0]]

def choose_emission(emissionMat: np.ndarray):
    return choose_position(emissionMat)
