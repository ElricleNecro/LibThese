#include "gadget.h"

float* float1d(int n)
{
	float * ptf=NULL;
	if (n >0) {
		ptf = (float *) calloc(n, sizeof(float)) ;
	}
	if (ptf==NULL) {
		fprintf(stderr, "erreur allocation float1d\n");
		exit(EXIT_FAILURE);
	}
	return ptf;
}

void float1d_libere(float *ptf)
{
	/* liberation d'un tableau 1D de floats */
	free(ptf);
	return ;
}

#if 0
Particule Gadget_Read(const char *fname, Header *header, int files, bool b_potential, bool b_acceleration, bool b_rate_entropy, bool b_timestep)
{
	FILE *fd;
	char buf[200];
	int i, k, dummy, ntot_withmasses;
	int n, pc, pc_new, pc_sph;
	int NumPart = 0;
	Particule P = NULL;

#define SKIP fread(&dummy, sizeof(dummy), 1, fd);

	for(i = 0, pc = 0; i < files; i++, pc = pc_new)
	{
		if(files > 1)
			sprintf(buf, "%s.%d", fname, i);
		else
			sprintf(buf, "%s", fname);

		if(!(fd = fopen(buf, "r")))
		{
			perror("Can't open file:");
			printf("can't open file `%s`\n", buf);
			exit(EXIT_FAILURE);
		}

		printf("reading `%s' ...\n", buf);
		fflush(stdout);

		fread(&dummy, sizeof(dummy), 1, fd);
		fread(header, sizeof(Header), 1, fd);
		fread(&dummy, sizeof(dummy), 1, fd);

		if(files == 1)
		{
			for(k = 0, NumPart = 0, ntot_withmasses = 0; k < 6; k++)
				NumPart += header->npart[k];
		}
		else
		{
			for(k = 0, NumPart = 0, ntot_withmasses = 0; k < 6; k++)
				NumPart += header->npartTotal[k];
		}

		for(k = 0, ntot_withmasses = 0; k < 6; k++)
		{
			if(header->mass[k] == 0)
				ntot_withmasses += header->npart[k];
		}

		if(i == 0)
		{
			printf("allocating memory for %d particules...\n", NumPart);
			if( (P = malloc(NumPart * sizeof(struct _particule_data))) == NULL )
			{
				perror("Allocate memory failed:");
				return NULL;
			}
			printf("allocating memory...done\n");
		}

		SKIP;
		for(k = 0, pc_new = pc; k < 6; k++)
		{
			for(n = 0; n < header->npart[k]; n++)
			{
				fread(&P[pc_new].Pos[0], sizeof(float), 3, fd);
				pc_new++;
			}
		}
		SKIP;

		SKIP;
		for(k = 0, pc_new = pc; k < 6; k++)
		{
			for(n = 0; n < header->npart[k]; n++)
			{
				fread(&P[pc_new].Vit[0], sizeof(float), 3, fd);
				pc_new++;
			}
		}
		SKIP;


		SKIP;
		for(k = 0, pc_new = pc; k < 6; k++)
		{
			for(n = 0; n < header->npart[k]; n++)
			{
				/*fread(&Id[pc_new], sizeof(int), 1, fd);*/
				fread(&P[pc_new].Id, sizeof(int), 1, fd);
				pc_new++;
			}
		}
		SKIP;


		if(ntot_withmasses > 0)
			SKIP;
		for(k = 0, pc_new = pc; k < 6; k++)
		{
			for(n = 0; n < header->npart[k]; n++)
			{
				P[pc_new].Type = k;

				if(header->mass[k] == 0)
					fread(&P[pc_new].m, sizeof(float), 1, fd);
				else
					P[pc_new].m = header->mass[k];
				pc_new++;
			}
		}
		if(ntot_withmasses > 0)
			SKIP;


		if(header->npart[0] > 0)
		{
			SKIP;
			for(n = 0, pc_sph = pc; n < header->npart[0]; n++)
			{
				fread(&P[pc_sph].U, sizeof(float), 1, fd);
				pc_sph++;
			}
			SKIP;

			SKIP;
			for(n = 0, pc_sph = pc; n < header->npart[0]; n++)
			{
				fread(&P[pc_sph].Rho, sizeof(float), 1, fd);
				pc_sph++;
			}
			SKIP;

			if(header->flag_cooling)
			{
				SKIP;
				for(n = 0, pc_sph = pc; n < header->npart[0]; n++)
				{
					fread(&P[pc_sph].Ne, sizeof(float), 1, fd);
					pc_sph++;
				}
				SKIP;
			}
			else
				for(n = 0, pc_sph = pc; n < header->npart[0]; n++)
				{
					P[pc_sph].Ne = 1.0;
					pc_sph++;
				}
		}

		if( b_potential )
		{
			SKIP;
			for(k = 0, pc_new = pc; k < 6; k++)
			{
				for(n = 0; n < header->npart[k]; n++)
					fread(&P[pc_new].Pot, sizeof(float), 1, fd);
			}
			SKIP;
		}

		if( b_acceleration )
		{
			SKIP;
			for(k = 0, pc_new = pc; k < 6; k++)
			{
				for(n = 0; n < header->npart[k]; n++)
					fread(&P[pc_new].Acc[0], sizeof(float), 3, fd);
			}
			SKIP;
		}

		if( b_rate_entropy && header->npart[0] > 0 )
		{
			SKIP;
			for(n = 0, pc_sph = pc; n < header->npart[0]; n++)
			{
				fread(&P[pc_sph].dAdt, sizeof(float), 1, fd);
				pc_sph++;
			}
			SKIP;
		}

		if( b_timestep )
		{
			SKIP;
			for(k = 0, pc_new = pc; k < 6; k++)
			{
				for(n = 0; n < header->npart[k]; n++)
				{
					fread(&P[pc_new].ts, sizeof(float), 1, fd);
				}
			}
			SKIP;
		}

		fclose(fd);
	}

	return P;
}
#undef SKIP

