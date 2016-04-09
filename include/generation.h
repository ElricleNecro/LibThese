#ifndef GENERATION_H

#define GENERATION_H

#ifdef _OPENMP
#include <omp.h>
#endif
#include <stdio.h>
#include <tgmath.h>
#include <king/isotherm.h>

#include "types.h"
#include "tree.h"

#define vitess_gauss gauss_limit

typedef struct {
	double x, y, z, vx, vy, vz;
}Coord;

/**
 * Fonction générant des particules réparties de façon homogène dans un cube.
 *
 * @param[in] rmax Côté du cube.
 * @param[in] NbPart Nombre de particule à générer.
 * @param[inout] *seed Graine du générateur.
 * @return Tableau de dimension [NbPart][3] contenant les coordonnées générées.
 */
double** carree_homo(const double rmax, const int NbPart, long *seed);

double** carree_smooth(const double rmax, const double smoothing, const int NbPart, long *seed);

/**
 * Fonction générant des particules réparties de façon homogène dans une sphère.
 *
 * @param[in] rmax diamètre de la sphère.
 * @param[in] NbPart Nombre de particule à générer.
 * @param[inout] *seed Graine du générateur.
 * @return Tableau de dimension [NbPart][3] contenant les coordonnées générées.
 */
double** sphere_homo(const double rmax, const int NbPart, long *seed);

double** sphere_smooth(const double rmax, const double smoothing, const int NbPart, long *seed);

double** sphere_smooth_parallel(
		const double rmax,
		const double smoothing,
		const int NbPart,
		const int nb_thread,
		long *seed);

/**
 * Fonction générant des particules réparties de selon une gaussienne dans une sphère.
 *
 * @param[in] sig Écart type de la gaussienne.
 * @param[in] NbPart Nombre de particule à générer.
 * @param[inout] *seed Graine du générateur.
 * @return Tableau de dimension [NbPart][3] contenant les coordonnées générées.
 */
double** gauss(const double sig, const int NbPart, long *seed);

/**
 * Fonction générant des particules réparties de selon une gaussienne dans une sphère.
 *
 * @param[in] sig Écart type de la gaussienne.
 * @param[in] broke Coupure de la gaussienne : toutes les valeurs au-dessus de broke*sig seront ignorées.
 * @param[in] NbPart Nombre de particule à générer.
 * @param[inout] *seed Graine du générateur.
 * @return Tableau de dimension [NbPart][3] contenant les coordonnées générées.
 */
double** gauss_limit(const double sig, const double broke, const int NbPart, long *seed);

void	 King_gene(const King Amas, const int Nb_part_t1, double *r_grand, double **king_pos, double **king_vit, long *seed);
void	 King_Generate(const King Amas, const int Nb_part_t1, double *r_grand, Particule_d king, long *seed);

void	 Homo_Generate(const double rmax, const double vmax, const double m, const double WVir, const int NbPart, Particule_d res, long *seed);
void	 HomoGauss_Generate(const double rmax, const double sig, const double m, const double WVir, const int NbPart, Particule_d res, long *seed);
void	 HomoGaussLimited_Generate(const double rmax, const double sig, const double broke, const double m, const double WVir, const int NbPart, Particule_d res, long *seed);

void Fuji_Generate(const int Nb_part_t1, const double r_max, const double v_max, const double sig_v, const double rho_0, Particule_d king, double *r_grand, long *seed);

#endif /* end of include guard: GENERATION_H */
