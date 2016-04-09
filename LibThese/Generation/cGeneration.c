#include "generation.h"
#include <stdbool.h>

double** carree_smooth(const double rmax, const double smoothing, const int NbPart, long *seed)
{
	if( NbPart == 0 )
		return NULL;

	double **pos    = NULL;
	double xm       = 0.0,
	       ym       = 0.0,
	       zm       = 0.0,
	       new_rmax = 10.*rmax,
	       r        = 0.;

	pos = double2d(NbPart, 3);

	/*for (int i = 0; i < NbPart; i++)*/
	/*{*/
		/*xx = 1.0-2.0*ran2(seed);*/
		/*yy = 1.0-2.0*ran2(seed);*/
		/*zz = 1.0-2.0*ran2(seed);*/
		/*pos[i][0] = xx*rmax/2.0;*/
		/*pos[i][1] = yy*rmax/2.0;*/
		/*pos[i][2] = zz*rmax/2.0;*/
	/*}*/

	/*int ind = 0;*/
	/*do*/
	for(int ind = 0; ind < NbPart; )
	{
		pos[ind][0] = (1.0-2.0*ran2(seed))*new_rmax/2.0;
		pos[ind][1] = (1.0-2.0*ran2(seed))*new_rmax/2.0;
		pos[ind][2] = (1.0-2.0*ran2(seed))*new_rmax/2.0;
		r           = sqrt(pos[ind][0]*pos[ind][0] + pos[ind][1]*pos[ind][1] + pos[ind][2]*pos[ind][2]);
		if( ran2(seed) <= (erf( (rmax - r) / smoothing ) + 1.) / (erf(rmax/smoothing) + 1.) )
			ind++;
	}
	/*} while( ind < NbPart );*/

	xm = 0.0;
	ym = 0.0;
	zm = 0.0;

	for (int i = 0; i < NbPart; i++)
	{
		xm = xm + pos[i][0];
		ym = ym + pos[i][1];
		zm = zm + pos[i][2];
	}

	xm = xm/(float)(NbPart);
	ym = ym/(float)(NbPart);
	zm = zm/(float)(NbPart);

	for (int i = 0; i < NbPart; i++)
	{
		pos[i][0] = pos[i][0] - xm;
		pos[i][1] = pos[i][1] - xm;
		pos[i][2] = pos[i][2] - xm;
	}

	return pos;
}

double** carree_homo(const double rmax, const int NbPart, long *seed)
{
	if( NbPart == 0 )
		return NULL;

	//long   seed = -32;
	double **pos= NULL;
	double xx   = 0.0,
	       yy   = 0.0,
	       zz   = 0.0,
	       xm   = 0.0,
	       ym   = 0.0,
	       zm   = 0.0;
	       //pi   = 4.0*atan(1.0);

	pos = double2d(NbPart, 3);

//	FILE *fich = NULL;
//	fich = fopen("Seed_verif", "w");
	for (int i = 0; i < NbPart; i++)
	{

		xx = 1.0-2.0*ran2(seed);
//		fprintf(fich, "%ld\t", seed);
		yy = 1.0-2.0*ran2(seed);
//		fprintf(fich, "%ld\t", seed);
		zz = 1.0-2.0*ran2(seed);
//		fprintf(fich, "%ld\n", seed);
		pos[i][0] = xx*rmax/2.0;
		pos[i][1] = yy*rmax/2.0;
		pos[i][2] = zz*rmax/2.0;
	}
//	fclose(fich);

	xm = 0.0;
	ym = 0.0;
	zm = 0.0;

	for (int i = 0; i < NbPart; i++)
	{
		xm = xm + pos[i][0];
		ym = ym + pos[i][1];
		zm = zm + pos[i][2];
	}

	xm = xm/(float)(NbPart);
	ym = ym/(float)(NbPart);
	zm = zm/(float)(NbPart);

	for (int i = 0; i < NbPart; i++)
	{
		pos[i][0] = pos[i][0] - xm;
		pos[i][1] = pos[i][1] - xm;
		pos[i][2] = pos[i][2] - xm;
	}
//	fich=fopen("Stat_homo.res", "w");
//	for (int i = 0; i < NbPart; i++) {
//		for (int j = 0; j < 3; j++) {
//			fprintf(fich, "%g\t", pos[i][j]);
//		}
//		fprintf(fich, "\n");
//	}
//	fclose(fich);

	return pos;
}