bool Gadget_Write(const char *name, const Header header, const Particule part)
{
	FILE *fd = NULL;
	int blksize, NbPart = 0, ntot_withmasses = 0;
	float to_write;

#define SKIP  {fwrite(&blksize,sizeof(int),1,fd);}

	//fprintf(stderr, "File name : %s\n", name);

	if(!(fd = fopen(name, "w")))
	{
		perror("Can't open file for writing snapshot: ");
		return false;
	}

	//printf("\033[36mHeader du fichier Gadget (format 1) :\033[00m\n");
	//printf("\033[34m\tNombre de fichier par snapshot : %d\n", header.num_files);
	//printf("\tMasse et nombre d'éléments des catégories d'objet :\n");
	//for(int i = 0; i < 6; i++)
		//printf("\t\t%s : Masse %g, et %d élément%c (total : %d)\n", (i == 0)?"Gaz":( (i == 1)?"Halo":( (i == 2)?"Disk":( (i==3)?"Bulge":( (i==4)?"Stars":"Bndry" )))), header.mass[i], header.npart[i], (header.npart[i] > 1)?'s':' ', header.npartTotal[i]);
	//puts("\033[00m");
	//printf("\033[31m\tTaille de la boîte : %g\033[00m\n", header.BoxSize);

	blksize = sizeof(header);
	//fprintf(stderr, "Writing header (%d)...", blksize);
	SKIP;
	fwrite(&header, sizeof(header), 1, fd);
	SKIP;
	//fprintf(stderr, " done\n");

	blksize = 0;
	for (int n = 0; n < 6; n++)
	{
		NbPart          += header.npart[n];
		blksize         += header.npart[n];
		if( header.mass[n] == 0 )
			ntot_withmasses += header.npart[n];
	}
	blksize *= 3 * sizeof(float);

	//fprintf(stderr, "Writing positions (%d)...", blksize);
	SKIP;
	for(int i=0; i<NbPart; i++)
		for(int j=0; j<3; j++)
		{
			to_write = (float)part[i].Pos[j];
			fwrite(&to_write, sizeof(float), 1, fd);
		}
	SKIP;
	//fprintf(stderr, " done\n");

	/*blksize = 0;*/
	/*for (int n = 0; n < 6; n++)*/
	/*{*/
		/*blksize += header.npart[n];*/
	/*}*/
	/*blksize *= 3 * sizeof(float);*/

	//fprintf(stderr, "Writing velocities (%d)...", blksize);
	SKIP;
	for(int i=0; i<NbPart; i++)
		for(int j=0; j<3; j++)
		{
			to_write = (float)part[i].Vit[j];
			fwrite(&to_write, sizeof(float), 1, fd);
		}
	SKIP;
	//fprintf(stderr, " done\n");

	blksize = NbPart * sizeof(unsigned int);
	//fprintf(stderr, "Writing identities (%d)...", blksize);
	SKIP;
	for(int i=0; i<NbPart; i++)
		fwrite(&part[i].Id, sizeof(unsigned int), 1, fd);
	SKIP;
	//fprintf(stderr, " done\n");

	blksize = ntot_withmasses*sizeof(float);
	if( ntot_withmasses > 0 )
		SKIP;
	for(int i = 0; i < 6; i++)
	{
		if( header.mass[i] == 0. && header.npart[i] != 0 )
		{
			for(int i=0; i<header.npart[i]; i++)
			{
				to_write = (float)part[i].m;
				fwrite(&to_write, sizeof(float), 1, fd);
			}
		}
	}
	if( ntot_withmasses > 0 )
		SKIP;

	return true;
}

