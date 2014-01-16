#! /usr/bin/env python3
# -*- coding:Utf8 -*-

import sys
import numpy as np

def get_gadget( self, filename ):

	""" Pour la lecture des fichiers Gadget en un seul fichier ou plusieurs splittés """

	# on trouve le nombre de fichiers avec le préfixe donné en argument
	nmax = self.get_number_files( filename )

	# si pas de fichier splittés
	if nmax == 0 :

		# vérification de l'existence
		if not os.path.exists( filename ):
			print("\033[31;1mThe file " + filename + " doesn't exist !\nCheck the file name !\033[0m")
			sys.exit()

		# on lit les données Gadget
		rdg = ReadGadget( filename )
		header = rdg.read_header()
		positions = rdg.get_positions()

		# on renvoie le header et les positions
		self.show_header( header )
		return positions, header

	else :

		# on initialise le tableau des positions
		positions = list()

		for i in range( nmax ):

			# le nom du fichier splitté
			name = filename + "." + str( i+1 )

			# on lit le fichier splitté
			rdg = ReadGadget( name )
			header = rdg.read_header()
			positions.append( rdg.get_positions() )

		# on renvoie le header et les positions
		self.show_header( header )
		return np.array( positions, dtype="float32" ).flatten(), header

def get_allpos(lst):
	pos1 = []
	pos2 = []
	pos3 = []

	for file in lst:
		Gadget  = ReadGadget(file)
		Hea     = Gadget.read_header()
		pos_tmp = Gadget.get_positions()
		pos_tmp.shape = (len(pos_tmp)/3, 3)

		Id      = Gadget.get_identities()

		#pos = np.append(pos, [pos_tmp[i:i+3] for i in range(0, len(pos_tmp), 3)], axis=0)
		pos1    = np.append(pos1, pos_tmp[ (Id-1) == (1-1)])
		pos2    = np.append(pos2, pos_tmp[ (Id-1) == (2-1)])
		pos3    = np.append(pos3, pos_tmp[ (Id-1) == (3-1)])

		Gadget.close()

	pos1.shape = (len(pos1)/3, 3)
	pos2.shape = (len(pos2)/3, 3)
	pos3.shape = (len(pos3)/3, 3)

	return pos1, pos2, pos3

# pour lire les fichiers binaires en essais
class ReadBinaryBlock :

        """ Classe pour la lecture des fichiers binaires avec les blocs Fortran"""

        # initialisation
        def __init__( self, nomfichier ) :

                """ Initialisation """

                # on stocke le nom du fichier
                self.filename = nomfichier

                # on ouvre le fichier en mode binaire
                self.f = open( nomfichier, "rb" )

                # on pousse la précision au maximum pour les entiers
                sys.maxsize = 2**63 - 1

        # pour déterminer le type passer en argument
        def dtype( self, typ ) :

                """ Détermination du type numpy qui correspond au type passer en argument """

                # on retourne le type numpy qui correspond
                return np.dtype(typ)

        # lire début bloc
        def border_block( self ):

                """ Pour la lecture du début d'un bloc """

                # on lit la taille du bloc en début ou fin de bloc
                return np.fromfile( file = self.f, dtype=np.int32, count = 1 )[0]

        # pour lire les données qui sont stockées dans le tableau
        def get_data( self, typ, ndata ) :

                """ Pour lire les données entre les extrémités des blocs """

                # lecture des données
                return np.fromfile( file = self.f, dtype = self.dtype( typ ), count = ndata )

        # pour un lire un bloc de données
        def get_block ( self, typ ) :

                """ Pour la lecture simplifiée des données dans un bloc de données """

                # on détermine la taille des blocs en octets
                noctet = self.border_block()

                # on détermine la taille en octet du type passé en argument
                ntype = np.dtype( typ ).itemsize

                # on détermine le nombre d'éléments à lire
                ndata = int( noctet / ntype )

                # on lit le bloc dans son ensemble pour les données
                data = self.get_data( typ, np.array( ndata, dtype = "int32" ) )

                # on lit la dernière extrêmité du bloc pour le finir
                noctet_fin = self.border_block()

                # vérification bon déroulement
                if noctet != noctet_fin :

                        raise IOError ("\033[31;1mLes extrémités des blocs ne correspondent pas ! Il y a un problème dans les types à lire sûrement !\033[0m")

                # on retourne les données
                return data

        # pour fermer le fichier quand la variable n'est pas effacée
        def close( self ):

                """ Pour fermer le fichier si l'instance n'est pas effacée """

                self.f.close()

        # pour réouvrir le fichier
        def open(self):

                """ Pour réouvrir le fichier binaire à lire """

                self.f.close()
                self.f = open(self.filename, "rb")

        # pour la fermeture du fichier
        def __del__(self):

                """ Pour la fermeture du fichier """

                self.f.close()