double** sphere_homo(const double rmax, const int NbPart, long *seed)
{
	if( NbPart == 0 )
		return NULL;

	double **pos= NULL;
	double xx   = 0.0,
	       yy   = 0.0,
	       zz   = 0.0,
	       xm   = 0.0,
	       ym   = 0.0,
	       zm   = 0.0;
	int i;

	pos = double2d(NbPart, 3);

	for (i = 0; i < NbPart; i++)
	{
		xx = pow(ran2(seed), 1.0/3.0) * rmax;	// Rayon
		yy = 2.0*M_PI * ran2(seed);		// Phi entre 0, 2\pi
		zz = acos(1. - 2.0*ran2(seed));		// Theta entre 0, \pi

		pos[i][0] = xx * sin(zz) * cos(yy);
		pos[i][1] = xx * sin(zz) * sin(yy);
		pos[i][2] = xx * cos(zz);

		xm = xm + pos[i][0];
		ym = ym + pos[i][1];
		zm = zm + pos[i][2];

		//xx = 1.0-2.0*ran2(seed);
		//yy = 1.0-2.0*ran2(seed);
		//zz = 1.0-2.0*ran2(seed);
		//rr = sqrt(xx*xx + yy*yy + zz*zz);
		//if(rr >=  1.0)
		//{
			//i--;
			//continue;
		//}
		//pos[i][0] = xx*rmax/2.0;
		//pos[i][1] = yy*rmax/2.0;
		//pos[i][2] = zz*rmax/2.0;
		//d++;
	}

	//xm = 0.0;
	//ym = 0.0;
	//zm = 0.0;

	//for (i = 0; i < NbPart; i++)
	//{
		//xm = xm + pos[i][0];
		//ym = ym + pos[i][1];
		//zm = zm + pos[i][2];
	//}

	xm = xm/(float)(NbPart);
	ym = ym/(float)(NbPart);
	zm = zm/(float)(NbPart);

	for (i = 0; i < NbPart; i++)
	{
		pos[i][0] = pos[i][0] - xm;
		pos[i][1] = pos[i][1] - xm;
		pos[i][2] = pos[i][2] - xm;
	}

	return pos;
}

double** sphere_smooth(const double rmax, const double smoothing, const int NbPart, long *seed)
{
	if( NbPart == 0 )
		return NULL;

	double **pos    = NULL;
	double xx       = 0.0,
	       yy       = 0.0,
	       zz       = 0.0,
	       xm       = 0.0,
	       ym       = 0.0,
	       zm       = 0.0,
	       r        = 0.0,
	       new_rmax = 10.*rmax;
	int i;

	pos = double2d(NbPart, 3);

	for (i = 0; i < NbPart; )//i++)
	{
		xx = pow(ran2(seed), 1.0/3.0) * new_rmax;	// Rayon
		yy = 2.0*M_PI * ran2(seed);		// Phi entre 0, 2\pi
		zz = acos(1. - 2.0*ran2(seed));		// Theta entre 0, \pi

		pos[i][0] = xx * sin(zz) * cos(yy);
		pos[i][1] = xx * sin(zz) * sin(yy);
		pos[i][2] = xx * cos(zz);

		/*r         = sqrt(pos[i][0]*pos[i][0] + pos[i][1]*pos[i][1] + pos[i][2]*pos[i][2]);*/
		if( ran2(seed) <= (erf( (rmax - xx) / smoothing ) + 1.) / (erf(rmax/smoothing) + 1.) )
		{
			xm = xm + pos[i][0];
			ym = ym + pos[i][1];
			zm = zm + pos[i][2];
			i++;
		}
	}

	xm = xm/(float)(NbPart);
	ym = ym/(float)(NbPart);
	zm = zm/(float)(NbPart);

	for (i = 0; i < NbPart; i++)
	{
		pos[i][0] = pos[i][0] - xm;
		pos[i][1] = pos[i][1] - ym;
		pos[i][2] = pos[i][2] - zm;
	}

	return pos;
}


