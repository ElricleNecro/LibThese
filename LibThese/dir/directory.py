# -*- encoding: utf-8 -*-

import os
import re

def SearchFile(motif, pdir=".", recurse=False, exclude=None):
	"""Cherche dans le répertoire courant (et dans les sous-répertoires, si recurse = True (False par défaut)) si un motif ou un dossier contient la chaîne "motif".

	motif           :: motif recherché.
	pdir    = "."   :: Répertoire parent à partir duquel rechercher.
	recurse = False :: récursif ou non (défaut : non récursif).
	"""

	res = []

	for i in os.listdir(pdir):
		i = os.path.join(pdir, i)
		if recurse and os.path.isdir(i):
			#res.append(SearchFile(motif, pdir=i, recurse=recurse))
			res = res + SearchFile(motif, pdir=i, recurse=recurse)
			while [] in res:
				res.remove([])
		if re.search(motif, i) is not None:
			if exclude is None or re.search(exclude, i) is None:
				res.append(i)
	return res

def CopyFile(old, new):
	"""Copie des fichiers (old) vers un nouveau répertoire (new).

	old :: liste des fichiers à copier.
	new :: dossier de destination.
	"""

	for name in old:
		tmpold = os.path.basename(name)
		tmpnew = os.path.join(new, tmpold)
		print("Copie de " + tmpold + " dans " + tmpnew)

		with open(name, 'r') as fich1:
			with open(os.path.join(new, os.path.basename(name)), 'w') as fich2:
				lig = fich1.read()
				fich2.write(lig)