# pour la lecture des fichiers Gadget
class ReadGadget( ReadBinaryBlock ) :

        """ Une classe pour la lecture des fichiers Gadget """

        # initialisation
        def __init__(self, nomsnap):

                # on permet la lecture du fichier binaire avec la classe à cet effet
                super().__init__(nomsnap)

        # pour lire le header
        def read_header(self):

                """ Pour la lecture des données dans le header du fichier Gadget """
                self.f.seek(0)

                # le nombre d'octet dans le bloc du header
                noctet = self.border_block()

                # on boucle sur les types
                self.header = dict()
                self.header.update({"Npart":self.get_data("int32", 6)})
                self.header.update({"Massarr":self.get_data("float64", 6)})
                self.header.update({"Time":self.get_data("float64", 1)[0]})
                self.header.update({"Redshift":self.get_data("float64", 1)[0]})
                self.header.update({"FlagSfr":self.get_data("int32", 1)[0]})
                self.header.update({"FlagFeedBack":self.get_data("int32", 1)[0]})
                self.header.update({"Nall":self.get_data("int32", 6)})
                self.header.update({"FlagCooling":self.get_data("int32", 1)[0]})
                self.header.update({"NumFiles":self.get_data("int32", 1)[0]})
                self.header.update({"BoxSize":self.get_data("float64", 1)[0]})
                self.header.update({"Omega0":self.get_data("float64", 1)[0]})
                self.header.update({"OmegaLambda":self.get_data("float64", 1)[0]})
                self.header.update({"HubbleParam":self.get_data("float64", 1)[0]})
                self.header.update({"FlagAge":self.get_data("int32", 1)[0]})
                self.header.update({"FlagMetals":self.get_data("int32", 1)[0]})
                self.header.update({"NallHW":self.get_data("int32", 6)})
                self.header.update({"flag_entr_ics":self.get_data("int32", 1)[0]})
                self.header.update({"null":self.get_data("int32", 15)})

                # lecture de la fin des blocs
                noctet_fin = self.border_block()

                # vérification des erreurs
                if noctet != noctet_fin :

                        raise IOError ("\033[31;1mError reading Gadget file " + self.filename + "\033[0m")

                # on renvoie le header
                return self.header

        # on lit les positions des galaxies
        def get_positions(self):

                """ Pour lire les positions des particules dans le fichier de Gadget """

                # on se ramène en position 0
                self.f.seek(0)

                # on se déplace après le header
                self.f.seek(264)

                # on renvoie les positions
                return self.get_block("float32")

        # on lit les vitesses
        def get_velocities(self):

                """ Pour lire les vitesses des particules dans le fichier Gadget """

                try:
                        self.header
                except AttributeError:
                        self.read_header()

                # on se ramène en position 0
                self.f.seek(0)

                # on se déplace après le header
                self.f.seek(264 + 4 + 3 * sum(self.header["Npart"]) * np.dtype("float32").itemsize + 4)

                #print(264 + 3 * sum(self.header["Npart"]) * np.dtype("float32").itemsize + 8)

                # on lit les vitesses et les renvoie
                return self.get_block("float32")

        # on lit les identités des galaxies
        def get_identities(self):

                """ Pour lire les identités des particules dans le fichier Gadget """

                try:
                        self.header
                except NameError:
                        self.read_header()

                # on se ramène en position 0
                self.f.seek(0)

                # on se déplace après le header
                self.f.seek( 264 + 6 * sum(self.header["Npart"]) * np.dtype("float32").itemsize + 16 )

                # on lit les identités
                return self.get_block("int32")

        # on lit les masses si elles sont présentes
        def get_masses(self):

                """ Pour lire les masses dans le fichier Gadget si elles sont présentes """

                try:
                        self.header
                except NameError:
                        self.read_header()

                # on vérifie si on a des données à lire
                Nm = sum( np.where( self.header["Massarr"] == 0.0, self.header["Npart"], 0 ) )
                if Nm == 0 :

                        raise IOError ("\033[33;1mNo data for particles masses to be read !\033[0m")

                # on se ramène en position 0
                self.f.seek(0)

                # on se déplace après le header
                self.f.seek( 264 + 6 * sum(self.header["Npart"]) * np.dtype("float32").itemsize + 24 +
                        sum(self.header["Npart"]) * np.dtype("int32").itemsize )

                # on lit les masses
                return self.get_block("float32")

        # pour récupérer les énergies
        def get_energies(self):

                """ Pour lire les énergies des particules dans le fichier Gadget """

                try:
                        self.header
                except NameError:
                        self.read_header()

                # on vérifie que l'on a des particules à lire
                if self.header["Npart"][0] == 0 :

                        raise IOError ("\033[33;1mNo particles for energies to be read !\033[0m")

                # nombre de particules de masses
                Nm = sum( np.where( self.header["Massarr"] == 0.0, self.header["Npart"], 0 ) ) * np.dtype("float32").itemsize
                if Nm != 0 :
                        Nm += 8

                # on se ramène en position 0
                self.f.seek(0)

                # on se déplace après le header
                self.f.seek( 264 + 6 * sum(self.header["Npart"]) * np.dtype("float32").itemsize + 24 +
                        sum(self.header["Npart"]) * np.dtype("int32").itemsize + Nm)

                # on renvoie les énergies
                return self.get_block("float32")

        # pour récupérer les densités
        def get_densities(self):

                """ Pour lire les densités des particules si elles sont présentes """

                try:
                        self.header
                except NameError:
                        self.read_header()

                # on vérifie que l'on a des particules à lire
                if self.header["Npart"][0] == 0 :

                        raise IOError ("\033[33;1mNo particles for energies to be read !\033[0m")

                # nombre de particules de masses
                Nm = sum( np.where( self.header["Massarr"] == 0.0, self.header["Npart"], 0 ) ) * np.dtype("float32").itemsize
                if Nm != 0 :
                        Nm += 8

                # on se ramène en position 0
                self.f.seek(0)

                # on se déplace après le header
                self.f.seek( 264 + 6 * sum(self.header["Npart"]) * np.dtype("float32").itemsize + 24 +
                        sum(self.header["Npart"]) * np.dtype("int32").itemsize + Nm + 8 + self.header["Npart"][0] *
                        np.dtype("float32").itemsize )

                # on renvoie les densités
                return self.get_block("float32")