bool  write_gadget_file( const char *fname,
			 const Particule part1, const double mass_t1, const int Nb_part_t1, const int index_t1,
			 const Particule part2, const double mass_t2, const int Nb_part_t2, const int index_t2,
			 const double BoxSize,
			 const double LongFact,
			 const double VitFact)
{
	int blksize;

	FILE *fd = NULL;
	Header header;
	float  *inter_t1 = NULL,
	       *inter_t2 = NULL;

	/* fill file header */
	for(int n = 0; n < 6; n++)
	{
		header.npart[n] = 0;
		header.npartTotal[n] = (unsigned int) 0;
		header.npartTotalHighWord[n] = (unsigned int) 0; //(ntot_type_all[n] >> 32);
		header.mass[n] = 0.0;
	}

	header.npart[index_t1] += Nb_part_t1;
	header.npartTotal[index_t1] += Nb_part_t1;
	header.npart[index_t2] += Nb_part_t2;
	header.npartTotal[index_t2] += Nb_part_t2;
//	header.npartTotalHighWord[index_t1] = (unsigned int) (header.npartTotal[index_t1] >> 32);
//	header.npartTotalHighWord[index_t2] = (unsigned int) (header.npartTotal[index_t2] >> 32);

	header.mass[index_t1] += mass_t1;
	if( Nb_part_t2 != 0 )
		header.mass[index_t2] += mass_t2;

	header.time = 0.0;

	header.redshift = 0;

	header.flag_sfr = 0;
	header.flag_feedback = 0;
	header.flag_cooling = 0;
	header.flag_stellarage = 0;
	header.flag_metals = 0;

	header.num_files = 1;
	header.BoxSize = BoxSize / LongFact; // / 3.086e16;
	header.Omega0 = 0.0;
	header.OmegaLambda = 0.0;
	header.HubbleParam = 0.0;

	printf("\033[36mHeader du fichier Gadget (format 1) :\033[00m\n");
	printf("\033[34m\tNombre de fichier par snapshot : %d\n", header.num_files);
	printf("\tMasse et nombre d'éléments des catégories d'objet :\n");
	for(int i = 0; i < 6; i++)
		printf("\t\t%s : Masse %g, et %d élément%c (total : %d)\n", (i == 0)?"Gaz":( (i == 1)?"Halo":( (i == 2)?"Disk":( (i==3)?"Bulge":( (i==4)?"Stars":"Bndry" )))), header.mass[i], header.npart[i], (header.npart[i] > 1)?'s':' ', header.npartTotal[i]);
	puts("\033[00m");
	printf("\033[31m\tTaille de la boîte : %g\033[00m\n", header.BoxSize);


	/* open file and write header */

	if(!(fd = fopen(fname, "w")))
	{
		fprintf(stderr, "can't open file `%s' for writing snapshot.\n", fname);
		return false;
	}
/*
	if(All.SnapFormat == 2)
	{
		blksize = sizeof(int) + 4 * sizeof(char);
		SKIP;
		my_fwrite("HEAD", sizeof(char), 4, fd);
		nextblock = sizeof(header) + 2 * sizeof(int);
		my_fwrite(&nextblock, sizeof(int), 1, fd);
		SKIP;
	}
*/
	blksize = sizeof(header);
	SKIP;
	fwrite(&header, sizeof(header), 1, fd);
	SKIP;

/*	if(All.SnapFormat == 2)
	{
		blksize = sizeof(int) + 4 * sizeof(char);
		SKIP;
		my_fwrite(Tab_IO_Labels[blocknr], sizeof(char), 4, fd);
		nextblock = npart * bytes_per_blockelement + 2 * sizeof(int);
		my_fwrite(&nextblock, sizeof(int), 1, fd);
		SKIP;
	}
*/

	// ************************
	// Écriture des positions :
	// ************************
//	blksize = 3 * (Nb_part_t1 + Nb_part_t2) * sizeof(float); //bytes_per_blockelement;
	blksize = 0;
	for (int n = 0; n < 6; n++)
	{
		blksize += header.npart[n];
	}
	blksize *= 3 * sizeof(float);
	SKIP;

	float *inter = NULL;
	if( (inter = malloc(blksize) ) == NULL )
		fprintf(stderr, "Heing !!!\n"),exit(EXIT_FAILURE);
	int k = 0;
	for (int i = 0; i < Nb_part_t1; i++)
	{
		for (int j = 0; j < 3; j++)
		{
			inter[k] = part1[i].Pos[j] / LongFact; // / 3.086e16;
			k++;
		}
	}
	for (int i = 0; i < Nb_part_t2; i++)
	{
		for (int j = 0; j < 3; j++)
		{
			inter[k] = part2[i].Pos[j] / LongFact; // / 3.086e16;
			k++;
		}
	}
	fwrite(inter, sizeof(float), (size_t)(blksize/sizeof(float)), fd);
/*
	inter_t1 = float1d(3 * Nb_part_t1 + 3); //(float*)calloc(3 * Nb_part_t1 + 3, sizeof(float));

	int k = 0;
	for (int i = 0; i < Nb_part_t1; i++)
	{
		for (int j = 0; j < 3; j++)
		{
			inter_t1[k] = part_t1[i][j] / 3.086e16;
			k++;
		}
	}
	fwrite(inter_t1, sizeof(float), (size_t)(3*Nb_part_t1), fd);

	inter_t2 =  float1d(3 * Nb_part_t2 + 3); //(float*)calloc(3 * Nb_part_t2 + 3, sizeof(float));
	k = 0;
	for (int i = 0; i < Nb_part_t2; i++)
	{
		for (int j = 0; j < 3; j++)
		{
			inter_t2[k] = part_t2[i][j] / 3.086e16;
			k++;
		}
	}
	fwrite(inter_t2, sizeof(float), (size_t)(3*Nb_part_t2), fd);
*/	SKIP;

	// ***********************
	// Écriture des vitesses :
	// ***********************
	//blksize = 3 * (Nb_part_t1 + Nb_part_t2) * sizeof(float); //bytes_per_blockelement;
	blksize = 0;
	for (int n = 0; n < 6; n++)
	{
		blksize += header.npart[n];
	}
	blksize *= 3 * sizeof(float);
	SKIP;

	k = 0;
	for (int i = 0; i < Nb_part_t1; i++)
	{
		for (int j = 0; j < 3; j++)
		{
			inter[k] = part1[i].Vit[j] / VitFact; //;
			k++;
		}
	}
	for (int i = 0; i < Nb_part_t2; i++)
	{
		for (int j = 0; j < 3; j++)
		{
			inter[k] = part2[i].Vit[j] / VitFact; //;
			k++;
		}
	}
	fwrite(inter, sizeof(float), (size_t)(blksize/sizeof(float)), fd);
/*
	k = 0;
	for (int i = 0; i < Nb_part_t1; i++)
	{
		for (int j = 0; j < 3; j++)
		{
			inter_t1[k] = vit_t1[i][j];
			k++;
		}
	}
	fwrite(inter_t1, sizeof(float), (size_t)(3*Nb_part_t1), fd);

	k = 0;
	for (int i = 0; i < Nb_part_t2; i++)
	{
		for (int j = 0; j < 3; j++)
		{
			inter_t2[k] = vit_t2[i][j];
			k++;
		}
	}
	fwrite(inter_t2, sizeof(float), (size_t)(3*Nb_part_t2), fd);
*/	SKIP;

	// ****************
	// Identificateur :
	// ****************
	blksize = (Nb_part_t1 + Nb_part_t2) * sizeof(unsigned int); //bytes_per_blockelement;
	SKIP;

	unsigned int *int_tmp = NULL;
	int_tmp = (unsigned int*)calloc(Nb_part_t2 + Nb_part_t1, sizeof(unsigned int));
	for (int i = 0; i < Nb_part_t2 + Nb_part_t1; i++)
	{
		int_tmp[i] = (unsigned int)(i+1);
	}
	fwrite(int_tmp, sizeof(unsigned int), (size_t)((Nb_part_t1 + Nb_part_t2)), fd);

	SKIP;

	free(inter);
	free(int_tmp);
	float1d_libere(inter_t1);
	float1d_libere(inter_t2);
	fclose(fd);

	return true;
}