#define IM1 2147483563
#define IM2 2147483399
#define AM (1.0/IM1)
#define IMM1 (IM1-1)
#define IA1 40014
#define IA2 40692
#define IQ1 53668
#define IQ2 52774
#define IR1 12211
#define IR2 3791
#define NTAB 32
#define NDIV (1+IMM1/NTAB)
#define EPS 1.2e-7
#define RNMX (1.0-EPS)

static float p_ran2(long *idum)
{
	int         j;
	long        k;
	static long idum2 = 123456789;
	static long iy    = 0;
	static long iv[NTAB];
	float       temp;

#pragma omp threadprivate(idum2,iy,iv)

	if( *idum <= 0 )
	{							// Initialize.
		if( -(*idum) < 1 )
			*idum = 1;				// Be sure to prevent idum = 0.
		else
			*idum = -(*idum);

		idum2  = (*idum);

		for(j = NTAB + 7; j >= 0; j--)
		{						// Load the shuﬄe table (after 8 warm-ups).
			k     = (*idum) / IQ1;
			*idum = IA1 * (*idum - k * IQ1) - k * IR1;
			if( *idum < 0 )
				*idum += IM1;
			if( j < NTAB )
				iv[j]  = *idum;
		}
		iy     = iv[0];
	}
	k     = (*idum) / IQ1;					// Start here when not initializing.
	*idum = IA1 * (*idum - k * IQ1) - k * IR1;		// Compute idum=(IA1*idum) % IM1 without
	if(*idum < 0)
		*idum += IM1;					// overﬂows by Schrage’s method.
	k     = idum2 / IQ2;
	idum2 = IA2 * (idum2 - k * IQ2) - k * IR2;		// Compute idum2=(IA2*idum) % IM2 likewise.
	if(idum2 < 0)
		idum2 += IM2;
	j     = iy / NDIV;					// Will be in the range 0..NTAB-1.
	iy    = iv[j] - idum2;					// Here idum is shuﬄed, idum and idum2 are
	iv[j] = *idum;						// combined to generate output.
	if(iy < 1)
		iy    += IMM1;
	if( (temp = AM * iy) > RNMX)
		return RNMX;					// Because users don’t expect endpoint values.
	else
		return temp;
}

double** sphere_smooth_parallel(
		const double rmax,
		const double smoothing,
		const int NbPart,
		const int nb_thread,
		long *seed)
{
	if( NbPart == 0 )
		return NULL;

	double **pos    = NULL;
	double xx       = 0.0,
	       yy       = 0.0,
	       zz       = 0.0,
	       xm       = 0.0,
	       ym       = 0.0,
	       zm       = 0.0,
	       new_rmax = 10.*rmax;
	long *tab_seed  = NULL;
	long i_tab = NULL;
	int i, id,j;
	bool test;

	pos      = double2d(NbPart, 3);
	tab_seed = (long*)malloc(sizeof(long)*nb_thread);
	for(i=0; i<nb_thread; i++)
		tab_seed[i] = rand(); //p_ran2(seed);
#ifdef _OPENMP
	omp_set_num_threads(nb_thread);
#endif

	#pragma omp parallel shared(pos,tab_seed,new_rmax,seed,xm,ym,zm) \
			     private(i,id,xx,yy,zz,i_tab,test,j) \
			     default(none)
	{
#ifdef _OPENMP
		id = omp_get_thread_num();
		printf("Thread: %d\n", id);
#else
		id = 0;
#endif
		#pragma omp for schedule(dynamic) reduction(+:xm,ym,zm)
		for (i = 0; i < NbPart; i++)
		{
			do
			{
				i_tab = tab_seed[id];
				xx = pow(p_ran2(&i_tab), 1.0/3.0) * new_rmax;	// Rayon
				tab_seed[id] = i_tab;

				i_tab = tab_seed[id];
				yy = 2.0*M_PI * p_ran2(&i_tab);			// Phi entre 0, 2\pi
				tab_seed[id] = i_tab;

				i_tab = tab_seed[id];
				zz = acos(1. - 2.0*p_ran2(&i_tab));		// Theta entre 0, \pi
				tab_seed[id] = i_tab;

				pos[i][0] = xx * sin(zz) * cos(yy);
				pos[i][1] = xx * sin(zz) * sin(yy);
				pos[i][2] = xx * cos(zz);

				i_tab = tab_seed[id];
				test = !( p_ran2(&i_tab) <= (erf( (rmax - xx) / smoothing ) + 1.) / (erf(rmax/smoothing) + 1.) );
				//test = !( p_ran2(&i_tab) <= (( (rmax - xx) / smoothing ) + 1.) / ((rmax/smoothing) + 1.) );
				tab_seed[id] = i_tab;

			}
			while( test );

			xm = xm + pos[i][0];
			ym = ym + pos[i][1];
			zm = zm + pos[i][2];
		}
	}

	xm = xm/(float)(NbPart);
	ym = ym/(float)(NbPart);
	zm = zm/(float)(NbPart);

	#pragma omp parallel shared(pos,tab_seed,new_rmax,seed,xm,ym,zm) \
			     private(i,id,xx,yy,zz) \
			     default(none)
	{
#ifdef _OPENMP
		id = omp_get_thread_num();
#else
		id=0;
#endif
		#pragma omp for schedule(dynamic)
		for (i = 0; i < NbPart; i++)
		{
			pos[i][0] = pos[i][0] - xm;
			pos[i][1] = pos[i][1] - ym;
			pos[i][2] = pos[i][2] - zm;
		}
	}

	free(tab_seed);
	return pos;
}

