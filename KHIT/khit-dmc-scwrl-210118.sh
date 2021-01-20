#!/usr/bin/env bash
set -eE +o posix
set -o pipefail
export LANG=en_US.UTF-8
export LC_COLLATE=C

################
# ERROR CALL
################
declare -r prog_cmd=$(ps --no-headers -o command "$$")
error() {
	printf -- '%s :\n%s\n' "$prog_cmd" "$*" >&2
	set +eE
    trap -  ERR
    trap '' INT
    exit $(false)
}

err_report() {
	echo
	echo "$0 Error on line $1"
}

trap 'err_report $LINENO' ERR

################
# ARGUMENT
################
DARCPDB_ARG=$1
WORKDIR_ARG=$2
OUTPUT_ARG=$3

if [ -z $DARCPDB_ARG ] && [ -z $WORKDIR_ARG ] && [ -z $OUTPUT_ARG ]; then
	echo
	echo "usage) bash $0 [DARC output pdb] [working dir] [final output path]"
	echo
	echo "	arg1) DARC output pdb (absolute path)"
	echo "	arg2) Working directory  ex) Server local disk"
	echo "	arg3) Final output path"
	echo
	exit 1
fi

################
# IMPORTANT PARAMETER
################
declare -r LIG=LIG
declare -r N_CONFORMER=5000
declare -r N_THREAD=20

