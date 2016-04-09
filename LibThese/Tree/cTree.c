#ifdef USE_TIMER
#include <time.h>
#endif

#include "tree.h"

int Level_Max = 50;
int NB_bro = 8;
int Zc = 0;
double G = 6.67e-11;

void Tree_SetG(double nG)
{
	G = nG;
}
double Tree_GetG(void)
{
	return G;
}

void Echange(Particule_d a, Particule_d b)
{
	struct _particule_data_d tmp;

	memcpy(&tmp, a, sizeof(struct _particule_data_d));
	memcpy(a,    b, sizeof(struct _particule_data_d));
	memcpy(b, &tmp, sizeof(struct _particule_data_d));
}

TNoeud Create_Tree(Particule_d posvits, const int NbPart, const int NbMin, const struct _particule_data_d Center, const double taille)
{
	TNoeud root = NULL;
	root        = Tree_Init(NbPart, Center.Pos[0], Center.Pos[1], Center.Pos[2], taille);
	if( root == NULL )
		fprintf(stderr, "Erreur avec Tree_Init !!!\n"),exit(EXIT_FAILURE);
	root->first = &posvits[0];

	//fprintf(stderr, "%g %g %g %g\n", Center.Pos[0], Center.Pos[1], Center.Pos[2], taille);

	//qsort(posvits, (size_t)NbPart, sizeof(Part), qsort_partstr);

	Tree_Build2(root, NbPart, NbMin);

	return root;
}

int NotIn(struct _particule_data_d cherch, Particule_d Tab, const int NbVois)
{
	for(int i = 0; i < NbVois; i++)
		if( Tab[i].Id == cherch.Id )
			return 0;
	return 1;
}

void Tree_var(const int LMax)
{
	Level_Max = LMax;

	NB_bro    = 8;
}

TNoeud Tree_Init(int NbPart, double xc, double yc, double zc, double cote)
{
	TNoeud root  = NULL;

	root         = malloc(sizeof(*root));
	if( root == NULL )
	{
		perror("malloc a rencontré un probléme ");
		fprintf(stderr, "\033[31m%s::%s::%d ==> Échec de l'allocation du noeud\033[00m\n",
			__FILE__, __func__, __LINE__
		       );
		return NULL;
	}
	root->N      = NbPart;
	root->level  = 0;
	root->x      = xc;
	root->y      = yc;
	root->z      = zc;
	root->cote   = cote;

	root->first  = NULL;
	root->parent = NULL;
	root->frere  = NULL;
	root->fils   = NULL;

	return root;
}

