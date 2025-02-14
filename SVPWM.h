/*
 * SVPWM.h
 *
 *  Created on: Nov 25, 2024
 *      Author: brzycki
 */

#ifndef DEVICE_SVPWM_H_
#define DEVICE_SVPWM_H_

#include <math.h>
#define PI 3.141592653f//;
#define one_by_sqrt6 0.40824829f
#define one_by_sqrt2 0.70710678f
#define sqrt2_by_sqrt3 0.816496581f
#define pi_by_3 1.04719755f
#define one_by_pi_by_3 0.9549296596425f
#define angle_dt (0.0314159f*1.0)


struct SVPWM_vectors {
    float d1d4;
    float d2d5;
    float d3d6;
    float t0;
    float t1;
    float t2;
    float mod_index;
};

typedef struct SVPWM_vectors SVPWM;
SVPWM svPWM(float Ud, float Uq, float theta, float U_dc);



#endif /* DEVICE_SVPWM_H_ */
