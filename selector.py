import uproot # for uproot4

import argparse
import glob
import awkward as ak
from numba import jit
import numpy as np
from tqdm import tqdm
import time


# using glob
#dir_path = "/x4/cms/dylee/Delphes/data/Storage/Second_data/root/signal/condorDelPyOut/*.root"
#file_list = glob.glob(dir_path)



def read_data(file_list):
	
	# using file list
	#f = open('file_list')
	#file_list = [line.rstrip() for line in f]


	# using input args
	flist=[]
	for f in file_list:
		flist.append(f + ':Delphes')
	branches = ["Jet.PT","Jet.Eta","Jet.Phi","Jet.BTag","ScalarHT.HT","Muon.PT","Muon.Eta","Muon.Phi","Muon_size","Electron.PT","Electron.Eta","Electron.Phi","Electron_size"]

	return flist, branches



#@jit # for future developer...
def Loop(flist,brancher):

	# define array
	histo={}
	print(flist)

	# --Start File Loop
	for arrays in uproot.iterate(flist,branches): #  for Uproot4

		print("processing array: ",len(arrays))

		## 1 -- Conver branch as array
		Jet = ak.zip({
			"PT"		: arrays["Jet.PT"],
			"Eta"	   : arrays["Jet.Eta"],
			"Phi"	   : arrays["Jet.Phi"],
			#"T"		 : arrays["Jet.T"],
			"BTag"		  : arrays["Jet.BTag"],
		
			})
		'''
		FatJet = ak.zip({
			"PT"		: arrays["FatJet.PT"],
			"Mass"		  : arrays["FatJet.Mass"],
		})
		'''

		HT = arrays["ScalarHT.HT"]

		Electron = ak.zip({
				"PT" : arrays["Electron.PT"],
				"Phi" : arrays["Electron.Phi"],
				"Eta" : arrays["Electron.Eta"],
				"size" : arrays["Electron_size"]
				})
		
		Muon = 	ak.zip({
				"PT" :arrays["Muon.PT"],
				"Phi" : arrays["Muon.Phi"],
				"Eta" : arrays["Muon.Eta"],
				"size" : arrays["Muon_size"]
				})


		## 2 -- Selections
		
		# Jet selection (jet multiplicity // jet identification )
		Jet_sel_mask = (abs(Jet.Eta)  <=2.4)  & (Jet.PT > 35)
		Jet_evt_sel_mask = ak.num(Jet) >= 9

		Jet = Jet[Jet_evt_sel_mask]
		HT = HT[Jet_evt_sel_mask]
		Electorn = Electron[Jet_evt_sel_mask]
		Muon = Muon[Jet_evt_sel_mask]

		#FatJet	   = FatJet[Jet_evt_sel_mask]

		# HT selection
		HT_mask   = ak.flatten(HT >= 700)

		Jet = Jet[HT_mask]
		HT = HT[HT_mask]
		Electron = Electron[HT_mask]
		Muon = Muon[HT_mask]


		#FatJet	   = FatJet[HT_mask]

		# B-jet selection
		Bjet = Jet.BTag > 0.5
		Btag_mask = ak.sum(Bjet,axis=-1) >= 1

		Jet = Jet[Btag_mask]
		HT = HT[Btag_mask]
		Electron = Electron[Btag_mask]
		Muon = Muon[Btag_mask]		

		#FatJet	   = FatJet[Btag_mask]
		
		#Lepton Veto-method that how we did it before
		#Lepton identification // leptonic veto

		Veto_E = Electron[Electron.PT>15]
		Veto_M = Muon[Muon.PT>15]  
		Veto_L = (ak.num(Veto_E)+ak.num(Veto_M)) == 0  
		
		Jet = Jet[Veto_L]  
		Bjet = Bjet[Veto_L]
		HT = HT[Veto_L]
		Electron = Electron[Veto_L]
		Muon = Muon[Veto_L]
		
		#Lepton Veto-method NURION

		numLepton = (Electron.size + Muon.size)
		Veto_L = (numLepton ==  0)
		
		Jet = Jet[Veto_L]
		Bjet = Bjet[Veto_L]
		HT = HT[Veto_L]
		Electron = Electron[Veto_L]
		Muon = Muon[Veto_L]

		'''
		# Fat-jet selection
		Fat_jet_sel_mask = FatJet.PT > 30
		Fat_jet_evt_mask = ak.num(FatJet[Fat_jet_sel_mask]) > 0
		
		Jet		  = Jet[Fat_jet_evt_mask]
		HT			 = HT[Fat_jet_evt_mask]
		FatJet	   = FatJet[Fat_jet_evt_mask]
		

		# Fat-jet mass selection
		Fat_jet_mass_mask = ak.sum(FatJet.Mass,axis=-1) >= 500
	
		Jet_sel		  = Jet[Fat_jet_mass_mask]
		HT_sel			 = HT[Fat_jet_mass_mask]
		FatJet_sel	   = FatJet[Fat_jet_mass_mask]
		'''

		## 3 -- Prepare histogram 

		# All Jets
		h_jet_eta = ak.to_numpy(ak.flatten(Jet.Eta))
		h_jet_phi = ak.to_numpy(ak.flatten(Jet.Phi))
		
		#print(Jet[:,0].Eta)
		'''
		# Leading Jets
		h_jet_eta = ak.to_numpy((Jet.Eta[:,0]))
		h_jet_phi = ak.to_numpy((Jet[:,0].Phi))
		'''


		# Others
		h_Njet  = ak.to_numpy(ak.num(Jet))
		h_HT    = ak.to_numpy(ak.flatten(HT))
		h_Nbjet = ak.to_numpy(ak.sum(Jet.BTag > 0.5,axis=-1))
		

		# test print out
		#print(h_Njet,len(h_Njet))
		#print(h_HT,len(h_HT))
		#print(h_Nbjet,len(h_Nbjet))
		#print(h_Mfjet,len(h_Mfjet))


		if len(histo) == 0:
			histo['Jet_eta'] = h_jet_eta
			histo['Jet_phi'] = h_jet_phi
			histo['Njet']    = h_Njet
			histo['Nbjet']   = h_Nbjet
			histo['HT']      = h_HT
			
		else:
			 histo['Jet_eta'] = np.concatenate((histo['Jet_eta'],h_jet_eta),axis=0)
			 histo['Jet_phi'] = np.concatenate((histo['Jet_phi'],h_jet_phi),axis=0)
			 histo['Njet'] = np.concatenate((histo['Njet'],h_Njet),axis=0)
			 histo['Nbjet'] = np.concatenate((histo['Nbjet'],h_Nbjet),axis=0)
			 histo['HT'] = np.concatenate((histo['HT'],h_HT),axis=0)
			 


			 print("length: ",len(histo['Jet_eta'] ))
	return histo



if __name__ == "__main__":


	parser = argparse.ArgumentParser()
	parser.add_argument(nargs='+' ,help='input files', dest='filename')
	parser.add_argument('--outname', '-o', help='outname')
	args  =parser.parse_args()


	start_time = time.time()
	flist, branches = read_data(args.filename)
	histo = Loop(flist,branches)

	

	outname = args.outname
	np.save(outname,histo,allow_pickle=True)
	print("--- %s seconds ---" % (time.time() - start_time))