double** gauss_limit(const double sig, const double broke, const int NbPart, long *seed)
{
	if( NbPart == 0 )
		return NULL;

	double **vit = NULL;
	vit = double2d(NbPart, 3);

	for (int i = 0; i < NbPart; i++)
	{
		for (int j = 0; j < 3; j++)
		{
			do
			{
				vit[i][j] = sqrt(-2.0*sig*log(ran2(seed)))*cos(2.0*acos(-1.0)*ran2(seed));
			} while(vit[i][j] >= broke*sig);
		}
	}

	return vit;
}

double** gauss(const double sig, const int NbPart, long *seed)
{
	if( NbPart == 0 )
		return NULL;

	double **vit = NULL;
	vit = double2d(NbPart, 3);

	for (int i = 0; i < NbPart; i++)
	{
		for (int j = 0; j < 3; j++)
		{
			vit[i][j] = sqrt(-2.0*sig*log(ran2(seed)))*cos(2.0*acos(-1.0)*ran2(seed));
		}
	}

	return vit;
}

void King_gene(const King Amas, const int Nb_part_t1, double *r_grand, double **king_pos, double **king_vit, long *seed)
{
	double normal    = King_distrib(&Amas, Amas.amas.m * King_don_pot(&Amas, 0));
	//long   seed      = -32;
	int    rejet     = 0,
	       i	 = 0;

	double x, y, z, vx, vy, vz;
	x = y = z = vx = vy = vz = 0.0;

        printf("Normalisation de f(E) = %g\n\n", normal);

	*r_grand = 0.0;

	fprintf(stderr, "\r\033[01m%03.3f%%\033[00m", ( (double)i ) / ( (double) Nb_part_t1 ) * 100.0 );
	while( i < Nb_part_t1 )
	{
		Coord tmp;

		tmp.x    = -Amas.amas.rmax + 2.0*Amas.amas.rmax*ran2(seed);
		tmp.y    = -Amas.amas.rmax + 2.0*Amas.amas.rmax*ran2(seed);
		tmp.z    = -Amas.amas.rmax + 2.0*Amas.amas.rmax*ran2(seed);
		tmp.vx   = -Amas.amas.vmax + 2.0*Amas.amas.vmax*ran2(seed);
		tmp.vy   = -Amas.amas.vmax + 2.0*Amas.amas.vmax*ran2(seed);
		tmp.vz   = -Amas.amas.vmax + 2.0*Amas.amas.vmax*ran2(seed);

		double v = sqrt(tmp.vx*tmp.vx + tmp.vy*tmp.vy + tmp.vz*tmp.vz),
		       r = sqrt(tmp.x*tmp.x + tmp.y*tmp.y + tmp.z*tmp.z);

		double E = Amas.amas.m * v*v /2.0 + Amas.amas.m * King_don_pot(&Amas, r);

		if( r <= Amas.amas.rmax && v <= Amas.amas.vmax && ran2(seed) <= King_distrib(&Amas, E)/normal )
		{
			if( *r_grand < r )
				*r_grand = r;
			king_pos[i][0]  = tmp.x;
			king_pos[i][1]  = tmp.y;
			king_pos[i][2]  = tmp.z;
			king_vit[i][0]  = tmp.vx;
			king_vit[i][1]  = tmp.vy;
			king_vit[i][2]  = tmp.vz;
			x+=tmp.x;
			y+=tmp.y;
			z+=tmp.z;
			vx+=tmp.vx;
			vy+=tmp.vy;
			vz+=tmp.vz;
			i++;
			fprintf(stderr, "\r\033[01m%03.3f%%\033[00m", ( (double)i ) / ( (double) Nb_part_t1 ) * 100.0 );
		}
		else
			rejet++;
	}
	fputs("\n", stderr);

	x/=Nb_part_t1;
	y/=Nb_part_t1;
	z/=Nb_part_t1;
	vx/=Nb_part_t1;
	vy/=Nb_part_t1;
	vz/=Nb_part_t1;

	printf("%g\t%g\t%g\n%g\t%g\t%g\n", x, y, z, vx, vy, vz);
}