char *remove_ext(const char* mystr)
{
	char *retstr;
	char *lastdot;
	if (mystr == NULL)
		return NULL;
	if ((retstr = (char*)malloc (strlen (mystr) + 1)) == NULL)
		return NULL;
	strcpy (retstr, mystr);
	lastdot = strrchr (retstr, '.');
	if (lastdot != NULL)
		*lastdot = '\0';
	return retstr;
}

bool write_gadget_conf( const char  *filename,
			const char  *ci_file,
			const double Tmax,
			const int    periodic,
			const double BS,
			const double LongConv,
			const double VitConv,
			const double MConv,
			const double Soft)
{
	FILE *fich = NULL;
	char *out_file = remove_ext(ci_file);

	if( (fich = fopen(filename, "w")) == NULL )
	{
		fprintf(stderr, "Impossible d'ouvrir le fichier %s\n", filename);
		return false;
	}

	fprintf(fich, "%%  Relevant files\n");
	fprintf(fich, "InitCondFile              %s\n", ci_file);
	fprintf(fich, "OutputDir                 res\n");
	fprintf(fich, "EnergyFile                energy.txt\n");
	fprintf(fich, "InfoFile                  info.txt\n");
	fprintf(fich, "TimingsFile               timings.txt\n");
	fprintf(fich, "CpuFile                   cpu.txt\n");
	fprintf(fich, "RestartFile               restart\n");
	fprintf(fich, "SnapshotFileBase          %s\n", out_file);
	fprintf(fich, "OutputListFilename        output_king.txt\n");
	fprintf(fich, "NumFilesPerSnapshot       1\n");
	fprintf(fich, "NumFilesWrittenInParallel 1\n");
	fprintf(fich, "ICFormat                  1\n");
	fprintf(fich, "SnapFormat                1\n");
	fprintf(fich, "\n");
	fprintf(fich, "%% CPU time -limit\n");
	fprintf(fich, "TimeLimitCPU              7200000\n");
	fprintf(fich, "ResubmitOn                0\n");
	fprintf(fich, "ResubmitCommand           my-scriptfile\n");
	fprintf(fich, "CpuTimeBetRestartFile     7200000.0    ; here in seconds\n");
	fprintf(fich, "\n");
	fprintf(fich, "%% Code options\n");
	fprintf(fich, "ComovingIntegrationOn     0\n");
	fprintf(fich, "\n");
	fprintf(fich, "TypeOfTimestepCriterion   0\n");
	fprintf(fich, "OutputListOn              0\n");
	fprintf(fich, "PeriodicBoundariesOn      %d\n", periodic);
	fprintf(fich, "\n");
	fprintf(fich, "%%  Caracteristics of run\n");
	fprintf(fich, "TimeBegin                 0.0\n");
	fprintf(fich, "TimeMax                   %g\n", Tmax);
	fprintf(fich, "\n");
	fprintf(fich, "Omega0                    0.0\n");
	fprintf(fich, "OmegaLambda               0.0\n");
	fprintf(fich, "OmegaBaryon               0.0\n");
	fprintf(fich, "HubbleParam               0.7\n");
	fprintf(fich, "BoxSize                   %g\n", BS / LongConv);
	fprintf(fich, "\n");
	fprintf(fich, "%% Output frequency\n");
	fprintf(fich, "TimeBetSnapshot           0.1\n");
	fprintf(fich, "TimeOfFirstSnapshot       0.001\n");
	fprintf(fich, "\n");
	fprintf(fich, "TimeBetStatistics         0.05\n");
	fprintf(fich, "\n");
	fprintf(fich, "%% Accuracy of time integration\n");
	fprintf(fich, "ErrTolIntAccuracy         0.025\n");
	fprintf(fich, "\n");
	fprintf(fich, "MaxRMSDisplacementFac     0.2\n");
	fprintf(fich, "\n");
	fprintf(fich, "CourantFac                0.15\n");
	fprintf(fich, "\n");
	fprintf(fich, "MaxSizeTimestep           1.0e-1\n");
	fprintf(fich, "MinSizeTimestep           1.0e-4\n");
	fprintf(fich, "\n");
	fprintf(fich, "%% Tree algorithm, force accuracy, domain update frequency\n");
	fprintf(fich, "ErrTolTheta               0.5\n");
	fprintf(fich, "TypeOfOpeningCriterion    1\n");
	fprintf(fich, "ErrTolForceAcc            0.005\n");
	fprintf(fich, "\n");
	fprintf(fich, "TreeDomainUpdateFrequency 0.1\n");
	fprintf(fich, "\n");
	fprintf(fich, "%%  Further parameters of SPH\n");
	fprintf(fich, "DesNumNgb                 0\n");
	fprintf(fich, "MaxNumNgbDeviation        0\n");
	fprintf(fich, "ArtBulkViscConst          0.0\n");
	fprintf(fich, "InitGasTemp               0\n");
	fprintf(fich, "MinGasTemp                0\n");
	fprintf(fich, "\n");
	fprintf(fich, "%% Memory allocation\n");
	fprintf(fich, "PartAllocFactor           30.0\n");
	fprintf(fich, "TreeAllocFactor           5.0\n");
	fprintf(fich, "BufferSize                30\n");
	fprintf(fich, "\n");
	fprintf(fich, "%% System of units\n");
	fprintf(fich, "UnitLength_in_cm          %g\n", LongConv*1e2);
	fprintf(fich, "UnitMass_in_g             %g\n", MConv*1e3);
	fprintf(fich, "UnitVelocity_in_cm_per_s  %g\n", VitConv*1e2);
	fprintf(fich, "GravityConstantInternal   0\n");
	fprintf(fich, "\n");
	fprintf(fich, "%% Softening lengths\n");
	fprintf(fich, "MinGasHsmlFractional      0.25\n");
	fprintf(fich, "\n");
	fprintf(fich, "SofteningGas              %g\n", Soft);
	fprintf(fich, "SofteningHalo             %g\n", Soft);
	fprintf(fich, "SofteningDisk             %g\n", Soft);
	fprintf(fich, "SofteningBulge            %g\n", Soft);
	fprintf(fich, "SofteningStars            %g\n", Soft);
	fprintf(fich, "SofteningBndry            %g\n", Soft);
	fprintf(fich, "\n");
	fprintf(fich, "SofteningGasMaxPhys       %g\n", Soft);
	fprintf(fich, "SofteningHaloMaxPhys      %g\n", Soft);
	fprintf(fich, "SofteningDiskMaxPhys      %g\n", Soft);
	fprintf(fich, "SofteningBulgeMaxPhys     %g\n", Soft);
	fprintf(fich, "SofteningStarsMaxPhys     %g\n", Soft);
	fprintf(fich, "SofteningBndryMaxPhys     %g\n", Soft);
	fprintf(fich, "\n");
	fprintf(fich, "%% vim: ft=gadget\n");

	free(out_file);
	return true;
}

