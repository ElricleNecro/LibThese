import abc
import numpy as np

from matplotlib import pyplot    as plt
from matplotlib import widgets   as w
from astropy    import constants as const

from LibThese.Models.King import DimKing as King

def CalcMtot(w0, rc, sig_v):
	test = King(w0, rc, sig_v, G=const.G.value)
	test.DimSolve2()
	test.DimXAxis()
	test.CalcRho()
	test.CalcMtot()
	return test.Mtot

pCalcMtot = np.vectorize(CalcMtot)

def W0MtotCube(w0 : np.ndarray, rc_range : tuple, sigv_range : tuple, nb=25):
	res = list()
	for w in w0:
		rc, sv = np.meshgrid(\
				np.linspace(rc_range[0], rc_range[1], nb), \
				np.linspace(sigv_range[0], sigv_range[1], nb) \
			)
		res.append( [CalcMtot(w, rc, sv), rc, sv] )
	return res

class WithCursor(object, metaclass=abc.ABCMeta):
	def __init__(self, ax=None, \
			slname='slider', slmin=0, slmax=10, slinit=5, \
			axcolor='lightgoldenrodyellow'):
		if ax is None:
			self.fig = plt.figure()
			self.fig.subplots_adjust(left=0.25, bottom=0.25)
			self.ax = self.fig.add_subplot(111)

		self.slname = slname
		self.slmin  = slmin
		self.slmax  = slmax
		self.slinit = slinit

		self._Create_SAxes(axcolor)
		self._Create_Slider()

		self.slider.on_changed(self.update)

	def _Create_SAxes(self, axcolor):
		self._slax   = plt.axes([0.25, 0.1, 0.65, 0.03], axisbg=axcolor)

	def _Create_Slider(self):
		self.slider = w.Slider(self._slax, \
					self.slname, self.slmin, self.slmax, \
					valinit=self.slinit)

	@abc.abstractmethod
	def update(self, val):
		raise NotImplementedError

class W0(WithCursor):
	"""
	W0.rcr ::
	W0.sig_vr ::
	"""
	def __init__(self, w0r, rcr, sig_vr, **kwargs):
		self._rcr    = rcr
		self._sig_vr = sig_vr
		self._w0r    = w0r

		kwargs["slmin"] = self._w0r[0]
		kwargs["slmax"] = self._w0r[1]
		kwargs["slinit"] = self._w0r[0]
		kwargs["slname"] = r"$W_0$"

		super(W0, self).__init__(**kwargs)

		self.Populate()

	def Populate(self):
		self.rc, self.sig_v = np.meshgrid(np.linspace(self.rcr[0], self.rcr[1], self.rcr[2]), \
				      np.linspace(self.sig_vr[0], self.sig_vr[1], self.sig_vr[2]))

	def update(self, val):
		mtot = CalcMtot(self.slider.val, self.rc, self.sig_v)
		self.ax.pcolor(self.rc, self.sig_v, mtot.T)
		self.ax.figure.canvas.draw()

	@property
	def rcr(self):
		return self._rcr
	@rcr.setter
	def rcr(self, val):
		self._rcr = val
		self.Populate()

	@property
	def sig_vr(self):
		return self._sig_vr
	@sig_vr.setter
	def sig_vr(self, val):
		self._sig_vr = val
		self.Populate()

class W0Cube(WithCursor):
	def __init__(self, cube, **kwargs):
		self.cube = cube
		super(W0, self).__init__(**kwargs)

	def update(self, val):
		self.ax.pcolor(self.cube[val][1], self.cube[val][2], self.cube[val][0].T)
		self.ax.figure.canvas.draw()

if __name__ == '__main__':
	nb = 50
	rc, sig_v = np.meshgrid( \
					np.linspace(1*const.pc.value, 10.*const.pc.value, nb), \
					np.linspace(290, 2900, nb)
					)

	mtot = CalcMtot(12.5, rc, sig_v)
