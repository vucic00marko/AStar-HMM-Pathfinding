import numpy as np
from vertex import Vertex
from tkWindowInput import tk_window_input


def inner_mat_prod(v1: Vertex, v2: Vertex, outMat: np.ndarray, mat: np.ndarray) -> np.ndarray:

    dy = v1.x - v2.x
    dx = v1.y - v2.y
    v1_x_first = max(0, -dx)
    v1_x_second = min(3, 3 - dx)
    v1_y_first = max(0, -dy)
    v1_y_second = min(3, 3 - dy)

    v2_x_first = max(0, dx)
    v2_x_second = min(3, 3 + dx)
    v2_y_first = max(0, dy)
    v2_y_second = min(3, 3 + dy)

    z = np.zeros((3, 3))
    slice1 = outMat[v1_x_first: v1_x_second, v1_y_first: v1_y_second]
    slice2 = mat[v2_x_first: v2_x_second, v2_y_first: v2_y_second]
    z[v1_x_first: v1_x_second, v1_y_first: v1_y_second] = np.multiply(
        slice1, slice2)
    return z


def pred_form_stateEstimMat(temp_s_ver: Vertex, desiredStep: Vertex, transitionMat: np.ndarray, stateEstimMat: np.ndarray, ) -> np.ndarray:  # Prediction
    '''Computes future position probabilities. DesiredStep is one block shiftes in desired direction in relation to the temp_s_ver'''
    rotatedTransitionMat = np.copy(transitionMat)
    if desiredStep.x == temp_s_ver.x - 1:  # Rotates in desired direction of movement
        pass
    elif desiredStep.x == temp_s_ver.x + 1:
        rotatedTransitionMat = np.rot90(transitionMat, 2)
    elif desiredStep.y == temp_s_ver.y - 1:
        rotatedTransitionMat = np.rot90(transitionMat)
    elif desiredStep.y == temp_s_ver.y + 1:
        rotatedTransitionMat = np.rot90(transitionMat, -1)
    z = np.zeros((5, 5))
    for i in range(3):
        z[i:i+3, 1:4] += rotatedTransitionMat * stateEstimMat[i, 1]
    z[1:4, 0:3] += rotatedTransitionMat * stateEstimMat[1, 0]
    z[1:4, 2:5] += rotatedTransitionMat * stateEstimMat[1, 2]
    return z
