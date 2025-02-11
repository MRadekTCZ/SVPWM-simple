// SVPWM.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <stdio.h>
#include <math.h>
#define PI 3.141592653f//;
#define one_by_sqrt6 0.40824829f
#define one_by_sqrt2 0.70710678f
#define sqrt2_by_sqrt3 0.816496581f
#define pi_by_3 1.04719755f
#define one_by_pi_by_3 0.9549296596425f
#define angle_dt (0.0314159f*1.0)
#define one_by_sqrt3 0.577350269f
float angle = 2;//actual angle of PLL alfa beta vectors
float U_dc = 800;
float Ud = 300;
float Uq = 100;


struct SVPWM_vectors {
	float d1d4;
	float d2d5;
	float d3d6;
	float t0;
	float t1;
	float t2;
}svpwm;

typedef struct SVPWM_vectors SVPWM;



SVPWM svPWM(float Ud, float Uq, float theta, float U_dc)
{
	SVPWM duty_cycles;
	float phi = 0;
	float u_alfa = 0;
	float u_beta = 0;
	int sektor; // actual sector of PLL theta (1 of 6);
	float u_alfa_1 = 0; //part of alfa vector
	float u_alfa_2 = 0; //part of beta vector
	float u_beta_1 = 0;
	float u_beta_2 = 0;
	float PWM_vector_1[3] = { 0,0,0 };
	float PWM_vector_2[3] = { 0,0,0 };
	float PWM_vector_0[3] = { 0,0,0 };
	const short int OUT[6][3] = { {1,0,0},{1,1,0},{0,1,0},{0,1,1},{0,0,1},{1,0,1} }; //space vectors
	//We need only 3 transistor states, but I want to start indexing from 1 to be consinstant with theory in paper. Compiler will book space in memory for even number of bytes anyway.
	unsigned short int T1[3 + 1];
	unsigned short int T2[3 + 1];
	unsigned short int T0[3 + 1];
	float time1_vector, time2_vector, time0_vector;





	u_alfa = Ud * cosf(theta) - Uq * sinf(theta);
	u_beta = Ud * sinf(theta) + Uq * cosf(theta);
	phi = atan2f(-u_beta, -u_alfa) + PI;
	sektor = floorf(phi * one_by_pi_by_3);
	switch (sektor)
	{
	case 0:
		u_alfa_1 = sqrt2_by_sqrt3 * U_dc;
		u_beta_1 = 0.0;
		u_alfa_2 = one_by_sqrt6 * U_dc;
		u_beta_2 = one_by_sqrt2 * U_dc;
		break;
	case 1:
		u_alfa_1 = one_by_sqrt6 * U_dc;
		u_beta_1 = one_by_sqrt2 * U_dc;
		u_alfa_2 = -one_by_sqrt6 * U_dc;
		u_beta_2 = one_by_sqrt2 * U_dc;
		break;
	case 2:
		u_alfa_1 = -one_by_sqrt6 * U_dc;
		u_beta_1 = one_by_sqrt2 * U_dc;
		u_alfa_2 = -sqrt2_by_sqrt3 * U_dc;
		u_beta_2 = 0.0;
		break;
	case 3:
		u_alfa_1 = -sqrt2_by_sqrt3 * U_dc;
		u_beta_1 = 0.0;
		u_alfa_2 = -one_by_sqrt6 * U_dc;
		u_beta_2 = -one_by_sqrt2 * U_dc;
		break;
	case 4:
		u_alfa_1 = -one_by_sqrt6 * U_dc;
		u_beta_1 = -one_by_sqrt2 * U_dc;
		u_alfa_2 = one_by_sqrt6 * U_dc;
		u_beta_2 = -one_by_sqrt2 * U_dc;
		break;
	case 5:
		u_alfa_1 = one_by_sqrt6 * U_dc;
		u_beta_1 = -one_by_sqrt2 * U_dc;
		u_alfa_2 = sqrt2_by_sqrt3 * U_dc;
		u_beta_2 = 0.0;
		break;
	}


	time1_vector = (u_alfa * u_beta_2 - u_beta * u_alfa_2) / (u_alfa_1 * u_beta_2 - u_beta_1 * u_alfa_2);
	time2_vector = ((-u_alfa * u_beta_1 + u_beta * u_alfa_1) / (u_alfa_1 * u_beta_2 - u_beta_1 * u_alfa_2));
	time0_vector = 1 - time1_vector - time2_vector;


	;
	//First sector part
	T1[1] = OUT[sektor][0];
	T1[2] = OUT[sektor][1];
	T1[3] = OUT[sektor][2];

	PWM_vector_1[0] = T1[1] * time1_vector;
	PWM_vector_1[1] = T1[2] * time1_vector;
	PWM_vector_1[2] = T1[3] * time1_vector;

	//Second sector part	
	if (sektor == 5)
	{
		T2[1] = OUT[0][0];
		T2[2] = OUT[0][1];
		T2[3] = OUT[0][2];
	}
	else
	{
		T2[1] = OUT[sektor + 1][0];
		T2[2] = OUT[sektor + 1][1];
		T2[3] = OUT[sektor + 1][2];

	}
	PWM_vector_2[0] = T2[1] * time2_vector;
	PWM_vector_2[1] = T2[2] * time2_vector;
	PWM_vector_2[2] = T2[3] * time2_vector;

	/******/
	//zero vector part - optional part for less transistor switching. Don't have to be added. 
	if ((PWM_vector_1[0] + PWM_vector_2[0] + PWM_vector_1[1] + PWM_vector_2[1] + PWM_vector_1[2] + PWM_vector_2[2]) >= 1.5)
	{
		T0[1] = 1;
		T0[2] = 1;
		T0[3] = 1;
	}
	else
	{
		T0[1] = 0;
		T0[2] = 0;
		T0[3] = 0;
	}
	/******/

	PWM_vector_0[0] = T0[1] * time0_vector;
	PWM_vector_0[1] = T0[2] * time0_vector;
	PWM_vector_0[2] = T0[3] * time0_vector;

	//Sum of time vectors
	duty_cycles.d1d4 = PWM_vector_1[0] + PWM_vector_2[0] + PWM_vector_0[0];
	duty_cycles.d2d5 = PWM_vector_1[1] + PWM_vector_2[1] + PWM_vector_0[1];
	duty_cycles.d3d6 = PWM_vector_1[2] + PWM_vector_2[2] + PWM_vector_0[2];
	duty_cycles.t0 = time0_vector;
	duty_cycles.t1 = time1_vector;
	duty_cycles.t2 = time2_vector;
	return duty_cycles;
}
int main()
{
	angle = angle + angle_dt;
	if (angle >= 2 * PI)angle = angle - 2 * PI;
	if (angle < 0) angle = angle + 2 * PI; // shift 2pi for negative values
	svpwm = svPWM(Ud, Uq, angle, U_dc);

	printf("T[1]: %f, T[2]: %f, T[3]: %f", svpwm.d1d4, svpwm.d2d5, svpwm.d3d6);
}


