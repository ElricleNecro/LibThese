#include "types.h"

Part  Part_add(Part a, Part b)
{
	b.x  += a.x;
	b.y  += a.y;
	b.z  += a.z;
	b.vx += a.vx;
	b.vy += a.vy;
	b.vz += a.vz;
	b.v  += a.v;
	b.r  += a.r;

	return b;
}

Part* Part1d(const int n)
{
	Part * ptf=NULL;
	if (n >0) {
		ptf = (Part *) calloc(n, sizeof(Part)) ;
	}
	if (ptf==NULL) {
		fprintf(stderr, "erreur allocation Part1d\n");
		exit(EXIT_FAILURE);
	}
	return ptf;
}

void Part1d_libere(Part *ptf)
{
	/* liberation d'un tableau 1D de Parts */
	free(ptf);
	return ;
}

int qsort_partstr(const void *a, const void *b)
{
	const Part *p1 = (const Part*)a,
		   *p2 = (const Part*)b;

	if( p1->r > p2->r )//sqrt(p1->x*p1->x + p1->y*p1->y) > sqrt(p2->x*p2->x + p2->y*p2->y))
		return 1;
	else if( p1->r < p2->r )
		return -1;
	else
		return 0;
}

int qsort_partaxe(const void *a, const void *b)
{
	const Part *p1 = (const Part*)a,
		   *p2 = (const Part*)b;

	if( p1->x > p2->x )
		return 1;
	else if( p1->x < p2->x )
		return -1;
	else
		return 0;
}

int by_id(const void *a, const void *b)
{
	const struct _particule_data_d *p1 = (const struct _particule_data_d*)a,
				       *p2 = (const struct _particule_data_d*)b;
	return p1->Id - p2->Id;
}

void sort_by_id(Particule_d tab, const int N)
{
	qsort(tab, N, sizeof(struct _particule_data_d), by_id);
}

int by_type(const void *a, const void *b)
{
	const struct _particule_data_d *p1 = (const struct _particule_data_d*)a,
				       *p2 = (const struct _particule_data_d*)b;
	if( p1->Type == p2->Type )
		return p1->Id - p2->Id;
	return p1->Type - p2->Type;
}

void sort_by_type(Particule_d tab, const int N)
{
	qsort(tab, N, sizeof(struct _particule_data_d), by_type);
}

Particule_d Concat(const Particule_d a, const int Na, const Particule_d b, const int Nb)
{
	Particule_d new = malloc( sizeof(struct _particule_data_d) * (Na + Nb) );
	if(new == NULL)
	{
		perror("Concat Error:");
		return NULL;
	}

	memcpy(new,      a, Na * sizeof(struct _particule_data_d));
	memcpy(&new[Na], b, Nb * sizeof(struct _particule_data_d));

	return new;
}

void Echange(Particule_d a, Particule_d b)
{
	struct _particule_data_d tmp;

	memcpy(&tmp, a, sizeof(struct _particule_data_d));
	memcpy(a,    b, sizeof(struct _particule_data_d));
	memcpy(b, &tmp, sizeof(struct _particule_data_d));
}