void King_Generate(const King Amas, const int Nb_part_t1, double *r_grand, Particule_d king, long *seed)
{
	double normal    = King_distrib(&Amas, Amas.amas.m * King_don_pot(&Amas, 0));
	//long   seed      = -32;
	long   rejet     = 0;
	int    i	 = 0;

	double x, y, z, vx, vy, vz;
	x = y = z = vx = vy = vz = 0.0;

        printf("Normalisation de f(E) = %g\n\n", normal);

	*r_grand = 0.0;

	fprintf(stderr, "\r\033[01m%03.3f%%\033[00m", ( (double)i ) / ( (double) Nb_part_t1 ) * 100.0 );
	while( i < Nb_part_t1 )
	{
		Coord tmp;

		tmp.x    = -Amas.amas.rmax + 2.0*Amas.amas.rmax*ran2(seed);
		tmp.y    = -Amas.amas.rmax + 2.0*Amas.amas.rmax*ran2(seed);
		tmp.z    = -Amas.amas.rmax + 2.0*Amas.amas.rmax*ran2(seed);
		tmp.vx   = -Amas.amas.vmax + 2.0*Amas.amas.vmax*ran2(seed);
		tmp.vy   = -Amas.amas.vmax + 2.0*Amas.amas.vmax*ran2(seed);
		tmp.vz   = -Amas.amas.vmax + 2.0*Amas.amas.vmax*ran2(seed);

		double v = sqrt(tmp.vx*tmp.vx + tmp.vy*tmp.vy + tmp.vz*tmp.vz),
		       r = sqrt(tmp.x*tmp.x + tmp.y*tmp.y + tmp.z*tmp.z);

		double E = Amas.amas.m * v*v /2.0 + Amas.amas.m * King_don_pot(&Amas, r);

		if( r <= Amas.amas.rmax && v <= Amas.amas.vmax && ran2(seed) <= King_distrib(&Amas, E)/normal )
		{
			if( *r_grand < r )
				*r_grand = r;
			king[i].Pos[0]   = tmp.x;
			king[i].Pos[1]   = tmp.y;
			king[i].Pos[2]   = tmp.z;
			king[i].Vit[0]   = tmp.vx;
			king[i].Vit[1]   = tmp.vy;
			king[i].Vit[2]   = tmp.vz;

			x		+=tmp.x;
			y		+=tmp.y;
			z		+=tmp.z;
			vx		+=tmp.vx;
			vy		+=tmp.vy;
			vz		+=tmp.vz;

			i++;
			fprintf(stderr, "\r\033[01m%03.3f%%\033[00m", ( (double)i ) / ( (double) Nb_part_t1 ) * 100.0 );
		}
		else
			rejet++;

	}
	fputs("\n", stderr);

	x  /= Nb_part_t1;
	y  /= Nb_part_t1;
	z  /= Nb_part_t1;
	vx /= Nb_part_t1;
	vy /= Nb_part_t1;
	vz /= Nb_part_t1;

	printf("%g\t%g\t%g\n%g\t%g\t%g\n", x, y, z, vx, vy, vz);
	for(int j = 0; j < Nb_part_t1; j++)
	{
		king[j].Pos[0] -= x;
		king[j].Pos[1] -= y;
		king[j].Pos[2] -= z;
	}
}

