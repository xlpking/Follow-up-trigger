OT3list=/Volumes/Data/Documents/GitHub/Follow-up-trigger/GWAC_OT3.txt
#OT3list=/home/gwac/software/GWAC_OT3.txt
if test ! -r oldlist
then
	touch oldlist
fi

xgaia_dr2 ( )
{
	cat listmatch1 | while read line
	do
		echo "xgaia_dr2"
		str_radec=`echo $line | awk '{print($2"+"$3)}'`
		str_ot3=`echo $line | awk '{print($1)}'`
		outputfile=`echo $str_ot3 | awk '{print($1"_gaiadr2.txt")}'`
		python find_gaia_dr2.py  -r 2 "$str_radec" >$outputfile
		wait
		echo "ouputfile is $outputfile"
                sed -n '66,66p' $outputfile >tmp
                cat tmp
                if test -s tmp
                then
                    echo "================" >>xgetcat.log
                    echo "have source in the Gaia dr2 for $str_ot3" >>xgetcat.log
                    cat $outputfile >>xgetcat.log
                    echo "=============" >>xgetcat.log
                else
                    echo "=============" >>xgetcat.log
                    echo "no source in the Gaia dr2 for $str_ot3" 
                    echo "no source in the Gaia dr2 for $str_ot3" >>xgetcat.log 
                    echo "=============" >>xgetcat.log
                fi
	done
	echo "========over for this run======="
}


xchecknewsource ( )
{

diff oldlist $OT3list | grep  ">" | tr -d '>' | column -t | head -1 >listmatch1
Nline=`cat listmatch1 | wc -l | awk '{print($1)}'`
if [ $Nline > 0  ]
then
	echo "have new source"
	xgaia_dr2
	wait
	cat listmatch1 >>oldlist
fi

}

xgetcat ( )
{
	if test -s $OT3list
	then
		echo "have $OT3list"
		xchecknewsource
		#xgaia_dr2
	else
		echo "no souce file"
	fi
}
while :
do
	echo "new run"
	xgetcat
	sleep 10
done