################
# TMP PARAMETER
################
declare PDB_FILE=${DARCPDB_ARG##*/}
declare SAMPLE_NAME=${PDB_FILE%%.*}
IFS='_' read -r -a PDB_ARRAY <<<"${SAMPLE_NAME}"

################
# FOLDER
################
declare STORE_DIR=$WORKDIR_ARG/$SAMPLE_NAME
declare TMP_DIR=$STORE_DIR/tmp
declare DOCK_RES_DIR=$STORE_DIR/dock_res
declare DOCK_RES_SCWRL_DIR=$STORE_DIR/dock_res_scwrl

################
# LIBRARY
################
LIB_PATH=/lwork01/neoscan_lib
MFF_LIB=$LIB_PATH/MMFF94.mff
XML_LIB=$LIB_PATH/dock.xml
ENVA_LIB_PATH=/KHIT2/LIB/enva
HINGE_LIB_PATH=/KHIT2/LIB/hinge
ENVA_LIB=$ENVA_LIB_PATH/${PDB_ARRAY[0]}_${PDB_ARRAY[1]}.out
HINGE_LIB=$HINGE_LIB_PATH/${PDB_ARRAY[1]:0:4}atoms_ch.txt

################
# TOOLS
################
declare GEAR_PATH=/lwork01/neoscan_gear
declare -r REDUCE=$GEAR_PATH/reduce
declare -r BABEL=$(type -P babel)
declare -r BALLOON=$GEAR_PATH/balloon
declare -r ENVA=$GEAR_PATH/enva_v1.5
declare -r SCWRL4=$GEAR_PATH/Scwrl4
declare -r ISKEW=$GEAR_PATH/iskew
declare -r RMSD=$GEAR_PATH/rmsd_het
declare ROSETTA_PATH=/lwork01/rosetta_src_2019.40.60963_bundle/
declare -r MPIRUN=$(type -P mpirun)
declare -r MOL_TO_PARAM=$ROSETTA_PATH/main/source/scripts/python/public/molfile_to_params.py
declare -r RLD_MPI=$ROSETTA_PATH/main/source/bin/rosetta_scripts.mpi.linuxgccrelease

################
# ACTION
################
_00_checkToolLibDir() {
	for x in ${REDUCE} ${BABEL} ${BALLOON} ${ENVA} ${SCWRL4} ${ISKEW} ${RMSD} ${MPIRUN}  ${MOL_TO_PARAM} ${RLD_MPI}; do
		test -f $x || error "$_ : program not found."
	done

	for x in ${MFF_LIB} ${XML_LIB} ${ENVA_LIB} ${HINGE_LIB}; do
		test -f $x || error "$_ : file not found."
	done

	for x in ${DOCK_RES_DIR} ${DOCK_RES_SCWRL_DIR}; do
		test -d $x || mkdir -p $_
	done
}

_01_mpiRLD() {
	test -d $TMP_DIR || mkdir -p $TMP_DIR

	local _00_darc_pdb=$1

	local _01_ligand_pdb=$TMP_DIR/${SAMPLE_NAME}_ligand.pdb
	local _02_ligand_red_pdb=$TMP_DIR/${SAMPLE_NAME}_ligand_red.pdb
	local _03_ligand_sdf=$TMP_DIR/${SAMPLE_NAME}_ligand.sdf
	local _04_conformer_sdf=$TMP_DIR/conformer.sdf
	local _07_lig_confomer_pdb=$TMP_DIR/${LIG}_conformers.pdb
	local _08_ligand_red_mol2=$TMP_DIR/${SAMPLE_NAME}_ligand_red.mol2
	local _09_lig_params=$TMP_DIR/${LIG}.params
	local _10_protein_pdb=$TMP_DIR/${SAMPLE_NAME}_protein.pdb
	local _11_receptor_pdb=$TMP_DIR/${SAMPLE_NAME}_receptor.pdb
	local _12_crystal_complex_pdb=$TMP_DIR/crystal_complex.pdb
	local _13_option=$TMP_DIR/option
	local _14_score_sc=$TMP_DIR/score_${SAMPLE_NAME}.sc
	local _15_total_score_r_tsv=$STORE_DIR/${SAMPLE_NAME}_total_score_r.tsv

	# 1)
	awk '/HETATM/ && /'${LIG}'/ && !/OXT/ {print} END {print "END"}' $_00_darc_pdb > $_01_ligand_pdb
	$REDUCE -Trim $_01_ligand_pdb > $_02_ligand_red_pdb
	$BABEL -ipdb $_02_ligand_red_pdb -osdf $_03_ligand_sdf
	$BALLOON -f $MFF_LIB --nconfs 50 --nGenerations 300 --rebuildGeometry $_03_ligand_sdf $_04_conformer_sdf
	cd $TMP_DIR
	$MOL_TO_PARAM -n $LIG -p $LIG --no-param $_04_conformer_sdf
	 
	local _05_lig_pdbs=(`find $TMP_DIR -type f -prune -regextype posix-egrep -regex "$TMP_DIR/${LIG}_[0-9]{4}.pdb" -print`)
	for pdb in ${_05_lig_pdbs[@]}; do
		lig_name=${pdb%%.*}
		awk '/HETATM/ {if($(NF)!="H") print}' $pdb > ${lig_name}_c.pdb
	done
	 
	local _06_lig_c_pdbs=(`find $TMP_DIR -type f -prune -name "LIG_*_c.pdb" | sort -V`)
	cat ${_06_lig_c_pdbs[@]} > $_07_lig_confomer_pdb

	# 2)
	$BABEL -ipdb $_01_ligand_pdb -omol2 $_08_ligand_red_mol2
	$MOL_TO_PARAM -n $LIG -p $LIG --no-pdb --keep-names --recharge=0 $_08_ligand_red_mol2
	echo "PDB_ROTAMERS $_07_lig_confomer_pdb" >> $_09_lig_params

	# 3)
	awk '/ATOM/ && !/OXT/ {print} END{print "TER"}' $_00_darc_pdb > $_10_protein_pdb
	$REDUCE -Trim $_10_protein_pdb > $_11_receptor_pdb
	awk '
	{
		if(ARGV[1]==FILENAME){
			if(index($0,"ATOM")>0 && index($0,"OXT")==0 && index($0,"HOH")==0)
				{print}
		}
		else{
			if(FNR==1)
				{print "TER"}
			else {
				if(index($0,"OXT")==0) {
					if(index($0,"HETATM")>0)
						{print (substr($0,1,21) "X" substr($0,23))}
					else if(index($0,"ATOM")>0)
						{gsub("ATOM  ","HETATM",$0); print (substr($0,1,21) "X" substr($0,23))}
				}
			}
		}
	} END{print "END"}' $_11_receptor_pdb $_02_ligand_red_pdb > $_12_crystal_complex_pdb

	# 4)
	cat > $_13_option << EOF
-in:file:s $_12_crystal_complex_pdb
-in:file:extra_res_fa $_09_lig_params
-out:path:all $DOCK_RES_DIR
-out:file:scorefile $_14_score_sc
-nstruct $N_CONFORMER
-packing:ex1
-packing:ex2
-packing:no_optH false
-packing:flip_HNQ true
-packing:ignore_ligand_chi true
-parser:protocol $XML_LIB
-mistakes:restore_pre_talaris_2013_behavior true
-qsar:max_grid_cache_size 1
EOF

	$MPIRUN -np $N_THREAD $RLD_MPI @ ${_13_option} > $TMP_DIR/run_log
	grep "SCORE:" $_14_score_sc | awk '{OFS="\t"; print $(NF), $2, $(NF-2), $(NF-11), $(NF-7), $(NF-6)}' > $_15_total_score_r_tsv
}

_02_multiScwrl4(){
	local _scwrl_script=$TMP_DIR/run_scwrl.sh
	local _16_crystal_complex_pdbs=(`find $DOCK_RES_DIR -type f -prune -regextype posix-egrep -regex "$DOCK_RES_DIR/crystal_complex_[0-9]{4}.pdb" -print | sort -V`)

	for pdb in ${_16_crystal_complex_pdbs[@]}; do
		lig_name=${pdb%%.*}
		complex_pdb=${pdb##*/}
		echo "${SCWRL4} -i $pdb -o ${lig_name}_t.pdb ; grep \"HETATM\" $pdb > ${lig_name}_het.pdb ; cat ${lig_name}_{t,het}.pdb > $DOCK_RES_SCWRL_DIR/$complex_pdb"
	done > $_scwrl_script

	cat $_scwrl_script | xargs -P${N_THREAD}  -I@ bash -c "$@@"
}

_03_multiEnva(){
	local _enva_script=$TMP_DIR/run_enva.sh
	local _18_scwrl_complex_pdbs=(`find $DOCK_RES_SCWRL_DIR -type f -prune -regextype posix-egrep -regex "$DOCK_RES_SCWRL_DIR/crystal_complex_[0-9]{4}.pdb" -print | sort -V`)

	for pdb in ${_18_scwrl_complex_pdbs[@]}; do
		lig_name=${pdb%%.*}
		echo "$ENVA -a $pdb > ${lig_name}_aa.out ; $ENVA -c $pdb > ${lig_name}.out"
	done > $_enva_script

	cat $_enva_script | xargs -P${N_THREAD} -I@ bash -c "$@@"
}

_04_sumEnva_a(){
	local _12_crystal_complex_pdb=$TMP_DIR/crystal_complex.pdb
	local _17_crystal_complex_aa_pdb=$TMP_DIR/crystal_complex_aa.pdb
	local _19_enva_a_outs=(`find $DOCK_RES_SCWRL_DIR -type f -prune -name "crystal_complex_*_aa.out" -print | sort -V`)
	local _21_total_rac_ct=$TMP_DIR/total_rac_ct.txt

	$ENVA -a $_12_crystal_complex_pdb > $_17_crystal_complex_aa_pdb

	awk '
	{
		if (ARGV[1]==FILENAME) {
			if($1=="HETATM" && $(NF-3)!="HEM" && $(NF)>0)
				{REF[$(NF-5)"_"$(NF-3)"_"$(NF-2)]=$(NF-5)"_"$(NF-3)"_"$(NF-2)}
		}

		else if (ARGV[2]==FILENAME) {
			for (list in REF) {
				if($1=="ATOM" && list==$6"_"$4"_"$3) {
					ARR_mt_raccs[list]=$(NF)+1
				}
			}
		}

		else {
			split(FILENAME, path, "/");
			name=substr(path[length(path)],1,index(path[length(path)],"_aa.out")-1);

			PROCINFO["sorted_in"]="@ind_num_asc"
			if ($6"_"$4"_"$3 in REF){
				if ($1=="ATOM" || $1=="HETATM") {
						if(name in ARR_raccs)
							{ARR_raccs[name]=ARR_raccs[name]"\t"$(NF)+1; HEAD=HEAD"\tAA_"$6"_"$4"_"$3}
						else
							{ARR_raccs[name]=$(NF)+1 ; HEAD="AA_"$6"_"$4"_"$3}
				}
			}
		}
	}
	END{
		OFS="\t";
		OFMT="%.6f";
		VAR_mt_sum=0;

		for (complex_aa in ARR_mt_raccs) {
			VAR_mt_sum+=ARR_mt_raccs[complex_aa]
		}

		for (aa in ARR_raccs){
			split(ARR_raccs[aa], score, "\t");
			for (i=1; i<=length(score); i++) {
				if(aa in ARR_racc_sum)
					{ARR_racc_sum[aa]+=score[i]}
				else
					{ARR_racc_sum[aa]=score[i]}
			}
		}

		print "PDB",HEAD,"total_rec_acc\tdelta_racc";
		for (pdb in ARR_raccs){
			VAR_del_racc=ARR_racc_sum[pdb]-VAR_mt_sum
			print pdb, ARR_raccs[pdb], ARR_racc_sum[pdb], VAR_del_racc
		}
	}' ${ENVA_LIB} ${_17_crystal_complex_aa_pdb} ${_19_enva_a_outs[@]} > $_21_total_rac_ct
}

_05_sumEnva_c(){
	local _20_enva_c_outs=(`find $DOCK_RES_SCWRL_DIR -type f -prune -regextype posix-egrep -regex "$DOCK_RES_SCWRL_DIR/crystal_complex_[0-9]{4}.out" -print | sort -V`)
	local _22_total_rac_ct2=$TMP_DIR/total_rac_ct2.txt
	local _24_total_sk1=$TMP_DIR/total_sk1.txt

	for cc in ${_20_enva_c_outs[@]}; do
		awk '
		BEGIN{
			INDEX=1;
		}
		{
			if (ARGV[1]==FILENAME) {
				if($1=="HETATM" && $(NF)>0)
					{REF[$(NF-5)"_"$(NF-3)"_"$(NF-2)]=INDEX; INDEX=INDEX+1}
			}

			else if (ARGV[2]==FILENAME) {
				HINGE[$0]=$0
			}

			else {
				split(FILENAME, path, "/");
				name=substr(path[length(path)],1,index(path[length(path)],".out")-1);

				if ($1=="HETATM" && $(NF)>0 && index($0,"HEM")==0) {
					if(name in ARR_lig_acc)
						{ARR_lig_acc[name]=ARR_lig_acc[name]","$10}
					else
						{ARR_lig_acc[name]=$10}

					if($(NF-5)"_"$(NF-3)"_"$(NF-2) in REF) {
						if($(NF-1)<2.0) {
							if(name in ARR_n_bb_n)
								{ARR_n_bb_n[name]=ARR_n_bb_n[name]+1}
							else
								{ARR_n_bb_n[name]=1}
						}
						if(name in ARR_matching_count)
							{ARR_matching_count[name]=ARR_matching_count[name]+1}
						else
							{ARR_matching_count[name]=1}

						if(name in ARR_ref_index)
							{ARR_ref_index[name]=ARR_ref_index[name]"\n"REF[$(NF-5)"_"$(NF-3)"_"$(NF-2)]}
						else
							{ARR_ref_index[name]=REF[$(NF-5)"_"$(NF-3)"_"$(NF-2)]}	
					}
					else {
						ARR_ref_index[name]="\n"
					}
				}

				for (target in HINGE) {
					split(target, s, "_");
					if (length(s)==3) {check=$(NF-5)"_"$(NF-3)"_"$(NF-2)}
					else if (length(s)==2) {check=$(NF-5)"_"$(NF-3)}

					if (target == check) {
						if ($(NF-1)<4.5) {
							if(name in ARR_hdist)
								{ARR_hdist[name]=ARR_hdist[name]","$(NF-1)}
							else
								{ARR_hdist[name]=$(NF-1)}
							if ($(NF-1)<2.0) {
								if(name in ARR_tn_nn)
									{ARR_tn_nn[name]=ARR_tn_nn[name]}
							}
						}
					}
				}
			}
		}
		END{
			OFS="\t";
			OFMT="%.6f";

			for (pdb in ARR_lig_acc) {
				split(ARR_lig_acc[pdb], score, ",");
				for (i=1; i<=length(score); i++ ) {
					if (pdb in ARR_lig_sum)
						{ARR_lig_sum[pdb]=ARR_lig_sum[pdb]+score[i]}
					else
						{ARR_lig_sum[pdb]=score[i]}
				}
				if (length(score)!=0)
					{ARR_ave_lig_acc[pdb]=ARR_lig_sum[pdb]/length(score)+0.1}
				else
					{ARR_ave_lig_acc[pdb]=0.1}

			}

			print "PDB\tHINGE_dist\tHINGE_count\tave_lig_acc\t%Match\tNorm_Bump"
			PROCINFO["sorted_in"]="@ind_num_asc"
			for (pdb in ARR_lig_acc) {
				split(ARR_hdist[pdb],hdist,",");
				if(length(hdist)>0) {
					for (x=1; x<=length(hdist); x++) {
						if(x==1)
							{VAR_min_dist=hdist[x]}
						else
							{if(VAR_min_dist>hist[x]) {VAR_min_dist=hdist[x]}}
					}
				}
				else {
					VAR_min_dist="-"
				}
				VAR_ratio=ARR_matching_count[pdb]/length(REF)
				VAR_cts=length(hdist)-(length(ARR_tn_nn[name]))^2

				print \
				pdb,
				VAR_min_dist,
				VAR_cts,
				ARR_ave_lig_acc[pdb],
				VAR_ratio,
				ARR_matching_count[pdb]-(ARR_n_bb_n[pdb])^2
			}

			for (pdb in ARR_ref_index) {
				print ARR_ref_index[pdb] | "sort -V > '${TMP_DIR}'/"pdb".ser"
			}
		}' ${ENVA_LIB} ${HINGE_LIB} $cc
	done | sort | uniq > $_22_total_rac_ct2

	local _23_crystal_complex_ser=(`find $TMP_DIR -name "*ser" -print | sort -V`)
	for ser in ${_23_crystal_complex_ser[@]}; do
		echo "PDB	skewness	Class	Decision"
		($ISKEW $ser) | awk '{gsub("nan","1.000000"); split($0,a,"/"); print a[length(a)]}' || true
	done | sort | uniq > ${_24_total_sk1}
}

_06_rmsd() {
	local _00_darc_pdb=$1

	local _18_scwrl_complex_pdbs=(`find $DOCK_RES_SCWRL_DIR -type f -prune -regextype posix-egrep -regex "$DOCK_RES_SCWRL_DIR/crystal_complex_[0-9]{4}.pdb" -print | sort -V`)
	local _25_rmsd=$TMP_DIR/rmsd.txt

	for pdb in ${_18_scwrl_complex_pdbs[@]}; do
		echo "PDB	rmsd"
		$RMSD ${_00_darc_pdb%%.pdb} ${pdb%%.pdb} | awk '{split($0,a,"/"); print a[length(a)]}'
	done | sort | uniq > $_25_rmsd
}

_07_mergeEnva(){
	local _21_total_rac_ct=$TMP_DIR/total_rac_ct.txt
	local _22_total_rac_ct2=$TMP_DIR/total_rac_ct2.txt
	local _24_total_sk1=$TMP_DIR/total_sk1.txt
	local _25_rmsd=$TMP_DIR/rmsd.txt
	local _26_total_hinge_scwrl=$STORE_DIR/${SAMPLE_NAME}_total_hinge_scwrl.txt

	join -t$'\t' <(join -t$'\t' ${_25_rmsd} ${_21_total_rac_ct}) <(join -t$'\t' ${_24_total_sk1} ${_22_total_rac_ct2}) | \
	awk '{
		OFS="\t";

		printf $1 "\t" $2 "\t" $(NF)"\t"
		for (i=3; i<NF-7; i++)
			{printf $(i) "\t"}
		print $(NF-2), $(NF-1), $(NF-7), $(NF-6), $(NF-5), $(NF-4), $(NF-3)
	}' > $_26_total_hinge_scwrl
}

_08_cleanTmp() {
	rm -rf $TMP_DIRk
	rm $DOCK_RES_DIR/*_{het,t}.pdb
	rm $DOCK_RES_SCWRL_DIR/*out
}

_09_compressData() {
	local _00_darc_pdb=$1
	local _output=$2

	cd $STORE_DIR/..
	cp ${_00_darc_pdb} ${STORE_DIR}
	tar cfz $_output/${SAMPLE_NAME}_scwrl.tar.gz ${SAMPLE_NAME}
}

_10_rmWorkDir() {
	rm -r $STORE_DIR
}
#####################
# MAIN
#####################
main() {
	local _00_darc_pdb=$1
	local _output=$2

	time _00_checkToolLibDir
	time _01_mpiRLD ${_00_darc_pdb}				# 50min - 샘플에 따라 변화함
	time _02_multiScwrl4					# 30min
	time _03_multiEnva					# 4min
	time _04_sumEnva_a					# 1min
	time _05_sumEnva_c					# 1min
	time _06_rmsd ${_00_darc_pdb}
	time _07_mergeEnva
	time _08_cleanTmp
	time _09_compressData ${_00_darc_pdb} ${_output}	# 3min
	time _10_rmWorkDir

	trap - RETURN INT
	echo "==done==" >&2
}

main ${DARCPDB_ARG} ${OUTPUT_ARG}