static inline double Fuji_distrib(const double r, const double u, const double j, const double sig_v, const double rho_0)
{
	return rho_0 * pow( 2.*M_PI*sig_v*sig_v, -3.0/2.0) * exp(- (u*u + j*j/(r*r)) / (2.*sig_v*sig_v) );
}

void Fuji_Generate(const int Nb_part_t1, const double r_max, const double v_max, const double sig_v, const double rho_0, Particule_d king, double *r_grand, long *seed)
{
	unsigned int i = 0,
		     k = 0;
	unsigned int rejet = 0;
	//double normal = Fuji_distrib(0.1, 0., 0., sig_v, rho_0);
	double normal = 4./3. * M_PI * r_max * r_max * r_max; //Fuji_distrib(0.1, 0., 0., sig_v, rho_0);
	double v, r, j, u;
	double x = 0.,
	       y = 0.,
	       z = 0.,
	       vx = 0.,
	       vy = 0.,
	       vz = 0.;

	while( i < Nb_part_t1 )
	{
		for(k=0; k<3; k++)
			king[i].Pos[k] = ran2(seed) * r_max;
		for(k=0; k<3; k++)
			king[i].Vit[k] = ran2(seed) * v_max;

		v = sqrt(king[i].Vit[0]*king[i].Vit[0] + king[i].Vit[1]*king[i].Vit[1] + king[i].Vit[2]*king[i].Vit[2]);
		r = sqrt(king[i].Pos[0]*king[i].Pos[0] + king[i].Pos[1]*king[i].Pos[1] + king[i].Pos[2]*king[i].Pos[2]);
		j = sqrt(	  (king[i].Vit[1] * king[i].Pos[2] - king[i].Pos[1] * king[i].Vit[2])*(king[i].Vit[1] * king[i].Pos[2] - king[i].Pos[1] * king[i].Vit[2])
				+ (king[i].Pos[0] * king[i].Vit[2] - king[i].Pos[2]*king[i].Vit[0])*(king[i].Pos[0] * king[i].Vit[2] - king[i].Pos[2]*king[i].Vit[0])
				+ (king[i].Pos[1] * king[i].Vit[0] - king[i].Pos[0] * king[i].Vit[1])*(king[i].Pos[1] * king[i].Vit[0] - king[i].Pos[0] * king[i].Vit[1])
			);
		u = ( king[i].Pos[0]*king[i].Vit[0] + king[i].Pos[1]*king[i].Vit[1] + king[i].Pos[2]*king[i].Vit[2] ) / r;

		if( r <= r_max && v <= v_max && ran2(seed) <= Fuji_distrib(r, u, j, sig_v, rho_0)/normal )
		{
			if( *r_grand < r )
				*r_grand = r;

			x		+= king[i].Pos[0];
			y		+= king[i].Pos[1];
			z		+= king[i].Pos[2];
			vx		+= king[i].Vit[0];
			vy		+= king[i].Vit[1];
			vz		+= king[i].Vit[2];

			i++;
		}
		else
			rejet++;

	}

	x  /= Nb_part_t1;
	y  /= Nb_part_t1;
	z  /= Nb_part_t1;
	vx /= Nb_part_t1;
	vy /= Nb_part_t1;
	vz /= Nb_part_t1;

	for(int j = 0; j < Nb_part_t1; j++)
	{
		king[j].Pos[0] -= x;
		king[j].Pos[1] -= y;
		king[j].Pos[2] -= z;
	}
}
