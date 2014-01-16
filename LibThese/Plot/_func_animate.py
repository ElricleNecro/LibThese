# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 17:33:23 2013

@author: Guillaume Plum
"""


def AnimateMap(*data):
	from matplotlib import pyplot    as plt
	from matplotlib import animation as an

	fig = plt.figure()
	axs = fig.add_subplot(111, xlabel=r"$r$", ylabel=r"$\vec{v}.\vec{r} / |\vec{r}|$", title=r"Movie Theater!")

	#dat = []
	#ims = []
	#for a in lst:
		#dat.append(ps.Map(a, logger="Animation Logger", log_level=0))

	a = ps.Map(data[-1])
	tmpx, tmpy, tmp = a._calc()
	x_min, x_max = tmpx.min(), tmpx.max()
	y_min, y_max = tmpy.min(), tmpy.max()

	axs.set_xlim(x_min, x_max)
	axs.set_ylim(y_min, y_max)

	#l = axs.pcolormesh([], [], [[]])

	lines = None
	def init():
		a = ps.Map(data[0])
		X, Y, Z = a._calc()
		l = axs.pcolormesh(X, Y, Z)
		return l,

	def update(num):
		axs.cla()
		axs.set_xlim(x_min, x_max)
		axs.set_ylim(y_min, y_max)

		a = ps.Map(data[num])
		X, Y, Z = a._calc()
		#lines.set_array(Z)
		#l       = plt.pcolormesh()
		#l.set_array(Z)
		l       = axs.pcolormesh(X, Y, Z)

		#l = data[num].Plot(num=axs, fig=fig)
		return l,

	#an.FuncAnimation(fig, ims, frames=len(lst), fargs=(dat,), interval=50, blit=True)
	an.FuncAnimation(fig, update, frames=np.arange(1, len(data)), init_func=init, interval=50, blit=True)

	fig.show()

def _save(fig, name, outdir, format):
	from os.path import basename
	fig.savefig(outdir + basename(name) + "." + format, format=format, transparent=False)

def PSMovie(lst, ax=None, set_lim=True, minmax=None, format="%.4g", topng=False):
	"""Affiche l'évolution de l'espace pour une suite de fichier gadget sous forme de Film.
	lst : liste de fichier à afficher,
	set_lim=True : imposer les dimensions du graphe,
	minmax=None : Limites des axes à imposer,
	format="%.4g" : format d'affichage de l'unité de temps.
	"""

	# Quelques import spécifique à la fonction :
	from matplotlib import pyplot as plt
	from pacmanprogressbar import Pacman

	# On prépare la barre de progression :
	p = Pacman(start=0, end=len(lst))

	# On prépare la fenêtre sur laquelle on va tracer :
	if ax is None:
		fig = plt.figure()
		ax  = fig.add_subplot(111)

	# On commence l'animation :
	for i, a in enumerate(lst):
		# On efface le graphique précédent :
		ax.cla()

		# On fixe les limites du graphiques si demandé :
		if set_lim:
			ax.set_ylim(-3000, 3000)
			ax.set_xlim(0, 70)

		# On charge l'espace des phases :
		map = ps.Map(a)

		# Titre du graphique :
		ax.set_title( "Gadget time unit : " + format%map.head["Time"])
		ax.set_xlabel(r"$|\vec{r}|$")
		ax.set_ylabel(r"$\vec{v}.\vec{r} / |\vec{r}|$")

		# Calcul des données :
		X, Y, Z = map._calc()

		# Tracé :
		ax.pcolormesh(X, Y, Z)
		ax.figure.canvas.draw()

		if topng:
			_save(ax.figure, a, "/tmp/", "png")

		# Mise à jour de la barre de progression :
		p.progress(i)

	#"""Affiche l'évolution de l'espace pour une suite de fichier gadget sous forme de Film.
	#lst : liste de fichier à afficher,
	#set_lim=True : imposer les dimensions du graphe,
	#minmax=None : Limites des axes à imposer,
	#format="%.4g" : format d'affichage de l'unité de temps.
	#"""
	#from matplotlib import pyplot as plt
	#from pacmanprogressbar import Pacman

	#p = Pacman(start=0, end=len(lst))

	#fig = plt.figure()
	#ax = fig.add_subplot(111, title=r"$\rho(r)$ of King", xlabel=r"$r$", ylabel=r"$\rho(r)$")

	##pl = preload(lst)

	##for a in pl:
	#for i, a in enumerate(lst):
		#ax.cla()
		#if set_lim:
			#ax.set_ylim(-3000, 3000)
			#ax.set_xlim(0, 70)
		#map = ps.Map(a)
		#ax.set_title( "Gadget time unit : " + format%map.head["Time"])
		#X, Y, Z = map._calc()
		##X, Y, Z = a._calc()
		#ax.pcolormesh(X, Y, Z)
		##if minmax is None:
			##ax.imshow(Z, extent=[X.min(), X.max(), Y.min(), Y.max()], aspect='auto', interpolation='bilinear', origin='lower')
		##else:
			##ax.imshow(Z, extent=minmax, aspect='auto', interpolation='bilinear', origin='lower')
		#ax.figure.canvas.draw()
		#p.progress(i)

def PSMovieSaved(lst, filename, set_lim=True, minmax=None, format="%.4g"):
	"""Affiche l'évolution de l'espace pour une suite de fichier gadget sous forme de Film.
	lst : liste de fichier à afficher,
	set_lim=True : imposer les dimensions du graphe,
	minmax=None : Limites des axes à imposer,
	format="%.4g" : format d'affichage de l'unité de temps.
	"""

	# Quelques import spécifique à la fonction :
	from matplotlib import pyplot as plt
	from matplotlib import animation as an
	from pacmanprogressbar import Pacman

	# On prépare la barre de progression :
	p = Pacman(start=0, end=len(lst))

	# On prépare la fenêtre sur laquelle on va tracer :
	fig = plt.figure()
	ax  = fig.add_subplot(111, title = r"$\rho(r)$ of King", xlabel = r"$r$", ylabel = r"$\rho(r)$")

	# On prépare ce qui va nous permettre d'enregistrer la vidéo :

	FFMpegWriter = an.writers['imagemagick']
	metadata     = dict(title='Phase Space Evolution for Henon collapse at Viriel -0.3', artist='Guillaume Plum')
	writer       = FFMpegWriter(fps=15, metadata=metadata)

	#moviewriter = an.MencoderWriter(fps=25, metadata={'title':'Phase Space Evolution for Henon with Viriel of -0.3', 'artist':'Guillaume Plum', 'subject':'Henon Collapse'})

	# On commence l'enregistrement :
	with writer.saving(fig, filename, 100):
		for i, a in enumerate(lst):
			# On efface le graphique précédent :
			ax.cla()

			# On fixe les limites du graphiques si demandé :
			if set_lim:
				ax.set_ylim(-3000, 3000)
				ax.set_xlim(0, 70)

			# On charge l'espace des phases :
			map = ps.Map(a)

			# Titre du graphique :
			ax.set_title( "Gadget time unit : " + format%map.head["Time"])

			# Calcul des données :
			X, Y, Z = map._calc()

			# Tracé :
			ax.pcolormesh(X, Y, Z)
			#ax.figure.canvas.draw()

			# Capture du graphique par la classe créant la vidéo :
			writer.grab_frame()

			# Mise à jour de la barre de progression :
			p.progress(i)

