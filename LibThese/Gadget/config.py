# -*- encoding: utf-8 -*-

from   LibThese.plot                   import Read_File

class GadgetConfig(object):
	Param      = dict()
	Categories = dict(
			Time   = ["TimeOfFirstSnapshot",
				  "TimeBegin",
				  "TimeMax",
				  "TimeBetSnapshot",
				  "TimeBetStatistics",
				  "MinSizeTimestep",
				  "MaxSizeTimestep"
				],
			Units  = ["UnitLength_in_cm",
				  "UnitMass_in_g",
				  "UnitVelocity_in_cm_per_s",
				  "GravityConstantInternal"
				],
			Soft   = ["SofteningGas",
				  "SofteningGasMaxPhys",
				  "SofteningHalo",
				  "SofteningHaloMaxPhys",
				  "SofteningDisk",
				  "SofteningDiskMaxPhys",
				  "SofteningBulge",
				  "SofteningBulgeMaxPhys",
				  "SofteningStars",
				  "SofteningStarsMaxPhys",
				  "SofteningBndry",
				  "SofteningBndryMaxPhys"],
			Files  = ["InitCondFile",
				  "ICFormat",
				  "SnapshotFileBase",
				  "SnapFormat",
				  "NumFilesPerSnapshot",
				  "NumFilesWrittenInParallel",
				  "OutputDir",
				  "OutputListOn",
				  "OutputListFilename",
				  "RestartFile",
				  "CpuTimeBetRestartFile",
				  "EnergyFile",
				  "InfoFile",
				  "TimingsFile",
				  "CpuFile"
				],
			Cosmo  = ["Omega0",
				  "OmegaBaryon",
				  "OmegaLambda",
				  "HubbleParam"
				],
			Conf   = ["ResubmitOn",
				  "ResubmitCommand",
				  "TypeOfOpeningCriterion",
				  "TypeOfTimestepCriterion",
				  "ErrTolTheta",
				  "ErrTolIntAccuracy",
				  "ErrTolForceAcc",
				  "TreeDomainUpdateFrequency",
				  "TreeAllocFactor",
				  "BufferSize",
				  "PartAllocFactor"
				  "CourantFac",
				  "MaxRMSDisplacementFac",
				],
			SParam = ["BoxSize",
				  "PeriodicBoundariesOn",
				  "ComovingIntegrationOn",
				  "MaxNumNgbDeviation"
				],
			Physic = ["MinGasTemp",
				  "MinGasHsmlFractional",
				  "InitGasTemp",
				  "ArtBulkViscConst"
				]
		     )
	filename   = None

	def __init__(self, filename):
		self.filename = filename

		self.Param["InitCondFile"]              = None
		self.Param["ICFormat"]                  = 1
		self.Param["OutputDir"]                 = None
		self.Param["SnapshotFileBase"]          = None
		self.Param["SnapFormat"]                = 1
		self.Param["NumFilesPerSnapshot"]       = 1
		self.Param["NumFilesWrittenInParallel"] = 1
		self.Param["RestartFile"]               = "restart"
		self.Param["CpuTimeBetRestartFile"]     = 72000
		self.Param["OutputListOn"]              = 0
		self.Param["OutputListFilename"]        = None

		self.Param["EnergyFile"]                = "energy.log"
		self.Param["InfoFile"]                  = "info.log"
		self.Param["TimingsFile"]               = "timings.log"
		self.Param["CpuFile"]                   = "cpu.log"
		self.Param["TimeLimitCPU"]              = 72000
		self.Param["ResubmitOn"]                = 0
		self.Param["ResubmitCommand"]           = None

		self.Param["BoxSize"]                   = 0.
		self.Param["ComovingIntegrationOn"]     = 0
		self.Param["TypeOfTimestepCriterion"]   = 0
		self.Param["PeriodicBoundariesOn"]      = 0

		self.Param["TimeBegin"]                 = 0.0
		self.Param["TimeMax"]                   = 1.0
		self.Param["TimeBetSnapshot"]           = 0.1
		self.Param["TimeOfFirstSnapshot"]       = 0.1
		self.Param["TimeBetStatistics"]         = 0.05
		self.Param["MaxSizeTimestep"]           = 1e-5
		self.Param["MinSizeTimestep"]           = 0.

		self.Param["Omega0"]                    = 0.
		self.Param["OmegaLambda"]               = 0.
		self.Param["OmegaBaryon"]               = 0.
		self.Param["HubbleParam"]               = 0.

		self.Param["InitGasTemp"]               = 0
		self.Param["MinGasTemp"]                = 0
		self.Param["MinGasHsmlFractional"]      = 0.25
		self.Param["MaxRMSDisplacementFac"]     = 0.2
		self.Param["CourantFac"]                = 0.15
		self.Param["ErrTolTheta"]               = 0.5
		self.Param["ErrTolForceAcc"]            = 0.005
		self.Param["ErrTolIntAccuracy"]         = 0.025
		self.Param["TypeOfOpeningCriterion"]    = 1
		self.Param["TreeDomainUpdateFrequency"] = 0.1
		self.Param["DesNumNgb"]                 = 0
		self.Param["ArtBulkViscConst"]          = 0.0
		self.Param["MaxNumNgbDeviation"]        = 0
		self.Param["PartAllocFactor"]           = 30.0
		self.Param["TreeAllocFactor"]           = 5.0
		self.Param["BufferSize"]                = 30

		self.Param["UnitLength_in_cm"]          = None
		self.Param["UnitMass_in_g"]             = None
		self.Param["UnitVelocity_in_cm_per_s"]  = None
		self.Param["GravityConstantInternal"]   = 1

		self.Param["SofteningGas"]              = None
		self.Param["SofteningHalo"]             = None
		self.Param["SofteningDisk"]             = None
		self.Param["SofteningBulge"]            = None
		self.Param["SofteningStars"]            = None
		self.Param["SofteningBndry"]            = None
		self.Param["SofteningGasMaxPhys"]       = None
		self.Param["SofteningHaloMaxPhys"]      = None
		self.Param["SofteningDiskMaxPhys"]      = None
		self.Param["SofteningBulgeMaxPhys"]     = None
		self.Param["SofteningStarsMaxPhys"]     = None
		self.Param["SofteningBndryMaxPhys"]     = None

	def __getattr__(self, name):
		if name in self.Param:
			return self.Param[name]
		return super(Config, self).__getattr__(name)

	def __setattr__(self, name, value):
		if name in self.Param:
			self.Param[name] = value
		else:
			super(Config, self).__setattr__(name, value)

	def __str__(self):
		res = str()
		for key in gadget_cfg.Param:
			res += "%025s"%(key) + " " + str(gadget_cfg.Param[key]) + "\n"
		return res

	def __repr__(self):
		return "<%s :: %s -- %d>"%(__name__, self.filename, id(self))

	def IsNone(self):
		res = list()
		for a in self.Param:
			if self.Param[a] is None:
				res += [a]

		return res

	def SeeDict(self):
		print(self.Param)

	def Write(self):
		with open(self.filename, "w") as f:
			for k in self.Param:
				f.write( "{key:25}\t{value}\n".format(key=k, value=self.Param[k]) )