void Tree_Save(TNoeud root, FILE *fich)
{
//	if( root->frere == NULL )
//	{
		fprintf(fich, "%.16g %.16g %.16g %d %d\n", (root->x - root->cote / 2.0), (root->y + root->cote / 2.0), (root->z + root->cote / 2.0), root->level, root->N);
		fprintf(fich, "%.16g %.16g %.16g %d %d\n", (root->x + root->cote / 2.0), (root->y + root->cote / 2.0), (root->z + root->cote / 2.0), root->level, root->N);
		fprintf(fich, "%.16g %.16g %.16g %d %d\n", (root->x + root->cote / 2.0), (root->y - root->cote / 2.0), (root->z + root->cote / 2.0), root->level, root->N);
		fprintf(fich, "%.16g %.16g %.16g %d %d\n", (root->x - root->cote / 2.0), (root->y - root->cote / 2.0), (root->z + root->cote / 2.0), root->level, root->N);
		fprintf(fich, "%.16g %.16g %.16g %d %d\n", (root->x - root->cote / 2.0), (root->y + root->cote / 2.0), (root->z + root->cote / 2.0), root->level, root->N);
		fprintf(fich, "\n");

		fprintf(fich, "%.16g %.16g %.16g %d %d\n", (root->x - root->cote / 2.0), (root->y + root->cote / 2.0), (root->z - root->cote / 2.0), root->level, root->N);
		fprintf(fich, "%.16g %.16g %.16g %d %d\n", (root->x + root->cote / 2.0), (root->y + root->cote / 2.0), (root->z - root->cote / 2.0), root->level, root->N);
		fprintf(fich, "%.16g %.16g %.16g %d %d\n", (root->x + root->cote / 2.0), (root->y - root->cote / 2.0), (root->z - root->cote / 2.0), root->level, root->N);
		fprintf(fich, "%.16g %.16g %.16g %d %d\n", (root->x - root->cote / 2.0), (root->y - root->cote / 2.0), (root->z - root->cote / 2.0), root->level, root->N);
		fprintf(fich, "%.16g %.16g %.16g %d %d\n", (root->x - root->cote / 2.0), (root->y + root->cote / 2.0), (root->z - root->cote / 2.0), root->level, root->N);
		fprintf(fich, "\n");

		fprintf(fich, "%.16g %.16g %.16g %d %d\n", (root->x - root->cote / 2.0), (root->y - root->cote / 2.0), (root->z - root->cote / 2.0), root->level, root->N);
		fprintf(fich, "%.16g %.16g %.16g %d %d\n", (root->x - root->cote / 2.0), (root->y - root->cote / 2.0), (root->z + root->cote / 2.0), root->level, root->N);
		fprintf(fich, "\n");

		fprintf(fich, "%.16g %.16g %.16g %d %d\n", (root->x + root->cote / 2.0), (root->y - root->cote / 2.0), (root->z - root->cote / 2.0), root->level, root->N);
		fprintf(fich, "%.16g %.16g %.16g %d %d\n", (root->x + root->cote / 2.0), (root->y - root->cote / 2.0), (root->z + root->cote / 2.0), root->level, root->N);
		fprintf(fich, "\n");

		fprintf(fich, "%.16g %.16g %.16g %d %d\n", (root->x + root->cote / 2.0), (root->y + root->cote / 2.0), (root->z - root->cote / 2.0), root->level, root->N);
		fprintf(fich, "%.16g %.16g %.16g %d %d\n", (root->x + root->cote / 2.0), (root->y + root->cote / 2.0), (root->z + root->cote / 2.0), root->level, root->N);
		fprintf(fich, "\n");

		fprintf(fich, "%.16g %.16g %.16g %d %d\n", (root->x - root->cote / 2.0), (root->y + root->cote / 2.0), (root->z - root->cote / 2.0), root->level, root->N);
		fprintf(fich, "%.16g %.16g %.16g %d %d\n", (root->x - root->cote / 2.0), (root->y + root->cote / 2.0), (root->z + root->cote / 2.0), root->level, root->N);
		fprintf(fich, "\n");
		fprintf(fich, "\n");
//	}

//	if( root->level > Level_Max / 3 )
//		fprintf (stderr, "\033[32m|_ %s:: Level = %d ; x in ]%.16g, %.16g] ; y in ]%.16g, %.16g]\033[00m\n",
//				__func__,
//				root->level,
//				root->x - root->cote / 2.0, root->x + root->cote / 2.0,
//				root->y - root->cote / 2.0, root->y + root->cote / 2.0
//			);

	if( root->frere != NULL )
		Tree_Save(root->frere, fich);
	if( root->fils != NULL )
		Tree_Save(root->fils, fich);
}

int Tree_Read(TNoeud root, FILE *fich)
{
	int res = 0, err = 0;
	if( fscanf(fich, "%lf %lf %lf %d %lf %d", &root->x, &root->y, &root->z, &root->level, &root->cote, &res) != 6 )
		return -6;

	if( root->frere != NULL )
	{
		err = Tree_Read(root->frere, fich);
		if( err != 0 )
			return err;
	}
	if( res == 1 )
	{
		err = Tree_Read(root->fils, fich);
		if( err != 0 )
			return err;
	}

	return 0;
}

void Tree_Free(TNoeud root)
{
	if( root->fils != NULL )
		Tree_Free(root->fils);
	if( root->frere != NULL )
		Tree_Free(root->frere);
	free(root), root = NULL;
}

