import glob
import subprocess


##### -----Please add input hist list here
#4top
#file_list  = glob.glob("/pnfs/knu.ac.kr/data/cms/store/user/soan/4top_ex1/*.root")

#QCD_HT1000
#file_list  = glob.glob("/pnfs/knu.ac.kr/data/cms/store/user/jiwoong/QCD_PU_1M_gen/HT1000/QCD_HT1000/*.root")

#QCD_HT1500
#file_list = glob.glob("/pnfs/knu.ac.kr/data/cms/store/user/jiwoong/QCD_PU_1M_gen/HT1500/QCD_HT1500/*.root")

#QCD_HT2000
file_list = glob.glob("/pnfs/knu.ac.kr/data/cms/store/user/jiwoong/QCD_PU_1M_gen/HT2000/QCD_HT2000/*.root")


def calc_Nout(maxfile,nfile):
	nfile = maxfile + nfile - 1
	nout = int(nfile / maxfile)
	return(nout)



##### -----Please add batch size here 
maxfile=10 # Max number of input files for each run 




nfile=len(file_list) #  Number of total input files
nout  = calc_Nout(maxfile,nfile) # Number of output files
for i in range(nout):
	start = i*maxfile 
	end = start + maxfile 
	
	infiles = (' '.join(file_list[start:end]))


	#fn_out = "4top_" + str(i) + ".npy"
	#fn_out = "QCD1000_" + str(i) + ".npy"
	#fn_out = "QCD1500_" + str(i) + ".npy"
	fn_out = "QCD2000_" + str(i) + ".npy"


	print("############################## SET: ",fn_out)
	print(infiles)
	
	# Run specific excutable codes
	args = 'python' + ' '+ 'selector.py' + ' ' + '--outname' + ' ' + fn_out + ' '+  infiles
	subprocess.call(args,shell=True)
