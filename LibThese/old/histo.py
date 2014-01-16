import numpy		 as np
import matplotlib.pyplot as plt
import matplotlib.cm	 as cm

def PlotCarte(pos, tlist=[(0, 1), (0, 2), (1, 2)], num="Carte de l'objet", clm=cm.jet, nbbin=300, Axis=None, contrast=-20):
	fig, axs = plt.subplots(len(tlist), 1, num=num, squeeze=True)

	for i, tup in enumerate(tlist):
		axs[i].cla()
		tmp = PlotHisto(pos, axCar1=axs[i], ind=tup, clm=clm, nbbin=nbbin, Axis=Axis, contrast=contrast)
		color = fig.colorbar(tmp, ax=axs[i])

	return fig, axs, color

def PlotHisto(Part, axCar1=None, ind=(0, 1), clm=cm.jet, nbbin=300, Axis=None, contrast=-20):
	if Axis is None:
		Axis = np.array( [np.min(Part[:,ind[0]]), np.max(Part[:,ind[0]]), np.min(Part[:,ind[1]]), np.max(Part[:,ind[1]]) ] )

	FieldRange = [ [Axis[0], Axis[1]], [Axis[2], Axis[3]] ]

	if axCar1 is None:
		Carte1 = plt.figure("Carte " + str(ind))
		axCar1 = Carte1.add_subplot(111)

	hist, X, Y = np.histogram2d(Part[:,ind[0]], Part[:,ind[1]], bins=nbbin, range=FieldRange)

	print(Axis)
	axCar1.axis(Axis)

	Tr = hist.T
	Tr[ Tr == 0 ] = contrast
	#Tr = np.log10(np.where(hist.T <= 0, 10**(-0.01), hist.T))
	tmp = axCar1.pcolor(X, Y, Tr, cmap=clm)
	#axCar1.set_aspect('equal')
	ratio = (  np.max(Part[:,ind[0]]) - np.min(Part[:,ind[0]]) ) / (np.max(Part[:,ind[1]]) - np.min(Part[:,ind[1]]) )
	axCar1.set_aspect(ratio, adjustable='box') #'equal')

	return tmp