void Tree_Calc(TNoeud t1, const int NbPart)
{
	t1->CM        = 0.0;
	t1->cm.Pos[0] = 0.0;
	t1->cm.Pos[1] = 0.0;
	t1->cm.Pos[2] = 0.0;

	for(int i = 0; i < NbPart; i++)
	{
#ifdef P_DBG_TREECODE_P_CALC
		//for(int j = 0; j<=t1->level; j++) fprintf(stderr, " ");
		fprintf (stderr, "\033[33m|_ %s:: Level = %d ; x in ]%.16g, %.16g] ; y in ]%.16g, %.16g] ; z in ]%.16g, %.16g] :: P = (%.16g, %.16g, %.16g)::%d\033[00m\n",
				__func__,
				t1->level,
				t1->x - t1->cote / 2.0, t1->x + t1->cote / 2.0,
				t1->y - t1->cote / 2.0, t1->y + t1->cote / 2.0,
				t1->z - t1->cote / 2.0, t1->z + t1->cote / 2.0,
				t1->first[i].Pos[0], t1->first[i].Pos[1], t1->first[i].Pos[2], t1->first[i].Id
			);
#endif
		if( (t1->first[i].Pos[0] > t1->x - t1->cote / 2.0 && t1->first[i].Pos[0] <= t1->x + t1->cote / 2.0) &&
		    (t1->first[i].Pos[1] > t1->y - t1->cote / 2.0 && t1->first[i].Pos[1] <= t1->y + t1->cote / 2.0) &&
		    (t1->first[i].Pos[2] > t1->z - t1->cote / 2.0 && t1->first[i].Pos[2] <= t1->z + t1->cote / 2.0)
		  )
		{
			Echange(&t1->first[t1->N], &t1->first[i]);
			t1->CM   += t1->first[t1->N].m;
			t1->cm.Pos[0] += t1->first[t1->N].Pos[0];
			t1->cm.Pos[1] += t1->first[t1->N].Pos[1];
			t1->cm.Pos[2] += t1->first[t1->N].Pos[2];
			t1->N++;
#ifdef P_DBG_TREECODE_P_CALC
			//for(int j = 0; j<=t1->level; j++) fprintf(stderr, " ");
			fprintf(stderr, "\033[36m|_ %s:: Level = %d ==> Prise : %d\033[00m\n", __func__, t1->level, t1->N);
#endif
		}
#ifdef P_DBG_TREECODE_P_CALC
		else
		{
			//for(int j = 0; j<=t1->level; j++) fprintf(stderr, " ");
			fprintf (stderr, "\033[33m|_ %s:: Level = %d ; x in ]%.16g, %.16g] ; y in ]%.16g, %.16g] ; z in ]%.16g, %.16g] :: P = (%.16g, %.16g, %.16g)::%d\033[00m\n",
					__func__,
					t1->level,
					t1->x - t1->cote / 2.0, t1->x + t1->cote / 2.0,
					t1->y - t1->cote / 2.0, t1->y + t1->cote / 2.0,
					t1->z - t1->cote / 2.0, t1->z + t1->cote / 2.0,
					t1->first[i].Pos[0], t1->first[i].Pos[1], t1->first[i].Pos[2], t1->first[i].Id
				);
		}
#endif
	}

	if( t1->N != 0 )
	{
		t1->cm.Pos[0] /= t1->N;
		t1->cm.Pos[1] /= t1->N;
		t1->cm.Pos[2] /= t1->N;
#ifdef TREE_CM_BUILD_DEBUG_
		fprintf(stderr, "\033[35mCM :: (%g, %g, %g) ; %g (N == %d)\033[00m\n", t1->x, t1->y, t1->z, t1->CM, t1->N);
#endif
	}
}

TNoeud tmp_Build2(TNoeud root, int NbPart, int bro)
{
	TNoeud t1  = NULL;

	double xc, yc, zc;

	switch(bro)
	{
		case 1:
			xc = root->x - root->cote/4.0;
			yc = root->y + root->cote/4.0;
			zc = root->z + root->cote/4.0;
			break;
		case 2:
			xc = root->x + root->cote/4.0;
			yc = root->y + root->cote/4.0;
			zc = root->z + root->cote/4.0;
			break;
		case 3:
			xc = root->x + root->cote/4.0;
			yc = root->y - root->cote/4.0;
			zc = root->z + root->cote/4.0;
			break;
		case 4:
			xc = root->x - root->cote/4.0;
			yc = root->y - root->cote/4.0;
			zc = root->z + root->cote/4.0;
			break;
		case 5:
			xc = root->x - root->cote/4.0;
			yc = root->y - root->cote/4.0;
			zc = root->z - root->cote/4.0;
			break;
		case 6:
			xc = root->x + root->cote/4.0;
			yc = root->y - root->cote/4.0;
			zc = root->z - root->cote/4.0;
			break;
		case 7:
			xc = root->x + root->cote/4.0;
			yc = root->y + root->cote/4.0;
			zc = root->z - root->cote/4.0;
			break;
		case 8:
			xc = root->x - root->cote/4.0;
			yc = root->y + root->cote/4.0;
			zc = root->z - root->cote/4.0;
			break;
		default:
			fprintf(stderr, "\033[31m%s::Erreur : %d n'est pas prévu.\033[00m\n", __func__, bro);
			exit(EXIT_FAILURE);
	}

	t1         = Tree_Init( NbPart,
				xc,
				yc,
				zc,
				root->cote / 2.0
			      );
	if( t1 == NULL )
	{
		perror("malloc a rencontré un probléme ");
		fprintf(stderr, "\033[31m%s::%s::%d => Échec de l'allocation du noeud t1 de niveau %d\033[00m\n",
			__FILE__, __func__, __LINE__, root->level + 1);
		return NULL;
	}
	// Question : On garde un indice de la premiére case ou carément l'adresse de
	// la premiére case.
	t1->level  = root->level + 1;
	t1->cote   = root->cote / 2.0; //root->cote / (root->level + 1);
	t1->parent = root;

	return t1;
}

