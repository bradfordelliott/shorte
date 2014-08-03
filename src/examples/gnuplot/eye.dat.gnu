# This plot is based around GNUplot 4.4 and likely will
# not work in earlier versions
set terminal pngcairo transparent crop enhanced font "arial,10" size 600,600
set output "$OUTPUT_FILE"
set border 895 front linetype -1 linewidth 1.000
set grid nopolar
set grid xtics nomxtics ytics nomytics noztics nomztics \
 nox2tics nomx2tics noy2tics nomy2tics nocbtics nomcbtics
set grid layerdefault   linetype 0 linewidth 1.000,  linetype 0 linewidth 1.000
set style line 100  linetype 5 linewidth 0.500 pointtype 100 pointsize default
set view map
unset surface
set style data pm3d
set style function pm3d
set ticslevel 0
set nomcbtics
set palette model RGB
set palette model RGB defined (0 "#339933", 1 "yellow", 2 "orange", 3 "#ff0000" )
set title "Eye Monitor Plot (Voltage vs. Phase)"
set xlabel "Phase"
set xrange [ 0 : 62 ] noreverse nowriteback
set ylabel "Voltage" 
set yrange [ 0 : 126 ] noreverse nowriteback
set zrange [ * : * ] noreverse nowriteback  # (currently [0:60.0000] )
set cbrange [ 0 : * ] noreverse nowriteback  # (currently [-15.0000:4.00000] )
set lmargin  0
set pm3d implicit at b
set pm3d scansforward
splot "$DATA_FILE" notitle