//int  write_gadget_file( const char *fname,
//			const double** part_t1, const double** vit_t1, const double mass_t1, const int Nb_part_t1, const int index_t1,
//			const double** part_t2, const double** vit_t2, const double mass_t2, const int Nb_part_t2, const int index_t2,
//			const double BoxSize,
//			const double LongFact,
//			const double VitFact)
//{
//	int blksize;
//
//	FILE *fd = NULL;
//	Header header;
//	float  *inter_t1 = NULL,
//	       *inter_t2 = NULL;
//
//#define SKIP  {fwrite(&blksize,sizeof(int),1,fd);}
//
//	/* fill file header */
//	for(int n = 0; n < 6; n++)
//	{
//		header.npart[n] = 0;
//		header.npartTotal[n] = (unsigned int) 0;
//		header.npartTotalHighWord[n] = (unsigned int) 0; //(ntot_type_all[n] >> 32);
//		header.mass[n] = 0.0;
//	}
//
//	header.npart[index_t1] += Nb_part_t1;
//	header.npartTotal[index_t1] += Nb_part_t1;
//	header.npart[index_t2] += Nb_part_t2;
//	header.npartTotal[index_t2] += Nb_part_t2;
////	header.npartTotalHighWord[index_t1] = (unsigned int) (header.npartTotal[index_t1] >> 32);
////	header.npartTotalHighWord[index_t2] = (unsigned int) (header.npartTotal[index_t2] >> 32);
//
//	header.mass[index_t1] += mass_t1;
//	if( Nb_part_t2 != 0 )
//		header.mass[index_t2] += mass_t2;
//
//	header.time = 0.0;
//
//	header.redshift = 0;
//
//	header.flag_sfr = 0;
//	header.flag_feedback = 0;
//	header.flag_cooling = 0;
//	header.flag_stellarage = 0;
//	header.flag_metals = 0;
//
//	header.num_files = 1;
//	header.BoxSize = BoxSize / LongFact; // / 3.086e16;
//	header.Omega0 = 0.0;
//	header.OmegaLambda = 0.0;
//	header.HubbleParam = 0.0;
//
//	printf("\033[36mHeader du fichier Gadget (format 1) :\033[00m\n");
//	printf("\033[34m\tNombre de fichier par snapshot : %d\n", header.num_files);
//	printf("\tMasse et nombre d'éléments des catégories d'objet :\n");
//	for(int i = 0; i < 6; i++)
//		printf("\t\t%s : Masse %g, et %d élément%c (total : %d)\n", (i == 0)?"Gaz":( (i == 1)?"Halo":( (i == 2)?"Disk":( (i==3)?"Bulge":( (i==4)?"Stars":"Bndry" )))), header.mass[i], header.npart[i], (header.npart[i] > 1)?'s':' ', header.npartTotal[i]);
//	puts("\033[00m");
//	printf("\033[31m\tTaille de la boîte : %g\033[00m\n", header.BoxSize);
//
//
//	/* open file and write header */
//
//	if(!(fd = fopen(fname, "w")))
//	{
//		fprintf(stderr, "can't open file `%s' for writing snapshot.\n", fname);
//		return -1;
//	}
///*
//	if(All.SnapFormat == 2)
//	{
//		blksize = sizeof(int) + 4 * sizeof(char);
//		SKIP;
//		my_fwrite("HEAD", sizeof(char), 4, fd);
//		nextblock = sizeof(header) + 2 * sizeof(int);
//		my_fwrite(&nextblock, sizeof(int), 1, fd);
//		SKIP;
//	}
//*/
//	blksize = sizeof(header);
//	SKIP;
//	fwrite(&header, sizeof(header), 1, fd);
//	SKIP;
//
///*	if(All.SnapFormat == 2)
//	{
//		blksize = sizeof(int) + 4 * sizeof(char);
//		SKIP;
//		my_fwrite(Tab_IO_Labels[blocknr], sizeof(char), 4, fd);
//		nextblock = npart * bytes_per_blockelement + 2 * sizeof(int);
//		my_fwrite(&nextblock, sizeof(int), 1, fd);
//		SKIP;
//	}
//*/
//
//	// ************************
//	// Écriture des positions :
//	// ************************
////	blksize = 3 * (Nb_part_t1 + Nb_part_t2) * sizeof(float); //bytes_per_blockelement;
//	blksize = 0;
//	for (int n = 0; n < 6; n++)
//	{
//		blksize += header.npart[n];
//	}
//	blksize *= 3 * sizeof(float);
//	SKIP;
//
//	float *inter = NULL;
//	if( (inter = malloc(blksize) ) == NULL )
//		fprintf(stderr, "Heing !!!\n"),exit(EXIT_FAILURE);
//	int k = 0;
//	for (int i = 0; i < Nb_part_t1; i++)
//	{
//		for (int j = 0; j < 3; j++)
//		{
//			inter[k] = part_t1[i][j] / LongFact; // / 3.086e16;
//			k++;
//		}
//	}
//	for (int i = 0; i < Nb_part_t2; i++)
//	{
//		for (int j = 0; j < 3; j++)
//		{
//			inter[k] = part_t2[i][j] / LongFact; // / 3.086e16;
//			k++;
//		}
//	}
//	fwrite(inter, sizeof(float), (size_t)(blksize/sizeof(float)), fd);
///*
//	inter_t1 = float1d(3 * Nb_part_t1 + 3); //(float*)calloc(3 * Nb_part_t1 + 3, sizeof(float));
//
//	int k = 0;
//	for (int i = 0; i < Nb_part_t1; i++)
//	{
//		for (int j = 0; j < 3; j++)
//		{
//			inter_t1[k] = part_t1[i][j] / 3.086e16;
//			k++;
//		}
//	}
//	fwrite(inter_t1, sizeof(float), (size_t)(3*Nb_part_t1), fd);
//
//	inter_t2 =  float1d(3 * Nb_part_t2 + 3); //(float*)calloc(3 * Nb_part_t2 + 3, sizeof(float));
//	k = 0;
//	for (int i = 0; i < Nb_part_t2; i++)
//	{
//		for (int j = 0; j < 3; j++)
//		{
//			inter_t2[k] = part_t2[i][j] / 3.086e16;
//			k++;
//		}
//	}
//	fwrite(inter_t2, sizeof(float), (size_t)(3*Nb_part_t2), fd);
//*/	SKIP;
//
//	// ***********************
//	// Écriture des vitesses :
//	// ***********************
//	//blksize = 3 * (Nb_part_t1 + Nb_part_t2) * sizeof(float); //bytes_per_blockelement;
//	blksize = 0;
//	for (int n = 0; n < 6; n++)
//	{
//		blksize += header.npart[n];
//	}
//	blksize *= 3 * sizeof(float);
//	SKIP;
//
//	k = 0;
//	for (int i = 0; i < Nb_part_t1; i++)
//	{
//		for (int j = 0; j < 3; j++)
//		{
//			inter[k] = vit_t1[i][j] / VitFact; //;
//			k++;
//		}
//	}
//	for (int i = 0; i < Nb_part_t2; i++)
//	{
//		for (int j = 0; j < 3; j++)
//		{
//			inter[k] = vit_t2[i][j] / VitFact; //;
//			k++;
//		}
//	}
//	fwrite(inter, sizeof(float), (size_t)(blksize/sizeof(float)), fd);
///*
//	k = 0;
//	for (int i = 0; i < Nb_part_t1; i++)
//	{
//		for (int j = 0; j < 3; j++)
//		{
//			inter_t1[k] = vit_t1[i][j];
//			k++;
//		}
//	}
//	fwrite(inter_t1, sizeof(float), (size_t)(3*Nb_part_t1), fd);
//
//	k = 0;
//	for (int i = 0; i < Nb_part_t2; i++)
//	{
//		for (int j = 0; j < 3; j++)
//		{
//			inter_t2[k] = vit_t2[i][j];
//			k++;
//		}
//	}
//	fwrite(inter_t2, sizeof(float), (size_t)(3*Nb_part_t2), fd);
//*/	SKIP;
//
//	// ****************
//	// Identificateur :
//	// ****************
//	blksize = (Nb_part_t1 + Nb_part_t2) * sizeof(unsigned int); //bytes_per_blockelement;
//	SKIP;
//
//	unsigned int *int_tmp = NULL;
//	int_tmp = (unsigned int*)calloc(Nb_part_t2 + Nb_part_t1, sizeof(unsigned int));
//	for (int i = 0; i < Nb_part_t2 + Nb_part_t1; i++)
//	{
//		int_tmp[i] = (unsigned int)(i+1);
//	}
//	fwrite(int_tmp, sizeof(unsigned int), (size_t)((Nb_part_t1 + Nb_part_t2)), fd);
//
//	SKIP;
//
//	free(int_tmp);
//	float1d_libere(inter_t1);
//	float1d_libere(inter_t2);
//	fclose(fd);
//
//	return 0;
//}
#endif