int Tree_Build2(TNoeud root, int NbPart, int NbMin)
{
	if( root->level >= Level_Max )
		return 0;

	int Nb_use = 0,
	    bro    = 0;

	TNoeud t1   = NULL;
	t1          = tmp_Build2(root, 0, bro + 1);
	root->fils  = t1;

	if( Nb_use < NbPart )
	{
		t1->first  = &(root->first[Nb_use]);
		Tree_Calc(t1, NbPart);
	}

#ifdef P_DBG_TREECODE_P_CALC2
	fprintf(stderr, "\033[32m|-%s:: t1->N = %d ; deb = %d ; NbPart = %d, NbMin = %d\033[00m\n", __func__, t1->N, 0, NbPart, NbMin);
#endif

	if( t1->N == 0 )
		t1->first = NULL;

	//fprintf(stderr, "Brother %d : %d Particules.\n", bro, t1->N);
	Nb_use += t1->N;
	bro++;

	while( bro < NB_bro )
	{
//		t1	    = NULL;
//		t1          = tmp_Build2(root, 0, bro + 1);
//		root->frere = t1;
		t1->frere   = tmp_Build2(root, 0, bro + 1);
		t1          = t1->frere;

		if( Nb_use < NbPart )
		{
			t1->first  = &(root->first[Nb_use]);

			Tree_Calc(t1, NbPart - Nb_use);
		}

#ifdef P_DBG_TREECODE_P_CALC2
		fprintf(stderr, "\033[32m|-%s:: t%d->N = %d ; deb = %d ; NbPart = %d, NbMin = %d\033[00m\n", __func__, bro + 1, t1->N, Nb_use, NbPart, NbMin);
#endif

		if( t1->N == 0 )
			t1->first = NULL;

		//fprintf(stderr, "Brother %d : %d Particules.\n", bro, t1->N);

		Nb_use += t1->N;
		bro++;
	}

	if( Nb_use != NbPart )
	{
		fprintf(stderr, "\033[31m%s::Erreur :: Toute les particules n'ont pas été prise au niveau %d (%d au lieu de %d)!!!\033[00m\n", __func__, root->level, Nb_use, NbPart);
		exit(EXIT_FAILURE);
	}

	t1 = root->fils;
	do
	{
		if( t1->N > NbMin )
			Tree_Build2(t1, t1->N, NbMin);
		t1 = t1->frere;
	}
	while(t1 != NULL);

	return 1;
}

#ifdef PERIODIC
/*inline*/ double Tree_Dist(const TNoeud root, const Particule_d part, const double BS)
{
	// Calcul des distances particules--cube :
	double dx = 0.0,
	       dy = 0.0,
	       dz = 0.0,
	       d  = 0.0;

	//Faire par rapport au centre. max d-cote/2, 0
//	d  = part->x - root->x;
//	d  = NEAREST(d, (BS/2.0), BS);
//	dx = fmax( fmin(d, d - root->cote/2.0), 0.0);
	d  = fabs( root->x - part->Pos[0] );
	dx = fmax( 0., fmin( d, BS - d ) - root->cote/2.0 );

//	d  = part->x - root->x;
//	d  = NEAREST(d, (BS/2.0), BS);
//	dy = fmax( fmin(d, d - root->cote/2.0), 0.0);
	d  = fabs( root->y - part->Pos[1] );
	dy = fmax( 0., fmin( d, BS - d ) - root->cote/2.0 );

//	d  = part->x - root->x;
//	d  = NEAREST(d, (BS/2.0), BS);
//	dz = fmax( fmin(d, d - root->cote/2.0), 0.0);
	d  = fabs( root->z - part->Pos[2] );
	dz = fmax( 0., fmin( d, BS - d ) - root->cote/2.0 );

	return sqrt(dx*dx + dy*dy + dz*dz);
}
#else
/*inline*/ double Tree_Dist(const TNoeud root, const Particule_d part)
{
	double dx = 0.0,
	       dy = 0.0,
	       dz = 0.0,
	       d1 = 0.0,
	       d2 = 0.0;

//	d1 =
	d1 = part->Pos[0] - (root->x - root->cote/2.0);
	d2 = part->Pos[0] - (root->x + root->cote/2.0);

	if( d1 > 0.0 && d2 <= 0.0 )
		dx = 0.0;
	else
		dx = fmin(fabs(d1), fabs(d2));

	d1 = part->Pos[1] - (root->y - root->cote/2.0);
	d2 = part->Pos[1] - (root->y + root->cote/2.0);

	if( d1 > 0.0 && d2 <= 0.0 )
		dy = 0.0;
	else
		dy = fmin(fabs(d1), fabs(d2));

	d1 = part->Pos[2] - (root->z - root->cote/2.0);
	d2 = part->Pos[2] - (root->z + root->cote/2.0);

	if( d1 > 0.0 && d2 <= 0.0 )
		dz = 0.0;
	else
		dz = fmin(fabs(d1), fabs(d2));

	return sqrt( dx*dx + dy*dy + dz*dz );
}
#endif

double Tree_ExactPot(const TNoeud root, const Particule_d part, const double soft)
{
	double pot = 0.0;

	for(int i=0; i<root->N; i++)
	{
		if( root->first[i].Id != part->Id )
		{
			pot += -G * root->first[i].m / (
				sqrt( pow(root->first[i].Pos[0] - part->Pos[0], 2.0)
					+ pow(root->first[i].Pos[1] - part->Pos[1], 2.0)
					+ pow(root->first[i].Pos[2] - part->Pos[2], 2.0) )
				       	+ soft);
		}
	}
	return pot;
}

double Tree_ApproxPot(const TNoeud root, const Particule_d part, const double soft)
{
	double x = 0.0,
	       y = 0.0,
	       z = 0.0;
	x = root->cm.Pos[0];
	y = root->cm.Pos[1];
	z = root->cm.Pos[2];

	if( root->N != 0 )
		return -G * root->CM /
			(sqrt( pow(x - part->Pos[0], 2.0)
			       + pow(y - part->Pos[1], 2.0)
			       + pow(z - part->Pos[2], 2.0) ) + soft);
	else
		return 0.0;
}

#ifdef PERIODIC
#	ifdef __bool_true_false_are_defined
/*inline*/ bool Tree_Accept(const TNoeud root, const Particule_d part, const double accept, const double BS)
#	else
/*inline*/ int Tree_Accept(const TNoeud root, const Particule_d part, const double accept, const double BS)
#	endif
#else
#	ifdef __bool_true_false_are_defined
/*inline*/ bool Tree_Accept(const TNoeud root, const Particule_d part, const double accept)
#	else
/*inline*/ int Tree_Accept(const TNoeud root, const Particule_d part, const double accept)
#	endif
#endif
{
#ifdef PERIODIC
	if( Tree_Dist(root, part, BS) == 0.0)
#else
	if( Tree_Dist(root, part) == 0.0)
#endif
#ifdef __bool_true_false_are_defined
		return true;
#else
		return 1;
#endif
#ifdef PERIODIC
	return ( root->cote / Tree_Dist(root, part, BS) ) > accept;
#else
	return ( root->cote / Tree_Dist(root, part) ) > accept;
#endif
}

#ifdef PERIODIC
double Tree_CalcPot(TNoeud root, const Particule_d part, const double accept, const double soft, const double BS)
#else
double Tree_CalcPot(TNoeud root, const Particule_d part, const double accept, const double soft)
#endif
{
	double pot = 0.0;

#ifdef PERIODIC
	if( Tree_Accept(root, part, accept, BS) //( ( root->cote / Tree_Dist(root, part) ) > accept )
		&& root->fils != NULL
	  )
#else
	if( Tree_Accept(root, part, accept) //( ( root->cote / Tree_Dist(root, part) ) > accept )
		&& root->fils != NULL
	  )
#endif
	{
		TNoeud t1 = root->fils;
		do
		{
			//Tree_Voisin(t1, Tab, NbVois, part);
#ifdef PERIODIC
			pot += Tree_CalcPot(t1, part, accept, soft, BS);
#else
			pot += Tree_CalcPot(t1, part, accept, soft);
#endif
			t1   = t1->frere;
		}
		while(t1 != NULL);
		return pot;
	}

	if( root->fils == NULL )
		return pot + Tree_ExactPot(root, part, soft);
	else
	{
#ifdef TREE_CALCPOT_DEBUG_
	fprintf(stderr, "\033[31mUtilisation de ApproxPot :: %d (val : %g ; %g) (critere : %g, soft : %g)\033[00m\n",
#ifdef PERIODIC
			Tree_Accept(root, part, accept, BS),
#else
			Tree_Accept(root, part, accept),
#endif
			root->cote,
#ifdef PERIODIC
			Tree_Dist(root, part, BS),
#else
			Tree_Dist(root, part),
#endif
			accept,
			soft);
#endif
		return pot + Tree_ApproxPot(root, part, soft);
	}
}

